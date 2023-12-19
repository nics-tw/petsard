import pytest
from PETs_Experiment.Preprocessor import MissingistFactory
import pandas as pd

class TestMissingistFactory:
    def test_missing_method_drop(self):
        # Prepare test data
        df_data = pd.DataFrame({'A': [1, None, 3], 'B': [4, 6, None]})
        df_data_setting = {'missing_method': 'drop', 'missing_columns': ['A', 'B'], 'missing_columns_action': ['A', 'B']}

        # Create an instance of the class
        obj = MissingistFactory(df_data, **df_data_setting)

        # Call the method to be tested
        result = obj.handle()

        # Assert the result
        assert isinstance(result, tuple)
        assert isinstance(result[0], pd.DataFrame)
        assert isinstance(result[1], dict)
        assert result[0].shape[0] == 1
        assert 'A' in result[0].columns
        assert 'B' in result[0].columns

    def test_missing_method_mean(self):
        # Prepare test data
        df_data = pd.DataFrame({'A': [1, None, 3], 'B': [4, 6, None], 'C': [3, 5, 7]})
        df_data_setting = {'missing_method': 'mean' ,'missing_columns': ['A', 'B', 'C'], 'missing_columns_action': ['A', 'B', 'C']}
        df_expected = pd.DataFrame({'A': [1.0, 2.0, 3.0], 'B': [4.0, 6.0, 5.0], 'C': [3, 5, 7]})

        # Create an instance of the class
        obj = MissingistFactory(df_data, **df_data_setting)

        # Call the method to be tested
        result = obj.handle()

        # Assert the result
        assert isinstance(result, tuple)
        assert isinstance(result[0], pd.DataFrame)
        assert isinstance(result[1], dict)
        assert result[0].equals(df_expected)
        assert result[0].shape[0] == 3
        assert result[0].equals(df_expected)
        assert 'A' in result[0].columns
        assert 'B' in result[0].columns

    def test_missing_method_simple(self):
        # Prepare test data
        df_data = pd.DataFrame({'A': [1, None, 4], 'B': [4, 6, None], 'C': [3, 5, 7]})
        df_data_setting = {'missing_method': 3 ,'missing_columns': ['A', 'B', 'C'], 'missing_columns_action': ['A', 'B', 'C']}
        df_expected = pd.DataFrame({'A': [1.0, 3.0, 4.0], 'B': [4.0, 6.0, 3.0], 'C': [3, 5, 7]})
        
        # Create an instance of the class
        obj = MissingistFactory(df_data, **df_data_setting)
        
        # Call the method to be tested
        result = obj.handle()
        
        # Assert the result
        assert isinstance(result, tuple)
        assert isinstance(result[0], pd.DataFrame)
        assert isinstance(result[1], dict)
        assert result[0].equals(df_expected)
        assert result[0].shape[0] == 3
        assert result[0].equals(df_expected)
        assert 'A' in result[0].columns
        assert 'B' in result[0].columns

    def test_missing_method_not_supported(self):
        # Prepare test data
        df_data = pd.DataFrame({'A': [1, None, 3], 'B': [4, 6, None]})
        df_data_setting = {'missing_method': 'invalid', 'missing_columns': ['A', 'B'], 'missing_columns_action': ['A', 'B']}

        # Assert that a ValueError is raised when creating an instance of the class
        with pytest.raises(ValueError):
            MissingistFactory(df_data, **df_data_setting)