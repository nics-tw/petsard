import numpy as np
import pandas as pd
import pytest

from petsard.exceptions import UnfittedError
from petsard.processor.missing import (
    MissingDrop,
    MissingMean,
    MissingMedian,
    MissingSimple,
)


class Test_MissingMean:
    def test_mean_no_missing_values(self):
        # Prepare test data
        df_data = pd.DataFrame({"col1": [1.0, 2.0, 3.0]})

        # Create an instance of the class
        missing = MissingMean()
        missing.set_na_percentage(0.8)

        with pytest.raises(ValueError):
            missing.set_na_percentage(1.8)

        with pytest.raises(ValueError):
            missing.set_na_percentage(-1.8)

        with pytest.raises(UnfittedError):
            missing.transform(df_data["col1"])

        # Call the method to be tested
        missing.fit(df_data["col1"])

        transformed = missing.transform(df_data["col1"])

        rtransform = missing.inverse_transform(df_data["col1"])

        # Assert the result
        assert (transformed.values == np.array([1.0, 2.0, 3.0])).all()

        # Assert the result
        assert transformed.shape == (3,)
        assert rtransform.isna().any().any()

    def test_mean_with_missing_values(self):
        # Prepare test data
        df_data = pd.DataFrame({"col1": [1.0, None, 3.0]})
        df_expected = pd.Series(data=[1.0, 2.0, 3.0], name="col1")

        # Create an instance of the class
        missing = MissingMean()
        missing.set_na_percentage(0.8)

        with pytest.raises(ValueError):
            missing.set_na_percentage(1.8)

        with pytest.raises(ValueError):
            missing.set_na_percentage(-1.8)

        with pytest.raises(UnfittedError):
            missing.transform(df_data["col1"])

        # Call the method to be tested
        missing.fit(df_data["col1"])

        transformed = missing.transform(df_data["col1"])

        rtransform = missing.inverse_transform(df_data["col1"])

        # Assert the result
        assert (transformed.values == np.array([1.0, 2.0, 3.0])).all()

        # Assert the result
        assert transformed.shape == (3,)
        assert transformed.equals(df_expected)
        assert rtransform.isna().any().any()


class Test_MissingMedian:
    def test_median_no_missing_values(self):
        # Prepare test data
        df_data = pd.DataFrame({"col1": [1.0, 2.0, 3.0]})

        # Create an instance of the class
        missing = MissingMedian()
        missing.set_na_percentage(0.8)

        with pytest.raises(ValueError):
            missing.set_na_percentage(1.8)

        with pytest.raises(ValueError):
            missing.set_na_percentage(-1.8)

        with pytest.raises(UnfittedError):
            missing.transform(df_data["col1"])

        # Call the method to be tested
        missing.fit(df_data["col1"])

        transformed = missing.transform(df_data["col1"])

        rtransform = missing.inverse_transform(df_data["col1"])

        # Assert the result
        assert (transformed.values == np.array([1.0, 2.0, 3.0])).all()

        # Assert the result
        assert transformed.shape == (3,)
        assert rtransform.isna().any().any()

    def test_median_with_missing_values(self):
        # Prepare test data
        df_data = pd.DataFrame({"col1": [1.0, None, 3.0]})
        df_expected = pd.Series(data=[1.0, 2.0, 3.0], name="col1")

        # Create an instance of the class
        missing = MissingMedian()
        missing.set_na_percentage(0.8)

        with pytest.raises(ValueError):
            missing.set_na_percentage(1.8)

        with pytest.raises(ValueError):
            missing.set_na_percentage(-1.8)

        with pytest.raises(UnfittedError):
            missing.transform(df_data["col1"])

        # Call the method to be tested
        missing.fit(df_data["col1"])

        transformed = missing.transform(df_data["col1"])

        rtransform = missing.inverse_transform(df_data["col1"])

        # Assert the result
        assert (transformed.values == np.array([1.0, 2.0, 3.0])).all()

        # Assert the result
        assert transformed.shape == (3,)
        assert transformed.equals(df_expected)
        assert rtransform.isna().any().any()


class Test_MissingSimple:
    def test_simple_no_missing_values(self):
        # Prepare test data
        df_data = pd.DataFrame({"col1": [1.0, 2.0, 3.0]})

        # Create an instance of the class
        missing = MissingSimple(value=1.0)
        missing.set_na_percentage(0.8)

        with pytest.raises(ValueError):
            missing.set_na_percentage(1.8)

        with pytest.raises(ValueError):
            missing.set_na_percentage(-1.8)

        with pytest.raises(UnfittedError):
            missing.transform(df_data["col1"])

        # Call the method to be tested
        missing.fit(df_data["col1"])

        transformed = missing.transform(df_data["col1"])

        rtransform = missing.inverse_transform(df_data["col1"])

        # Assert the result
        assert (transformed.values == np.array([1.0, 2.0, 3.0])).all()

        # Assert the result
        assert transformed.shape == (3,)
        assert rtransform.isna().any().any()

    def test_simple_with_missing_values(self):
        # Prepare test data
        df_data = pd.DataFrame({"col1": [1.0, None, 3.0]})
        df_expected = pd.Series(data=[1.0, 2.0, 3.0], name="col1")

        # Create an instance of the class
        missing = MissingSimple(value=2.0)
        missing.set_na_percentage(0.8)

        with pytest.raises(ValueError):
            missing.set_na_percentage(1.8)

        with pytest.raises(ValueError):
            missing.set_na_percentage(-1.8)

        with pytest.raises(UnfittedError):
            missing.transform(df_data["col1"])

        # Call the method to be tested
        missing.fit(df_data["col1"])

        transformed = missing.transform(df_data["col1"])

        rtransform = missing.inverse_transform(df_data["col1"])

        # Assert the result
        assert (transformed.values == np.array([1.0, 2.0, 3.0])).all()

        # Assert the result
        assert transformed.shape == (3,)
        assert transformed.equals(df_expected)
        assert rtransform.isna().any().any()


class Test_MissingDrop:
    def test_drop_no_missing_values(self):
        # Prepare test data
        df_data = pd.DataFrame({"col1": [1.0, 2.0, 3.0]})

        # Create an instance of the class
        missing = MissingDrop()
        missing.set_na_percentage(0.8)

        with pytest.raises(ValueError):
            missing.set_na_percentage(1.8)

        with pytest.raises(ValueError):
            missing.set_na_percentage(-1.8)

        with pytest.raises(UnfittedError):
            missing.transform(df_data["col1"])

        # Call the method to be tested
        missing.fit(df_data["col1"])

        transformed = missing.transform(df_data["col1"])

        rtransform = missing.inverse_transform(df_data["col1"])

        # Assert the result
        assert (transformed == np.array([False, False, False])).all()

        # Assert the result
        assert transformed.shape == (3,)
        assert rtransform.isna().any().any()

    def test_drop_with_missing_values(self):
        # Prepare test data
        df_data = pd.DataFrame({"col1": [1.0, None, 3.0]})

        # Create an instance of the class
        missing = MissingDrop()
        missing.set_na_percentage(0.8)

        with pytest.raises(ValueError):
            missing.set_na_percentage(1.8)

        with pytest.raises(ValueError):
            missing.set_na_percentage(-1.8)

        with pytest.raises(UnfittedError):
            missing.transform(df_data["col1"])

        # Call the method to be tested
        missing.fit(df_data["col1"])

        transformed = missing.transform(df_data["col1"])

        rtransform = missing.inverse_transform(df_data["col1"])

        # Assert the result
        assert (transformed == np.array([False, True, False])).all()

        # Assert the result
        assert transformed.shape == (3,)
        assert rtransform.isna().any().any()
