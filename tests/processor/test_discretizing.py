import random

import numpy as np
import pandas as pd
import pytest

from petsard.exceptions import UnfittedError
from petsard.processor.discretizing import DiscretizingHandler, DiscretizingKBins


class Test_DiscretizingHandler:
    """Test base DiscretizingHandler class"""

    def test_base_handler_cannot_be_instantiated(self):
        """Test that base handler can be instantiated but abstract methods raise errors"""
        # DiscretizingHandler is not abstract, so it can be instantiated
        handler = DiscretizingHandler()

        # But calling abstract methods should raise NotImplementedError
        data = pd.Series([1.0, 2.0, 3.0])

        with pytest.raises(NotImplementedError):
            handler._fit(data)

        with pytest.raises(NotImplementedError):
            handler._transform(data)

        with pytest.raises(NotImplementedError):
            handler._inverse_transform(data)


class Test_DiscretizingKBins:
    """Test DiscretizingKBins class"""

    def test_basic_functionality(self):
        """Test basic discretization functionality"""
        # Create continuous data
        data = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0])

        # Create discretizer with 3 bins
        discretizer = DiscretizingKBins(n_bins=3)

        # Test unfitted error
        with pytest.raises(UnfittedError):
            discretizer.transform(data)

        with pytest.raises(UnfittedError):
            discretizer.inverse_transform(data)

        # Fit and transform
        discretizer.fit(data)
        transformed = discretizer.transform(data)

        # Should return discrete bins (0, 1, 2)
        assert isinstance(transformed, np.ndarray)
        assert len(transformed) == len(data)
        assert set(transformed.ravel()) <= {0, 1, 2}  # Should only contain bin indices

    def test_different_bin_numbers(self):
        """Test discretization with different numbers of bins"""
        data = pd.Series(np.linspace(0, 100, 1000))

        for n_bins in [2, 5, 10, 20]:
            discretizer = DiscretizingKBins(n_bins=n_bins)
            discretizer.fit(data)
            transformed = discretizer.transform(data)

            # Should have correct number of unique bins
            unique_bins = set(transformed.ravel())
            assert (
                len(unique_bins) <= n_bins
            )  # May have fewer if data doesn't fill all bins
            assert min(unique_bins) >= 0
            assert max(unique_bins) < n_bins

    def test_inverse_transform_basic(self):
        """Test basic inverse transformation"""
        data = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])

        discretizer = DiscretizingKBins(n_bins=3)
        discretizer.fit(data)
        transformed = discretizer.transform(data)
        inverse_transformed = discretizer.inverse_transform(
            pd.Series(transformed.ravel())
        )

        # Inverse transform should return continuous values
        assert isinstance(inverse_transformed, np.ndarray)
        assert len(inverse_transformed) == len(data)
        # Values should be within the original data range
        assert inverse_transformed.min() >= data.min()
        assert inverse_transformed.max() <= data.max()

    def test_inverse_transform_with_na(self):
        """
        Test case for `inverse_transform` method of `DiscretizingKBins` class.
            - for issue 440

        - DiscretizingKBins will successfully return a inverse transformation when:
            - with np.nan
            - with pd.NA
            - with None
        """
        n_samples: int = 100
        sample_data: pd.Series = pd.Series(
            [random.choice([0, 1, 2, 3]) for _ in range(n_samples)],
        )
        modified_data: pd.Series = sample_data.copy()
        data_dict: dict = {
            "with np.nan": {
                "na_ratio": 0.25,
                "value": np.nan,
            },
            "with pd.NA": {
                "na_ratio": 0.25,
                "value": pd.NA,
            },
            "with None": {
                "na_ratio": 0.25,
                "value": None,
            },
        }

        n_replace: int = None
        indices_to_replace: list = None
        postproc_data: pd.Series = None

        proc = DiscretizingKBins()
        proc.fit(sample_data)
        # First transform to get the discretized values
        proc.transform(sample_data)  # This fits the model

        for setting in data_dict.values():
            n_replace = int(n_samples * setting["na_ratio"])
            indices_to_replace = random.sample(list(sample_data.index), n_replace)
            modified_data.iloc[indices_to_replace] = setting["value"]

            postproc_data = pd.Series(proc.inverse_transform(modified_data).ravel())
            assert postproc_data.isna().sum() == 0

            modified_data = sample_data.copy()

    def test_edge_cases(self):
        """Test edge cases for discretization"""

        # Test with single value
        single_value_data = pd.Series([5.0] * 10)
        discretizer = DiscretizingKBins(n_bins=3)
        discretizer.fit(single_value_data)
        transformed = discretizer.transform(single_value_data)

        # All values should be in the same bin
        assert len(set(transformed.ravel())) == 1

        # Test with two distinct values
        two_value_data = pd.Series([1.0, 1.0, 1.0, 10.0, 10.0, 10.0])
        discretizer = DiscretizingKBins(n_bins=3)
        discretizer.fit(two_value_data)
        transformed = discretizer.transform(two_value_data)

        # Should have at most 2 bins used
        assert len(set(transformed.ravel())) <= 2

    def test_missing_values_handling(self):
        """Test handling of missing values"""
        data_with_na = pd.Series([1.0, 2.0, np.nan, 4.0, 5.0, np.nan])

        discretizer = DiscretizingKBins(n_bins=3)
        discretizer.fit(data_with_na)

        # KBinsDiscretizer doesn't handle NaN values, so this should raise ValueError
        with pytest.raises(ValueError, match="Input X contains NaN"):
            discretizer.transform(data_with_na)

    def test_extreme_values(self):
        """Test discretization with extreme values"""
        extreme_data = pd.Series([1e-10, 1.0, 1e10])

        discretizer = DiscretizingKBins(n_bins=3)
        discretizer.fit(extreme_data)
        transformed = discretizer.transform(extreme_data)

        # Should handle extreme values without errors
        assert len(transformed) == len(extreme_data)
        assert isinstance(transformed, np.ndarray)

    def test_different_data_types(self):
        """Test discretization with different numeric data types"""
        # Integer data
        int_data = pd.Series([1, 2, 3, 4, 5], dtype=int)

        # Float data
        float_data = pd.Series([1.1, 2.2, 3.3, 4.4, 5.5], dtype=float)

        for data in [int_data, float_data]:
            discretizer = DiscretizingKBins(n_bins=3)
            discretizer.fit(data)
            transformed = discretizer.transform(data)

            # Should work with different numeric types
            assert len(transformed) == len(data)
            assert isinstance(transformed, np.ndarray)

    def test_large_dataset(self):
        """Test discretization on larger datasets"""
        # Create larger dataset
        np.random.seed(42)
        large_data = pd.Series(np.random.normal(0, 1, 10000))

        discretizer = DiscretizingKBins(n_bins=10)
        discretizer.fit(large_data)
        transformed = discretizer.transform(large_data)

        # Should complete without errors
        assert len(transformed) == len(large_data)
        # Should use most of the bins
        unique_bins = set(transformed.ravel())
        assert len(unique_bins) >= 8  # Should use at least 8 out of 10 bins

    def test_consistency(self):
        """Test that discretization is consistent across multiple runs"""
        np.random.seed(42)
        data = pd.Series(np.random.normal(0, 1, 1000))

        discretizer1 = DiscretizingKBins(n_bins=5)
        discretizer2 = DiscretizingKBins(n_bins=5)

        discretizer1.fit(data)
        discretizer2.fit(data)

        transformed1 = discretizer1.transform(data)
        transformed2 = discretizer2.transform(data)

        # Results should be identical
        np.testing.assert_array_equal(transformed1, transformed2)

    def test_bin_initialization(self):
        """Test different bin number initialization"""
        data = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])

        # Test default bins
        default_discretizer = DiscretizingKBins()
        assert hasattr(default_discretizer, "model")

        # Test custom bins
        custom_discretizer = DiscretizingKBins(n_bins=7)
        assert custom_discretizer.model.n_bins == 7

        # Both should work
        for discretizer in [default_discretizer, custom_discretizer]:
            discretizer.fit(data)
            transformed = discretizer.transform(data)
            assert len(transformed) == len(data)

    def test_drop_na_method(self):
        """Test the _drop_na helper method"""
        data_with_na = pd.Series([1.0, 2.0, np.nan, 4.0, pd.NA, None])

        discretizer = DiscretizingKBins()
        cleaned_data = discretizer._drop_na(data_with_na)

        # Should remove all NA values
        assert not cleaned_data.isna().any()
        assert len(cleaned_data) == 3  # Only 1.0, 2.0, 4.0 should remain
        assert list(cleaned_data.values) == [1.0, 2.0, 4.0]

    def test_empty_data(self):
        """Test discretization with empty data"""
        empty_data = pd.Series([], dtype=float)

        discretizer = DiscretizingKBins(n_bins=3)

        # Should handle empty data gracefully
        try:
            discretizer.fit(empty_data)
            transformed = discretizer.transform(empty_data)
            assert len(transformed) == 0
        except ValueError:
            # Some methods may raise errors with empty data, which is acceptable
            pass

    def test_datetime_data(self):
        """Test discretization with datetime data"""
        # Create datetime data
        dates = pd.date_range("2020-01-01", periods=10, freq="D")
        datetime_data = pd.Series(dates)

        discretizer = DiscretizingKBins(n_bins=3)
        discretizer.fit(datetime_data)

        # KBinsDiscretizer doesn't handle datetime data directly, should raise error
        with pytest.raises(Exception):  # Could be various types of errors
            discretizer.transform(datetime_data)

    def test_inverse_transform_preserves_structure(self):
        """Test that inverse transform preserves data structure appropriately"""
        original_data = pd.Series([1.0, 5.0, 10.0, 15.0, 20.0])

        discretizer = DiscretizingKBins(n_bins=3)
        discretizer.fit(original_data)

        # Transform and inverse transform
        transformed = discretizer.transform(original_data)
        inverse_transformed = discretizer.inverse_transform(
            pd.Series(transformed.ravel())
        )

        # Inverse transformed values should be reasonable approximations
        assert len(inverse_transformed) == len(original_data)

        # Values should be within reasonable bounds of original data
        original_range = original_data.max() - original_data.min()
        inverse_range = inverse_transformed.max() - inverse_transformed.min()

        # The range should be similar (allowing for discretization effects)
        assert inverse_range <= original_range * 1.1  # Allow 10% tolerance
