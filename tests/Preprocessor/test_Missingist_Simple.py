import pandas as pd
import pytest
from PETsARD.Preprocessor.Missingist_Simple import Missingist_Simple

class TestMissingistSimple:
    def test_simple_no_missing_values(self):
        # Prepare test data
        df_data = pd.DataFrame({'A': [1.0, 2.0, 3.0]})
        df_data_setting = {'missing_method': 'simple' , 'missing_columns_action': 'A'}
        
        # Create an instance of the class
        obj = Missingist_Simple(df_data['A'], **df_data_setting)
        
        # Call the method to be tested
        result = obj.handle()
        
        # Assert the result
        assert result.shape == (3,)
    
    def test_simple_with_missing_values(self):
        # Prepare test data
        df_data = pd.DataFrame({'A': [1.0, None, 3.0]})
        df_data_setting = {'missing_method': 3, 'missing_columns_action': 'A'}
        df_expected = pd.Series(data=[1.0, 3.0, 3.0], name='A')

        # Create an instance of the class
        obj = Missingist_Simple(df_data['A'], **df_data_setting)
        
        # Call the method to be tested
        result = obj.handle()
        
        # Assert the result
        assert result.shape == (3,)
        assert result.equals(df_expected)