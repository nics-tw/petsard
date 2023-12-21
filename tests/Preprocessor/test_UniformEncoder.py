import pytest
from PETs_Experiment.Preprocessor.UniformEncoder import UniformEncoder
import pandas as pd
import numpy as np
from PETs_Experiment.Error import UnfittedError

class TestUniformEncoder:
    def test_UniformEncoder(self):
        # Prepare test data
        df_data1 = ['A'] * 7 + ['B'] * 3 + ['C'] * 5 + ['D'] * 5
        df_data2 = [0] * 20
        df_data = pd.DataFrame({'col1': pd.Categorical(df_data1), 'col2': df_data2})

        # Data for triggering error
        df_data1_error = ['A'] * 7 + ['B'] * 3 + ['E'] * 5 + ['D'] * 5
        df_data_error = pd.DataFrame({'col1': df_data1_error, 'col2': df_data2})

        # Create an instance of the class
        ue = UniformEncoder()

        with pytest.raises(UnfittedError):
            ue.transform(df_data)

        with pytest.raises(UnfittedError):
            ue.inverse_transform(df_data)

        # Call the method to be tested
        ue.fit(df_data['col1'])
        
        assert set(ue.labels) == set(['A', 'B', 'C', 'D']) # type: ignore
        assert len(ue.lower_values) == 4 # type: ignore
        assert len(ue.upper_values) == 4 # type: ignore
        assert ue.lower_values[2] == ue.upper_values[1] # type: ignore

        with pytest.raises(ValueError):
            ue.transform(df_data_error['col1'])

        transformed = ue.transform(df_data['col1'])

        print(transformed)

        assert type(transformed) == pd.Series
        assert transformed.dtypes == np.float64
        assert transformed.min() >= 0
        assert transformed.max() <= 1

        # Data for triggering error
        transformed_error = transformed.copy()
        transformed_error[0] = 2.9

        with pytest.raises(ValueError):
            ue.inverse_transform(transformed_error)

        rtransformed = ue.inverse_transform(transformed)

        assert list(rtransformed.values) == list(df_data['col1'].values)

    