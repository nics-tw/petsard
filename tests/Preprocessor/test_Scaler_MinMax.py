import pandas as pd
import pytest
from PETs_Experiment.Preprocessor.Scaler_MinMax import Scaler_MinMax
from sklearn.preprocessing import MinMaxScaler

class TestScalerMinMax:
    # Test case for handle method
    def test_handle(self):
        # Create a sample dataframe
        df_data = pd.DataFrame({'col1': [1.0, 2.0, 3.0], 'col2': [4.0, 5.0, 6.0]})
        df_data_setting = {'scaling_method': 'minmax' ,'scaling_columns': ['col1', 'col2'], 'scaling_columns_action': ['col1', 'col2']}
        df_expected = pd.DataFrame({'col1': [0.0, 0.5, 1.0], 'col2': [0.0, 0.5, 1.0]})
        
        # Create an instance of Scaler_MinMax
        scaler = Scaler_MinMax(df_data, **df_data_setting)
        
        # Call the handle method
        result = scaler.handle()
        
        # Assert that the returned result is a tuple containing dataframe and dictionary
        assert isinstance(result, tuple)
        assert isinstance(result[0], pd.DataFrame)
        assert isinstance(result[1], dict)
        
        # Assert that the dataframe is correct
        assert df_expected.equals(result[0])
        
        # Assert that the dictionary contains the scaler object
        assert 'col1' in result[1]
        assert 'col2' in result[1]
        assert isinstance(result[1]['col1'], MinMaxScaler)
        assert isinstance(result[1]['col2'], MinMaxScaler)