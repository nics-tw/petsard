import pandas as pd
import pytest
from PETs_Experiment.Preprocessor.Outlierist_Zscore import Outlierist_Zscore

class TestOutlierZscore:
    def test_Zscore_no_outliers(self):
        # Prepare test data
        df_data = pd.DataFrame({'A': [1.0, 2.0, 3.0], 'B': pd.to_datetime(['2020-10-01', '2020-10-02', '2020-10-03'])})
        df_data_setting = {'outlier_method': 'zscore' , 'outlier_columns': ['A', 'B'], 'outlier_columns_action': ['A', 'B']}
        df_expected = pd.DataFrame({'A': [1.0, 2.0, 3.0], 'B': pd.to_datetime(['2020-10-01', '2020-10-02', '2020-10-03'])})
        
        # Create an instance of the class
        obj = Outlierist_Zscore(df_data, **df_data_setting)
        
        # Call the method to be tested
        result = obj.handle()
        
        # Assert the result
        assert type(result) == pd.DataFrame
        assert result.shape == (3, 2)
        assert result.equals(df_expected)

    def test_Zscore_with_outliers(self):
        # Prepare test data
        df_data = pd.DataFrame({'A': [0.0] * 10000 + [10000.0], 'B': pd.to_datetime(['2222-12-12']).append(pd.to_datetime(['2022-12-13']*10000))})
        df_data_setting = {'outlier_method': 'zscore' , 'outlier_columns': ['A', 'B'], 'outlier_columns_action': ['A', 'B']}
        df_expected = pd.DataFrame({'A': [0.0]*9999, 'B': pd.to_datetime(['2022-12-13']*9999)})
        
        # Create an instance of the class
        obj = Outlierist_Zscore(df_data, **df_data_setting)
        
        # Call the method to be tested
        result = obj.handle()
        
        # Assert the result
        assert type(result) == pd.DataFrame
        assert result.equals(df_expected)