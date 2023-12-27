import numpy as np
import pandas as pd
import pytest
from PETs_Experiment.Processor.Outlierist import Outlierist_ZScore, Outlierist_IQR
from PETs_Experiment.Error import UnfittedError

class Test_Outlierist_ZScore:
    def test_ZScore_no_outliers(self):
        # Prepare test data
        df_data = pd.DataFrame({'col1': [1.0, 2.0, 3.0], 'col2': pd.to_datetime(['2020-10-01', '2020-10-02', '2020-10-03'])})
        
        # Create an instance of the class
        outlierist1 = Outlierist_ZScore()

        with pytest.raises(UnfittedError):
            outlierist1.transform(df_data['col1'])
        
        # Call the method to be tested
        outlierist1.fit(df_data['col1'])

        transformed1 = outlierist1.transform(df_data['col1'])
        
        # Assert the result
        assert (transformed1 == np.array([False, False, False])).all()

        # Create an instance of the class
        outlierist2 = Outlierist_ZScore()

        with pytest.raises(UnfittedError):
            outlierist2.transform(df_data['col2'])
        
        # Call the method to be tested
        outlierist2.fit(df_data['col2'])

        transformed2 = outlierist2.transform(df_data['col2'])
        
        # Assert the result
        assert (transformed2 == np.array([False, False, False])).all()

    def test_Zscore_with_outliers(self):
        # Prepare test data
        df_data = pd.DataFrame({'col1': [0.0] * 10000 + [10000.0], 'col2': pd.to_datetime(['2222-12-12']).append(pd.to_datetime(['2022-12-13']*10000))})
        df_expected1 = np.array([False] * 10000 + [True])
        df_expected2 = np.array([True] + [False] * 10000)
        
        # Create an instance of the class
        outlierist1 = Outlierist_ZScore()

        with pytest.raises(UnfittedError):
            outlierist1.transform(df_data['col1'])
        
        # Call the method to be tested
        outlierist1.fit(df_data['col1'])

        transformed1 = outlierist1.transform(df_data['col1'])
        
        # Assert the result
        assert (transformed1.reshape(-1) == df_expected1).all()

        # Create an instance of the class
        outlierist2 = Outlierist_ZScore()

        with pytest.raises(UnfittedError):
            outlierist2.transform(df_data['col2'])
        
        # Call the method to be tested
        outlierist2.fit(df_data['col2'])

        transformed2 = outlierist2.transform(df_data['col2'])
        
        # Assert the result
        assert (transformed2.reshape(-1) == df_expected2).all()

class Test_Outlierist_IQR:
    def test_IQR_no_outliers(self):
        # Prepare test data
        df_data = pd.DataFrame({'col1': [1.0, 2.0, 3.0], 'col2': pd.to_datetime(['2020-10-01', '2020-10-02', '2020-10-03'])})
        
        # Create an instance of the class
        outlierist1 = Outlierist_IQR()

        with pytest.raises(UnfittedError):
            outlierist1.transform(df_data['col1'])
        
        # Call the method to be tested
        outlierist1.fit(df_data['col1'])

        transformed1 = outlierist1.transform(df_data['col1'])
        
        # Assert the result
        assert (transformed1 == np.array([False, False, False])).all()

        # Create an instance of the class
        outlierist2 = Outlierist_IQR()

        with pytest.raises(UnfittedError):
            outlierist2.transform(df_data['col2'])
        
        # Call the method to be tested
        outlierist2.fit(df_data['col2'])

        transformed2 = outlierist2.transform(df_data['col2'])
        
        # Assert the result
        assert (transformed2 == np.array([False, False, False])).all()

    def test_Zscore_with_outliers(self):
        # Prepare test data
        df_data = pd.DataFrame({'col1': [0.0] * 10000 + [10000.0], 'col2': pd.to_datetime(['2222-12-12']).append(pd.to_datetime(['2022-12-13']*10000))})
        df_expected1 = np.array([False] * 10000 + [True])
        df_expected2 = np.array([True] + [False] * 10000)
        
        # Create an instance of the class
        outlierist1 = Outlierist_IQR()

        with pytest.raises(UnfittedError):
            outlierist1.transform(df_data['col1'])
        
        # Call the method to be tested
        outlierist1.fit(df_data['col1'])

        transformed1 = outlierist1.transform(df_data['col1'])
        
        # Assert the result
        assert (transformed1.reshape(-1) == df_expected1).all()

        # Create an instance of the class
        outlierist2 = Outlierist_IQR()

        with pytest.raises(UnfittedError):
            outlierist2.transform(df_data['col2'])
        
        # Call the method to be tested
        outlierist2.fit(df_data['col2'])

        transformed2 = outlierist2.transform(df_data['col2'])
        
        # Assert the result
        assert (transformed2.reshape(-1) == df_expected2).all()