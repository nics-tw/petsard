import itertools
import warnings
from dataclasses import dataclass, field

import pandas as pd

from petsard.constrainer.constrainer_base import BaseConstrainer


@dataclass
class FieldProportionsConfig:
    """
    用於定義欄位比例保留的配置類別。

    Attributes:
        field_proportions (list[dict]): 包含欄位比例保留規則的列表。每個規則是一個字典，包含：
            - fields: 欄位名稱（str）或欄位列表（list[str]）
            - mode: 可以是 'all'（所有值分布）或 'missing'（僅缺失值）
            - tolerance: (可選) 允許的原始比例與過濾後比例的最大差異，預設為 0.1（10%）

        original_proportions (dict): 存儲原始資料中各欄位的比例分布。
            在 verify_data 階段計算並存儲，避免在檢查階段重複計算。

    Methods:
        verify_data(data: pd.DataFrame, target_n_rows: int) -> None:
            驗證資料中是否有所有需要的欄位，檢查設定是否有效，並計算原始資料的比例分布。

        check_proportions(filtered_data: pd.DataFrame) -> tuple[bool, list[dict]]:
            檢查過濾後的資料是否維持了指定欄位的比例要求，並返回違反規則的詳細信息。
    """

    field_proportions: list[dict] = field(default_factory=list)
    original_proportions: dict = field(default_factory=dict)
    target_n_rows: int = field(default=None, init=False)  # Set internally

    def __post_init__(self):
        """驗證配置的有效性"""
        valid_modes: list[str] = ["all", "missing"]
        msgs: list[str] = []
        seen_fields: set = set()

        for i, proportion_rule in enumerate(self.field_proportions):
            # 檢查規則是否為字典
            if not isinstance(proportion_rule, dict):
                msg = f"錯誤: 第 {i + 1} 項比例規則應該是字典: {proportion_rule}"
                msgs.append(msg)
                continue

            # 檢查必要的鍵
            required_keys = {"fields", "mode"}
            if not required_keys.issubset(proportion_rule.keys()):
                missing_keys = required_keys - set(proportion_rule.keys())
                msg = f"錯誤: 第 {i + 1} 項比例規則缺少必要的鍵: {missing_keys}"
                msgs.append(msg)
                continue

            fields = proportion_rule["fields"]
            mode = proportion_rule["mode"]
            tolerance = proportion_rule.get("tolerance", 0.1)  # 預設值為 0.1 (10%)

            # 檢查欄位格式
            if isinstance(fields, str):
                # 單一欄位
                field_key = fields
            elif isinstance(fields, list):
                # 欄位列表
                if not fields:
                    msg = f"錯誤: 第 {i + 1} 項比例規則的欄位列表不能為空"
                    msgs.append(msg)
                    continue

                # 檢查列表中每個元素是否為字串
                for field in fields:
                    if not isinstance(field, str):
                        msg = f"錯誤: 第 {i + 1} 項比例規則的欄位列表中的元素應該都是字串: {field}"
                        msgs.append(msg)

                field_key = tuple(fields)
            else:
                msg = f"錯誤: 第 {i + 1} 項比例規則的欄位應該是字串或字串列表: {fields}"
                msgs.append(msg)
                continue

            # 檢查欄位重複
            if field_key in seen_fields:
                msg = f"錯誤: 第 {i + 1} 項比例規則的欄位 {field_key} 重複定義"
                msgs.append(msg)
            else:
                seen_fields.add(field_key)

            # 檢查模式是否有效
            if mode not in valid_modes:
                msg = (
                    f"錯誤: 第 {i + 1} 項比例規則的模式 '{mode}' 不在 {valid_modes} 中"
                )
                msgs.append(msg)

            # 檢查容忍度是否為有效的數值（如果提供的話）
            if (
                not isinstance(tolerance, (int, float))
                or tolerance < 0
                or tolerance > 1
            ):
                msg = f"錯誤: 第 {i + 1} 項比例規則的容忍度應該是 0 到 1 之間的數值: {tolerance}"
                msgs.append(msg)

        if any(msgs):
            raise ValueError("\n".join(map(str, msgs)))

    def verify_data(self, data: pd.DataFrame, target_n_rows: int) -> None:
        """
        驗證資料中是否有所有需要的欄位，檢查設定是否有效，並計算原始資料的比例分布。

        Args:
            data (pd.DataFrame): 要驗證的資料框。
            target_n_rows (int): 預期的過濾後資料行數。

        Raises:
            ValueError: 當資料中缺少必要欄位或設定無效時。
        """
        # 設定 target_n_rows
        if target_n_rows is None or target_n_rows <= 0:
            raise ValueError("target_n_rows 必須是正整數")
        self.target_n_rows = target_n_rows

        # 收集所有需要的欄位名稱
        required_fields = set()
        for rule in self.field_proportions:
            fields = rule["fields"]
            if isinstance(fields, str):
                required_fields.add(fields)
            elif isinstance(fields, list):
                required_fields.update(fields)

        # 檢查資料中是否有所有需要的欄位
        missing_fields = required_fields - set(data.columns)
        if missing_fields:
            raise ValueError(f"資料中缺少以下欄位: {missing_fields}")

        # 計算原始資料的比例分布
        self.original_proportions = {}
        self.min_max_counts = {}  # 存儲每個條件的最小和最大樣本數

        for rule in self.field_proportions:
            fields = rule["fields"]
            mode = rule["mode"]
            tolerance = rule.get("tolerance", 0.1)  # 預設值為 0.1 (10%)

            # 處理單一欄位
            if isinstance(fields, str):
                field = fields
                if field not in data.columns:
                    continue

                key = (field, mode)

                # 計算 'all' 模式 - 所有值的分布
                if mode == "all" and key not in self.original_proportions:
                    # 計算原始比例
                    value_counts = (
                        data[field].value_counts(dropna=False, normalize=True).to_dict()
                    )
                    self.original_proportions[key] = value_counts

                    # 計算每個值的最小和最大樣本數
                    count_bounds = {}
                    for value, prop in value_counts.items():
                        target_count = int(prop * self.target_n_rows)
                        # 最小樣本數：原始比例減去容忍度，乘以目標行數
                        min_count = int((prop - tolerance) * self.target_n_rows)
                        # 最大樣本數：原始比例加上容忍度，乘以目標行數
                        max_count = int((prop + tolerance) * self.target_n_rows)
                        count_bounds[value] = {
                            "min": min_count,
                            "max": max_count,
                            "target": target_count,
                        }
                    self.min_max_counts[key] = count_bounds

                # 計算 'missing' 模式 - 僅缺失值的比例
                elif mode == "missing" and key not in self.original_proportions:
                    missing_prop = data[field].isna().mean()
                    self.original_proportions[key] = missing_prop

                    # 計算缺失值的最小和最大樣本數
                    target_count = int(missing_prop * self.target_n_rows)
                    min_count = int((missing_prop - tolerance) * self.target_n_rows)
                    max_count = int((missing_prop + tolerance) * self.target_n_rows)
                    self.min_max_counts[key] = {
                        "缺失值": {
                            "min": min_count,
                            "max": max_count,
                            "target": target_count,
                        }
                    }

            # 處理欄位組合（列表格式）
            elif isinstance(fields, list):
                fields_tuple = tuple(fields)
                # 檢查所有欄位是否都存在
                all_fields_exist = all(field in data.columns for field in fields)
                if not all_fields_exist:
                    continue

                key = (fields_tuple, mode)

                # 處理 'missing' 模式
                if mode == "missing" and key not in self.original_proportions:
                    # 創建包含每個欄位是否為空的組合
                    missing_patterns = {}
                    count_bounds = {}

                    # 為每個欄位建立 isna() 標記
                    isna_df = pd.DataFrame()
                    for field in fields:
                        isna_df[f"{field}_isna"] = data[field].isna()

                    # 計算每種缺失模式的比例
                    patterns = list(
                        itertools.product([True, False], repeat=len(fields))
                    )
                    for pattern in patterns:
                        mask = pd.Series(True, index=data.index)
                        for i, field in enumerate(fields):
                            if pattern[i]:
                                mask &= isna_df[f"{field}_isna"]
                            else:
                                mask &= ~isna_df[f"{field}_isna"]

                        pattern_key = pattern
                        pattern_prop = mask.mean()
                        missing_patterns[pattern_key] = pattern_prop

                        target_count = int(pattern_prop * self.target_n_rows)
                        # 計算每個模式的最小和最大樣本數
                        min_count = int((pattern_prop - tolerance) * self.target_n_rows)
                        max_count = int((pattern_prop + tolerance) * self.target_n_rows)

                        # 建立模式的可讀描述
                        pattern_desc = ", ".join(
                            [
                                f"{fields[i]}:{'缺失' if p else '非缺失'}"
                                for i, p in enumerate(pattern)
                            ]
                        )

                        count_bounds[pattern_key] = {
                            "desc": pattern_desc,
                            "min": min_count,
                            "max": max_count,
                            "target": target_count,
                        }

                    self.original_proportions[key] = missing_patterns
                    self.min_max_counts[key] = count_bounds

                # 處理 'all' 模式
                elif mode == "all" and key not in self.original_proportions:
                    # 為欄位組合創建一個連接值
                    combined = data[fields].apply(lambda row: tuple(row), axis=1)

                    # 計算每個組合值的比例
                    value_counts = combined.value_counts(
                        dropna=False, normalize=True
                    ).to_dict()
                    self.original_proportions[key] = value_counts

                    # 計算每個組合值的最小和最大樣本數
                    count_bounds = {}
                    for value, prop in value_counts.items():
                        target_count = int(prop * self.target_n_rows)
                        min_count = int((prop - tolerance) * self.target_n_rows)
                        max_count = int((prop + tolerance) * self.target_n_rows)
                        count_bounds[value] = {
                            "min": min_count,
                            "max": max_count,
                            "target": target_count,
                        }
                    self.min_max_counts[key] = count_bounds

        # 最後修正 min_max：避免浮點運算問題
        for idx, props in self.min_max_counts.items():
            for value, counts in props.items():
                curr_min: int = counts["min"]
                curr_max: int = counts["max"]
                target: int = counts["target"]

                if target == 0:
                    self.min_max_counts[idx][value]["min"] = 0
                    self.min_max_counts[idx][value]["max"] = 0
                else:
                    self.min_max_counts[idx][value]["min"] = max(1, curr_min)

                if target == self.target_n_rows:
                    self.min_max_counts[idx][value]["min"] = self.target_n_rows
                    self.min_max_counts[idx][value]["max"] = self.target_n_rows
                else:
                    self.min_max_counts[idx][value]["max"] = min(
                        (self.target_n_rows - 1), curr_max
                    )

    def check_proportions(self, filtered_data: pd.DataFrame) -> tuple[bool, list[dict]]:
        """
        檢查過濾後的資料是否維持了指定欄位的比例要求

        Args:
            filtered_data (pd.DataFrame): 過濾後的資料

        Returns:
            tuple[bool, list[dict]]:
                - bool: 是否所有比例規則都符合要求
                - list[dict]: 違反規則的詳細信息列表
        """
        # 確保已經計算了原始比例和樣本數限制
        if not self.original_proportions or not hasattr(self, "min_max_counts"):
            raise ValueError("尚未計算原始資料的比例分布，請先呼叫 verify_data 方法")

        all_rules_satisfied = True
        violations = []
        filtered_n_rows = len(filtered_data)

        for rule in self.field_proportions:
            fields = rule["fields"]
            mode = rule["mode"]
            tolerance = rule.get("tolerance", 0.1)  # 預設值為 0.1 (10%)

            # 處理單一欄位
            if isinstance(fields, str):
                field = fields
                if field not in filtered_data.columns:
                    continue

                key = (field, mode)

                # 檢查 'all' 模式 - 所有值的分布
                if (
                    mode == "all"
                    and key in self.original_proportions
                    and key in self.min_max_counts
                ):
                    # 獲取原始資料的比例和樣本數限制
                    original_counts = self.original_proportions[key]
                    count_bounds = self.min_max_counts[key]

                    # 計算過濾後資料的實際計數
                    value_counts = (
                        filtered_data[field].value_counts(dropna=False).to_dict()
                    )

                    # 檢查每個值的實際計數是否在允許範圍內
                    for value in set(original_counts.keys()):
                        if value not in count_bounds:
                            continue

                        bounds = count_bounds[value]
                        min_count = bounds["min"]
                        max_count = bounds["max"]
                        target_count = bounds["target"]
                        actual_count = value_counts.get(value, 0)

                        # 檢查是否違反限制
                        if actual_count < min_count or actual_count > max_count:
                            all_rules_satisfied = False
                            violations.append(
                                {
                                    "欄位": field,
                                    "值": value,
                                    "原始比例": original_counts[value],
                                    "過濾後比例": actual_count / filtered_n_rows
                                    if filtered_n_rows > 0
                                    else 0,
                                    "實際計數": actual_count,
                                    "最小計數": min_count,
                                    "最大計數": max_count,
                                    "目標計數": target_count,
                                    "容忍度": tolerance,
                                    "模式": mode,
                                }
                            )

                # 檢查 'missing' 模式 - 僅缺失值的比例
                elif (
                    mode == "missing"
                    and key in self.original_proportions
                    and key in self.min_max_counts
                ):
                    # 獲取原始資料的缺失比例和樣本數限制
                    orig_missing_prop = self.original_proportions[key]
                    count_bounds = self.min_max_counts[key]["缺失值"]

                    # 計算過濾後資料的實際缺失計數
                    actual_missing_count = filtered_data[field].isna().sum()

                    min_count = count_bounds["min"]
                    max_count = count_bounds["max"]
                    target_count = count_bounds["target"]

                    # 檢查是否違反限制
                    if (
                        actual_missing_count < min_count
                        or actual_missing_count > max_count
                    ):
                        all_rules_satisfied = False
                        violations.append(
                            {
                                "欄位": field,
                                "值": "缺失值",
                                "原始比例": orig_missing_prop,
                                "過濾後比例": actual_missing_count / filtered_n_rows
                                if filtered_n_rows > 0
                                else 0,
                                "實際計數": actual_missing_count,
                                "最小計數": min_count,
                                "最大計數": max_count,
                                "目標計數": target_count,
                                "容忍度": tolerance,
                                "模式": mode,
                            }
                        )

            # 處理欄位組合（列表格式）
            elif isinstance(fields, list):
                fields_tuple = tuple(fields)
                # 檢查所有欄位是否都存在
                all_fields_exist = all(
                    field in filtered_data.columns for field in fields
                )
                if not all_fields_exist:
                    continue

                key = (fields_tuple, mode)

                # 處理 'missing' 模式
                if (
                    mode == "missing"
                    and key in self.original_proportions
                    and key in self.min_max_counts
                ):
                    # 獲取原始資料的缺失模式比例和樣本數限制
                    original_missing_patterns = self.original_proportions[key]
                    count_bounds = self.min_max_counts[key]

                    # 計算過濾後資料中每種缺失模式的實際計數
                    isna_df = pd.DataFrame()
                    for field in fields:
                        isna_df[f"{field}_isna"] = filtered_data[field].isna()

                    patterns = list(original_missing_patterns.keys())
                    for pattern in patterns:
                        if pattern not in count_bounds:
                            continue

                        bounds = count_bounds[pattern]
                        pattern_desc = bounds["desc"]
                        min_count = bounds["min"]
                        max_count = bounds["max"]
                        target_count = bounds["target"]

                        # 計算實際計數
                        mask = pd.Series(True, index=filtered_data.index)
                        for i, field in enumerate(fields):
                            if pattern[i]:
                                mask &= isna_df[f"{field}_isna"]
                            else:
                                mask &= ~isna_df[f"{field}_isna"]

                        actual_count = mask.sum()

                        # 檢查是否違反限制
                        if actual_count < min_count or actual_count > max_count:
                            all_rules_satisfied = False
                            violations.append(
                                {
                                    "欄位": fields_tuple,
                                    "值": pattern_desc,
                                    "原始比例": original_missing_patterns[pattern],
                                    "過濾後比例": actual_count / filtered_n_rows
                                    if filtered_n_rows > 0
                                    else 0,
                                    "實際計數": actual_count,
                                    "最小計數": min_count,
                                    "最大計數": max_count,
                                    "目標計數": target_count,
                                    "容忍度": tolerance,
                                    "模式": mode,
                                }
                            )

                # 處理 'all' 模式
                elif (
                    mode == "all"
                    and key in self.original_proportions
                    and key in self.min_max_counts
                ):
                    # 獲取原始資料的比例和樣本數限制
                    original_counts = self.original_proportions[key]
                    count_bounds = self.min_max_counts[key]

                    # 計算過濾後資料的實際計數
                    combined = filtered_data[fields].apply(
                        lambda row: tuple(row), axis=1
                    )
                    value_counts = combined.value_counts(dropna=False).to_dict()

                    # 檢查每個組合值的實際計數是否在允許範圍內
                    for value in set(original_counts.keys()):
                        if value not in count_bounds:
                            continue

                        bounds = count_bounds[value]
                        min_count = bounds["min"]
                        max_count = bounds["max"]
                        target_count = bounds["target"]
                        actual_count = value_counts.get(value, 0)

                        # 檢查是否違反限制
                        if actual_count < min_count or actual_count > max_count:
                            all_rules_satisfied = False
                            violations.append(
                                {
                                    "欄位": fields_tuple,
                                    "值": str(value),
                                    "原始比例": original_counts[value],
                                    "過濾後比例": actual_count / filtered_n_rows
                                    if filtered_n_rows > 0
                                    else 0,
                                    "實際計數": actual_count,
                                    "最小計數": min_count,
                                    "最大計數": max_count,
                                    "目標計數": target_count,
                                    "容忍度": tolerance,
                                    "模式": mode,
                                }
                            )

        return all_rules_satisfied, violations


class FieldProportionsConstrainer(BaseConstrainer):
    """Field proportions constrainer for maintaining data distribution proportions"""

    def __init__(self, config: dict):
        """
        Initialize field proportions constrainer

        Args:
            config: Dictionary containing field proportions configuration
                {
                    'field_proportions': [...]
                }
        """
        super().__init__(config)
        self.proportions_config = None
        self._setup_config()

    def _setup_config(self):
        """Setup the field proportions configuration"""
        try:
            # Handle different config formats
            if isinstance(self.config, list):
                # Direct list format: [{'fields': 'category', 'mode': 'all', 'tolerance': 0.1}, ...]
                config_dict = {"field_proportions": self.config}
            elif isinstance(self.config, dict):
                if "field_proportions" in self.config and isinstance(
                    self.config["field_proportions"], list
                ):
                    # New simplified format: {'field_proportions': [...]}
                    config_dict = {
                        "field_proportions": self.config["field_proportions"]
                    }
                else:
                    # Fallback: assume the whole config is the field proportions config
                    config_dict = self.config
            else:
                raise ValueError(f"Invalid config format: {type(self.config)}")

            self.proportions_config = FieldProportionsConfig(**config_dict)
        except Exception as e:
            raise ValueError(f"Invalid field proportions configuration: {e}")

    def _set_target_rows(self, target_rows: int):
        """Internal method to set target rows from Constrainer"""
        self.target_rows = target_rows

    def validate_config(self) -> bool:
        """Validate if the configuration is legal"""
        try:
            # Configuration validation is done in FieldProportionsConfig.__post_init__
            return self.proportions_config is not None
        except Exception:
            return False

    def apply(self, df: pd.DataFrame, target_rows: int = None) -> pd.DataFrame:
        """
        Apply field proportions constraint to the data

        Args:
            df: Input DataFrame
            target_rows: Target number of rows (provided by Constrainer)

        Returns:
            DataFrame after applying field proportions constraint
        """
        if df.empty:
            return df

        # Set target rows if provided
        if target_rows is not None:
            self._set_target_rows(target_rows)

        # Verify data and setup proportions if not already done
        if not self.proportions_config.original_proportions:
            if not hasattr(self, "target_rows") or self.target_rows is None:
                raise ValueError("target_rows must be provided")
            self.proportions_config.verify_data(df, self.target_rows)

        # Apply the constraint filtering
        result_df, ops_df = self._constraint_filter_field_proportions(
            df, self.proportions_config
        )

        return result_df

    def _constraint_filter_field_proportions(
        self,
        data: pd.DataFrame,
        config: FieldProportionsConfig = None,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        根據給定的欄位比例保留條件過濾 DataFrame，確保欄位的值分布計數維持在可接受範圍內。

        Args:
            data (pd.DataFrame)：要過濾的資料
            config (FieldProportionsConfig)：包含欄位比例保留的設定類別

        Returns:
            tuple[pd.DataFrame, pd.DataFrame]：
                - 過濾後的資料，索引已重置
                - 操作記錄資料框，包含過濾動作、條件、影響行數等資訊
        """
        if (
            config is None
            or not hasattr(config, "original_proportions")
            or not config.original_proportions
            or not hasattr(config, "min_max_counts")
            or not config.min_max_counts
        ):
            return data, pd.DataFrame()

        # 複製資料以避免修改原始資料
        data_result = data.copy()
        initial_rows = len(data_result)

        # 創建操作記錄的列表
        ops_records = []

        # 設定最大迭代次數，避免無限循環
        max_iterations = 50
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # 檢查是否符合所有條件
            proportions_satisfied, violations = config.check_proportions(data_result)

            # 如果沒有違反比例要求，直接返回
            if proportions_satisfied:
                break

            # 將違規條件按類型分類
            overflow_violations = []  # 計數過多的違規
            underflow_violations = []  # 計數過少的違規

            for violation in violations:
                actual_count = violation["實際計數"]
                min_count = violation["最小計數"]
                max_count = violation["最大計數"]

                if actual_count > max_count:
                    overflow_violations.append(violation)
                elif actual_count < min_count:
                    underflow_violations.append(violation)

            # 如果沒有計數過多的違規，而只有計數過少的違規，那麼我們可能無法進一步調整
            if not overflow_violations:
                break

            # 1. 先標記所有需要保護的資料（計數過少的條件）
            protect_mask = pd.Series(False, index=data_result.index)

            # 2. 找出第一個計數過多的違規條件，進行處理
            found_overflow = False

            for violation in overflow_violations:
                field_name = violation["欄位"]
                value = violation["值"]
                actual_count = violation["實際計數"]
                max_count = violation["最大計數"]
                mode = violation["模式"]

                # 計算需要移除的數量
                remove_needed = actual_count - max_count

                # 建立過濾條件遮罩
                if isinstance(field_name, str):
                    # 單一欄位
                    if mode == "all":
                        # 找出特定值的資料
                        if pd.isna(value):
                            value_mask = data_result[field_name].isna()
                        else:
                            value_mask = data_result[field_name] == value
                        condition_desc = f"欄位 {field_name} 的值 {value}"
                    else:  # mode == 'missing'
                        # 找出缺失值的資料
                        value_mask = data_result[field_name].isna()
                        condition_desc = f"欄位 {field_name} 的缺失值"
                else:
                    # 欄位組合
                    fields = (
                        field_name if isinstance(field_name, tuple) else [field_name]
                    )
                    if mode == "all":
                        # 處理欄位組合的特定值
                        if (
                            isinstance(value, str)
                            and value.startswith("(")
                            and value.endswith(")")
                        ):
                            # 解析字符串形式的元組
                            import ast

                            try:
                                parsed_value = ast.literal_eval(value)
                                if isinstance(parsed_value, tuple):
                                    value_mask = pd.Series(
                                        True, index=data_result.index
                                    )
                                    for i, field in enumerate(fields):
                                        if i < len(parsed_value):
                                            if pd.isna(parsed_value[i]):
                                                value_mask &= data_result[field].isna()
                                            else:
                                                value_mask &= (
                                                    data_result[field]
                                                    == parsed_value[i]
                                                )
                                else:
                                    value_mask = data_result[list(fields)].apply(
                                        lambda row: str(tuple(row)) == value, axis=1
                                    )
                            except:
                                value_mask = data_result[list(fields)].apply(
                                    lambda row: str(tuple(row)) == value, axis=1
                                )
                        else:
                            value_mask = data_result[list(fields)].apply(
                                lambda row: str(tuple(row)) == str(value), axis=1
                            )
                        condition_desc = f"欄位組合 {field_name} 的值 {value}"
                    else:  # mode == 'missing'
                        # 處理欄位組合的缺失模式 - 簡化處理
                        value_mask = pd.Series(False, index=data_result.index)
                        condition_desc = f"欄位組合 {field_name} 的 {value}"

                # 如果有可用的資料可以移除
                available_count = value_mask.sum()
                if available_count > 0:
                    # 決定要移除多少筆資料
                    remove_count = min(remove_needed, available_count)

                    # 隨機選擇要移除的索引
                    indices_to_remove = (
                        data_result[value_mask]
                        .sample(n=remove_count, random_state=42)
                        .index
                    )

                    # 記錄操作
                    detailed_record = {
                        "迭代次數": iteration,
                        "移除條件": condition_desc,
                        "移除原因": "計數過多",
                        "當前計數": actual_count,
                        "最大計數": max_count,
                        "需移除計數": remove_needed,
                        "實際移除筆數": remove_count,
                        "剩餘行數": len(data_result) - remove_count,
                    }

                    ops_records.append(detailed_record)

                    # 過濾資料
                    data_result = data_result.drop(indices_to_remove)

                    found_overflow = True
                    break  # 找到一個條件處理後就跳出，重新評估所有條件

            # 如果所有計數過多的條件都無法處理，則退出循環
            if not found_overflow:
                break

        # 最終檢查
        final_proportions_satisfied, final_violations = config.check_proportions(
            data_result
        )
        if not final_proportions_satisfied:
            warnings.warn(
                f"Final data still has {len(final_violations)} conditions not satisfied",
                stacklevel=2,
            )

        # 創建操作記錄的 DataFrame
        ops_df = (
            pd.DataFrame(ops_records)
            if ops_records
            else pd.DataFrame(
                columns=[
                    "迭代次數",
                    "移除條件",
                    "移除原因",
                    "當前計數",
                    "最大計數",
                    "需移除計數",
                    "實際移除筆數",
                    "剩餘行數",
                ]
            )
        )

        return data_result.reset_index(drop=True), ops_df
