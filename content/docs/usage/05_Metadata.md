---
title: "Metadata"
draft: false
weight: 16
toc: true
---

`Metadata` serves as an extension of the `Loader` module within `PETsARD`, capturing dataset properties and facilitating `Processor` initialisation. Below is the usage of `Metadata`.

```Python
from PETsARD.loader import Metadata


metadata = Metadata()
metadata.build_metadata(df)
```

# `Metadata`

If you are utilising the `Loader` in `PETsARD`, congratulations! You already have metadata accessible via `Loader.metadata.metadata`. However, if you are not using the `Loader`, you will need this module to create metadata. No input is required for its initialization.

```Python
metadata = Metadata()
```

## `build_metadata()`

Read the dataset and build the metadata.

**Parameters**

`data` (`pd.DataFrame`): The data to create metadata from.

## `to_sdv()`

Within the `sdv` library, several classes necessitate metadata specifically defined by `sdv`. This function offers a method to convert the metadata stored in `Metadata` to a format acceptable by `sdv`.

**Outputs**

`sdv_metadata` (dict): The metadata in `sdv` metadata format.

## `self.metadata`

The metadata is stored in `self.metadata` in the format of nested `dict`. It records the properties of each column (in the key `'col'`), including data type (`'dtype'`, align with `pandas`), percentage of `NA` (`'na_percentage'`), and inferred data type (`'inder_dtype'`, either one of the following: 'numerical', 'categorical', 'datetime', and 'object'). It records the properties of the dataset as well (in the key `'global'`), including the dimension of the dataset (`'row_num'` and `'col_num'`) and the overall `NA` percentage (`'na_percentage'`). Below are the structure and the example of `self.metadata`.

```Python
{
    'col': {
        col_name: {
            'dtype': dtype,
            'na_percentage': column_na_percentage,
            'infer_dtype': infer_dtype
        }, ...
    },
    'global': {
        'row_num': row_num,
        'col_num': col_num,
        'na_percentage': global_na_percentage
    }
}
```

```plain_text
{
    'col': {
        'age': {
            'dtype': dtype('int8'),
            'na_percentage': 0.0,
            'infer_dtype': 'numerical'
        },
        'workclass': {
            'dtype': CategoricalDtype(...),
            'na_percentage': 0.057307,
            'infer_dtype': 'categorical'
        }
    },
    'global': {
        'row_num': 48842,
        'col_num': 15,
        'na_percentage': 0.074117
    }
}
```
