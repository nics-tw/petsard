"""Tests for field functions module
測試欄位函數模組
"""

import numpy as np
import pandas as pd

from petsard.metadater.field.field_functions import (
    _comprehensive_type_analysis,
    _has_leading_zeros,
    build_field_metadata,
)
from petsard.metadater.field.field_types import FieldConfig


class TestComprehensiveTypeAnalysis:
    """Test cases for comprehensive type analysis
    完整類型分析的測試案例
    """

    def test_leading_zero_detection(self):
        """Test leading zero detection and preservation
        測試前導零檢測和保留
        """
        # Test data with leading zeros
        leading_zero_data = pd.Series(["001", "002", "010", "099"])
        config = FieldConfig(auto_detect_leading_zeros=True)

        result = _comprehensive_type_analysis(leading_zero_data, config)
        assert result == "string", f"前導零應該返回 string，但得到 {result}"

    def test_float_detection(self):
        """Test float number detection
        測試浮點數檢測
        """
        float_data = pd.Series(["1.5", "2.7", "3.14", "4.0"])
        config = FieldConfig()

        result = _comprehensive_type_analysis(float_data, config)
        assert result in ["float32", "float64"], (
            f"浮點數應該返回 float，但得到 {result}"
        )

    def test_integer_with_nulls(self):
        """Test integer with null values using nullable integers
        測試含空值整數使用 nullable integer
        """
        int_with_na = pd.Series(["10", "20", np.nan, "30"])
        config = FieldConfig(force_nullable_integers=True)

        result = _comprehensive_type_analysis(int_with_na, config)
        assert result.startswith("Int"), f"含空值整數應該返回 Int，但得到 {result}"

    def test_integer_without_nulls(self):
        """Test integer without null values
        測試無空值整數
        """
        int_no_na = pd.Series(["10", "20", "30", "40"])
        config = FieldConfig()

        result = _comprehensive_type_analysis(int_no_na, config)
        assert result.startswith("int"), f"無空值整數應該返回 int，但得到 {result}"

    def test_mixed_non_numeric_data(self):
        """Test mixed non-numeric data
        測試混合非數值資料
        """
        mixed_data = pd.Series(["abc", "def", "ghi"])
        config = FieldConfig()

        result = _comprehensive_type_analysis(mixed_data, config)
        assert result == "category", f"混合資料應該返回 category，但得到 {result}"

    def test_numeric_conversion_threshold(self):
        """Test numeric conversion threshold (80%)
        測試數值轉換門檻值 (80%)
        """
        # 60% numeric data (below threshold)
        mixed_data = pd.Series(["10", "20", "abc", "def", "ghi"])
        config = FieldConfig()

        result = _comprehensive_type_analysis(mixed_data, config)
        assert result == "category", (
            f"低於門檻值的混合資料應該返回 category，但得到 {result}"
        )

    def test_integer_dtype_handling(self):
        """Test handling of different integer dtypes from pd.to_numeric
        測試處理 pd.to_numeric 產生的不同整數類型
        """
        # This will be converted to int64 by pd.to_numeric
        int_data = pd.Series(["100", "200", "300"])
        config = FieldConfig()

        result = _comprehensive_type_analysis(int_data, config)
        assert result.startswith("int"), f"整數資料應該返回 int 類型，但得到 {result}"


class TestLeadingZeroDetection:
    """Test cases for leading zero detection
    前導零檢測的測試案例
    """

    def test_has_leading_zeros_positive(self):
        """Test positive cases for leading zero detection
        測試前導零檢測的正面案例
        """
        # More than 30% have leading zeros
        data = pd.Series(["001", "002", "010", "099", "100"])  # 4/5 = 80%
        assert _has_leading_zeros(data) is True

    def test_has_leading_zeros_negative(self):
        """Test negative cases for leading zero detection
        測試前導零檢測的負面案例
        """
        # Less than 30% have leading zeros
        data = pd.Series(["100", "200", "300", "001"])  # 1/4 = 25% < 30%
        assert _has_leading_zeros(data) is False

    def test_has_leading_zeros_empty_data(self):
        """Test leading zero detection with empty data
        測試空資料的前導零檢測
        """
        data = pd.Series([], dtype=object)
        assert _has_leading_zeros(data) is False

    def test_has_leading_zeros_all_na(self):
        """Test leading zero detection with all NA values
        測試全為 NA 值的前導零檢測
        """
        data = pd.Series([np.nan, np.nan, np.nan])
        assert _has_leading_zeros(data) is False

    def test_has_leading_zeros_mixed_types(self):
        """Test leading zero detection with mixed data types
        測試混合資料類型的前導零檢測
        """
        data = pd.Series(["001", "002", "abc", "010"])  # 3/4 = 75%
        assert _has_leading_zeros(data) is True


class TestFieldMetadataIntegration:
    """Test cases for field metadata integration with new features
    欄位元資料與新功能整合的測試案例
    """

    def test_build_field_metadata_with_leading_zeros(self):
        """Test building field metadata with leading zero detection
        測試建立含前導零檢測的欄位元資料
        """
        data = pd.Series(["001", "002", "003"])

        # With leading zero detection enabled
        config_on = FieldConfig(auto_detect_leading_zeros=True)
        metadata_on = build_field_metadata(data, "test_field", config_on)
        assert metadata_on.target_dtype == "string"

        # With leading zero detection disabled
        config_off = FieldConfig(auto_detect_leading_zeros=False)
        metadata_off = build_field_metadata(data, "test_field", config_off)
        # Should be treated as numeric and converted to int
        assert metadata_off.target_dtype.startswith("int")

    def test_build_field_metadata_with_nullable_integers(self):
        """Test building field metadata with nullable integers
        測試建立含 nullable integer 的欄位元資料
        """
        data = pd.Series([1, 2, np.nan, 4], dtype="float64")

        # With nullable integers enabled
        config_on = FieldConfig(force_nullable_integers=True)
        metadata_on = build_field_metadata(data, "test_field", config_on)
        assert metadata_on.target_dtype.startswith("Int")

        # With nullable integers disabled
        config_off = FieldConfig(force_nullable_integers=False)
        metadata_off = build_field_metadata(data, "test_field", config_off)
        # Should remain as regular int (but might be optimized)
        assert metadata_off.target_dtype.startswith("int")

    def test_build_field_metadata_dtype_optimization(self):
        """Test dtype optimization in field metadata
        測試欄位元資料中的類型優化
        """
        # Small integers should be optimized to int8
        small_int_data = pd.Series([1, 2, 3, 4])
        metadata = build_field_metadata(small_int_data, "small_int")
        assert metadata.target_dtype == "int8"

        # Large integers should use int64
        large_int_data = pd.Series([1000000, 2000000, 3000000])
        metadata = build_field_metadata(large_int_data, "large_int")
        assert metadata.target_dtype in ["int32", "int64"]

        # Small floats should be optimized to float32
        small_float_data = pd.Series([1.1, 2.2, 3.3])
        metadata = build_field_metadata(small_float_data, "small_float")
        assert metadata.target_dtype == "float32"


class TestAmbiguousDataScenarios:
    """Test cases for ambiguous data type scenarios
    容易誤判、型別判斷模糊資料情境的測試案例
    """

    def test_id_code_preservation(self):
        """Test preservation of ID codes with leading zeros
        測試保留前導零的識別代號
        """
        id_codes = pd.Series(["001", "002", "010", "099", "100"])
        config = FieldConfig(auto_detect_leading_zeros=True)

        result = _comprehensive_type_analysis(id_codes, config)
        assert result == "string", "識別代號應該保留為字串類型"

    def test_demographic_data_with_missing_values(self):
        """Test demographic data with missing values
        測試含缺失值的人口統計資料
        """
        demographic_data = pd.Series([25, 30, np.nan, 45, 50], dtype="float64")
        config = FieldConfig(force_nullable_integers=True)

        metadata = build_field_metadata(demographic_data, "demographic", config)
        assert metadata.target_dtype.startswith("Int"), (
            "人口統計資料應該使用 nullable integer"
        )

    def test_financial_amount_detection(self):
        """Test financial amount data as float numbers
        測試金額資料的浮點數檢測
        """
        amount_data = pd.Series([50000.5, 60000.7, np.nan, 75000.3, 80000.9])
        config = FieldConfig()

        result = _comprehensive_type_analysis(amount_data, config)
        assert result.startswith("float"), "金額資料應該被識別為浮點數"

    def test_score_integer_detection(self):
        """Test score data as integers
        測試分數資料的整數檢測
        """
        score_data = pd.Series([85, 90, 78, 92, 88])
        config = FieldConfig()

        metadata = build_field_metadata(score_data, "score", config)
        assert metadata.target_dtype.startswith("int"), "分數資料應該被識別為整數"

    def test_categorical_data_detection(self):
        """Test categorical data detection
        測試分類資料檢測
        """
        category_data = pd.Series(["A級", "B級", "C級", "A級", "B級"])
        config = FieldConfig()

        metadata = build_field_metadata(category_data, "category", config)
        assert metadata.target_dtype == "category", "分類資料應該被識別為分類資料"


class TestEdgeCases:
    """Test cases for edge cases and error handling
    邊界情況和錯誤處理的測試案例
    """

    def test_empty_series(self):
        """Test handling of empty series
        測試處理空序列
        """
        empty_data = pd.Series([], dtype=object)
        config = FieldConfig()

        result = _comprehensive_type_analysis(empty_data, config)
        assert result == "category", "空序列應該返回 category"

    def test_all_null_series(self):
        """Test handling of all-null series
        測試處理全空值序列
        """
        null_data = pd.Series([np.nan, np.nan, np.nan])
        config = FieldConfig()

        result = _comprehensive_type_analysis(null_data, config)
        # 全空值序列會被 pd.to_numeric 轉換為 float，然後優化為 float32
        assert result in ["float32", "category"], (
            "全空值序列應該返回 float32 或 category"
        )

    def test_single_value_series(self):
        """Test handling of single value series
        測試處理單值序列
        """
        single_data = pd.Series(["001"])
        config = FieldConfig(auto_detect_leading_zeros=True)

        result = _comprehensive_type_analysis(single_data, config)
        assert result == "string", "單個前導零值應該被識別為字串"

    def test_mixed_numeric_string_data(self):
        """Test handling of mixed numeric and string data
        測試處理混合數值和字串資料
        """
        mixed_data = pd.Series(["10", "20", "abc", "30", "def"])
        config = FieldConfig()

        result = _comprehensive_type_analysis(mixed_data, config)
        assert result == "category", "混合數值字串資料應該返回 category"

    def test_config_none_handling(self):
        """Test handling when config is None
        測試 config 為 None 的處理
        """
        data = pd.Series([1, 2, 3])

        result = _comprehensive_type_analysis(data, None)
        assert result.startswith("int"), "None config 應該使用預設配置"
