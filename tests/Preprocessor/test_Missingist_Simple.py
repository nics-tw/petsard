import pandas as pd
import pytest
from PETs_Experiment.Preprocessor.Missingist_Simple import Missingist_Simple

class TestMissingistSimple:
    def test_simple_no_missing_values(self):
        # Prepare test data
        df_data = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        df_data_setting = {'missing_method': 3 ,'missing_columns': ['A', 'B'], 'missing_columns_action': ['A', 'B']}
        
        # Create an instance of the class
        obj = Missingist_Simple(df_data, **df_data_setting)
        
        # Call the method to be tested
        result = obj.handle()
        
        # Assert the result
        assert result.shape[0] == 3
        assert 'A' in result.columns
        assert 'B' in result.columns
    
    def test_simple_with_missing_values(self):
        # Prepare test data
        df_data = pd.DataFrame({'A': [1, None, 4], 'B': [4, 6, None], 'C': [3, 5, 7]})
        df_data_setting = {'missing_method': 3 ,'missing_columns': ['A', 'B', 'C'], 'missing_columns_action': ['A', 'B', 'C']}
        df_expected = pd.DataFrame({'A': [1.0, 3.0, 4.0], 'B': [4.0, 6.0, 3.0], 'C': [3, 5, 7]})
        
        # Create an instance of the class
        obj = Missingist_Simple(df_data, **df_data_setting)
        
        # Call the method to be tested
        result = obj.handle()
        
        # Assert the result
        assert result.shape[0] == 3
        assert result.equals(df_expected)
        assert 'A' in result.columns
        assert 'B' in result.columns