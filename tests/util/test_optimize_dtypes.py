import pytest
import pandas as pd
import numpy as np
from pandas.api.types import is_integer_dtype, is_float_dtype
from PETsARD.util.optimize_dtypes import _optimized_numeric_dtypes

class TestOptimizedNumericDtypes:
    def test_optimized_numeric_dtypes_integer(self):
        # Test case for integer column
        col_data = pd.Series([1, 2, 3, 4, 5])
        expected_dtype = 'int8'

        result_dtype = _optimized_numeric_dtypes(col_data)

        assert result_dtype == expected_dtype

    def test_optimized_numeric_dtypes_float(self):
        # Test case for float column
        col_data = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        expected_dtype = 'float32'

        result_dtype = _optimized_numeric_dtypes(col_data)

        assert result_dtype == expected_dtype

    def test_optimized_numeric_dtypes_outside_range(self):
        # Test case for column outside the range of predefined data types
        col_data = pd.Series([1000000000000, 2000000000000, 3000000000000])
        expected_dtype = 'int64'

        result_dtype = _optimized_numeric_dtypes(col_data)

        assert result_dtype == expected_dtype

    def test_optimized_numeric_dtypes_original_dtype(self):
        # Test case for column where none of the ranges match
        col_data = pd.Series([1, 2, 3, 4, 5], dtype='int32')
        expected_dtype = 'int8'

        result_dtype = _optimized_numeric_dtypes(col_data)

        assert result_dtype == expected_dtype