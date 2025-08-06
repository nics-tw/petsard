import logging
import re
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

import pandas as pd

from petsard.adapter import BaseAdapter
from petsard.exceptions import SnapshotError, StatusError, TimingError, UnexecutedError
from petsard.metadater import MetadataChange, Metadater, SchemaMetadata
from petsard.processor import Processor
from petsard.synthesizer import Synthesizer


@dataclass(frozen=True)
class ExecutionSnapshot:
    """
    簡化的執行快照
    """

    snapshot_id: str
    module_name: str
    experiment_name: str
    timestamp: datetime
    metadata_before: SchemaMetadata | None = None
    metadata_after: SchemaMetadata | None = None
    context: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TimingRecord:
    """
    簡化的計時記錄
    """

    record_id: str
    module_name: str
    experiment_name: str
    step_name: str
    start_time: datetime
    end_time: datetime | None = None
    duration_seconds: float | None = None
    context: dict[str, Any] = field(default_factory=dict)

    def complete(self, end_time: datetime | None = None) -> "TimingRecord":
        """完成計時記錄"""
        if end_time is None:
            end_time = datetime.now()

        duration = round((end_time - self.start_time).total_seconds(), 2)

        return TimingRecord(
            record_id=self.record_id,
            module_name=self.module_name,
            experiment_name=self.experiment_name,
            step_name=self.step_name,
            start_time=self.start_time,
            end_time=end_time,
            duration_seconds=duration,
            context=self.context,
        )

    @property
    def formatted_duration(self) -> str:
        """格式化的持續時間"""
        return f"{self.duration_seconds:.2f}s" if self.duration_seconds else "N/A"


class TimingLogHandler(logging.Handler):
    """
    簡化的計時日誌處理器
    """

    def __init__(self, status_instance):
        super().__init__()
        self.status = status_instance
        self._timing_pattern = re.compile(
            r"TIMING_(\w+)\|([^|]+)\|([^|]+)\|([^|]+)(?:\|([^|]+))?"
        )

    def emit(self, record):
        """處理計時日誌記錄"""
        try:
            message = record.getMessage()
            if not message.startswith("TIMING_"):
                return

            match = self._timing_pattern.match(message)
            if not match:
                return

            timing_type, module_name, step_name, timestamp_str, duration_str = (
                match.groups()
            )
            timestamp = float(timestamp_str)
            duration = float(duration_str) if duration_str else None

            expt_name = self.status._current_experiments.get(module_name, "default")

            if timing_type == "START":
                self.status._handle_timing_start(
                    module_name, expt_name, step_name, timestamp
                )
            elif timing_type in ["END", "ERROR"]:
                context = {"status": "error" if timing_type == "ERROR" else "completed"}
                self.status._handle_timing_end(
                    module_name, expt_name, step_name, timestamp, duration, context
                )

        except (ValueError, TypeError, AttributeError):
            pass  # 靜默忽略解析錯誤


class Status:
    """
    以 Metadater 為核心的狀態管理器

    提供完整的進度快照機制，追蹤每個模組執行前後的元資料變化。
    保持與原有 Status 介面的相容性。
    """

    def __init__(
        self,
        config,
        max_snapshots: int = 1000,
        max_changes: int = 5000,
        max_timings: int = 10000,
    ):
        """
        初始化狀態管理器

        Args:
            config: 配置物件
            max_snapshots: 最大快照數量，防止記憶體洩漏
            max_changes: 最大變更記錄數量
            max_timings: 最大計時記錄數量
        """
        self.config = config
        self.sequence: list = config.sequence
        self._logger = logging.getLogger(f"PETsARD.{self.__class__.__name__}")

        # 核心 Metadater 實例 - 包含變更追蹤功能
        self.metadater = Metadater(max_changes=max_changes)

        # 狀態儲存 - 保持與原有介面相容
        self.status: dict = {}
        self.metadata: dict[str, SchemaMetadata] = {}

        # 優化的快照功能 - 使用 deque 限制大小
        self.max_snapshots = max_snapshots
        self.max_timings = max_timings

        self.snapshots: deque[ExecutionSnapshot] = deque(maxlen=max_snapshots)
        self._snapshot_counter = 0

        # 快照索引，使用弱引用字典避免記憶體洩漏
        self._snapshot_index: dict[str, ExecutionSnapshot] = {}

        # 優化的時間記錄功能
        self.timing_records: deque[TimingRecord] = deque(maxlen=max_timings)
        self._timing_counter = 0
        self._active_timings: dict[str, TimingRecord] = {}  # 追蹤進行中的計時

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
        self._current_experiments: dict[str, str] = {}

    def _generate_id(self, prefix: str, counter_attr: str) -> str:
        """
        統一的 ID 生成方法，避免程式碼重複

        Args:
            prefix: ID 前綴 (如 'snapshot', 'change', 'timing')
            counter_attr: 計數器屬性名稱 (如 '_snapshot_counter')

        Returns:
            str: 生成的唯一 ID
        """
        current_counter = getattr(self, counter_attr)
        setattr(self, counter_attr, current_counter + 1)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{current_counter + 1:06d}_{timestamp}"

    def _generate_snapshot_id(self) -> str:
        """生成快照 ID"""
        return self._generate_id("snapshot", "_snapshot_counter")

    def _generate_timing_id(self) -> str:
        """生成計時 ID"""
        return self._generate_id("timing", "_timing_counter")

    def _create_snapshot(
        self,
        module: str,
        expt: str,
        metadata_before: SchemaMetadata | None = None,
        metadata_after: SchemaMetadata | None = None,
        context: dict[str, Any] | None = None,
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
            context=context or {},
        )

        self.snapshots.append(snapshot)
        # 更新索引
        self._snapshot_index[snapshot.snapshot_id] = snapshot
        # 如果超過限制，清理舊的索引項目
        if (
            len(self.snapshots) == self.max_snapshots
            and len(self._snapshot_index) > self.max_snapshots
        ):
            # 清理不在 deque 中的索引項目
            valid_ids = {s.snapshot_id for s in self.snapshots}
            self._snapshot_index = {
                k: v for k, v in self._snapshot_index.items() if k in valid_ids
            }

        self._logger.debug(f"建立快照: {snapshot.snapshot_id} for {module}[{expt}]")
        return snapshot

    def start_timing(
        self,
        module: str,
        expt: str,
        step: str,
        context: dict[str, Any] | None = None,
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
        )

        self._active_timings[timing_key] = timing_record
        self._logger.debug(f"開始計時: {timing_key} - {timing_id}")

        return timing_id

    def end_timing(
        self,
        module: str,
        expt: str,
        step: str,
        context: dict[str, Any] | None = None,
    ) -> TimingRecord | None:
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
        )

        self.timing_records.append(completed_timing)

        formatted_duration = str(
            timedelta(seconds=round(completed_timing.duration_seconds))
        )
        self._logger.debug(f"結束計時: {timing_key} - 耗時: {formatted_duration}")

        return completed_timing

    def _create_timing_record(
        self,
        timing_id: str,
        module: str,
        expt: str,
        step: str,
        start_time: datetime,
        end_time: datetime | None = None,
        duration_seconds: float | None = None,
        context: dict[str, Any] | None = None,
    ) -> TimingRecord:
        """
        統一的計時記錄創建方法，避免程式碼重複

        Args:
            timing_id: 計時記錄 ID
            module: 模組名稱
            expt: 實驗名稱
            step: 步驟名稱
            start_time: 開始時間
            end_time: 結束時間
            duration_seconds: 持續時間（秒）
            context: 上下文資訊

        Returns:
            TimingRecord: 創建的計時記錄
        """
        return TimingRecord(
            record_id=timing_id,
            module_name=module,
            experiment_name=expt,
            step_name=step,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration_seconds,
            context=context or {},
        )

    def _handle_timing_start(self, module: str, expt: str, step: str, timestamp: float):
        """
        處理從 logging 解析的開始計時資訊

        Args:
            module: 模組名稱
            expt: 實驗名稱
            step: 步驟名稱
            timestamp: 時間戳
        """
        try:
            timing_id = self._generate_timing_id()
            timing_key = f"{module}_{expt}_{step}"
            start_time = datetime.fromtimestamp(timestamp)

            timing_record = self._create_timing_record(
                timing_id=timing_id,
                module=module,
                expt=expt,
                step=step,
                start_time=start_time,
                context={"source": "logging"},
            )

            self._active_timings[timing_key] = timing_record
            self._logger.debug(f"從 logging 開始計時: {timing_key} - {timing_id}")

        except (ValueError, OSError) as e:
            raise TimingError(f"無法處理計時開始事件: {e}") from e

    def _handle_timing_end(
        self,
        module: str,
        expt: str,
        step: str,
        timestamp: float,
        duration: float | None,
        context: dict[str, Any],
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
        try:
            timing_key = f"{module}_{expt}_{step}"
            end_time = datetime.fromtimestamp(timestamp)
            rounded_duration = round(duration, 2) if duration is not None else None

            if timing_key in self._active_timings:
                # 有對應的開始記錄
                active_timing = self._active_timings.pop(timing_key)
                merged_context = active_timing.context.copy()
                merged_context.update(context)

                completed_timing = self._create_timing_record(
                    timing_id=active_timing.record_id,
                    module=module,
                    expt=expt,
                    step=step,
                    start_time=active_timing.start_time,
                    end_time=end_time,
                    duration_seconds=rounded_duration,
                    context=merged_context,
                )
            else:
                # 沒有對應的開始記錄，創建孤立記錄
                timing_id = self._generate_timing_id()
                start_time = datetime.fromtimestamp(timestamp - (duration or 0))
                orphaned_context = {**context, "source": "logging", "orphaned": True}

                completed_timing = self._create_timing_record(
                    timing_id=timing_id,
                    module=module,
                    expt=expt,
                    step=step,
                    start_time=start_time,
                    end_time=end_time,
                    duration_seconds=rounded_duration,
                    context=orphaned_context,
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

        except (ValueError, OSError) as e:
            raise TimingError(f"無法處理計時結束事件: {e}") from e

    def put(self, module: str, expt: str, operator: BaseAdapter):
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

            # 使用 Metadater 追蹤元資料變更
            if metadata_before is not None:
                self.metadater.track_metadata_change(
                    change_type="update",
                    target_type="schema",
                    target_id=new_metadata.schema_id,
                    before_state=metadata_before,
                    after_state=new_metadata,
                    module_context=f"{module}[{expt}]",
                )
            else:
                self.metadater.track_metadata_change(
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

    def get_result(self, module: str) -> dict | pd.DataFrame:
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

    def get_snapshots(self, module: str = None) -> list[ExecutionSnapshot]:
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

    def get_snapshot_by_id(self, snapshot_id: str) -> ExecutionSnapshot | None:
        """
        根據 ID 取得特定快照 - 優化版本使用索引

        Args:
            snapshot_id: 快照 ID

        Returns:
            Optional[ExecutionSnapshot]: 快照物件或 None
        """
        return self._snapshot_index.get(snapshot_id)

    def get_change_history(self, module: str = None) -> list[MetadataChange]:
        """
        取得變更歷史

        Args:
            module: 可選的模組名稱過濾

        Returns:
            List[MetadataChange]: 變更記錄列表
        """
        return self.metadater.get_change_history(module)

    def get_metadata_evolution(self, module: str = "Loader") -> list[SchemaMetadata]:
        """
        取得特定模組的元資料演進歷史 - 優化版本避免重複

        Args:
            module: 模組名稱

        Returns:
            List[SchemaMetadata]: 元資料演進列表
        """
        evolution = []
        seen_ids = set()

        for snapshot in self.snapshots:
            if snapshot.module_name == module:
                if (
                    snapshot.metadata_before
                    and snapshot.metadata_before.schema_id not in seen_ids
                ):
                    evolution.append(snapshot.metadata_before)
                    seen_ids.add(snapshot.metadata_before.schema_id)
                if (
                    snapshot.metadata_after
                    and snapshot.metadata_after.schema_id not in seen_ids
                ):
                    evolution.append(snapshot.metadata_after)
                    seen_ids.add(snapshot.metadata_after.schema_id)
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
            # 驗證快照完整性
            if not snapshot.metadata_after:
                raise SnapshotError(f"快照 {snapshot_id} 沒有可恢復的元資料")

            if not hasattr(snapshot.metadata_after, "schema_id"):
                raise SnapshotError(f"快照 {snapshot_id} 的元資料格式無效")

            # 恢復元資料狀態
            self.metadata[snapshot.module_name] = snapshot.metadata_after
            self._logger.info(
                f"已從快照 {snapshot_id} 恢復 {snapshot.module_name} 的元資料"
            )
            return True

        except SnapshotError as e:
            self._logger.error(f"快照恢復失敗: {e}")
            return False
        except (AttributeError, KeyError) as e:
            self._logger.error(f"快照資料存取錯誤: {e}")
            return False
        except Exception as e:
            self._logger.error(f"未預期的快照恢復錯誤: {e}", exc_info=True)
            raise StatusError(f"快照恢復過程中發生未預期錯誤: {e}") from e

    def get_status_summary(self) -> dict[str, Any]:
        """
        取得狀態摘要資訊

        Returns:
            Dict[str, Any]: 狀態摘要
        """
        change_summary = self.metadater.get_change_summary()
        return {
            "sequence": self.sequence,
            "active_modules": list(self.status.keys()),
            "metadata_modules": list(self.metadata.keys()),
            "total_snapshots": len(self.snapshots),
            "total_changes": change_summary["total_changes"],
            "last_snapshot": self.snapshots[-1].snapshot_id if self.snapshots else None,
            "last_change": change_summary["latest_change"],
            "change_types": change_summary["change_types"],
            "target_types": change_summary["target_types"],
        }

    def get_timing_records(self, module: str = None) -> list[TimingRecord]:
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
        取得適合 Reporter 使用的時間記錄資料 - 優化版本

        Returns:
            pd.DataFrame: 時間記錄的 DataFrame
        """
        if not self.timing_records:
            return pd.DataFrame()

        # 使用列表推導式和預分配，提升性能
        data = [
            {
                "record_id": record.record_id,
                "module_name": record.module_name,
                "experiment_name": record.experiment_name,
                "step_name": record.step_name,
                "start_time": record.start_time.isoformat(),
                "end_time": record.end_time.isoformat() if record.end_time else None,
                "duration_seconds": record.duration_seconds,
                **record.context,  # 展開 context 中的額外資訊
            }
            for record in self.timing_records
        ]

        return pd.DataFrame(data)
