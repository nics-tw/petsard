from datetime import date, datetime

import numpy as np
import pandas as pd
import pytest

from petsard.exceptions import UnfittedError
from petsard.processor.encoder import (
    EncoderDateDiff,
    EncoderLabel,
    EncoderMinguoDate,
    EncoderOneHot,
    EncoderUniform,
)


class TestEncoderUniform:
    """Test EncoderUniform with comprehensive scenarios"""

    @pytest.fixture
    def basic_categorical_data(self):
        """Basic categorical data for testing"""
        return pd.Series(["A"] * 7 + ["B"] * 3 + ["C"] * 5 + ["D"] * 5)

    @pytest.fixture
    def data_with_na(self):
        """Categorical data with missing values"""
        return pd.Series(["A", "B", np.nan, "C", "A", np.nan])

    @pytest.fixture
    def high_cardinality_data(self):
        """High cardinality categorical data"""
        return pd.Series([f"cat_{i}" for i in range(100)])

    def test_basic_functionality(self, basic_categorical_data):
        """Test basic EncoderUniform functionality"""
        encoder = EncoderUniform()

        # Test unfitted error
        with pytest.raises(UnfittedError):
            encoder.transform(basic_categorical_data)

        with pytest.raises(UnfittedError):
            encoder.inverse_transform(basic_categorical_data)

        # Fit and test
        encoder.fit(basic_categorical_data)

        assert set(encoder.labels) == set(["A", "B", "C", "D"])
        assert len(encoder.lower_values) == 4
        assert len(encoder.upper_values) == 4
        assert encoder.lower_values[2] == encoder.upper_values[1]

        # Transform
        transformed = encoder.transform(basic_categorical_data)

        assert isinstance(transformed, np.ndarray)
        assert transformed.dtype == np.float64
        assert transformed.min() >= 0
        assert transformed.max() <= 1

        # Inverse transform
        rtransformed = encoder.inverse_transform(transformed)
        assert list(rtransformed) == list(basic_categorical_data.values)

    def test_with_missing_values(self, data_with_na):
        """Test EncoderUniform with missing values"""
        encoder = EncoderUniform()
        encoder.fit(data_with_na)

        transformed = encoder.transform(data_with_na)
        assert isinstance(transformed, np.ndarray)

        # Check that NaN values are handled
        na_mask = pd.isna(data_with_na)
        assert np.isfinite(transformed[~na_mask]).all()

        rtransformed = encoder.inverse_transform(transformed)
        # Compare non-NA values
        non_na_original = data_with_na[~na_mask].values
        non_na_restored = rtransformed[~na_mask].values
        assert list(non_na_original) == list(non_na_restored)

    def test_unknown_categories_error(self, basic_categorical_data):
        """Test error when transforming unknown categories"""
        encoder = EncoderUniform()
        encoder.fit(basic_categorical_data)

        # Try to transform data with unknown category
        unknown_data = pd.Series(["A", "B", "E"])  # E is unknown
        with pytest.raises(ValueError):
            encoder.transform(unknown_data)

    def test_invalid_range_error(self, basic_categorical_data):
        """Test error when inverse transforming out-of-range values"""
        encoder = EncoderUniform()
        encoder.fit(basic_categorical_data)

        transformed = encoder.transform(basic_categorical_data)

        # Create out-of-range data
        invalid_data = transformed.copy()
        invalid_data[0] = 2.0  # Out of [0,1] range

        with pytest.raises(ValueError):
            encoder.inverse_transform(invalid_data)

    def test_high_cardinality(self, high_cardinality_data):
        """Test with high cardinality data"""
        encoder = EncoderUniform()
        encoder.fit(high_cardinality_data)

        assert len(encoder.labels) == 100

        transformed = encoder.transform(high_cardinality_data)
        assert transformed.min() >= 0
        assert transformed.max() <= 1

        rtransformed = encoder.inverse_transform(transformed)
        assert list(rtransformed) == list(high_cardinality_data.values)

    def test_single_category(self):
        """Test with single category data"""
        single_cat_data = pd.Series(["A"] * 5)
        encoder = EncoderUniform()
        encoder.fit(single_cat_data)

        transformed = encoder.transform(single_cat_data)
        # All values should be in the same range
        assert np.all(transformed >= 0) and np.all(transformed <= 1)

        rtransformed = encoder.inverse_transform(transformed)
        assert list(rtransformed) == list(single_cat_data.values)


class TestEncoderLabel:
    """Test EncoderLabel with comprehensive scenarios"""

    @pytest.fixture
    def basic_categorical_data(self):
        """Basic categorical data for testing"""
        return pd.Series(["A"] * 7 + ["B"] * 3 + ["C"] * 5 + ["D"] * 5)

    @pytest.fixture
    def numeric_categorical_data(self):
        """Numeric categorical data"""
        return pd.Series([1, 2, 3, 1, 2, 3, 1])

    def test_basic_functionality(self, basic_categorical_data):
        """Test basic EncoderLabel functionality"""
        encoder = EncoderLabel()

        # Test unfitted error
        with pytest.raises(UnfittedError):
            encoder.transform(basic_categorical_data)

        with pytest.raises(UnfittedError):
            encoder.inverse_transform(basic_categorical_data)

        # Fit and test
        encoder.fit(basic_categorical_data)

        assert set(encoder.labels) == set(["A", "B", "C", "D"])

        # Transform
        transformed = encoder.transform(basic_categorical_data)

        assert isinstance(transformed, np.ndarray)
        assert transformed.dtype == int
        assert transformed.min() >= 0
        assert transformed.max() < len(encoder.labels)

        # Inverse transform
        rtransformed = encoder.inverse_transform(transformed)
        assert list(rtransformed) == list(basic_categorical_data.values)

    def test_numeric_categories(self, numeric_categorical_data):
        """Test EncoderLabel with numeric categories"""
        encoder = EncoderLabel()
        encoder.fit(numeric_categorical_data)

        transformed = encoder.transform(numeric_categorical_data)
        rtransformed = encoder.inverse_transform(transformed)

        assert list(rtransformed) == list(numeric_categorical_data.values)

    def test_unknown_categories_error(self, basic_categorical_data):
        """Test error when transforming unknown categories"""
        encoder = EncoderLabel()
        encoder.fit(basic_categorical_data)

        # Try to transform data with unknown category
        unknown_data = pd.Series(["A", "B", "E"])  # E is unknown
        with pytest.raises(ValueError):
            encoder.transform(unknown_data)

    def test_proc_type_attribute(self):
        """Test PROC_TYPE attribute"""
        encoder = EncoderLabel()
        assert encoder.PROC_TYPE == ("encoder", "discretizing")


class TestEncoderOneHot:
    """Test EncoderOneHot functionality"""

    @pytest.fixture
    def basic_categorical_data(self):
        """Basic categorical data for testing"""
        return pd.Series(["A", "B", "C", "A", "B"])

    def test_basic_functionality(self, basic_categorical_data):
        """Test basic EncoderOneHot functionality"""
        encoder = EncoderOneHot()

        # Test unfitted error
        with pytest.raises(UnfittedError):
            encoder.transform(basic_categorical_data)

        # Fit and test
        encoder.fit(basic_categorical_data)

        assert set(encoder.labels) == set(["A", "B", "C"])

        # Transform (returns original data, stores result in _transform_temp)
        result = encoder.transform(basic_categorical_data)
        assert result.equals(basic_categorical_data)  # Should return original data
        assert encoder._transform_temp is not None
        assert encoder._transform_temp.shape[1] == 2  # drop="first", so 3-1=2 columns

    def test_sparse_output_disabled(self, basic_categorical_data):
        """Test that sparse output is disabled"""
        encoder = EncoderOneHot()
        encoder.fit(basic_categorical_data)
        encoder.transform(basic_categorical_data)

        # Should be dense array, not sparse
        assert isinstance(encoder._transform_temp, np.ndarray)
        assert not hasattr(encoder._transform_temp, "toarray")


class TestEncoderMinguoDate:
    """Test EncoderMinguoDate functionality"""

    @pytest.fixture
    def minguo_date_data(self):
        """Minguo date data for testing"""
        return pd.Series([1120903, 1130101, 1121225])  # YYYMMDD format

    @pytest.fixture
    def minguo_string_data(self):
        """Minguo date string data"""
        return pd.Series(["112-09-03", "113-01-01", "112-12-25"])

    def test_basic_functionality(self, minguo_date_data):
        """Test basic EncoderMinguoDate functionality"""
        encoder = EncoderMinguoDate()

        # Test unfitted error
        with pytest.raises(UnfittedError):
            encoder.transform(minguo_date_data)

        # Fit and test
        encoder.fit(minguo_date_data)

        # Transform
        transformed = encoder.transform(minguo_date_data)
        assert isinstance(transformed, pd.Series)

        # Check that dates are converted to AD
        for dt in transformed:
            if pd.notna(dt):
                assert isinstance(dt, (datetime, pd.Timestamp))
                assert dt.year >= 2023  # Should be AD years

        # Inverse transform
        rtransformed = encoder.inverse_transform(transformed)
        assert list(rtransformed) == list(minguo_date_data.values)

    def test_string_format(self, minguo_string_data):
        """Test with string format dates"""
        encoder = EncoderMinguoDate(input_format="str-")
        encoder.fit(minguo_string_data)

        transformed = encoder.transform(minguo_string_data)
        rtransformed = encoder.inverse_transform(transformed)

        assert list(rtransformed) == list(minguo_string_data.values)

    def test_fix_strategies(self):
        """Test fix strategies for invalid dates"""
        invalid_dates = pd.Series([1120230, 1121332])  # Invalid month/day

        encoder = EncoderMinguoDate(fix_strategies="recommend")
        encoder.fit(invalid_dates)

        # Should not raise error due to fix strategies
        transformed = encoder.transform(invalid_dates)
        assert len(transformed) == len(invalid_dates)

    def test_output_formats(self, minguo_date_data):
        """Test different output formats"""
        # Test date output
        encoder_date = EncoderMinguoDate(output_format="date")
        encoder_date.fit(minguo_date_data)
        result_date = encoder_date.transform(minguo_date_data)

        for dt in result_date:
            if pd.notna(dt):
                assert isinstance(dt, date)

        # Test string output
        encoder_string = EncoderMinguoDate(output_format="string")
        encoder_string.fit(minguo_date_data)
        result_string = encoder_string.transform(minguo_date_data)

        for dt in result_string:
            if pd.notna(dt):
                assert isinstance(dt, str)


class TestEncoderDateDiff:
    """Test EncoderDateDiff functionality"""

    @pytest.fixture
    def date_data(self):
        """Date data for testing"""
        return pd.DataFrame(
            {
                "baseline_date": pd.to_datetime(
                    ["2024-01-01", "2024-01-15", "2024-02-01"]
                ),
                "compare_date": pd.to_datetime(
                    ["2024-01-10", "2024-01-20", "2024-02-15"]
                ),
                "other_col": [1, 2, 3],
            }
        )

    def test_basic_functionality(self, date_data):
        """Test basic EncoderDateDiff functionality"""
        encoder = EncoderDateDiff(
            baseline_date="baseline_date", related_date_list=["compare_date"]
        )

        # Test unfitted error
        with pytest.raises(UnfittedError):
            encoder.transform(date_data)

        # Fit and test
        encoder.fit(date_data)

        # Transform
        transformed = encoder.transform(date_data)
        assert isinstance(transformed, pd.DataFrame)
        assert "baseline_date" in transformed.columns
        assert "compare_date" in transformed.columns

        # Check that compare_date is now numeric (days difference)
        assert pd.api.types.is_numeric_dtype(transformed["compare_date"])

        # Expected differences: 9, 5, 14 days
        expected_diffs = [9, 5, 14]
        actual_diffs = transformed["compare_date"].tolist()
        assert actual_diffs == expected_diffs

    def test_different_units(self, date_data):
        """Test different time units"""
        # Test weeks
        encoder_weeks = EncoderDateDiff(
            baseline_date="baseline_date",
            related_date_list=["compare_date"],
            diff_unit="weeks",
        )
        encoder_weeks.fit(date_data)
        result_weeks = encoder_weeks.transform(date_data)

        # Should be approximately 9/7, 5/7, 14/7 weeks
        expected_weeks = [9 / 7, 5 / 7, 14 / 7]
        actual_weeks = result_weeks["compare_date"].tolist()
        for expected, actual in zip(expected_weeks, actual_weeks):
            assert abs(expected - actual) < 0.01

    def test_absolute_value(self, date_data):
        """Test absolute value option"""
        # Create data where baseline is after compare date
        reverse_data = date_data.copy()
        reverse_data["baseline_date"], reverse_data["compare_date"] = (
            reverse_data["compare_date"],
            reverse_data["baseline_date"],
        )

        encoder = EncoderDateDiff(
            baseline_date="baseline_date",
            related_date_list=["compare_date"],
            absolute_value=True,
        )
        encoder.fit(reverse_data)
        result = encoder.transform(reverse_data)

        # All differences should be positive
        assert (result["compare_date"] >= 0).all()

    def test_inverse_transform(self, date_data):
        """Test inverse transformation"""
        encoder = EncoderDateDiff(
            baseline_date="baseline_date", related_date_list=["compare_date"]
        )
        encoder.fit(date_data)

        transformed = encoder.transform(date_data)
        rtransformed = encoder.inverse_transform(transformed)

        # Baseline date should remain unchanged
        pd.testing.assert_series_equal(
            rtransformed["baseline_date"], date_data["baseline_date"]
        )

        # Compare date should be restored (approximately)
        original_dates = date_data["compare_date"]
        restored_dates = pd.to_datetime(rtransformed["compare_date"])

        for orig, restored in zip(original_dates, restored_dates):
            assert abs((orig - restored).days) <= 1  # Allow 1 day tolerance

    def test_missing_baseline_column_error(self, date_data):
        """Test error when baseline column is missing"""
        encoder = EncoderDateDiff(
            baseline_date="nonexistent_column", related_date_list=["compare_date"]
        )

        with pytest.raises(ValueError):
            encoder.fit(date_data)

    def test_missing_related_column_error(self, date_data):
        """Test error when related column is missing"""
        encoder = EncoderDateDiff(
            baseline_date="baseline_date", related_date_list=["nonexistent_column"]
        )

        with pytest.raises(ValueError):
            encoder.fit(date_data)

    def test_invalid_diff_unit_error(self):
        """Test error with invalid diff_unit"""
        with pytest.raises(ValueError):
            EncoderDateDiff(
                baseline_date="baseline_date",
                related_date_list=["compare_date"],
                diff_unit="invalid_unit",
            )


class TestEncoderEdgeCases:
    """Test edge cases for all encoders"""

    def test_empty_data(self):
        """Test encoders with empty data"""
        empty_data = pd.Series([], dtype=object)

        encoder = EncoderUniform()
        encoder.fit(empty_data)

        transformed = encoder.transform(empty_data)
        assert len(transformed) == 0

    def test_single_value_data(self):
        """Test encoders with single value"""
        single_data = pd.Series(["A"])

        encoder = EncoderUniform()
        encoder.fit(single_data)

        transformed = encoder.transform(single_data)
        assert len(transformed) == 1
        assert 0 <= transformed[0] <= 1

        rtransformed = encoder.inverse_transform(transformed)
        assert rtransformed[0] == "A"

    def test_all_missing_data(self):
        """Test encoders with all missing data"""
        all_na_data = pd.Series([np.nan, np.nan, np.nan])

        encoder = EncoderUniform()
        encoder.fit(all_na_data)

        # Should handle all-NA data gracefully
        transformed = encoder.transform(all_na_data)
        assert len(transformed) == 3
