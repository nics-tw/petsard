import pandas as pd
import pytest
from PETsARD.Preprocessor.Encoder_Label import Encoder_Label
from sklearn.preprocessing import LabelEncoder

class TestEncoderLabel:
    # Test case for handle method
    def test_handle(self):
        # Create a sample dataframe
        df_data1 = ['A'] * 7 + ['B'] * 3 + ['C'] * 5 + ['D'] * 5
        df_data2 = [0] * 20
        df_data = pd.DataFrame({'col1': pd.Categorical(df_data1), 'col2': df_data2})
        df_data_setting = {'encoding_method': 'label' ,'encoding_columns': ['col1', 'col2'], 'encoding_columns_action': ['col1', 'col2']}
        df_expected = pd.DataFrame({'col1': LabelEncoder().fit_transform(df_data1), 'col2': df_data2})
        
        # Create an instance of Scaler_MinMax
        encoder = Encoder_Label(df_data, **df_data_setting)
        
        # Call the handle method
        result = encoder.handle()
        
        # Assert that the returned result is a tuple containing dataframe and dictionary
        assert isinstance(result, tuple)
        assert isinstance(result[0], pd.DataFrame)
        assert isinstance(result[1], dict)
        
        # Assert that the dataframe is correct
        assert df_expected.equals(result[0])
        
        # Assert that the dictionary contains the encoder object
        assert 'col1' in result[1]
        assert 'col2' not in result[1]
        assert isinstance(result[1]['col1'], LabelEncoder)