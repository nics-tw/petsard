import numpy as np
import pandas as pd
import pytest

from PETsARD.util.safe_dtype import safe_dtype

def test_safe_dtype():
    # Test case for np.dtype
    assert safe_dtype(np.int32) == 'int32'
    assert safe_dtype(np.float64) == 'float64'

    # Test case for built-in types
    assert safe_dtype(int) == 'int'
    assert safe_dtype(float) == 'float'
    assert safe_dtype(str) == 'str'

    # Test case for pd.CategoricalDtype
    cat_dtype = pd.CategoricalDtype(categories=['A', 'B', 'C'])
    assert safe_dtype(cat_dtype) == 'category'

    # Test case for pd.IntervalDtype
    interval_dtype = pd.IntervalDtype(subtype=np.int64)
    assert safe_dtype(interval_dtype) == 'interval[int64]'

    # Test case for pd.PeriodDtype
    period_dtype = pd.PeriodDtype(freq='D')
    assert safe_dtype(period_dtype) == 'period[D]'

    # Test case for pd.SparseDtype
    sparse_dtype = pd.SparseDtype(dtype=np.float32)
    assert safe_dtype(sparse_dtype) == 'Sparse[float32, nan]'

    # Test case for string representation
    assert safe_dtype('int') == 'int'
    assert safe_dtype('float') == 'float'
    assert safe_dtype('str') == 'str'

    # Test case for unsupported data type
    with pytest.raises(TypeError):
        safe_dtype(list)

    with pytest.raises(TypeError):
        safe_dtype(None)