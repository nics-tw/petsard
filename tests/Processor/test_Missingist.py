import numpy as np
import pandas as pd
import pytest
from PETsARD.Processor.Missingist import Missingist_Mean, Missingist_Median, Missingist_Simple, Missingist_Drop
from PETsARD.Error import UnfittedError

class Test_Missingist_Mean:
    def test_mean_no_missing_values(self):
        # Prepare test data
        df_data = pd.DataFrame({'col1': [1.0, 2.0, 3.0]})
        
        # Create an instance of the class
        missingist = Missingist_Mean(na_percentage = 0.8)

        with pytest.raises(UnfittedError):
            missingist.transform(df_data['col1'])
        
        # Call the method to be tested
        missingist.fit(df_data['col1'])

        transformed = missingist.transform(df_data['col1'])

        rtransform = missingist.inverse_transform(df_data['col1'])
        
        # Assert the result
        assert (transformed.values == np.array([1.0, 2.0, 3.0])).all()

        # Assert the result
        assert transformed.shape == (3,)
        assert rtransform.isna().any().any()
    
    def test_mean_with_missing_values(self):
        # Prepare test data
        df_data = pd.DataFrame({'col1': [1.0, None, 3.0]})
        df_expected = pd.Series(data=[1.0, 2.0, 3.0], name='col1')
        
        # Create an instance of the class
        missingist = Missingist_Mean(na_percentage = 0.8)

        with pytest.raises(UnfittedError):
            missingist.transform(df_data['col1'])
        
        # Call the method to be tested
        missingist.fit(df_data['col1'])

        transformed = missingist.transform(df_data['col1'])

        rtransform = missingist.inverse_transform(df_data['col1'])
        
        # Assert the result
        assert (transformed.values == np.array([1.0, 2.0, 3.0])).all()

        # Assert the result
        assert transformed.shape == (3,)
        assert transformed.equals(df_expected)
        assert rtransform.isna().any().any()

class Test_Missingist_Median:
    def test_median_no_missing_values(self):
        # Prepare test data
        df_data = pd.DataFrame({'col1': [1.0, 2.0, 3.0]})
        
        # Create an instance of the class
        missingist = Missingist_Median(na_percentage = 0.8)

        with pytest.raises(UnfittedError):
            missingist.transform(df_data['col1'])
        
        # Call the method to be tested
        missingist.fit(df_data['col1'])

        transformed = missingist.transform(df_data['col1'])

        rtransform = missingist.inverse_transform(df_data['col1'])
        
        # Assert the result
        assert (transformed.values == np.array([1.0, 2.0, 3.0])).all()

        # Assert the result
        assert transformed.shape == (3,)
        assert rtransform.isna().any().any()
    
    def test_median_with_missing_values(self):
        # Prepare test data
        df_data = pd.DataFrame({'col1': [1.0, None, 3.0]})
        df_expected = pd.Series(data=[1.0, 2.0, 3.0], name='col1')
        
        # Create an instance of the class
        missingist = Missingist_Median(na_percentage = 0.8)

        with pytest.raises(UnfittedError):
            missingist.transform(df_data['col1'])
        
        # Call the method to be tested
        missingist.fit(df_data['col1'])

        transformed = missingist.transform(df_data['col1'])

        rtransform = missingist.inverse_transform(df_data['col1'])
        
        # Assert the result
        assert (transformed.values == np.array([1.0, 2.0, 3.0])).all()

        # Assert the result
        assert transformed.shape == (3,)
        assert transformed.equals(df_expected)
        assert rtransform.isna().any().any()

class Test_Missingist_Simple:
    def test_simple_no_missing_values(self):
        # Prepare test data
        df_data = pd.DataFrame({'col1': [1.0, 2.0, 3.0]})
        
        # Create an instance of the class
        missingist = Missingist_Simple(na_percentage = 0.8, value=1.0)

        with pytest.raises(UnfittedError):
            missingist.transform(df_data['col1'])
        
        # Call the method to be tested
        missingist.fit(df_data['col1'])

        transformed = missingist.transform(df_data['col1'])

        rtransform = missingist.inverse_transform(df_data['col1'])
        
        # Assert the result
        assert (transformed.values == np.array([1.0, 2.0, 3.0])).all()

        # Assert the result
        assert transformed.shape == (3,)
        assert rtransform.isna().any().any()
    
    def test_simple_with_missing_values(self):
        # Prepare test data
        df_data = pd.DataFrame({'col1': [1.0, None, 3.0]})
        df_expected = pd.Series(data=[1.0, 2.0, 3.0], name='col1')
        
        # Create an instance of the class
        missingist = Missingist_Simple(na_percentage = 0.8, value=2.0)

        with pytest.raises(UnfittedError):
            missingist.transform(df_data['col1'])
        
        # Call the method to be tested
        missingist.fit(df_data['col1'])

        transformed = missingist.transform(df_data['col1'])

        rtransform = missingist.inverse_transform(df_data['col1'])
        
        # Assert the result
        assert (transformed.values == np.array([1.0, 2.0, 3.0])).all()

        # Assert the result
        assert transformed.shape == (3,)
        assert transformed.equals(df_expected)
        assert rtransform.isna().any().any()

class Test_Missingist_Drop:
    def test_drop_no_missing_values(self):
        # Prepare test data
        df_data = pd.DataFrame({'col1': [1.0, 2.0, 3.0]})
        
        # Create an instance of the class
        missingist = Missingist_Drop(na_percentage = 0.8)

        with pytest.raises(UnfittedError):
            missingist.transform(df_data['col1'])
        
        # Call the method to be tested
        missingist.fit(df_data['col1'])

        transformed = missingist.transform(df_data['col1'])

        rtransform = missingist.inverse_transform(df_data['col1'])
        
        # Assert the result
        assert (transformed == np.array([False, False, False])).all()

        # Assert the result
        assert transformed.shape == (3,)
        assert rtransform.isna().any().any()
    
    def test_drop_with_missing_values(self):
        # Prepare test data
        df_data = pd.DataFrame({'col1': [1.0, None, 3.0]})
        
        # Create an instance of the class
        missingist = Missingist_Drop(na_percentage = 0.8)

        with pytest.raises(UnfittedError):
            missingist.transform(df_data['col1'])
        
        # Call the method to be tested
        missingist.fit(df_data['col1'])

        transformed = missingist.transform(df_data['col1'])

        rtransform = missingist.inverse_transform(df_data['col1'])
        
        # Assert the result
        assert (transformed == np.array([False, True, False])).all()

        # Assert the result
        assert transformed.shape == (3,)
        assert rtransform.isna().any().any()