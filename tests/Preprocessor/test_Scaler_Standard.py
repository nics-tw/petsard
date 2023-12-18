import pandas as pd
import pytest
from PETs_Experiment.Preprocessor.Scaler_Standard import Scaler_Standard
from sklearn.preprocessing import StandardScaler

# Test case for handle method
def test_handle():
    # Create a sample dataframe
    df_data = pd.DataFrame({'col1': [1, 2, 3], 'col2': [4, 5, 6]})
    df_data_setting = {'scaling_method': 'standard' ,'scaling_columns': ['col1', 'col2'], 'scaling_columns_action': ['col1', 'col2']}
    df_expected = pd.DataFrame(StandardScaler().fit_transform(df_data), columns=['col1', 'col2'])
    
    # Create an instance of Scaler_MinMax
    scaler = Scaler_Standard(df_data, **df_data_setting)
    
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
    assert isinstance(result[1]['col1'], StandardScaler)
    assert isinstance(result[1]['col2'], StandardScaler)