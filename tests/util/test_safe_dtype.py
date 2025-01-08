import numpy as np
import pandas as pd
import pytest

from petsard.util import safe_dtype


def test_safe_dtype():
    # Test case for np.dtype
    assert safe_dtype(np.int32) == "int32"
    assert safe_dtype(np.float64) == "float64"

    # Test case for built-in types
    assert safe_dtype(int) == "int"
    assert safe_dtype(float) == "float"
    assert safe_dtype(str) == "str"

    # Test case for pd.CategoricalDtype
    cat_dtype = pd.CategoricalDtype(categories=["A", "B", "C"])
    assert safe_dtype(cat_dtype) == "category[object]"

    # Test case for pd.IntervalDtype
    interval_dtype = pd.IntervalDtype(subtype=np.int64)
    assert safe_dtype(interval_dtype) == "interval[int64]"

    # Test case for pd.PeriodDtype
    period_dtype = pd.PeriodDtype(freq="D")
    assert safe_dtype(period_dtype) == "period[d]"

    # Test case for pd.SparseDtype
    sparse_dtype = pd.SparseDtype(dtype=np.float32)
    assert safe_dtype(sparse_dtype) == "sparse[float32, nan]"

    # Test case for string representation
    assert safe_dtype("int") == "int"
    assert safe_dtype("float") == "float"
    assert safe_dtype("str") == "str"

    # Test case for unsupported data type
    with pytest.raises(TypeError):
        safe_dtype(list)

    with pytest.raises(TypeError):
        safe_dtype(None)


class TestOptimizedNumericDtypes:
    def test_optimized_integer(self):
        # Test case for integer column
        col_data = pd.Series([1, 2, 3, 4, 5])
        expected_dtype = "int8"

        result_dtype = safe_dtype(col_data)

        assert result_dtype == expected_dtype

    def test_optimized_float(self):
        # Test case for float column
        col_data = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        expected_dtype = "float32"

        result_dtype = safe_dtype(col_data)

        assert result_dtype == expected_dtype

    def test_optimized_outside_range(self):
        # Test case for column outside the range of predefined data types
        col_data = pd.Series([1000000000000, 2000000000000, 3000000000000])
        expected_dtype = "int64"

        result_dtype = safe_dtype(col_data)

        assert result_dtype == expected_dtype

    def test_optimized_original_dtype(self):
        # Test case for column where none of the ranges match
        col_data = pd.Series([1, 2, 3, 4, 5], dtype="int32")
        expected_dtype = "int8"

        result_dtype = safe_dtype(col_data)

        assert result_dtype == expected_dtype
