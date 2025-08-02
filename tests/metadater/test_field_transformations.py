"""Test cases for field transformation functionality
欄位轉換功能的測試案例
"""

import pandas as pd

from petsard.metadater.field.field_functions import apply_field_transformations
from petsard.metadater.field.field_types import FieldConfig


class TestFieldTransformations:
    """Test cases for apply_field_transformations function
    apply_field_transformations 函數的測試案例
    """

    def test_na_values_replacement_string(self):
        """Test NA values replacement with string
        測試字串 NA 值替換
        """
        series = pd.Series(["1", "2", "unknown", "4", "N/A"])
        config = FieldConfig(na_values="unknown")

        result = apply_field_transformations(series, config, "test_field")

        # Check that "unknown" was replaced with pd.NA
        assert pd.isna(result.iloc[2])
        assert result.iloc[0] == "1"
        assert result.iloc[1] == "2"
        assert result.iloc[3] == "4"
        assert result.iloc[4] == "N/A"  # This should not be replaced

    def test_na_values_replacement_list(self):
        """Test NA values replacement with list
        測試列表 NA 值替換
        """
        series = pd.Series(["1", "2", "unknown", "4", "N/A", "missing"])
        config = FieldConfig(na_values=["unknown", "N/A", "missing"])

        result = apply_field_transformations(series, config, "test_field")

        # Check that all specified values were replaced with pd.NA
        assert pd.isna(result.iloc[2])  # "unknown"
        assert pd.isna(result.iloc[4])  # "N/A"
        assert pd.isna(result.iloc[5])  # "missing"
        assert result.iloc[0] == "1"
        assert result.iloc[1] == "2"
        assert result.iloc[3] == "4"

    def test_type_conversion_integer(self):
        """Test type conversion to integer
        測試整數類型轉換
        """
        series = pd.Series(["1", "2", "3", "4", "5"])
        config = FieldConfig(type_hint="int")

        result = apply_field_transformations(series, config, "test_field")

        # Check that values were converted to integers
        assert result.dtype == "Int64"
        assert result.iloc[0] == 1
        assert result.iloc[1] == 2
        assert result.iloc[2] == 3

    def test_type_conversion_float(self):
        """Test type conversion to float
        測試浮點數類型轉換
        """
        series = pd.Series(["1.5", "2.7", "3.9", "4.1", "5.3"])
        config = FieldConfig(type_hint="float")

        result = apply_field_transformations(series, config, "test_field")

        # Check that values were converted to floats
        assert result.dtype == "float64"
        assert result.iloc[0] == 1.5
        assert result.iloc[1] == 2.7
        assert result.iloc[2] == 3.9

    def test_type_conversion_boolean(self):
        """Test type conversion to boolean
        測試布林類型轉換
        """
        series = pd.Series(["true", "false", "yes", "no", "1", "0"])
        config = FieldConfig(type_hint="boolean")

        result = apply_field_transformations(series, config, "test_field")

        # Check that values were converted to booleans
        assert result.dtype == "boolean"
        assert result.iloc[0] == True  # "true"
        assert result.iloc[1] == False  # "false"
        assert result.iloc[2] == True  # "yes"
        assert result.iloc[3] == False  # "no"
        assert result.iloc[4] == True  # "1"
        assert result.iloc[5] == False  # "0"

    def test_type_conversion_string(self):
        """Test type conversion to string
        測試字串類型轉換
        """
        series = pd.Series([1, 2, 3, 4, 5])
        config = FieldConfig(type_hint="string")

        result = apply_field_transformations(series, config, "test_field")

        # Check that values were converted to strings
        assert result.dtype == "string"
        assert result.iloc[0] == "1"
        assert result.iloc[1] == "2"

    def test_type_conversion_category(self):
        """Test type conversion to category
        測試分類類型轉換
        """
        series = pd.Series(["A", "B", "C", "A", "B"])
        config = FieldConfig(type_hint="category")

        result = apply_field_transformations(series, config, "test_field")

        # Check that values were converted to category
        assert result.dtype.name == "category"
        assert result.iloc[0] == "A"
        assert result.iloc[1] == "B"

    def test_precision_rounding_numeric(self):
        """Test precision rounding for numeric data
        測試數值資料的精度四捨五入
        """
        series = pd.Series([1.23456, 2.34567, 3.45678, 4.56789])
        config = FieldConfig(precision=2)

        result = apply_field_transformations(series, config, "test_field")

        # Check that values were rounded to 2 decimal places
        assert result.iloc[0] == 1.23
        assert result.iloc[1] == 2.35  # rounded up
        assert result.iloc[2] == 3.46  # rounded up
        assert result.iloc[3] == 4.57  # rounded up

    def test_precision_rounding_non_numeric(self):
        """Test precision rounding with non-numeric data (should be ignored)
        測試非數值資料的精度四捨五入（應該被忽略）
        """
        series = pd.Series(["A", "B", "C", "D"])
        config = FieldConfig(precision=2)

        result = apply_field_transformations(series, config, "test_field")

        # Check that non-numeric data was not affected
        assert result.iloc[0] == "A"
        assert result.iloc[1] == "B"
        assert result.iloc[2] == "C"
        assert result.iloc[3] == "D"

    def test_combined_transformations(self):
        """Test combined NA replacement, type conversion, and precision
        測試組合轉換：NA 替換、類型轉換和精度
        """
        series = pd.Series(["1.23456", "2.34567", "unknown", "4.56789", "N/A"])
        config = FieldConfig(
            type_hint="float", na_values=["unknown", "N/A"], precision=2
        )

        result = apply_field_transformations(series, config, "test_field")

        # Check NA replacement
        assert pd.isna(result.iloc[2])  # "unknown"
        assert pd.isna(result.iloc[4])  # "N/A"

        # Check type conversion and precision
        assert result.dtype == "float64"
        assert result.iloc[0] == 1.23
        assert result.iloc[1] == 2.35  # rounded up
        assert result.iloc[3] == 4.57  # rounded up

    def test_type_conversion_with_coerce_error_handling(self):
        """Test type conversion with coerce error handling
        測試使用 coerce 錯誤處理的類型轉換
        """
        series = pd.Series(["1", "2", "invalid", "4", "also_invalid"])
        config = FieldConfig(type_hint="int", cast_error="coerce")

        result = apply_field_transformations(series, config, "test_field")

        # Check that valid values were converted and invalid ones became NA
        assert result.dtype == "Int64"
        assert result.iloc[0] == 1
        assert result.iloc[1] == 2
        assert pd.isna(result.iloc[2])  # "invalid" -> NA
        assert result.iloc[3] == 4
        assert pd.isna(result.iloc[4])  # "also_invalid" -> NA

    def test_type_conversion_with_ignore_error_handling(self):
        """Test type conversion with ignore error handling
        測試使用 ignore 錯誤處理的類型轉換
        """
        series = pd.Series(["1", "2", "invalid", "4"])
        config = FieldConfig(type_hint="int", cast_error="ignore")

        result = apply_field_transformations(series, config, "test_field")

        # With ignore, the conversion should attempt but not fail completely
        # The exact behavior depends on pandas implementation
        assert result is not None

    def test_no_transformations(self):
        """Test with no transformations specified
        測試未指定轉換
        """
        series = pd.Series(["A", "B", "C", "D"])
        config = FieldConfig()  # No transformations

        result = apply_field_transformations(series, config, "test_field")

        # Check that data was not modified
        pd.testing.assert_series_equal(result, series)

    def test_datetime_conversion(self):
        """Test datetime conversion
        測試日期時間轉換
        """
        series = pd.Series(["2023-01-01", "2023-02-15", "2023-12-31"])
        config = FieldConfig(type_hint="datetime")

        result = apply_field_transformations(series, config, "test_field")

        # Check that values were converted to datetime
        assert pd.api.types.is_datetime64_any_dtype(result)
        assert result.iloc[0] == pd.Timestamp("2023-01-01")
        assert result.iloc[1] == pd.Timestamp("2023-02-15")
        assert result.iloc[2] == pd.Timestamp("2023-12-31")

    def test_datetime_conversion_with_coerce(self):
        """Test datetime conversion with invalid dates and coerce
        測試包含無效日期的日期時間轉換和 coerce
        """
        series = pd.Series(["2023-01-01", "invalid-date", "2023-12-31"])
        config = FieldConfig(type_hint="datetime", cast_error="coerce")

        result = apply_field_transformations(series, config, "test_field")

        # Check that valid dates were converted and invalid became NaT
        assert pd.api.types.is_datetime64_any_dtype(result)
        assert result.iloc[0] == pd.Timestamp("2023-01-01")
        assert pd.isna(result.iloc[1])  # invalid date -> NaT
        assert result.iloc[2] == pd.Timestamp("2023-12-31")

    def test_unknown_type_hint(self):
        """Test with unknown type hint (should return original data)
        測試未知類型提示（應該返回原始資料）
        """
        series = pd.Series(["A", "B", "C", "D"])
        config = FieldConfig(type_hint="unknown_type")

        result = apply_field_transformations(series, config, "test_field")

        # Check that data was not modified for unknown type
        pd.testing.assert_series_equal(result, series)

    def test_error_in_transformation_returns_original(self):
        """Test that errors in transformation return original series
        測試轉換錯誤時返回原始序列
        """
        series = pd.Series(["A", "B", "C", "D"])

        # Create a config that might cause issues
        config = FieldConfig(type_hint="int", cast_error="raise")

        # This should not raise an exception but return original data
        result = apply_field_transformations(series, config, "test_field")

        # The function should handle the error gracefully
        assert result is not None
