import random
import string
from datetime import timedelta

import numpy as np
import pandas as pd
import pytest
from scipy import sparse

from petsard.util import safe_astype


@pytest.fixture
def test_data():
    size = 42
    # set seed also
    random.seed(size)
    np.random.seed(size)

    # Special process for float64: https://github.com/numpy/numpy/issues/16695
    float64_samples: np.ndarray = np.random.uniform(
        low=0,
        high=np.finfo(np.float64).max,
        size=size,
    ).astype(np.float64)
    float64_samples[
        np.random.choice(
            size,
            size // 2,
            replace=False,
        )
    ] *= -1

    nullable_int_samples: list = list(
        np.random.randint(
            np.iinfo(np.int64).min,
            np.iinfo(np.int64).max,
            size=size,
            dtype=np.int64,
        )
    )
    nullable_int_samples = [
        None
        if idx in list(np.random.choice(size, size=size // 2, replace=False))
        else val
        for idx, val in enumerate(nullable_int_samples)
    ]

    object_samples: pd.Series = pd.concat(
        [
            pd.Series([f"str_{i}" for i in range(size // 4)]),
            pd.Series(np.random.randint(0, size, size=(size // 4))),
            pd.Series(np.random.rand(size // 4)),
            pd.Series([np.nan] * (size - 3 * (size // 4))),
        ]
    )
    object_samples = object_samples.sample(frac=1).reset_index(drop=True)

    data = {
        # bool
        "bool": np.random.choice([True, False], size=size),
        # category
        "category": pd.Categorical(
            np.random.choice(
                ["cat", "dog", "bird"],
                size=size,
            )
        ),
        # complex
        "complex": np.random.choice(
            [complex(x, y) for x in range(1, size + 1) for y in range(1, size + 1)],
            size=size,
        ),
        # datetime
        "datetime": pd.to_datetime(
            pd.date_range(
                start=pd.Timestamp.now(),
                periods=size,
            )
        ),
        # float
        "float16": np.random.uniform(
            low=np.finfo(np.float16).min,
            high=np.finfo(np.float16).max,
            size=size,
        ).astype(np.float16),
        "float32": np.random.uniform(
            low=np.finfo(np.float32).min,
            high=np.finfo(np.float32).max,
            size=size,
        ).astype(np.float32),
        "float64": float64_samples,
        # int
        "int8": np.random.randint(
            np.iinfo(np.int8).min,
            np.iinfo(np.int8).max,
            size=size,
            dtype=np.int8,
        ),
        "int16": np.random.randint(
            np.iinfo(np.int16).min,
            np.iinfo(np.int16).max,
            size=size,
            dtype=np.int16,
        ),
        "int32": np.random.randint(
            np.iinfo(np.int32).min,
            np.iinfo(np.int32).max,
            size=size,
            dtype=np.int32,
        ),
        "int64": np.random.randint(
            np.iinfo(np.int64).min,
            np.iinfo(np.int64).max,
            size=size,
            dtype=np.int64,
        ),
        "nullable_int": nullable_int_samples,
        # interval
        "interval": [
            pd.Interval(i, i + offset)
            for i, offset in enumerate(np.random.randint(size, size=size))
        ],
        # object
        "object": object_samples,
        # object_string
        "object_string": [
            "".join(random.choices(string.ascii_lowercase, k=3)) for _ in range(size)
        ],
        # period
        "period": pd.period_range(
            pd.Timestamp.now(),
            periods=size,
            freq="D",
        ),
        # sparse
        "sparse": pd.arrays.SparseArray(
            sparse.random(
                1,
                size,
                density=0.1,
                random_state=size,
            ).A[0]
        ),
        # timedelta
        "timedelta": [
            timedelta(days=int(d)) for d in np.random.randint(1, size, size=size)
        ],
    }

    filter_col: list[str] = [
        # 'bool',
        "category",
        # 'complex',
        "datetime",
        "float16",
        "float32",
        # 'float64',
        "int8",
        "int16",
        "int32",
        # 'int64',
        # 'interval',
        "nullable_int",
        "object",
        "object_string",
        # 'period',
        # 'sparse',
        # 'timedelta',
    ]

    return pd.DataFrame({key: data[key] for key in filter_col})


@pytest.mark.parametrize(
    "declare_dtype, expected_success_cols",
    [
        (
            "int8",
            [
                "int8",
                "float16",
                "float32",
            ],
        ),
        (
            "int16",
            [
                "int8",
                "int16",
                "float16",
                "float32",
            ],
        ),
        (
            "int32",
            [
                "int8",
                "int16",
                "int32",
                "float16",
                "float32",
            ],
        ),
        (
            "int64",
            [
                "int8",
                "int16",
                "int32",
                "float16",
                "float32",
            ],
        ),
        (
            "float16",
            [
                "int8",
                "int16",
                "int32",
                "float16",
                "float32",
                "nullable_int",
            ],
        ),
        (
            "float32",
            [
                "int8",
                "int16",
                "int32",
                "float16",
                "float32",
                "nullable_int",
            ],
        ),
        (
            "float64",
            [
                "int8",
                "int16",
                "int32",
                "float16",
                "float32",
                "nullable_int",
            ],
        ),
        (
            "object",
            [
                "int8",
                "int16",
                "int32",
                "float16",
                "float32",
                "nullable_int",
                "object",
                "object_string",
                "category",
                "datetime",
            ],
        ),
        (
            "category",
            [
                "int8",
                "int16",
                "int32",
                "float16",
                "float32",
                "nullable_int",
                "object",
                "object_string",
                "category",
                "datetime",
            ],
        ),
        (
            "datetime64[ns]",
            [
                "int8",
                "int16",
                "int32",
                "float16",
                "float32",
                "nullable_int",
                "datetime",
            ],
        ),
    ],
)
def test_safe_astype(test_data, declare_dtype, expected_success_cols):
    for col_name in expected_success_cols:
        if declare_dtype == "float32" and col_name in [
            "float16",
            "nullable_int",
        ]:
            continue

        col = test_data[col_name]
        new_col = safe_astype(col, declare_dtype)
        assert new_col.dtype.name == declare_dtype, (
            f"Unexpected failure for {col_name} with {declare_dtype}"
        )

    for col_name, dtypes in test_data.dtypes.items():
        if col_name not in expected_success_cols:
            col = test_data[col_name]
            try:
                new_col = safe_astype(col, declare_dtype)
                assert False, f"Unexpected success for {col_name} with {declare_dtype}"
            except (TypeError, ValueError, NotImplementedError):
                pass
