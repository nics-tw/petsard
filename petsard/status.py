"""
PETsARD Status Module - 以 Metadater 為核心的狀態管理

本模組提供以 Metadater 為核心的狀態管理機制，包含完整的進度快照功能。
"""

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from petsard.exceptions import UnexecutedError
from petsard.metadater import Metadater, SchemaMetadata
from petsard.operator import BaseOperator
from petsard.processor import Processor
from petsard.synthesizer import Synthesizer


@dataclass(frozen=True)
class ExecutionSnapshot:
    """
    執行快照 - 記錄每個模組執行前後的完整狀態

    Attributes:
        snapshot_id: 快照唯一識別碼
        module_name: 模組名稱
        experiment_name: 實驗名稱
        timestamp: 快照建立時間
        metadata_before: 執行前的元資料狀態
        metadata_after: 執行後的元資料狀態
        execution_context: 執行上下文資訊
    """

    snapshot_id: str
    module_name: str
    experiment_name: str
    timestamp: datetime
    metadata_before: Optional[SchemaMetadata] = None
    metadata_after: Optional[SchemaMetadata] = None
    execution_context: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MetadataChange:
    """
    元資料變更記錄

    Attributes:
        change_id: 變更唯一識別碼
        change_type: 變更類型 ('create', 'update', 'delete')
        target_type: 目標類型 ('schema', 'field')
        target_id: 目標識別碼
        before_state: 變更前狀態
        after_state: 變更後狀態
        timestamp: 變更時間
        module_context: 模組上下文
    """

    change_id: str
    change_type: str  # 'create', 'update', 'delete'
    target_type: str  # 'schema', 'field'
    target_id: str
    before_state: Optional[Any] = None
    after_state: Optional[Any] = None
    timestamp: datetime = field(default_factory=datetime.now)
    module_context: str = ""


@dataclass(frozen=True)
class TimingRecord:
    """
    計時記錄 - 記錄每個模組和步驟的執行時間

    Attributes:
        record_id: 記錄唯一識別碼
        module_name: 模組名稱
        experiment_name: 實驗名稱
        step_name: 步驟名稱 (如 'run', 'fit', 'sample', 'eval' 等)
        start_time: 開始時間
        end_time: 結束時間
        duration_seconds: 執行時間（秒）
        context: 額外的上下文資訊
        duration_precision: duration_seconds 的小數位數精度，預設為 2
    """

    record_id: str
    module_name: str
    experiment_name: str
    step_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    context: Dict[str, Any] = field(default_factory=dict)
    duration_precision: int = 2

    def complete(
        self,
        end_time: Optional[datetime] = None,
        duration_precision: Optional[int] = None,
    ) -> "TimingRecord":
        """完成計時記錄"""
        if end_time is None:
            end_time = datetime.now()

        duration = (end_time - self.start_time).total_seconds()

        # 使用指定的精度或預設精度
        precision = (
            duration_precision
            if duration_precision is not None
            else self.duration_precision
        )
        rounded_duration = round(duration, precision)

        return TimingRecord(
            record_id=self.record_id,
            module_name=self.module_name,
            experiment_name=self.experiment_name,
            step_name=self.step_name,
            start_time=self.start_time,
            end_time=end_time,
            duration_seconds=rounded_duration,
            context=self.context,
            duration_precision=precision,
        )

    def get_formatted_duration(self) -> str:
        """取得格式化的持續時間字串"""
        if self.duration_seconds is None:
            return "N/A"
        return f"{self.duration_seconds:.{self.duration_precision}f}s"


class TimingLogHandler(logging.Handler):
    """
    自定義 logging handler 來捕獲 Operator 的時間資訊
    """

    def __init__(self, status_instance):
        super().__init__()
        self.status = status_instance
        self._timing_pattern = re.compile(
            r"TIMING_(START|END|ERROR)\|([^|]+)\|([^|]+)\|([^|]+)(?:\|([^|]+))?(?:\|(.+))?"
        )

    def emit(self, record):
        """處理 log 記錄，解析時間資訊"""
        try:
            message = record.getMessage()
            match = self._timing_pattern.match(message)

            if match:
                timing_type = match.group(1)  # START, END, ERROR
                module_name = match.group(2)  # 模組名稱
                step_name = match.group(3)  # 步驟名稱
                timestamp = float(match.group(4))  # 時間戳
                duration = float(match.group(5)) if match.group(5) else None  # 持續時間
                error_msg = match.group(6) if match.group(6) else None  # 錯誤訊息

                # 從 status 中取得當前模組的實驗名稱
                # 嘗試匹配模組名稱（移除 "Op" 後綴）
                clean_module_name = module_name.replace("Op", "")
                expt_name = self.status._current_experiments.get(
                    clean_module_name, "default"
                )

                # 如果還是找不到，嘗試直接匹配
                if expt_name == "default":
                    expt_name = self.status._current_experiments.get(
                        module_name, "default"
                    )

                if timing_type == "START":
                    self.status._handle_timing_start(
                        module_name, expt_name, step_name, timestamp
                    )
                elif timing_type in ["END", "ERROR"]:
                    context = {}
                    if timing_type == "ERROR" and error_msg:
                        context["error"] = error_msg
                        context["status"] = "error"
                    else:
                        context["status"] = "completed"

                    self.status._handle_timing_end(
                        module_name, expt_name, step_name, timestamp, duration, context
                    )

        except Exception:
            # 避免 logging handler 本身出錯影響主程式
            pass


class Status:
    """
    以 Metadater 為核心的狀態管理器

    提供完整的進度快照機制，追蹤每個模組執行前後的元資料變化。
    保持與原有 Status 介面的相容性。
    """

    def __init__(self, config):
        """
        初始化狀態管理器

        Args:
            config: 配置物件
        """
        self.config = config
        self.sequence: list = config.sequence
        self._logger = logging.getLogger(f"PETsARD.{self.__class__.__name__}")

        # 核心 Metadater 實例
        self.metadater = Metadater()

        # 狀態儲存 - 保持與原有介面相容
        self.status: dict = {}
        self.metadata: dict[str, SchemaMetadata] = {}

        # 新增的快照和變更追蹤功能
        self.snapshots: List[ExecutionSnapshot] = []
        self.change_history: List[MetadataChange] = []
        self._snapshot_counter = 0
        self._change_counter = 0

        # 新增的時間記錄功能
        self.timing_records: List[TimingRecord] = []
        self._timing_counter = 0
        self._active_timings: Dict[str, TimingRecord] = {}  # 追蹤進行中的計時

        # 原有功能的相容性支援
        if "Splitter" in self.sequence:
            self.exist_train_indices: list[set] = []
        if "Reporter" in self.sequence:
            self.report: dict = {}

        # 設置 logging handler 來捕獲時間資訊
        self._timing_handler = TimingLogHandler(self)
        self._timing_handler.setLevel(logging.INFO)

        # 將 handler 添加到 PETsARD 的根 logger
        petsard_logger = logging.getLogger("PETsARD")
        petsard_logger.addHandler(self._timing_handler)

        # 儲存當前實驗名稱的映射
        self._current_experiments: Dict[str, str] = {}

    def _generate_snapshot_id(self) -> str:
        """生成快照 ID"""
        self._snapshot_counter += 1
        return f"snapshot_{self._snapshot_counter:06d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def _generate_change_id(self) -> str:
        """生成變更 ID"""
        self._change_counter += 1
        return f"change_{self._change_counter:06d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def _generate_timing_id(self) -> str:
        """生成計時 ID"""
        self._timing_counter += 1
        return f"timing_{self._timing_counter:06d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def _create_snapshot(
        self,
        module: str,
        expt: str,
        metadata_before: Optional[SchemaMetadata] = None,
        metadata_after: Optional[SchemaMetadata] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> ExecutionSnapshot:
        """
        建立執行快照

        Args:
            module: 模組名稱
            expt: 實驗名稱
            metadata_before: 執行前元資料
            metadata_after: 執行後元資料
            context: 執行上下文

        Returns:
            ExecutionSnapshot: 建立的快照
        """
        snapshot = ExecutionSnapshot(
            snapshot_id=self._generate_snapshot_id(),
            module_name=module,
            experiment_name=expt,
            timestamp=datetime.now(),
            metadata_before=metadata_before,
            metadata_after=metadata_after,
            execution_context=context or {},
        )

        self.snapshots.append(snapshot)
        self._logger.debug(f"建立快照: {snapshot.snapshot_id} for {module}[{expt}]")
        return snapshot

    def _track_metadata_change(
        self,
        change_type: str,
        target_type: str,
        target_id: str,
        before_state: Optional[Any] = None,
        after_state: Optional[Any] = None,
        module_context: str = "",
    ) -> MetadataChange:
        """
        追蹤元資料變更

        Args:
            change_type: 變更類型
            target_type: 目標類型
            target_id: 目標 ID
            before_state: 變更前狀態
            after_state: 變更後狀態
            module_context: 模組上下文

        Returns:
            MetadataChange: 變更記錄
        """
        change = MetadataChange(
            change_id=self._generate_change_id(),
            change_type=change_type,
            target_type=target_type,
            target_id=target_id,
            before_state=before_state,
            after_state=after_state,
            module_context=module_context,
        )

        self.change_history.append(change)
        self._logger.debug(
            f"追蹤變更: {change.change_id} - {change_type} {target_type}"
        )
        return change

    def start_timing(
        self,
        module: str,
        expt: str,
        step: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        開始計時

        Args:
            module: 模組名稱
            expt: 實驗名稱
            step: 步驟名稱
            context: 額外的上下文資訊

        Returns:
            str: 計時記錄 ID
        """
        timing_id = self._generate_timing_id()
        timing_key = f"{module}_{expt}_{step}"

        timing_record = TimingRecord(
            record_id=timing_id,
            module_name=module,
            experiment_name=expt,
            step_name=step,
            start_time=datetime.now(),
            context=context or {},
            duration_precision=2,  # 預設精度為 2
        )

        self._active_timings[timing_key] = timing_record
        self._logger.debug(f"開始計時: {timing_key} - {timing_id}")

        return timing_id

    def end_timing(
        self,
        module: str,
        expt: str,
        step: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[TimingRecord]:
        """
        結束計時

        Args:
            module: 模組名稱
            expt: 實驗名稱
            step: 步驟名稱
            context: 額外的上下文資訊

        Returns:
            Optional[TimingRecord]: 完成的計時記錄，如果沒有找到對應的開始記錄則返回 None
        """
        timing_key = f"{module}_{expt}_{step}"

        if timing_key not in self._active_timings:
            self._logger.warning(f"找不到對應的開始計時記錄: {timing_key}")
            return None

        active_timing = self._active_timings.pop(timing_key)

        # 合併額外的上下文資訊
        if context:
            merged_context = active_timing.context.copy()
            merged_context.update(context)
        else:
            merged_context = active_timing.context

        completed_timing = active_timing.complete()
        # 更新 context
        completed_timing = TimingRecord(
            record_id=completed_timing.record_id,
            module_name=completed_timing.module_name,
            experiment_name=completed_timing.experiment_name,
            step_name=completed_timing.step_name,
            start_time=completed_timing.start_time,
            end_time=completed_timing.end_time,
            duration_seconds=completed_timing.duration_seconds,
            context=merged_context,
            duration_precision=completed_timing.duration_precision,
        )

        self.timing_records.append(completed_timing)

        formatted_duration = str(
            timedelta(seconds=round(completed_timing.duration_seconds))
        )
        self._logger.debug(f"結束計時: {timing_key} - 耗時: {formatted_duration}")

        return completed_timing

    def _handle_timing_start(self, module: str, expt: str, step: str, timestamp: float):
        """
        處理從 logging 解析的開始計時資訊

        Args:
            module: 模組名稱
            expt: 實驗名稱
            step: 步驟名稱
            timestamp: 時間戳
        """
        timing_id = self._generate_timing_id()
        timing_key = f"{module}_{expt}_{step}"

        timing_record = TimingRecord(
            record_id=timing_id,
            module_name=module,
            experiment_name=expt,
            step_name=step,
            start_time=datetime.fromtimestamp(timestamp),
            context={"source": "logging"},
            duration_precision=2,  # 預設精度為 2
        )

        self._active_timings[timing_key] = timing_record
        self._logger.debug(f"從 logging 開始計時: {timing_key} - {timing_id}")

    def _handle_timing_end(
        self,
        module: str,
        expt: str,
        step: str,
        timestamp: float,
        duration: Optional[float],
        context: Dict[str, Any],
    ):
        """
        處理從 logging 解析的結束計時資訊

        Args:
            module: 模組名稱
            expt: 實驗名稱
            step: 步驟名稱
            timestamp: 結束時間戳
            duration: 持續時間（秒）
            context: 上下文資訊
        """
        timing_key = f"{module}_{expt}_{step}"

        if timing_key in self._active_timings:
            # 有對應的開始記錄
            active_timing = self._active_timings.pop(timing_key)

            # 合併上下文
            merged_context = active_timing.context.copy()
            merged_context.update(context)

            completed_timing = TimingRecord(
                record_id=active_timing.record_id,
                module_name=active_timing.module_name,
                experiment_name=active_timing.experiment_name,
                step_name=active_timing.step_name,
                start_time=active_timing.start_time,
                end_time=datetime.fromtimestamp(timestamp),
                duration_seconds=round(duration, 2) if duration is not None else None,
                context=merged_context,
                duration_precision=2,
            )
        else:
            # 沒有對應的開始記錄，直接創建一個完整的記錄
            timing_id = self._generate_timing_id()
            start_time = datetime.fromtimestamp(timestamp - (duration or 0))

            completed_timing = TimingRecord(
                record_id=timing_id,
                module_name=module,
                experiment_name=expt,
                step_name=step,
                start_time=start_time,
                end_time=datetime.fromtimestamp(timestamp),
                duration_seconds=round(duration, 2) if duration is not None else None,
                context={**context, "source": "logging", "orphaned": True},
                duration_precision=2,
            )

        self.timing_records.append(completed_timing)

        formatted_duration = (
            str(timedelta(seconds=round(completed_timing.duration_seconds)))
            if completed_timing.duration_seconds
            else "N/A"
        )
        self._logger.debug(
            f"從 logging 結束計時: {timing_key} - 耗時: {formatted_duration}"
        )

    def put(self, module: str, expt: str, operator: BaseOperator):
        """
        新增模組狀態和操作器到狀態字典

        這是核心方法，整合了 Metadater 的快照功能

        Args:
            module: 當前模組名稱
            expt: 當前實驗名稱
            operator: 當前操作器
        """
        # 記錄當前模組的實驗名稱，供 logging handler 使用
        self._current_experiments[module] = expt
        # 取得執行前的元資料狀態
        metadata_before = self.metadata.get(module) if module in self.metadata else None

        # 狀態更新邏輯 (保持原有邏輯)
        if module in self.status:
            module_seq_idx = self.sequence.index(module)
            module_to_keep = set(self.sequence[: module_seq_idx + 1])
            keys_to_remove = [key for key in self.status if key not in module_to_keep]
            for exist_module in keys_to_remove:
                del self.status[exist_module]

        # 使用 Metadater 管理元資料
        if module in ["Loader", "Splitter", "Preprocessor"]:
            new_metadata = operator.get_metadata()

            # 追蹤元資料變更
            if metadata_before is not None:
                self._track_metadata_change(
                    change_type="update",
                    target_type="schema",
                    target_id=new_metadata.schema_id,
                    before_state=metadata_before,
                    after_state=new_metadata,
                    module_context=f"{module}[{expt}]",
                )
            else:
                self._track_metadata_change(
                    change_type="create",
                    target_type="schema",
                    target_id=new_metadata.schema_id,
                    after_state=new_metadata,
                    module_context=f"{module}[{expt}]",
                )

            self.set_metadata(module, new_metadata)

        # Reporter 處理
        if module == "Reporter":
            self.set_report(report=operator.get_result())

        # Splitter 處理 - 更新 exist_train_indices
        if module == "Splitter" and hasattr(operator, "get_train_indices"):
            train_indices = operator.get_train_indices()
            self.update_exist_train_indices(train_indices)

        # 建立執行快照
        metadata_after = self.metadata.get(module)
        self._create_snapshot(
            module=module,
            expt=expt,
            metadata_before=metadata_before,
            metadata_after=metadata_after,
            context={
                "operator_type": type(operator).__name__,
                "sequence_position": self.sequence.index(module)
                if module in self.sequence
                else -1,
            },
        )

        # 更新狀態字典 (保持原有格式)
        temp = {}
        temp["expt"] = expt
        temp["operator"] = operator
        self.status[module] = temp

        self._logger.info(
            f"狀態已更新: {module}[{expt}] - 快照數量: {len(self.snapshots)}"
        )

    # === 原有介面方法 (保持相容性) ===

    def set_report(self, report: dict) -> None:
        """新增報告資料到報告字典"""
        if not hasattr(self, "report"):
            raise UnexecutedError

        for eval_expt_name, report_data in report.items():
            self.report[eval_expt_name] = report_data.copy()

    def get_pre_module(self, curr_module: str) -> str:
        """取得序列中的前一個模組"""
        module_idx = self.sequence.index(curr_module)
        if module_idx == 0:
            return None
        else:
            return self.sequence[module_idx - 1]

    def get_result(self, module: str) -> Union[dict, pd.DataFrame]:
        """取得特定模組的結果"""
        return self.status[module]["operator"].get_result()

    def get_full_expt(self, module: str = None) -> dict:
        """取得模組名稱和對應實驗名稱的字典"""
        if module is None:
            return {
                seq_module: self.status[seq_module]["expt"]
                for seq_module in self.sequence
                if seq_module in self.status
            }
        else:
            if module not in self.sequence:
                from petsard.exceptions import ConfigError

                raise ConfigError

            module_idx = self.sequence.index(module) + 1
            sub_sequence = self.sequence[:module_idx]
            return {
                seq_module: self.status[seq_module]["expt"]
                for seq_module in sub_sequence
            }

    def get_exist_train_indices(self) -> list[set]:
        """取得 Splitter 模組生成的唯一訓練索引集合列表"""
        return self.exist_train_indices

    def update_exist_train_indices(self, new_indices: list[set]) -> None:
        """
        更新 exist_train_indices，將新的訓練索引加入到集合列表中

        Args:
            new_indices: 新的訓練索引集合列表 list[set]
        """
        if not hasattr(self, "exist_train_indices"):
            self.exist_train_indices = []

        for index_set in new_indices:
            self.exist_train_indices.append(index_set)

    def set_metadata(self, module: str, metadata: SchemaMetadata) -> None:
        """設定給定模組的元資料"""
        self.metadata[module] = metadata

    def get_metadata(self, module: str = "Loader") -> SchemaMetadata:
        """取得資料集的元資料"""
        if module not in self.metadata:
            raise UnexecutedError
        return self.metadata[module]

    def get_synthesizer(self) -> Synthesizer:
        """取得合成器實例"""
        if "Synthesizer" in self.status:
            return self.status["Synthesizer"]["operator"].synthesizer
        else:
            raise UnexecutedError

    def get_processor(self) -> Processor:
        """取得資料集的處理器"""
        if "Preprocessor" in self.status:
            return self.status["Preprocessor"]["operator"].processor
        else:
            raise UnexecutedError

    def get_report(self) -> dict:
        """取得 Reporter 模組生成的報告資料"""
        if not hasattr(self, "report"):
            raise UnexecutedError
        return self.report

    # === 新增的快照和變更追蹤方法 ===

    def get_snapshots(self, module: str = None) -> List[ExecutionSnapshot]:
        """
        取得快照列表

        Args:
            module: 可選的模組名稱過濾

        Returns:
            List[ExecutionSnapshot]: 快照列表
        """
        if module is None:
            return self.snapshots.copy()
        else:
            return [s for s in self.snapshots if s.module_name == module]

    def get_snapshot_by_id(self, snapshot_id: str) -> Optional[ExecutionSnapshot]:
        """
        根據 ID 取得特定快照

        Args:
            snapshot_id: 快照 ID

        Returns:
            Optional[ExecutionSnapshot]: 快照物件或 None
        """
        for snapshot in self.snapshots:
            if snapshot.snapshot_id == snapshot_id:
                return snapshot
        return None

    def get_change_history(self, module: str = None) -> List[MetadataChange]:
        """
        取得變更歷史

        Args:
            module: 可選的模組名稱過濾

        Returns:
            List[MetadataChange]: 變更記錄列表
        """
        if module is None:
            return self.change_history.copy()
        else:
            return [c for c in self.change_history if module in c.module_context]

    def get_metadata_evolution(self, module: str = "Loader") -> List[SchemaMetadata]:
        """
        取得特定模組的元資料演進歷史

        Args:
            module: 模組名稱

        Returns:
            List[SchemaMetadata]: 元資料演進列表
        """
        evolution = []
        for snapshot in self.snapshots:
            if snapshot.module_name == module:
                if snapshot.metadata_before:
                    evolution.append(snapshot.metadata_before)
                if snapshot.metadata_after:
                    evolution.append(snapshot.metadata_after)
        return evolution

    def restore_from_snapshot(self, snapshot_id: str) -> bool:
        """
        從快照恢復狀態 (基礎實作)

        Args:
            snapshot_id: 快照 ID

        Returns:
            bool: 是否成功恢復
        """
        snapshot = self.get_snapshot_by_id(snapshot_id)
        if snapshot is None:
            self._logger.error(f"找不到快照: {snapshot_id}")
            return False

        try:
            # 基礎恢復邏輯 - 恢復元資料狀態
            if snapshot.metadata_after:
                self.metadata[snapshot.module_name] = snapshot.metadata_after
                self._logger.info(
                    f"已從快照 {snapshot_id} 恢復 {snapshot.module_name} 的元資料"
                )
                return True
        except Exception as e:
            self._logger.error(f"從快照恢復失敗: {e}")
            return False

        return False

    def get_status_summary(self) -> Dict[str, Any]:
        """
        取得狀態摘要資訊

        Returns:
            Dict[str, Any]: 狀態摘要
        """
        return {
            "sequence": self.sequence,
            "active_modules": list(self.status.keys()),
            "metadata_modules": list(self.metadata.keys()),
            "total_snapshots": len(self.snapshots),
            "total_changes": len(self.change_history),
            "last_snapshot": self.snapshots[-1].snapshot_id if self.snapshots else None,
            "last_change": self.change_history[-1].change_id
            if self.change_history
            else None,
        }

    def get_timing_records(self, module: str = None) -> List[TimingRecord]:
        """
        取得特定模組的時間記錄

        Args:
            module: 可選的模組名稱過濾，如果為 None 則返回所有記錄

        Returns:
            List[TimingRecord]: 時間記錄列表
        """
        if module is None:
            return self.timing_records.copy()
        else:
            return [r for r in self.timing_records if r.module_name == module]

    def get_timing_report_data(self) -> pd.DataFrame:
        """
        取得適合 Reporter 使用的時間記錄資料

        Returns:
            pd.DataFrame: 時間記錄的 DataFrame
        """
        if not self.timing_records:
            return pd.DataFrame()

        data = []
        for record in self.timing_records:
            data.append(
                {
                    "record_id": record.record_id,
                    "module_name": record.module_name,
                    "experiment_name": record.experiment_name,
                    "step_name": record.step_name,
                    "start_time": record.start_time.isoformat(),
                    "end_time": record.end_time.isoformat()
                    if record.end_time
                    else None,
                    "duration_seconds": record.duration_seconds,
                    **record.context,  # 展開 context 中的額外資訊
                }
            )

        return pd.DataFrame(data)
