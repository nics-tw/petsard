import pandas as pd
import pytest
from PETs_Experiment.Preprocessor.Outlierist_IQR import Outlierist_IQR

class TestOutlieristIQR:
    def test_IQR_no_outliers(self):
        # Prepare test data
        df_data = pd.DataFrame({'A': [1.0, 2.0, 3.0], 'B': pd.to_datetime(['2020-10-01', '2020-10-02', '2020-10-03'])})
        df_data_setting = {'outlier_method': 'iqr' , 'outlier_columns': ['A', 'B'], 'outlier_columns_action': ['A', 'B']}
        df_expected = pd.DataFrame({'A': [1.0, 2.0, 3.0], 'B': pd.to_datetime(['2020-10-01', '2020-10-02', '2020-10-03'])})
        
        # Create an instance of the class
        obj = Outlierist_IQR(df_data, **df_data_setting)
        
        # Call the method to be tested
        result = obj.handle()
        
        # Assert the result
        assert type(result) == pd.DataFrame
        assert result.shape == (3, 2)
        assert result.equals(df_expected)

    def test_IQR_with_outliers(self):
        # Prepare test data
        df_data = pd.DataFrame({'A': [1.0, 2.0, 3.0, 10000.0, 3.0], 'B': pd.to_datetime(['2020-10-01', '2020-10-02', '2020-10-03', '2020-10-01', '2021-10-01'])})
        df_data_setting = {'outlier_method': 'iqr' , 'outlier_columns': ['A', 'B'], 'outlier_columns_action': ['A', 'B']}
        df_expected = pd.DataFrame({'A': [1.0, 2.0, 3.0], 'B': pd.to_datetime(['2020-10-01', '2020-10-02', '2020-10-03'])})
        
        # Create an instance of the class
        obj = Outlierist_IQR(df_data, **df_data_setting)
        
        # Call the method to be tested
        result = obj.handle()
        
        # Assert the result
        assert type(result) == pd.DataFrame
        assert result.shape == (3, 2)
        assert result.equals(df_expected)