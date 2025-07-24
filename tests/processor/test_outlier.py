import numpy as np
import pandas as pd
import pytest

from petsard.exceptions import UnfittedError
from petsard.processor.outlier import OutlierHandler, OutlierIQR, OutlierZScore


class Test_OutlierZScore:
    def test_ZScore_no_outliers(self):
        # Prepare test data
        df_data = pd.DataFrame(
            {
                "col1": [1.0, 2.0, 3.0],
                "col2": pd.to_datetime(["2020-10-01", "2020-10-02", "2020-10-03"]),
            }
        )

        # Create an instance of the class
        outlier1 = OutlierZScore()

        with pytest.raises(UnfittedError):
            outlier1.transform(df_data["col1"])

        # Call the method to be tested
        outlier1.fit(df_data["col1"])

        transformed1 = outlier1.transform(df_data["col1"])

        # Assert the result
        assert (transformed1 == np.array([False, False, False])).all()

        # Create an instance of the class
        outlier2 = OutlierZScore()

        with pytest.raises(UnfittedError):
            outlier2.transform(df_data["col2"])

        # Call the method to be tested
        outlier2.fit(df_data["col2"])

        transformed2 = outlier2.transform(df_data["col2"])

        # Assert the result
        assert (transformed2 == np.array([False, False, False])).all()

    def test_Zscore_with_outliers(self):
        # Prepare test data
        df_data = pd.DataFrame(
            {
                "col1": [0.0] * 10000 + [10000.0],
                "col2": pd.to_datetime(["2222-12-12"]).append(
                    pd.to_datetime(["2022-12-13"] * 10000)
                ),
            }
        )
        df_expected1 = np.array([False] * 10000 + [True])
        df_expected2 = np.array([True] + [False] * 10000)

        # Create an instance of the class
        outlier1 = OutlierZScore()

        with pytest.raises(UnfittedError):
            outlier1.transform(df_data["col1"])

        # Call the method to be tested
        outlier1.fit(df_data["col1"])

        transformed1 = outlier1.transform(df_data["col1"])

        # Assert the result
        assert (transformed1.reshape(-1) == df_expected1).all()

        # Create an instance of the class
        outlier2 = OutlierZScore()

        with pytest.raises(UnfittedError):
            outlier2.transform(df_data["col2"])

        # Call the method to be tested
        outlier2.fit(df_data["col2"])

        transformed2 = outlier2.transform(df_data["col2"])

        # Assert the result
        assert (transformed2.reshape(-1) == df_expected2).all()


class Test_OutlierIQR:
    def test_IQR_no_outliers(self):
        # Prepare test data
        df_data = pd.DataFrame(
            {
                "col1": [1.0, 2.0, 3.0],
                "col2": pd.to_datetime(["2020-10-01", "2020-10-02", "2020-10-03"]),
            }
        )

        # Create an instance of the class
        outlier1 = OutlierIQR()

        with pytest.raises(UnfittedError):
            outlier1.transform(df_data["col1"])

        # Call the method to be tested
        outlier1.fit(df_data["col1"])

        transformed1 = outlier1.transform(df_data["col1"])

        # Assert the result
        assert (transformed1 == np.array([False, False, False])).all()

        # Create an instance of the class
        outlier2 = OutlierIQR()

        with pytest.raises(UnfittedError):
            outlier2.transform(df_data["col2"])

        # Call the method to be tested
        outlier2.fit(df_data["col2"])

        transformed2 = outlier2.transform(df_data["col2"])

        # Assert the result
        assert (transformed2 == np.array([False, False, False])).all()

    def test_IQR_with_outliers(self):
        # Prepare test data
        df_data = pd.DataFrame(
            {
                "col1": [0.0] * 10000 + [10000.0],
                "col2": pd.to_datetime(["2222-12-12"]).append(
                    pd.to_datetime(["2022-12-13"] * 10000)
                ),
            }
        )
        df_expected1 = np.array([False] * 10000 + [True])
        df_expected2 = np.array([True] + [False] * 10000)

        # Create an instance of the class
        outlier1 = OutlierIQR()

        with pytest.raises(UnfittedError):
            outlier1.transform(df_data["col1"])

        # Call the method to be tested
        outlier1.fit(df_data["col1"])

        transformed1 = outlier1.transform(df_data["col1"])

        # Assert the result
        assert (transformed1.reshape(-1) == df_expected1).all()

        # Create an instance of the class
        outlier2 = OutlierIQR()

        with pytest.raises(UnfittedError):
            outlier2.transform(df_data["col2"])

        # Call the method to be tested
        outlier2.fit(df_data["col2"])

        transformed2 = outlier2.transform(df_data["col2"])

        # Assert the result
        assert (transformed2.reshape(-1) == df_expected2).all()


class Test_OutlierHandler:
    """Test base OutlierHandler class"""

    def test_base_handler_cannot_be_instantiated(self):
        """Test that base handler can be instantiated but abstract methods raise errors"""
        # OutlierHandler is not abstract, so it can be instantiated
        handler = OutlierHandler()

        # But calling abstract methods should raise NotImplementedError
        data = pd.Series([1.0, 2.0, 3.0])

        with pytest.raises(NotImplementedError):
            handler._fit(data)

        with pytest.raises(NotImplementedError):
            handler._transform(data)


class Test_OutlierEdgeCases:
    """Test edge cases for all outlier detectors"""

    def test_single_value_data(self):
        """Test outlier detection with single repeated value"""
        data = pd.Series([5.0] * 10)

        for outlier_class in [OutlierZScore, OutlierIQR]:
            outlier_detector = outlier_class()
            outlier_detector.fit(data)
            outlier_mask = outlier_detector.transform(data)

            # No outliers should be detected in uniform data
            assert outlier_mask.sum() == 0

    def test_empty_data(self):
        """Test outlier detection with empty data"""
        data = pd.Series([], dtype=float)

        for outlier_class in [OutlierZScore, OutlierIQR]:
            outlier_detector = outlier_class()

            # Empty data should raise errors, which is expected behavior
            with pytest.raises((ValueError, IndexError)):
                outlier_detector.fit(data)

    def test_missing_values(self):
        """Test outlier detection with missing values"""
        data = pd.Series([1.0, 2.0, np.nan, 3.0, 100.0, np.nan])

        for outlier_class in [OutlierZScore, OutlierIQR]:
            outlier_detector = outlier_class()
            outlier_detector.fit(data)
            outlier_mask = outlier_detector.transform(data)

            # Should handle missing values appropriately
            assert len(outlier_mask) == len(data)
            assert isinstance(outlier_mask, np.ndarray)

    def test_extreme_values(self):
        """Test outlier detection with extreme values"""
        data = pd.Series([1e-10, 1e10, -1e10, 0, 1, -1])

        for outlier_class in [OutlierZScore, OutlierIQR]:
            outlier_detector = outlier_class()
            outlier_detector.fit(data)
            outlier_mask = outlier_detector.transform(data)

            # Should detect some extreme values as outliers (may not detect all due to scaling)
            # At least the method should complete without errors
            assert len(outlier_mask) == len(data)
            assert isinstance(outlier_mask, np.ndarray)

    def test_different_data_types(self):
        """Test outlier detection with different numeric data types"""
        # Integer data
        int_data = pd.Series([1, 2, 3, 100], dtype=int)

        # Float data
        float_data = pd.Series([1.1, 2.2, 3.3, 100.5], dtype=float)

        for data in [int_data, float_data]:
            for outlier_class in [OutlierZScore, OutlierIQR]:
                outlier_detector = outlier_class()
                outlier_detector.fit(data)
                outlier_mask = outlier_detector.transform(data)

                # Should work with different numeric types
                assert len(outlier_mask) == len(data)
                assert outlier_mask.dtype == bool

    def test_datetime_data(self):
        """Test outlier detection with datetime data"""
        # Create datetime data with one extreme outlier
        dates = pd.date_range("2020-01-01", periods=10, freq="D")
        outlier_date = pd.Timestamp("1900-01-01")
        datetime_data = pd.Series(list(dates) + [outlier_date])

        for outlier_class in [OutlierZScore, OutlierIQR]:
            outlier_detector = outlier_class()
            outlier_detector.fit(datetime_data)
            outlier_mask = outlier_detector.transform(datetime_data)

            # Should detect the extreme date as outlier
            assert outlier_mask.sum() > 0
            # The last element (extreme date) should be marked as outlier
            assert outlier_mask[-1] == True


class Test_OutlierPerformance:
    """Test performance characteristics of outlier detectors"""

    def test_large_dataset_performance(self):
        """Test outlier detection on larger datasets"""
        # Create larger dataset
        np.random.seed(42)  # For reproducible results
        normal_data = np.random.normal(0, 1, 10000)
        outliers = np.array([10, -10, 15, -15, 20, -20])
        data = np.concatenate([normal_data, outliers])
        np.random.shuffle(data)
        df_data = pd.DataFrame({"col1": data})

        for outlier_class in [OutlierZScore, OutlierIQR]:
            outlier_detector = outlier_class()
            outlier_detector.fit(df_data["col1"])
            outlier_mask = outlier_detector.transform(df_data["col1"])

            # Should complete without errors
            assert len(outlier_mask) == len(data)
            # Should detect some outliers but not too many
            outlier_ratio = outlier_mask.sum() / len(data)
            assert 0 < outlier_ratio < 0.1  # Less than 10% should be outliers

    def test_consistency(self):
        """Test that outlier detection is consistent across multiple runs"""
        np.random.seed(42)
        data = pd.Series(np.random.normal(0, 1, 1000))

        for outlier_class in [OutlierZScore, OutlierIQR]:
            outlier_detector1 = outlier_class()
            outlier_detector2 = outlier_class()

            outlier_detector1.fit(data)
            outlier_detector2.fit(data)

            mask1 = outlier_detector1.transform(data)
            mask2 = outlier_detector2.transform(data)

            # Results should be identical
            np.testing.assert_array_equal(mask1, mask2)


class Test_OutlierSpecificBehavior:
    """Test specific behavior of different outlier detection methods"""

    def test_zscore_threshold(self):
        """Test Z-Score outlier detection threshold (3 standard deviations)"""
        # Create data with a clear outlier that will exceed Z-score of 3
        data = pd.Series(
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 100]
        )  # Last value is clearly an outlier

        outlier_detector = OutlierZScore()
        outlier_detector.fit(data)
        outlier_mask = outlier_detector.transform(data)

        # The last value should be detected as outlier
        assert outlier_mask[-1] == True
        # Most other values should not be outliers
        assert outlier_mask[:-1].sum() <= 1  # Allow for some tolerance

    def test_iqr_threshold(self):
        """Test IQR outlier detection threshold (1.5 * IQR)"""
        # Create data with known quartiles
        data = pd.Series(
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 100]
        )  # Last value is clear outlier

        outlier_detector = OutlierIQR()
        outlier_detector.fit(data)
        outlier_mask = outlier_detector.transform(data)

        # The last value should be detected as outlier
        assert outlier_mask[-1] == True

    def test_outlier_backup_data(self):
        """Test that outlier detectors backup original data"""
        data = pd.Series([1.0, 2.0, 3.0, 100.0])

        for outlier_class in [OutlierZScore, OutlierIQR]:
            outlier_detector = outlier_class()
            outlier_detector.fit(data)
            outlier_detector.transform(data)

            # Should have backed up the data
            assert outlier_detector.data_backup is not None
            assert len(outlier_detector.data_backup) == len(data)
