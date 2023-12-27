import pytest
from PETsARD.Preprocessor.EncoderFactory import EncoderFactory
from PETsARD.Preprocessor.UniformEncoder import UniformEncoder
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

class TestEncoderFactory:
    def test_label_encoder(self):
        # Prepare test data
        df_data1 = ['A'] * 7 + ['B'] * 3 + ['C'] * 5 + ['D'] * 5
        df_data2 = [0] * 20
        df_data = pd.DataFrame({'col1': pd.Categorical(df_data1), 'col2': df_data2})
        kwargs = {'encoding_method': 'label', 'encoding_columns_action': ['col1']}
        df_expected = pd.DataFrame({'col1': LabelEncoder().fit_transform(df_data1), 'col2': df_data2})

        # Create an instance of the class
        encoder_factory = EncoderFactory(df_data, **kwargs)

        # Call the method to be tested
        result = encoder_factory.handle()

        # Assert the result
        assert isinstance(result, tuple)
        assert isinstance(result[0], pd.DataFrame)
        assert isinstance(result[1], dict)
        assert isinstance(result[1]['col1'], LabelEncoder)
        assert result[0].equals(df_expected)

    def test_uniform_encoder(self):
        # Prepare test data
        df_data1 = ['A'] * 7 + ['B'] * 3 + ['C'] * 5 + ['D'] * 5
        df_data2 = [0] * 20
        df_data = pd.DataFrame({'col1': pd.Categorical(df_data1), 'col2': df_data2})
        kwargs = {'encoding_method': 'uniform', 'encoding_columns_action': ['col1']}

        # Create an instance of the class
        encoder_factory = EncoderFactory(df_data, **kwargs)

        # Call the method to be tested
        result = encoder_factory.handle()

        # Assert that the returned result is a tuple containing dataframe and dictionary
        assert isinstance(result, tuple)
        assert isinstance(result[0], pd.DataFrame)
        assert isinstance(result[1], dict)
        
        # Assert that the dictionary contains the encoder object
        assert 'col1' in result[1]
        assert 'col2' not in result[1]
        assert isinstance(result[1]['col1'], UniformEncoder)

        # Assert that the dataframe is correct
        assert result[0]['col1'].dtypes == np.float64
        

    