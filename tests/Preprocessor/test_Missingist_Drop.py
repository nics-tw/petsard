import pandas as pd
import pytest
from PETs_Experiment.Preprocessor.Missingist_Drop import Missingist_Drop

class TestMissingistDrop:
    def test_drop_no_missing_values(self):
        # Prepare test data
        df_data = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        df_data_setting = {'missing_method': 'drop' ,'missing_columns': ['A', 'B'], 'missing_columns_action': ['A', 'B']}
        
        # Create an instance of the class
        obj = Missingist_Drop(df_data, **df_data_setting)
        
        # Call the method to be tested
        result = obj.handle()
        
        # Assert the result
        assert result.shape[0] == 3
        assert 'A' in result.columns
        assert 'B' in result.columns
    
    def test_drop_with_missing_values(self):
        # Prepare test data
        df_data = pd.DataFrame({'A': [1, None, 3], 'B': [4, 6, None]})
        df_data_setting = {'missing_method': 'drop' ,'missing_columns': ['A', 'B'], 'missing_columns_action': ['A', 'B']}
        
        # Create an instance of the class
        obj = Missingist_Drop(df_data, **df_data_setting)
        
        # Call the method to be tested
        result = obj.handle()
        
        # Assert the result
        assert result.shape[0] == 1
        assert 'A' in result.columns
        assert 'B' in result.columns