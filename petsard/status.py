"""
PETsARD Status Module - 以 Metadater 為核心的狀態管理

本模組提供以 Metadater 為核心的狀態管理機制，包含完整的進度快照功能。
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
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

        # 原有功能的相容性支援
        if "Splitter" in self.sequence:
            self.exist_train_indices: list[set] = []
        if "Reporter" in self.sequence:
            self.report: dict = {}

    def _generate_snapshot_id(self) -> str:
        """生成快照 ID"""
        self._snapshot_counter += 1
        return f"snapshot_{self._snapshot_counter:06d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def _generate_change_id(self) -> str:
        """生成變更 ID"""
        self._change_counter += 1
        return f"change_{self._change_counter:06d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

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

    def put(self, module: str, expt: str, operator: BaseOperator):
        """
        新增模組狀態和操作器到狀態字典

        這是核心方法，整合了 Metadater 的快照功能

        Args:
            module: 當前模組名稱
            expt: 當前實驗名稱
            operator: 當前操作器
        """
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
