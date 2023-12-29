import pytest
from PETsARD.Preprocessor.OutlieristFactory import OutlieristFactory
import pandas as pd

class TestOutlieristFactory:
    def test_IQR_outlier(self):
        # Prepare test data
        df_data = pd.DataFrame({'A': [0.0] * 10000 + [10000.0], 'B': pd.to_datetime(['2222-12-12']).append(pd.to_datetime(['2022-12-13']*10000))})
        kwargs = {'outlier_method': 'iqr', 'outlier_columns_action': ['A', 'B']}
        df_expected = pd.DataFrame({'A': [0.0]*9999, 'B': pd.to_datetime(['2022-12-13']*9999)})

        # Create an instance of the class
        outlierist_factory = OutlieristFactory(df_data, **kwargs)

        # Call the method to be tested
        result = outlierist_factory.handle()

        # Assert the result
        assert result.equals(df_expected)

    def test_IsolationForest_outlier(self):
        # Prepare test data
        df_data = pd.DataFrame({'A': [0.0] * 10000 + [10000.0], 'B': pd.to_datetime(['2222-12-12']).append(pd.to_datetime(['2022-12-13']*10000))})
        kwargs = {'outlier_method': 'isof', 'outlier_columns_action': ['A', 'B']}
        df_expected = pd.DataFrame({'A': [0.0]*9999, 'B': pd.to_datetime(['2022-12-13']*9999)})

        # Create an instance of the class
        outlierist_factory = OutlieristFactory(df_data, **kwargs)

        # Call the method to be tested
        result = outlierist_factory.handle()

        # Assert the result
        assert result.equals(df_expected)

    def test_LOF_outlier(self):
        # Prepare test data
        df_data = pd.DataFrame({'A': [0.0] * 10000 + [10000.0], 'B': pd.to_datetime(['2222-12-12']).append(pd.to_datetime(['2022-12-13']*10000))})
        kwargs = {'outlier_method': 'lof', 'outlier_columns_action': ['A', 'B']}
        df_expected = pd.DataFrame({'A': [0.0]*9999, 'B': pd.to_datetime(['2022-12-13']*9999)})

        # Create an instance of the class
        outlierist_factory = OutlieristFactory(df_data, **kwargs)

        # Call the method to be tested
        result = outlierist_factory.handle()

        # Assert the result
        assert result.equals(df_expected)

    def test_Zscore_outlier(self):
        # Prepare test data
        df_data = pd.DataFrame({'A': [0.0] * 10000 + [10000.0], 'B': pd.to_datetime(['2222-12-12']).append(pd.to_datetime(['2022-12-13']*10000))})
        kwargs = {'outlier_method': 'zscore', 'outlier_columns_action': ['A', 'B']}
        df_expected = pd.DataFrame({'A': [0.0]*9999, 'B': pd.to_datetime(['2022-12-13']*9999)})

        # Create an instance of the class
        outlierist_factory = OutlieristFactory(df_data, **kwargs)

        # Call the method to be tested
        result = outlierist_factory.handle()

        # Assert the result
        assert result.equals(df_expected)

    def test_invalid_scaling_method(self):
        # Prepare test data
        df_data = pd.DataFrame({'A': [1.0, 2.0, 3.0], 'B': [4.0, 5.0, 6.0]})
        kwargs = {'outlier_method': 'test', 'outlier_columns_action': ['A', 'B']}

        # Assert that a ValueError is raised when creating an instance of the class
        with pytest.raises(ValueError):
            OutlieristFactory(df_data, **kwargs)