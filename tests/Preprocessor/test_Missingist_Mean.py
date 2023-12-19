import pandas as pd
import pytest
from PETs_Experiment.Preprocessor.Missingist_Mean import Missingist_Mean

class TestMissingistMean:
    def test_mean_no_missing_values(self):
        # Prepare test data
        df_data = pd.DataFrame({'A': [1, 2, 3]})
        df_data_setting = {'missing_method': 'mean' , 'missing_columns_action': 'A'}
        
        # Create an instance of the class
        obj = Missingist_Mean(df_data['A'], **df_data_setting)
        
        # Call the method to be tested
        result = obj.handle()
        
        # Assert the result
        assert result.shape == (3,)
    
    def test_mean_with_missing_values(self):
        # Prepare test data
        df_data = pd.DataFrame({'A': [1, None, 3]})
        df_data_setting = {'missing_method': 'mean', 'missing_columns_action': 'A'}
        df_expected = pd.Series(data=[1.0, 2.0, 3.0], name='A')
        
        # Create an instance of the class
        obj = Missingist_Mean(df_data['A'], **df_data_setting)
        
        # Call the method to be tested
        result = obj.handle()

        print(type(result))
        
        # Assert the result
        assert result.shape == (3,)
        assert result.equals(df_expected)