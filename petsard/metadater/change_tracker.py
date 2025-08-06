"""
元資料變更追蹤模組

提供元資料變更的記錄、追蹤和查詢功能。
"""

import logging
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


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
    before_state: Any | None = None
    after_state: Any | None = None
    timestamp: datetime = field(default_factory=datetime.now)
    module_context: str = ""


class MetadataChangeTracker:
    """
    元資料變更追蹤器

    負責記錄和管理元資料的變更歷史，提供查詢和分析功能。
    """

    def __init__(self, max_changes: int = 5000):
        """
        初始化變更追蹤器

        Args:
            max_changes: 最大變更記錄數量，防止記憶體洩漏
        """
        self._logger = logging.getLogger(f"PETsARD.{self.__class__.__name__}")
        self.max_changes = max_changes
        self.change_history: deque[MetadataChange] = deque(maxlen=max_changes)
        self._change_counter = 0

    def _generate_change_id(self) -> str:
        """生成變更 ID"""
        self._change_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"change_{self._change_counter:06d}_{timestamp}"

    def track_change(
        self,
        change_type: str,
        target_type: str,
        target_id: str,
        before_state: Any | None = None,
        after_state: Any | None = None,
        module_context: str = "",
    ) -> MetadataChange:
        """
        追蹤元資料變更

        Args:
            change_type: 變更類型 ('create', 'update', 'delete')
            target_type: 目標類型 ('schema', 'field')
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

    def get_change_history(self, module: str = None) -> list[MetadataChange]:
        """
        取得變更歷史

        Args:
            module: 可選的模組名稱過濾

        Returns:
            List[MetadataChange]: 變更記錄列表
        """
        if module is None:
            return list(self.change_history)
        else:
            return [c for c in self.change_history if module in c.module_context]

    def get_changes_by_target(
        self, target_type: str, target_id: str = None
    ) -> list[MetadataChange]:
        """
        根據目標類型和 ID 取得變更記錄

        Args:
            target_type: 目標類型 ('schema', 'field')
            target_id: 可選的目標 ID

        Returns:
            List[MetadataChange]: 符合條件的變更記錄
        """
        changes = [c for c in self.change_history if c.target_type == target_type]

        if target_id is not None:
            changes = [c for c in changes if c.target_id == target_id]

        return changes

    def get_latest_change(self) -> MetadataChange | None:
        """
        取得最新的變更記錄

        Returns:
            Optional[MetadataChange]: 最新的變更記錄，如果沒有則返回 None
        """
        return self.change_history[-1] if self.change_history else None

    def clear_history(self) -> None:
        """清空變更歷史"""
        self.change_history.clear()
        self._change_counter = 0
        self._logger.info("變更歷史已清空")

    def get_summary(self) -> dict[str, Any]:
        """
        取得變更追蹤摘要

        Returns:
            Dict[str, Any]: 摘要資訊
        """
        if not self.change_history:
            return {
                "total_changes": 0,
                "change_types": {},
                "target_types": {},
                "latest_change": None,
            }

        change_types = {}
        target_types = {}

        for change in self.change_history:
            change_types[change.change_type] = (
                change_types.get(change.change_type, 0) + 1
            )
            target_types[change.target_type] = (
                target_types.get(change.target_type, 0) + 1
            )

        return {
            "total_changes": len(self.change_history),
            "change_types": change_types,
            "target_types": target_types,
            "latest_change": self.change_history[-1].change_id,
        }
