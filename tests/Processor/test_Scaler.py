import pytest
import pandas as pd
import numpy as np
from PETsARD.Processor.Scaler import Scaler_Standard, Scaler_ZeroCenter, Scaler_MinMax
from sklearn.preprocessing import StandardScaler
from PETsARD.Error import UnfittedError

class Test_Scaler_Standard:
    # Test case for handle method
    def test_Scaler_Standard(self):
        # Create a sample dataframe
        df_data = pd.DataFrame({'col1': [1.0, 2.0, 3.0], 'col2': [4.0, 5.0, 6.0]})
        df_expected = pd.DataFrame(StandardScaler().fit_transform(df_data), columns=['col1', 'col2'])
        
        # Create an instance of Scaler_MinMax
        scaler = Scaler_Standard()
        
        with pytest.raises(UnfittedError):
            scaler.transform(df_data['col1'])

        with pytest.raises(UnfittedError):
            scaler.inverse_transform(df_data['col1'])

        # Call the method to be tested
        scaler.fit(df_data['col1'])
        
        transformed = scaler.transform(df_data['col1'])
        
        # Assert that the dataframe is correct
        assert list(transformed) == list(df_expected['col1'].values)

class Test_Scaler_ZeroCenter:
    # Test case for handle method
    def test_Scaler_ZeroCenter(self):
        # Create a sample dataframe
        df_data = pd.DataFrame({'col1': [1.0, 2.0, 3.0], 'col2': [4.0, 5.0, 6.0]})
        df_expected = pd.DataFrame({'col1': [-1.0, 0.0, 1.0], 'col2': [-1.0, 0.0, 1.0]})
        
        # Create an instance of Scaler_MinMax
        scaler = Scaler_ZeroCenter()
        
        with pytest.raises(UnfittedError):
            scaler.transform(df_data['col1'])

        with pytest.raises(UnfittedError):
            scaler.inverse_transform(df_data['col1'])

        # Call the method to be tested
        scaler.fit(df_data['col1'])
        
        transformed = scaler.transform(df_data['col1'])
        
        # Assert that the dataframe is correct
        assert list(transformed) == list(df_expected['col1'].values)

class Test_Scaler_MinMax:
    # Test case for handle method
    def test_Scaler_MinMax(self):
        # Create a sample dataframe
        df_data = pd.DataFrame({'col1': [1.0, 2.0, 3.0], 'col2': [4.0, 5.0, 6.0]})
        df_expected = pd.DataFrame({'col1': [0.0, 0.5, 1.0], 'col2': [0.0, 0.5, 1.0]})
        
        # Create an instance of Scaler_MinMax
        scaler = Scaler_MinMax()
        
        with pytest.raises(UnfittedError):
            scaler.transform(df_data['col1'])

        with pytest.raises(UnfittedError):
            scaler.inverse_transform(df_data['col1'])

        # Call the method to be tested
        scaler.fit(df_data['col1'])
        
        transformed = scaler.transform(df_data['col1'])
        
        # Assert that the dataframe is correct
        assert list(transformed) == list(df_expected['col1'].values)