import numpy as np
import pandas as pd
import pytest

from petsard.exceptions import UnfittedError
from petsard.processor.missing import (
    MissingDrop,
    MissingMean,
    MissingMedian,
    MissingMode,
    MissingSimple,
)


class Test_MissingMean:
    def test_mean_no_missing_values(self):
        # Prepare test data
        df_data = pd.DataFrame({"col1": [1.0, 2.0, 3.0]})

        # Create an instance of the class
        missing = MissingMean()
        missing.set_na_percentage(0.8)

        with pytest.raises(ValueError):
            missing.set_na_percentage(1.8)

        with pytest.raises(ValueError):
            missing.set_na_percentage(-1.8)

        with pytest.raises(UnfittedError):
            missing.transform(df_data["col1"])

        # Call the method to be tested
        missing.fit(df_data["col1"])

        transformed = missing.transform(df_data["col1"])

        # Set up for inverse transform
        missing.set_imputation_index(list(range(len(df_data))))
        rtransform = missing.inverse_transform(df_data["col1"])

        # Assert the result
        assert (transformed.values == np.array([1.0, 2.0, 3.0])).all()

        # Assert the result
        assert transformed.shape == (3,)
        assert rtransform.isna().any().any()

    def test_mean_with_missing_values(self):
        # Prepare test data
        df_data = pd.DataFrame({"col1": [1.0, None, 3.0]})
        df_expected = pd.Series(data=[1.0, 2.0, 3.0], name="col1")

        # Create an instance of the class
        missing = MissingMean()
        missing.set_na_percentage(0.8)

        with pytest.raises(ValueError):
            missing.set_na_percentage(1.8)

        with pytest.raises(ValueError):
            missing.set_na_percentage(-1.8)

        with pytest.raises(UnfittedError):
            missing.transform(df_data["col1"])

        # Call the method to be tested
        missing.fit(df_data["col1"])

        transformed = missing.transform(df_data["col1"])

        # Set up for inverse transform
        missing.set_imputation_index(list(range(len(df_data))))
        rtransform = missing.inverse_transform(df_data["col1"])

        # Assert the result
        assert (transformed.values == np.array([1.0, 2.0, 3.0])).all()

        # Assert the result
        assert transformed.shape == (3,)
        assert transformed.equals(df_expected)
        assert rtransform.isna().any().any()


class Test_MissingMedian:
    def test_median_no_missing_values(self):
        # Prepare test data
        df_data = pd.DataFrame({"col1": [1.0, 2.0, 3.0]})

        # Create an instance of the class
        missing = MissingMedian()
        missing.set_na_percentage(0.8)

        with pytest.raises(ValueError):
            missing.set_na_percentage(1.8)

        with pytest.raises(ValueError):
            missing.set_na_percentage(-1.8)

        with pytest.raises(UnfittedError):
            missing.transform(df_data["col1"])

        # Call the method to be tested
        missing.fit(df_data["col1"])

        transformed = missing.transform(df_data["col1"])

        # Set up for inverse transform
        missing.set_imputation_index(list(range(len(df_data))))
        rtransform = missing.inverse_transform(df_data["col1"])

        # Assert the result
        assert (transformed.values == np.array([1.0, 2.0, 3.0])).all()

        # Assert the result
        assert transformed.shape == (3,)
        assert rtransform.isna().any().any()

    def test_median_with_missing_values(self):
        # Prepare test data
        df_data = pd.DataFrame({"col1": [1.0, None, 3.0]})
        df_expected = pd.Series(data=[1.0, 2.0, 3.0], name="col1")

        # Create an instance of the class
        missing = MissingMedian()
        missing.set_na_percentage(0.8)

        with pytest.raises(ValueError):
            missing.set_na_percentage(1.8)

        with pytest.raises(ValueError):
            missing.set_na_percentage(-1.8)

        with pytest.raises(UnfittedError):
            missing.transform(df_data["col1"])

        # Call the method to be tested
        missing.fit(df_data["col1"])

        transformed = missing.transform(df_data["col1"])

        # Set up for inverse transform
        missing.set_imputation_index(list(range(len(df_data))))
        rtransform = missing.inverse_transform(df_data["col1"])

        # Assert the result
        assert (transformed.values == np.array([1.0, 2.0, 3.0])).all()

        # Assert the result
        assert transformed.shape == (3,)
        assert transformed.equals(df_expected)
        assert rtransform.isna().any().any()


class Test_MissingSimple:
    def test_simple_no_missing_values(self):
        # Prepare test data
        df_data = pd.DataFrame({"col1": [1.0, 2.0, 3.0]})

        # Create an instance of the class
        missing = MissingSimple(value=1.0)
        missing.set_na_percentage(0.8)

        with pytest.raises(ValueError):
            missing.set_na_percentage(1.8)

        with pytest.raises(ValueError):
            missing.set_na_percentage(-1.8)

        with pytest.raises(UnfittedError):
            missing.transform(df_data["col1"])

        # Call the method to be tested
        missing.fit(df_data["col1"])

        transformed = missing.transform(df_data["col1"])

        # Set up for inverse transform
        missing.set_imputation_index(list(range(len(df_data))))
        rtransform = missing.inverse_transform(df_data["col1"])

        # Assert the result
        assert (transformed.values == np.array([1.0, 2.0, 3.0])).all()

        # Assert the result
        assert transformed.shape == (3,)
        assert rtransform.isna().any().any()

    def test_simple_with_missing_values(self):
        # Prepare test data
        df_data = pd.DataFrame({"col1": [1.0, None, 3.0]})
        df_expected = pd.Series(data=[1.0, 2.0, 3.0], name="col1")

        # Create an instance of the class
        missing = MissingSimple(value=2.0)
        missing.set_na_percentage(0.8)

        with pytest.raises(ValueError):
            missing.set_na_percentage(1.8)

        with pytest.raises(ValueError):
            missing.set_na_percentage(-1.8)

        with pytest.raises(UnfittedError):
            missing.transform(df_data["col1"])

        # Call the method to be tested
        missing.fit(df_data["col1"])

        transformed = missing.transform(df_data["col1"])

        # Set up for inverse transform
        missing.set_imputation_index(list(range(len(df_data))))
        rtransform = missing.inverse_transform(df_data["col1"])

        # Assert the result
        assert (transformed.values == np.array([1.0, 2.0, 3.0])).all()

        # Assert the result
        assert transformed.shape == (3,)
        assert transformed.equals(df_expected)
        assert rtransform.isna().any().any()


class Test_MissingDrop:
    def test_drop_no_missing_values(self):
        # Prepare test data
        df_data = pd.DataFrame({"col1": [1.0, 2.0, 3.0]})

        # Create an instance of the class
        missing = MissingDrop()
        missing.set_na_percentage(0.8)

        with pytest.raises(ValueError):
            missing.set_na_percentage(1.8)

        with pytest.raises(ValueError):
            missing.set_na_percentage(-1.8)

        with pytest.raises(UnfittedError):
            missing.transform(df_data["col1"])

        # Call the method to be tested
        missing.fit(df_data["col1"])

        transformed = missing.transform(df_data["col1"])

        # Set up for inverse transform
        missing.set_imputation_index(list(range(len(df_data))))
        rtransform = missing.inverse_transform(df_data["col1"])

        # Assert the result
        assert (transformed == np.array([False, False, False])).all()

        # Assert the result
        assert transformed.shape == (3,)
        assert rtransform.isna().any().any()

    def test_drop_with_missing_values(self):
        # Prepare test data
        df_data = pd.DataFrame({"col1": [1.0, None, 3.0]})

        # Create an instance of the class
        missing = MissingDrop()
        missing.set_na_percentage(0.8)

        with pytest.raises(ValueError):
            missing.set_na_percentage(1.8)

        with pytest.raises(ValueError):
            missing.set_na_percentage(-1.8)

        with pytest.raises(UnfittedError):
            missing.transform(df_data["col1"])

        # Call the method to be tested
        missing.fit(df_data["col1"])

        transformed = missing.transform(df_data["col1"])

        # Set up for inverse transform
        missing.set_imputation_index(list(range(len(df_data))))
        rtransform = missing.inverse_transform(df_data["col1"])

        # Assert the result
        assert (transformed == np.array([False, True, False])).all()

        # Assert the result
        assert transformed.shape == (3,)
        assert rtransform.isna().any().any()


class TestMissingMode:
    """Test MissingMode functionality"""

    def test_mode_categorical_data(self):
        """Test MissingMode with categorical data"""
        # Prepare test data - "A" appears most frequently
        df_data = pd.DataFrame({"col1": ["A", "A", "A", "B", "B", None, "C"]})

        missing = MissingMode()
        missing.set_na_percentage(0.8)

        with pytest.raises(UnfittedError):
            missing.transform(df_data["col1"])

        # Fit and transform
        missing.fit(df_data["col1"])
        transformed = missing.transform(df_data["col1"])

        # The missing value should be filled with "A" (mode)
        assert transformed.iloc[5] == "A"
        assert not transformed.isna().any()

        # Test inverse transform
        # Set up for inverse transform
        missing.set_imputation_index(list(range(len(df_data))))
        rtransform = missing.inverse_transform(df_data["col1"])
        assert rtransform.isna().any()

    def test_mode_numerical_data(self):
        """Test MissingMode with numerical data"""
        # Prepare test data - 1.0 appears most frequently
        df_data = pd.DataFrame({"col1": [1.0, 1.0, 1.0, 2.0, 2.0, None, 3.0]})

        missing = MissingMode()
        missing.fit(df_data["col1"])
        transformed = missing.transform(df_data["col1"])

        # The missing value should be filled with 1.0 (mode)
        assert transformed.iloc[5] == 1.0
        assert not transformed.isna().any()

    def test_mode_multiple_modes(self):
        """Test MissingMode when there are multiple modes"""
        # Data with multiple modes (A and B both appear twice)
        df_data = pd.DataFrame({"col1": ["A", "A", "B", "B", None, "C"]})

        missing = MissingMode()
        missing.fit(df_data["col1"])
        transformed = missing.transform(df_data["col1"])

        # Should pick one of the modes
        filled_value = transformed.iloc[4]
        assert filled_value in ["A", "B"]
        assert not transformed.isna().any()


class TestMissingWithDifferentDataTypes:
    """Test missing value handlers with different data types"""

    @pytest.fixture
    def integer_data_with_na(self):
        """Integer data with missing values"""
        return pd.DataFrame({"col1": [1, 2, None, 4, 5]})

    @pytest.fixture
    def float_data_with_na(self):
        """Float data with missing values"""
        return pd.DataFrame({"col1": [1.1, 2.2, None, 4.4, 5.5]})

    @pytest.fixture
    def string_data_with_na(self):
        """String data with missing values"""
        return pd.DataFrame({"col1": ["apple", "banana", None, "cherry", "date"]})

    @pytest.fixture
    def datetime_data_with_na(self):
        """Datetime data with missing values"""
        return pd.DataFrame(
            {
                "col1": pd.to_datetime(
                    ["2024-01-01", "2024-01-02", None, "2024-01-04", "2024-01-05"]
                )
            }
        )

    def test_mean_with_integer_data(self, integer_data_with_na):
        """Test MissingMean with integer data"""
        missing = MissingMean()
        missing.fit(integer_data_with_na["col1"])
        transformed = missing.transform(integer_data_with_na["col1"])

        # Mean of [1, 2, 4, 5] = 3.0
        assert transformed.iloc[2] == 3.0
        assert not transformed.isna().any()

    def test_mean_with_float_data(self, float_data_with_na):
        """Test MissingMean with float data"""
        missing = MissingMean()
        missing.fit(float_data_with_na["col1"])
        transformed = missing.transform(float_data_with_na["col1"])

        # Mean of [1.1, 2.2, 4.4, 5.5] = 3.3
        expected_mean = (1.1 + 2.2 + 4.4 + 5.5) / 4
        assert abs(transformed.iloc[2] - expected_mean) < 1e-10
        assert not transformed.isna().any()

    def test_median_with_integer_data(self, integer_data_with_na):
        """Test MissingMedian with integer data"""
        missing = MissingMedian()
        missing.fit(integer_data_with_na["col1"])
        transformed = missing.transform(integer_data_with_na["col1"])

        # Median of [1, 2, 4, 5] = 3.0
        assert transformed.iloc[2] == 3.0
        assert not transformed.isna().any()

    def test_mode_with_string_data(self, string_data_with_na):
        """Test MissingMode with string data"""
        missing = MissingMode()
        missing.fit(string_data_with_na["col1"])
        transformed = missing.transform(string_data_with_na["col1"])

        # Should fill with one of the values (all appear once)
        filled_value = transformed.iloc[2]
        assert filled_value in ["apple", "banana", "cherry", "date"]
        assert not transformed.isna().any()

    def test_drop_with_datetime_data(self, datetime_data_with_na):
        """Test MissingDrop with datetime data"""
        missing = MissingDrop()
        missing.fit(datetime_data_with_na["col1"])
        transformed = missing.transform(datetime_data_with_na["col1"])

        # Should return boolean mask
        expected = [False, False, True, False, False]
        assert list(transformed) == expected


class TestMissingWithExtremeValues:
    """Test missing value handlers with extreme values"""

    def test_mean_with_extreme_values(self):
        """Test MissingMean with extreme values"""
        extreme_data = pd.DataFrame({"col1": [1e10, -1e10, None, 1e-10, -1e-10]})

        missing = MissingMean()
        missing.fit(extreme_data["col1"])
        transformed = missing.transform(extreme_data["col1"])

        # Should handle extreme values without overflow
        assert np.isfinite(transformed.iloc[2])
        assert not transformed.isna().any()

    def test_median_with_extreme_values(self):
        """Test MissingMedian with extreme values"""
        extreme_data = pd.DataFrame({"col1": [1e10, -1e10, None, 1e-10, -1e-10]})

        missing = MissingMedian()
        missing.fit(extreme_data["col1"])
        transformed = missing.transform(extreme_data["col1"])

        # Median should be between the extreme values
        assert np.isfinite(transformed.iloc[2])
        assert not transformed.isna().any()

    def test_simple_with_extreme_replacement_value(self):
        """Test MissingSimple with extreme replacement value"""
        data = pd.DataFrame({"col1": [1.0, 2.0, None, 4.0, 5.0]})

        missing = MissingSimple(value=1e20)
        missing.fit(data["col1"])
        transformed = missing.transform(data["col1"])

        assert transformed.iloc[2] == 1e20
        assert not transformed.isna().any()


class TestMissingWithAllMissingData:
    """Test missing value handlers with all missing data"""

    @pytest.fixture
    def all_missing_data(self):
        """Data with all missing values"""
        return pd.DataFrame({"col1": [None, None, None, None]})

    def test_mean_with_all_missing(self, all_missing_data):
        """Test MissingMean with all missing data"""
        missing = MissingMean()
        missing.fit(all_missing_data["col1"])
        transformed = missing.transform(all_missing_data["col1"])

        # Should handle all-missing case gracefully
        # Typically fills with NaN or 0
        assert len(transformed) == 4

    def test_median_with_all_missing(self, all_missing_data):
        """Test MissingMedian with all missing data"""
        missing = MissingMedian()
        missing.fit(all_missing_data["col1"])
        transformed = missing.transform(all_missing_data["col1"])

        # Should handle all-missing case gracefully
        assert len(transformed) == 4

    def test_mode_with_all_missing(self, all_missing_data):
        """Test MissingMode with all missing data"""
        missing = MissingMode()
        missing.fit(all_missing_data["col1"])

        # MissingMode should raise error when there's no mode (all missing)
        with pytest.raises(IndexError, match="Cannot choose from an empty sequence"):
            missing.transform(all_missing_data["col1"])

    def test_drop_with_all_missing(self, all_missing_data):
        """Test MissingDrop with all missing data"""
        missing = MissingDrop()
        missing.fit(all_missing_data["col1"])
        transformed = missing.transform(all_missing_data["col1"])

        # Should return all True (all rows to be dropped)
        assert list(transformed) == [True, True, True, True]


class TestMissingParameterValidation:
    """Test parameter validation for missing value handlers"""

    def test_na_percentage_validation(self):
        """Test NA percentage validation"""
        missing = MissingMean()

        # Valid percentages
        missing.set_na_percentage(0.0)
        missing.set_na_percentage(0.5)
        missing.set_na_percentage(1.0)

        # Invalid percentages
        with pytest.raises(ValueError):
            missing.set_na_percentage(-0.1)

        with pytest.raises(ValueError):
            missing.set_na_percentage(1.1)

        with pytest.raises(ValueError):
            missing.set_na_percentage(2.0)

    def test_simple_value_parameter(self):
        """Test MissingSimple value parameter"""
        # Test with different value types
        MissingSimple(value=0)
        MissingSimple(value=0.0)
        MissingSimple(value="default")
        MissingSimple(value=None)

        # Test that value is used correctly
        data = pd.DataFrame({"col1": [1, 2, None, 4]})
        missing = MissingSimple(value=999)
        missing.fit(data["col1"])
        transformed = missing.transform(data["col1"])

        assert transformed.iloc[2] == 999


class TestMissingInverseTransform:
    """Test inverse transform functionality for missing value handlers"""

    def test_inverse_transform_restores_missing_values(self):
        """Test that inverse transform restores missing values"""
        data = pd.DataFrame({"col1": [1.0, 2.0, None, 4.0, 5.0]})

        for MissingClass in [
            MissingMean,
            MissingMedian,
            MissingMode,
            MissingSimple,
            MissingDrop,
        ]:
            if MissingClass == MissingSimple:
                missing = MissingClass(value=0.0)
            else:
                missing = MissingClass()

            missing.set_na_percentage(0.2)  # 20% missing
            missing.fit(data["col1"])

            # Transform should fill missing values
            transformed = missing.transform(data["col1"])
            if MissingClass != MissingDrop:
                assert not transformed.isna().any()

            # Inverse transform should restore some missing values
            # Set up for inverse transform
            missing.set_imputation_index(list(range(len(data))))
            rtransformed = missing.inverse_transform(data["col1"])
            assert rtransformed.isna().any()

    def test_inverse_transform_with_different_na_percentages(self):
        """Test inverse transform with different NA percentages"""
        data = pd.DataFrame({"col1": [1.0, 2.0, 3.0, 4.0, 5.0]})

        missing = MissingMean()

        # Test with different NA percentages
        for na_pct in [0.0, 0.2, 0.5, 0.8, 1.0]:
            missing.set_na_percentage(na_pct)
            missing.fit(data["col1"])

            # Set up for inverse transform
            missing.set_imputation_index(list(range(len(data))))
            rtransformed = missing.inverse_transform(data["col1"])

            if na_pct == 0.0:
                # No missing values should be introduced
                assert not rtransformed.isna().any()
            elif na_pct == 1.0:
                # All values should be missing
                assert rtransformed.isna().all()
            else:
                # Some values should be missing
                actual_na_pct = rtransformed.isna().sum() / len(rtransformed)
                # Allow some tolerance due to random sampling
                assert abs(actual_na_pct - na_pct) < 0.3


class TestMissingEdgeCases:
    """Test edge cases for missing value handlers"""

    def test_single_value_data(self):
        """Test with single value data"""
        single_data = pd.DataFrame({"col1": [5.0]})

        missing = MissingMean()
        missing.fit(single_data["col1"])
        transformed = missing.transform(single_data["col1"])

        assert len(transformed) == 1
        assert transformed.iloc[0] == 5.0

    def test_empty_data(self):
        """Test with empty data"""
        empty_data = pd.DataFrame({"col1": pd.Series([], dtype=float)})

        missing = MissingMean()
        missing.fit(empty_data["col1"])
        transformed = missing.transform(empty_data["col1"])

        assert len(transformed) == 0

    def test_data_with_inf_values(self):
        """Test with infinite values"""
        inf_data = pd.DataFrame({"col1": [1.0, np.inf, None, -np.inf, 5.0]})

        missing = MissingMean()
        missing.fit(inf_data["col1"])

        # Should handle infinite values gracefully
        transformed = missing.transform(inf_data["col1"])
        assert len(transformed) == 5

    def test_proc_type_attributes(self):
        """Test PROC_TYPE attributes for all missing handlers"""
        handlers = [MissingMean, MissingMedian, MissingMode, MissingSimple, MissingDrop]

        for HandlerClass in handlers:
            handler = (
                HandlerClass()
                if HandlerClass != MissingSimple
                else HandlerClass(value=0)
            )
            assert hasattr(handler, "PROC_TYPE")
            assert "missing" in handler.PROC_TYPE
