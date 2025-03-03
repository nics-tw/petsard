import numpy as np
import pandas as pd
import pytest
from sklearn.preprocessing import StandardScaler

from petsard.exceptions import UnfittedError
from petsard.processor.scaler import (
    ScalerLog,
    ScalerMinMax,
    ScalerStandard,
    ScalerTimeAnchor,
    ScalerZeroCenter,
)


class BaseScalerTest:
    """Base class for all scaler tests"""

    @property
    def scaler_class(self):
        """The scaler class to be tested"""
        raise NotImplementedError

    def test_unfitted_error(self):
        """Test that unfitted scaler raises proper error"""
        df_data = pd.DataFrame({"col1": [1.0, 2.0, 3.0]})
        scaler = self.scaler_class()

        with pytest.raises(UnfittedError):
            scaler.transform(df_data["col1"])

        with pytest.raises(UnfittedError):
            scaler.inverse_transform(df_data["col1"])


class Test_ScalerStandard(BaseScalerTest):
    @property
    def scaler_class(self):
        return ScalerStandard

    def test_standard_scaling(self):
        # Create a sample dataframe
        df_data = pd.DataFrame({"col1": [1.0, 2.0, 3.0], "col2": [4.0, 5.0, 6.0]})
        df_expected = pd.DataFrame(
            StandardScaler().fit_transform(df_data), columns=["col1", "col2"]
        )

        # Create an instance of the class
        scaler = self.scaler_class()
        scaler.fit(df_data["col1"])
        transformed = scaler.transform(df_data["col1"])

        # Assert that the dataframe is correct
        assert list(transformed) == list(df_expected["col1"].values)


class Test_ScalerZeroCenter(BaseScalerTest):
    @property
    def scaler_class(self):
        return ScalerZeroCenter

    def test_zero_center_scaling(self):
        # Create a sample dataframe
        df_data = pd.DataFrame({"col1": [1.0, 2.0, 3.0], "col2": [4.0, 5.0, 6.0]})
        df_expected = pd.DataFrame({"col1": [-1.0, 0.0, 1.0], "col2": [-1.0, 0.0, 1.0]})

        # Create an instance of the class
        scaler = self.scaler_class()
        scaler.fit(df_data["col1"])
        transformed = scaler.transform(df_data["col1"])

        # Assert that the dataframe is correct
        assert list(transformed) == list(df_expected["col1"].values)


class Test_ScalerMinMax(BaseScalerTest):
    @property
    def scaler_class(self):
        return ScalerMinMax

    def test_minmax_scaling(self):
        # Create a sample dataframe
        df_data = pd.DataFrame({"col1": [1.0, 2.0, 3.0], "col2": [4.0, 5.0, 6.0]})
        df_expected = pd.DataFrame({"col1": [0.0, 0.5, 1.0], "col2": [0.0, 0.5, 1.0]})

        # Create an instance of the class
        scaler = self.scaler_class()
        scaler.fit(df_data["col1"])
        transformed = scaler.transform(df_data["col1"])

        # Assert that the dataframe is correct
        assert list(transformed) == list(df_expected["col1"].values)


class Test_ScalerLog(BaseScalerTest):
    @property
    def scaler_class(self):
        return ScalerLog

    def test_log_scaling(self):
        # Create a sample dataframe with positive values
        df_data = pd.DataFrame({"col1": [1.0, 2.0, 3.0]})

        # Create an instance of the class
        scaler = self.scaler_class()
        scaler.fit(df_data["col1"])
        transformed = scaler.transform(df_data["col1"])

        # Test expected log values
        expected = np.log(df_data["col1"].values)
        assert np.allclose(transformed.ravel(), expected)

    def test_negative_values(self):
        # Test negative values
        df_negative = pd.DataFrame({"col1": [-1.0, 0.0, 1.0]})
        scaler = self.scaler_class()
        with pytest.raises(ValueError):
            scaler.fit(df_negative["col1"])


class Test_ScalerTimeAnchor(BaseScalerTest):
    @property
    def scaler_class(self):
        return ScalerTimeAnchor

    def test_time_anchor_scaling(self):
        """Test scaling with reference series"""
        # Create sample datetime data
        reference_dates = pd.Series(
            pd.date_range(start="2024-01-01", periods=3, freq="D")
        )
        target_dates = pd.Series(pd.date_range(start="2024-01-02", periods=3, freq="D"))

        # Create scaler with days unit
        scaler = self.scaler_class(unit="D")

        # Set reference series and fit
        scaler.set_reference_time(reference_dates)
        scaler.fit(target_dates)

        # Transform target column
        transformed = scaler.transform(target_dates)

        # Each target date should be 1 day after its reference date
        expected = np.array([1.0, 1.0, 1.0]).reshape(-1, 1)
        np.testing.assert_array_almost_equal(transformed, expected)

        # Test inverse transform
        inverse_transformed = scaler.inverse_transform(transformed)
        expected_dates = target_dates.values.reshape(-1, 1)
        np.testing.assert_array_equal(inverse_transformed, expected_dates)

    def test_time_anchor_seconds(self):
        """Test scaling with seconds unit"""
        # Create sample datetime data with 1 hour differences
        reference_dates = pd.Series(
            pd.date_range(start="2024-01-01", periods=3, freq="h")
        )
        target_dates = pd.Series(
            pd.date_range(start="2024-01-01 01:00", periods=3, freq="h")
        )

        # Create scaler with seconds unit
        scaler = self.scaler_class(unit="S")

        # Set reference series and fit
        scaler.set_reference_time(reference_dates)
        scaler.fit(target_dates)

        # Transform target column
        transformed = scaler.transform(target_dates)

        # Each target date should be 3600 seconds (1 hour) after its reference date
        expected = np.array([3600.0, 3600.0, 3600.0]).reshape(-1, 1)
        np.testing.assert_array_almost_equal(transformed, expected)

        # Test inverse transform
        inverse_transformed = scaler.inverse_transform(transformed)
        expected_dates = target_dates.values.reshape(-1, 1)
        np.testing.assert_array_equal(inverse_transformed, expected_dates)

    def test_missing_reference(self):
        """Test error when reference is not set"""
        dates = pd.Series(pd.date_range(start="2024-01-01", periods=3, freq="D"))

        scaler = self.scaler_class(unit="D")

        with pytest.raises(ValueError, match="Reference series not set"):
            scaler.fit(dates)

    def test_length_mismatch(self):
        """Test error when reference and target lengths don't match"""
        reference_dates = pd.Series(
            pd.date_range(start="2024-01-01", periods=3, freq="D")
        )
        target_dates = pd.Series(pd.date_range(start="2024-01-01", periods=4, freq="D"))

        scaler = self.scaler_class(unit="D")
        scaler.set_reference_time(reference_dates)

        with pytest.raises(
            ValueError, match="Target and reference must have same length"
        ):
            scaler.fit(target_dates)

    def test_invalid_unit(self):
        """Test error with invalid time unit"""
        with pytest.raises(
            ValueError, match="unit must be either 'D'\\(days\\) or 'S'\\(seconds\\)"
        ):
            self.scaler_class(unit="H")

    def test_invalid_data_type(self):
        """Test error with non-datetime data"""
        reference_dates = pd.Series(
            pd.date_range(start="2024-01-01", periods=3, freq="D")
        )
        invalid_data = pd.Series([1, 2, 3])

        scaler = self.scaler_class(unit="D")
        scaler.set_reference_time(reference_dates)

        with pytest.raises(ValueError, match="Data must be in datetime format"):
            scaler.fit(invalid_data)

    def test_invalid_reference_type(self):
        """Test error with non-datetime reference"""
        invalid_reference = pd.Series([1, 2, 3])
        dates = pd.Series(pd.date_range(start="2024-01-01", periods=3, freq="D"))

        scaler = self.scaler_class(unit="D")

        with pytest.raises(ValueError, match="Reference data must be datetime type"):
            scaler.set_reference_time(invalid_reference)
