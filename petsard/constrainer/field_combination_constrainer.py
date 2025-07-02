from typing import List

import pandas as pd

from petsard.exceptions import ConfigError


class FieldCombinationConstrainer:
    """
    Handle field combination constraints with flexible configuration

    Config format supports two types:
    1. Single field constraint:
    [
        (
            {'source_field': 'target_field'},
            {
                'source_value1': ['target_value1', 'target_value2'],
                'source_value2': 'specific_target_value'
            }
        )
    ]

    2. Multiple fields constraint:
    [
        (
            {('source_field1', 'source_field2'): 'target_field'},
            {
                ('source_value1', 'source_value2'): ['target_value1', 'target_value2'],
                ('source_value3', 'source_value4'): 'specific_target_value'
            }
        )
    ]
    """

    def __init__(self, constraints: List[tuple]):
        """
        Initialize the constrainer with given constraints

        Args:
            constraints: List of constraint configurations
        """
        self._validate_constraint_format(constraints)
        self.constraints = constraints

    def _validate_constraint_format(self, constraints):
        """
        Validate the format of input constraints

        Args:
            constraints: List of constraint configurations to validate

        Raises:
            ConfigError: If the constraint format is invalid
        """
        if not isinstance(constraints, list):
            raise ConfigError("Constraints must be a list")

        for constraint in constraints:
            # Check constraint is a tuple with two elements
            if not isinstance(constraint, tuple) or len(constraint) != 2:
                raise ConfigError(
                    f"Each constraint must be a tuple with two elements, got {constraint}"
                )

            # Validate field map
            field_map, conditions = constraint
            if not isinstance(field_map, dict) or len(field_map) != 1:
                raise ConfigError(
                    f"Field map must be a dictionary with exactly one key-value pair, got {field_map}"
                )

            # Validate source and target fields
            source_fields = list(field_map.keys())[0]
            if not (
                isinstance(source_fields, str)
                or (
                    isinstance(source_fields, tuple)
                    and all(isinstance(f, str) for f in source_fields)
                )
            ):
                raise ConfigError(
                    f"Source fields must be a string or tuple of strings, got {source_fields}"
                )

            # Validate target field
            target_field = list(field_map.values())[0]
            if not isinstance(target_field, str):
                raise ConfigError(f"Target field must be a string, got {target_field}")

            # Validate conditions
            if not isinstance(conditions, dict):
                raise ConfigError(f"Conditions must be a dictionary, got {conditions}")

            # Validate condition keys and values
            for source_value, allowed_values in conditions.items():
                # Check source value type
                if isinstance(source_fields, str):
                    # For single field, source value can be anything
                    pass
                elif isinstance(source_fields, tuple):
                    # For multi-field, source value must be a tuple of same length
                    if not (
                        isinstance(source_value, tuple)
                        and len(source_value) == len(source_fields)
                    ):
                        raise ConfigError(
                            f"Source value must be a tuple of length {len(source_fields)}, got {source_value}"
                        )

                # Check allowed values type
                if not isinstance(allowed_values, (list, tuple, str, int, float)):
                    raise ConfigError(
                        f"Allowed values must be a list, tuple, or single value, got {allowed_values}"
                    )

    def _is_na_value(self, value):
        """
        Check if a value represents NA

        Args:
            value: Input value to check

        Returns:
            Boolean indicating if the value is NA
        """
        # Only string "pd.NA" is considered NA
        return value == "pd.NA"

    def validate_config(self, df: pd.DataFrame) -> None:
        """
        Validate if the configuration is compatible with the given DataFrame

        Args:
            df: Input DataFrame to validate against

        Raises:
            ConfigError: If any required columns are missing
        """
        for constraint_group in self.constraints:
            # Parse source and target fields from the constraint
            field_map, _ = constraint_group

            # Extract source and target fields
            source_fields = list(field_map.keys())[0]
            target_field = list(field_map.values())[0]

            # Ensure source_fields is a tuple
            if isinstance(source_fields, str):
                source_fields = (source_fields,)

            # Check all fields exist
            all_fields = list(source_fields) + [target_field]
            missing_fields = [f for f in all_fields if f not in df.columns]

            if missing_fields:
                raise ConfigError(
                    f"Columns {missing_fields} do not exist in the DataFrame"
                )

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply field combination constraints to DataFrame

        Args:
            df: Input DataFrame to be filtered

        Returns:
            Filtered DataFrame that meets all constraints

        Raises:
            ConfigError: If configuration is incompatible with the DataFrame
        """
        # Perform complete validation before applying constraints
        self.validate_config(df)

        result = df.copy()

        for constraint_group in self.constraints:
            # Parse source and target fields from the constraint
            field_map, conditions = constraint_group

            # Extract source and target fields
            source_fields = list(field_map.keys())[0]
            target_field = list(field_map.values())[0]

            # Ensure source_fields is a tuple
            if isinstance(source_fields, str):
                source_fields = (source_fields,)

            # 初始化掩碼 - 默認保留所有行
            mask = pd.Series(True, index=result.index)

            # 對每個源值-目標值對應關係
            for source_values, allowed_values in conditions.items():
                if isinstance(source_values, str):
                    source_values = (source_values,)

                # 找到匹配源值的行
                source_mask = pd.Series(True, index=result.index)
                for field, value in zip(source_fields, source_values):
                    if self._is_na_value(value):
                        field_match = result[field].isna()
                    else:
                        # 對於 category 類型，先轉換為字符串再比較
                        if isinstance(result[field].dtype, pd.CategoricalDtype):
                            field_match = result[field].astype(str) == str(value)
                        else:
                            field_match = result[field] == value

                    source_mask &= field_match

                # 規範化允許值為列表
                if not isinstance(allowed_values, (list, tuple)):
                    allowed_values = [allowed_values]

                # 檢查目標值
                value_mask = result[target_field].isin(allowed_values)

                # 更清晰的邏輯：
                # - 源不匹配的行保留
                # - 源匹配且目標合法的行保留
                # - 源匹配但目標不合法的行移除
                row_mask = (~source_mask) | (source_mask & value_mask)

                # 更新總掩碼
                mask &= row_mask

            # 應用掩碼
            result = result[mask].reset_index(drop=True)

        return result
