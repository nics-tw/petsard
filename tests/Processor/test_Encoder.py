import pytest
import pandas as pd
import numpy as np
from PETs_Experiment.Processor.Encoder import Encoder_Uniform, Encoder_Label
from PETs_Experiment.Error import UnfittedError

class Test_Encoder_Uniform:
    def test_Encoder_Uniform(self):
        # Prepare test data
        df_data1 = ['A'] * 7 + ['B'] * 3 + ['C'] * 5 + ['D'] * 5
        df_data2 = [0] * 20
        df_data = pd.DataFrame({'col1': pd.Categorical(df_data1), 'col2': df_data2})

        # Data for triggering error
        df_data1_error = ['A'] * 7 + ['B'] * 3 + ['E'] * 5 + ['D'] * 5
        df_data_error = pd.DataFrame({'col1': df_data1_error, 'col2': df_data2})

        # Create an instance of the class
        encoder = Encoder_Uniform()

        with pytest.raises(UnfittedError):
            encoder.transform(df_data)

        with pytest.raises(UnfittedError):
            encoder.inverse_transform(df_data)

        # Call the method to be tested
        encoder.fit(df_data['col1'])
        
        assert set(encoder.labels) == set(['A', 'B', 'C', 'D'])
        assert len(encoder.lower_values) == 4
        assert len(encoder.upper_values) == 4
        assert encoder.lower_values[2] == encoder.upper_values[1]

        with pytest.raises(ValueError):
            encoder.transform(df_data_error['col1'])

        transformed = encoder.transform(df_data['col1'])

        print(transformed)

        assert type(transformed) == np.ndarray
        assert transformed.dtype == np.float64
        assert transformed.min() >= 0
        assert transformed.max() <= 1

        # Data for triggering error
        transformed_error = transformed.copy()
        transformed_error[0] = 2.9

        with pytest.raises(ValueError):
            encoder.inverse_transform(transformed_error)

        rtransformed = encoder.inverse_transform(transformed)

        assert list(rtransformed) == list(df_data['col1'].values)

class Test_Encoder_Label:
    def test_Encoder_Label(self):
        # Prepare test data
        df_data1 = ['A'] * 7 + ['B'] * 3 + ['C'] * 5 + ['D'] * 5
        df_data2 = [0] * 20
        df_data = pd.DataFrame({'col1': pd.Categorical(df_data1), 'col2': df_data2})

        # Data for triggering error
        df_data1_error = ['A'] * 7 + ['B'] * 3 + ['E'] * 5 + ['D'] * 5
        df_data_error = pd.DataFrame({'col1': df_data1_error, 'col2': df_data2})

        # Create an instance of the class
        encoder = Encoder_Label()

        with pytest.raises(UnfittedError):
            encoder.transform(df_data)

        with pytest.raises(UnfittedError):
            encoder.inverse_transform(df_data)

        # Call the method to be tested
        encoder.fit(df_data['col1'])
        
        assert set(encoder.labels) == set(['A', 'B', 'C', 'D'])

        with pytest.raises(ValueError):
            encoder.transform(df_data_error['col1'])

        transformed = encoder.transform(df_data['col1'])

        print(transformed)

        assert type(transformed) == np.ndarray
        assert transformed.dtype == int

        rtransformed = encoder.inverse_transform(transformed)

        assert list(rtransformed) == list(df_data['col1'].values)

    