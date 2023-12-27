import pytest
from PETs_Experiment.Preprocessor.ScalerFactory import ScalerFactory
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler

class TestScalerFactory:
    def test_standard_scaling(self):
        # Prepare test data
        df_data = pd.DataFrame({'A': [1.0, 2.0, 3.0], 'B': [4.0, 5.0, 6.0]})
        kwargs = {'scaling_method': 'standard', 'scaling_columns_action': ['A', 'B']}
        df_expected = pd.DataFrame(StandardScaler().fit_transform(df_data), columns=['A', 'B'])

        # Create an instance of the class
        scaler_factory = ScalerFactory(df_data, **kwargs)

        # Call the method to be tested
        result = scaler_factory.handle()

        # Assert the result
        assert isinstance(result, tuple)
        assert isinstance(result[0], pd.DataFrame)
        assert isinstance(result[1], dict)
        assert result[0].equals(df_expected)
        assert isinstance(result[1]['A'], StandardScaler)
        assert isinstance(result[1]['B'], StandardScaler)

    def test_minmax_scaling(self):
        # Prepare test data
        df_data = pd.DataFrame({'A': [1.0, 2.0, 3.0], 'B': [4.0, 5.0, 6.0]})
        kwargs = {'scaling_method': 'minmax', 'scaling_columns_action': ['A', 'B']}
        df_expected = pd.DataFrame({'A': [0.0, 0.5, 1.0], 'B': [0.0, 0.5, 1.0]})

        # Create an instance of the class
        scaler_factory = ScalerFactory(df_data, **kwargs)

        # Call the method to be tested
        result = scaler_factory.handle()

        # Assert the result
        assert isinstance(result, tuple)
        assert isinstance(result[0], pd.DataFrame)
        assert isinstance(result[1], dict)
        assert result[0].equals(df_expected)
        assert isinstance(result[1]['A'], MinMaxScaler)
        assert isinstance(result[1]['B'], MinMaxScaler)

    def test_zerocenter_scaling(self):
        # Prepare test data
        df_data = pd.DataFrame({'A': [1.0, 2.0, 3.0], 'B': [4.0, 5.0, 6.0]})
        kwargs = {'scaling_method': 'zerocenter', 'scaling_columns_action': ['A', 'B']}
        df_expected = pd.DataFrame({'A': [-1.0, 0.0, 1.0], 'B': [-1.0, 0.0, 1.0]})

        # Create an instance of the class
        scaler_factory = ScalerFactory(df_data, **kwargs)

        # Call the method to be tested
        result = scaler_factory.handle()

        # Assert the result
        assert isinstance(result, tuple)
        assert isinstance(result[0], pd.DataFrame)
        assert isinstance(result[1], dict)
        assert result[0].equals(df_expected)
        assert isinstance(result[1]['A'], StandardScaler)
        assert isinstance(result[1]['B'], StandardScaler)

    def test_invalid_scaling_method(self):
        # Prepare test data
        df_data = pd.DataFrame({'A': [1.0, 2.0, 3.0], 'B': [4.0, 5.0, 6.0]})
        kwargs = {'scaling_method': 'invalid', 'scaling_columns_action': ['A', 'B']}

        # Assert that a ValueError is raised when creating an instance of the class
        with pytest.raises(ValueError):
            ScalerFactory(df_data, **kwargs)