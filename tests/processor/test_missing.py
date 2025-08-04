import numpy as np
import pandas as pd
import pytest

from petsard.exceptions import UnfittedError
from petsard.processor.missing import (
    MissingDrop,
    MissingMean,
    MissingMedian,
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
        missing.set_imputation_index(
            [0, 1, 2]
        )  # Set imputation index for inverse_transform

        transformed = missing.transform(df_data["col1"])

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
        missing.set_imputation_index(
            [0, 1, 2]
        )  # Set imputation index for inverse_transform

        transformed = missing.transform(df_data["col1"])

        rtransform = missing.inverse_transform(df_data["col1"])

        # Assert the result
        assert (transformed.values == np.array([1.0, 2.0, 3.0])).all()

        # Assert the result
        assert transformed.shape == (3,)
        assert transformed.equals(df_expected)
        assert rtransform.isna().any().any()

    def test_mean_with_integer_dtype(self):
        """Test MissingMean with pandas nullable integer types (Int32, Int64, etc.)"""
        # Test Int32 type with missing values
        df_data = pd.DataFrame({"col1": pd.Series([10, None, 30], dtype="Int32")})

        # Create an instance of the class
        missing = MissingMean()
        missing.fit(df_data["col1"])

        # Transform should work without TypeError
        transformed = missing.transform(df_data["col1"])

        # The mean of [10, 30] is 20.0, which should be rounded to 20 for Int32
        expected = pd.Series([10, 20, 30], dtype="Int32", name="col1")

        # Assert the result
        assert transformed.equals(expected)
        assert transformed.dtype == "Int32"

        # Test Int64 type
        df_data_int64 = pd.DataFrame(
            {"col1": pd.Series([100, None, 300], dtype="Int64")}
        )
        missing_int64 = MissingMean()
        missing_int64.fit(df_data_int64["col1"])
        transformed_int64 = missing_int64.transform(df_data_int64["col1"])

        expected_int64 = pd.Series([100, 200, 300], dtype="Int64", name="col1")
        assert transformed_int64.equals(expected_int64)
        assert transformed_int64.dtype == "Int64"

    def test_mean_with_integer_dtype_fractional_mean(self):
        """Test MissingMean with integer dtype when mean has fractional part"""
        # Test case where mean is not a whole number
        df_data = pd.DataFrame({"col1": pd.Series([10, None, 31], dtype="Int32")})

        missing = MissingMean()
        missing.fit(df_data["col1"])
        transformed = missing.transform(df_data["col1"])

        # The mean of [10, 31] is 20.5, which should be rounded to 20 for Int32 (banker's rounding)
        expected = pd.Series([10, 20, 31], dtype="Int32", name="col1")

        assert transformed.equals(expected)
        assert transformed.dtype == "Int32"


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
        missing.set_imputation_index(
            [0, 1, 2]
        )  # Set imputation index for inverse_transform

        transformed = missing.transform(df_data["col1"])

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
        missing.set_imputation_index(
            [0, 1, 2]
        )  # Set imputation index for inverse_transform

        transformed = missing.transform(df_data["col1"])

        rtransform = missing.inverse_transform(df_data["col1"])

        # Assert the result
        assert (transformed.values == np.array([1.0, 2.0, 3.0])).all()

        # Assert the result
        assert transformed.shape == (3,)
        assert transformed.equals(df_expected)
        assert rtransform.isna().any().any()

    def test_median_with_integer_dtype(self):
        """Test MissingMedian with pandas nullable integer types (Int32, Int64, etc.)"""
        # Test Int32 type with missing values
        df_data = pd.DataFrame({"col1": pd.Series([10, None, 30], dtype="Int32")})

        # Create an instance of the class
        missing = MissingMedian()
        missing.fit(df_data["col1"])

        # Transform should work without TypeError
        transformed = missing.transform(df_data["col1"])

        # The median of [10, 30] is 20.0, which should be rounded to 20 for Int32
        expected = pd.Series([10, 20, 30], dtype="Int32", name="col1")

        # Assert the result
        assert transformed.equals(expected)
        assert transformed.dtype == "Int32"

        # Test Int64 type
        df_data_int64 = pd.DataFrame(
            {"col1": pd.Series([100, None, 300], dtype="Int64")}
        )
        missing_int64 = MissingMedian()
        missing_int64.fit(df_data_int64["col1"])
        transformed_int64 = missing_int64.transform(df_data_int64["col1"])

        expected_int64 = pd.Series([100, 200, 300], dtype="Int64", name="col1")
        assert transformed_int64.equals(expected_int64)
        assert transformed_int64.dtype == "Int64"

    def test_median_with_integer_dtype_fractional_median(self):
        """Test MissingMedian with integer dtype when median has fractional part"""
        # Test case where median is not a whole number
        df_data = pd.DataFrame({"col1": pd.Series([10, None, 31], dtype="Int32")})

        missing = MissingMedian()
        missing.fit(df_data["col1"])
        transformed = missing.transform(df_data["col1"])

        # The median of [10, 31] is 20.5, which should be rounded to 20 for Int32 (banker's rounding)
        expected = pd.Series([10, 20, 31], dtype="Int32", name="col1")

        assert transformed.equals(expected)
        assert transformed.dtype == "Int32"


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
        missing.set_imputation_index(
            [0, 1, 2]
        )  # Set imputation index for inverse_transform

        transformed = missing.transform(df_data["col1"])

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
        missing.set_imputation_index(
            [0, 1, 2]
        )  # Set imputation index for inverse_transform

        transformed = missing.transform(df_data["col1"])

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
        missing.set_imputation_index(
            [0, 1, 2]
        )  # Set imputation index for inverse_transform

        transformed = missing.transform(df_data["col1"])

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
        missing.set_imputation_index(
            [0, 1, 2]
        )  # Set imputation index for inverse_transform

        transformed = missing.transform(df_data["col1"])

        rtransform = missing.inverse_transform(df_data["col1"])

        # Assert the result
        assert (transformed == np.array([False, True, False])).all()

        # Assert the result
        assert transformed.shape == (3,)
        assert rtransform.isna().any().any()
