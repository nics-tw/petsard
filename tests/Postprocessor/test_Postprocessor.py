import pytest
from PETsARD.Postprocessor import Postprocessor
from PETsARD.Preprocessor.Preprocessor import Preprocessor
from sklearn.preprocessing import StandardScaler, LabelEncoder
import pandas as pd
import numpy as np

"""
BUG - For Scaler, it changes the original data!!!!!
"""

class TestPostprocessor:
    def test_decoding_ScalerFactory_ZeroCenter(self):

        ######## First part from test_Scaler_*.py ##############

        # Create a sample dataframe
        df_data = pd.DataFrame({'col1': [1.0, 2.0, 3.0], 'col2': [4.0, 5.0, 6.0]})
        df_expected = pd.DataFrame({'col1': [-1.0, 0.0, 1.0], 'col2': [-1.0, 0.0, 1.0]})
        
        # Create an instance of Preprocessor
        preproc = Preprocessor(df_data, missing=False, outlier=False, encoding=False, scaling=True, scaling_method='zerocenter')
        
        # Assert that the dataframe is correct
        assert df_expected.equals(preproc.data)

        ######## Test Postprocessor ##############

        postprocessor = Postprocessor(preproc.data, encoder=getattr(preproc, 'encoder', None), scaler=getattr(preproc, 'scaler', None), missingist=getattr(preproc, 'missingist', None))

        # Reset df_data
        df_data = pd.DataFrame({'col1': [1.0, 2.0, 3.0], 'col2': [4.0, 5.0, 6.0]})

        assert df_data.equals(postprocessor.data)

    def test_decoding_ScalerFactory_MinMax(self):

        ######## First part from test_Scaler_*.py ##############

        # Create a sample dataframe
        df_data = pd.DataFrame({'col1': [1.0, 2.0, 3.0], 'col2': [4.0, 5.0, 6.0]})
        df_expected = pd.DataFrame({'col1': [0.0, 0.5, 1.0], 'col2': [0.0, 0.5, 1.0]})
        
        # Create an instance of Preprocessor
        preproc = Preprocessor(df_data, missing=False, outlier=False, encoding=False, scaling=True, scaling_method='minmax')
        
        # Assert that the dataframe is correct
        assert df_expected.equals(preproc.data)

        ######## Test Postprocessor ##############

        postprocessor = Postprocessor(preproc.data, encoder=getattr(preproc, 'encoder', None), scaler=getattr(preproc, 'scaler', None), missingist=getattr(preproc, 'missingist', None))

        # Reset df_data
        df_data = pd.DataFrame({'col1': [1.0, 2.0, 3.0], 'col2': [4.0, 5.0, 6.0]})

        assert df_data.equals(postprocessor.data)

    def test_decoding_ScalerFactory_Standard(self):

        ######## First part from test_Scaler_*.py ##############

        # Create a sample dataframe
        df_data = pd.DataFrame({'col1': [1.0, 2.0, 3.0], 'col2': [4.0, 5.0, 6.0]})
        df_expected = pd.DataFrame(StandardScaler().fit_transform(df_data), columns=['col1', 'col2'])
        
        # Create an instance of Preprocessor
        preproc = Preprocessor(df_data, missing=False, outlier=False, encoding=False, scaling=True, scaling_method='standard')
        
        # Assert that the dataframe is correct
        assert df_expected.equals(preproc.data)

        ######## Test Postprocessor ##############

        postprocessor = Postprocessor(preproc.data, encoder=getattr(preproc, 'encoder', None), scaler=getattr(preproc, 'scaler', None), missingist=getattr(preproc, 'missingist', None))

        # Reset df_data
        df_data = pd.DataFrame({'col1': [1.0, 2.0, 3.0], 'col2': [4.0, 5.0, 6.0]})

        assert df_data.equals(postprocessor.data)

    def test_decoding_MissingistFactory_Mean(self):

        ######## First part from test_Missingist_*.py ##############

        # Prepare test data
        df_data = pd.DataFrame({'A': [1.0, None, 3.0], 'B': [4.0, 6.0, None], 'C': [3.0, 5.0, 7.0]})
        df_expected = pd.DataFrame({'A': [1.0, 2.0, 3.0], 'B': [4.0, 6.0, 5.0], 'C': [3.0, 5.0, 7.0]})

        # Create an instance of Preprocessor
        preproc = Preprocessor(df_data, missing=True, missing_method='mean', outlier=False, encoding=False, scaling=False)

        # Assert the result
        assert df_expected.equals(preproc.data)

        ######## Test Postprocessor ##############

        postprocessor = Postprocessor(df_data, encoder=getattr(preproc, 'encoder', None), scaler=getattr(preproc, 'scaler', None), missingist=getattr(preproc, 'missingist', None))

        print(postprocessor.data)
        
        assert postprocessor.data.isna().any().any()

    def test_decoding_MissingistFactory_Median(self):

        ######## First part from test_Missingist_*.py ##############

        # Prepare test data
        df_data = pd.DataFrame({'A': [1.0, None, 3.0], 'B': [4.0, 6.0, None], 'C': [3.0, 5.0, 7.0]})
        df_expected = pd.DataFrame({'A': [1.0, 2.0, 3.0], 'B': [4.0, 6.0, 5.0], 'C': [3.0, 5.0, 7.0]})

        # Create an instance of Preprocessor
        preproc = Preprocessor(df_data, missing=True, missing_method='median', outlier=False, encoding=False, scaling=False)

        # Assert the result
        assert df_expected.equals(preproc.data)

        ######## Test Postprocessor ##############

        postprocessor = Postprocessor(df_data, encoder=getattr(preproc, 'encoder', None), scaler=getattr(preproc, 'scaler', None), missingist=getattr(preproc, 'missingist', None))

        print(postprocessor.data)
        
        assert postprocessor.data.isna().any().any()

    def test_decoding_MissingistFactory_Simple(self):

        ######## First part from test_Missingist_*.py ##############

        # Prepare test data
        df_data = pd.DataFrame({'A': [1.0, None, 3.0], 'B': [4.0, 6.0, None], 'C': [3.0, 5.0, 7.0]})
        df_expected = pd.DataFrame({'A': [1.0, 3.0, 3.0], 'B': [4.0, 6.0, 3.0], 'C': [3.0, 5.0, 7.0]})

        # Create an instance of Preprocessor
        preproc = Preprocessor(df_data, missing=True, missing_method=3, outlier=False, encoding=False, scaling=False)

        # Assert the result
        assert df_expected.equals(preproc.data)

        ######## Test Postprocessor ##############

        postprocessor = Postprocessor(df_expected, encoder=getattr(preproc, 'encoder', None), scaler=getattr(preproc, 'scaler', None), missingist=getattr(preproc, 'missingist', None))

        print(postprocessor.data)
        
        assert postprocessor.data.isna().any().any()

    def test_decoding_MissingistFactory_Drop(self):

        ######## First part from test_Missingist_*.py ##############

        # Prepare test data
        df_data = pd.DataFrame({'A': [1.0, None, 3.0], 'B': [4.0, 6.0, None], 'C': [3.0, 5.0, 7.0]})

        # Create an instance of Preprocessor
        preproc = Preprocessor(df_data, missing=True, missing_method='drop', outlier=False, encoding=False, scaling=False)

        # Assert the result
        assert preproc.data.shape[0] == 1

        df_expected = df_data.fillna(0)

        ######## Test Postprocessor ##############

        postprocessor = Postprocessor(df_expected, encoder=getattr(preproc, 'encoder', None), scaler=getattr(preproc, 'scaler', None), missingist=getattr(preproc, 'missingist', None))

        print(postprocessor.data)
        
        assert postprocessor.data.isna().any().any()

    def test_decoding_EncoderFactory_Label(self):

        ######## First part from test_Encoder_*.py ##############

        # Create a sample dataframe
        df_data1 = ['A'] * 7 + ['B'] * 3 + ['C'] * 5 + ['D'] * 5
        df_data2 = [0] * 20
        df_data = pd.DataFrame({'col1': pd.Categorical(df_data1), 'col2': df_data2})
        df_expected = pd.DataFrame({'col1': LabelEncoder().fit_transform(df_data1), 'col2': df_data2})
        
        # Create an instance of Preprocessor
        preproc = Preprocessor(df_data, missing=False, outlier=False, encoding=True, encoding_method='label', scaling=False)
        
        # Assert that the dataframe is correct
        assert df_expected.equals(preproc.data)

        ######## Test Postprocessor ##############

        postprocessor = Postprocessor(preproc.data, encoder=getattr(preproc, 'encoder', None), scaler=getattr(preproc, 'scaler', None), missingist=getattr(preproc, 'missingist', None))

        # Reset df_data
        df_data = pd.DataFrame({'col1': df_data1, 'col2': df_data2})

        assert df_data.equals(postprocessor.data)

    def test_decoding_EncoderFactory_Uniform(self):

        ######## First part from test_Encoder_*.py ##############

        # Create a sample dataframe
        df_data1 = ['A'] * 7 + ['B'] * 3 + ['C'] * 5 + ['D'] * 5
        df_data2 = [0] * 20
        df_data = pd.DataFrame({'col1': pd.Categorical(df_data1), 'col2': df_data2})
        
        # Create an instance of Preprocessor
        preproc = Preprocessor(df_data, missing=False, outlier=False, encoding=True, encoding_method='uniform', scaling=False)
        
        # Assert that the dataframe is correct
        assert preproc.data['col1'].dtype == np.float64

        ######## Test Postprocessor ##############

        postprocessor = Postprocessor(preproc.data, encoder=getattr(preproc, 'encoder', None), scaler=getattr(preproc, 'scaler', None), missingist=getattr(preproc, 'missingist', None))

        # Reset df_data
        df_data = pd.DataFrame({'col1': pd.Categorical(df_data1), 'col2': df_data2})

        print(postprocessor.data.dtypes)
        print(df_data.dtypes)

        assert df_data.equals(postprocessor.data)