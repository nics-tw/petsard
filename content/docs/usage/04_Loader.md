---
title: "Loader"
draft: false
weight: 15
toc: true
---

The `Loader` module is responsible for loading the data into the memory for further procedure.

```python
from PETsARD import Loader


load = Loader('data.csv')
load.load()
```

# `Loader`

The basic usage of `Loader` is providing the file path for initialisation. We offer various optional parameters to facilitate customization according to specific requirements.

```Python
from PETsARD import Loader


load = Loader(
    filepath='benchmark/adult-income.csv',
    method=None,
    column_types={
        'category': [
            'workclass',
            'education',
            'marital-status',
            'occupation',
            'relationship',
            'race',
            'gender',
            'native-country',
            'income',
        ],
        'datetime': [],
    },
    header_names=None,
    na_values={
        'workclass': '?',
        'occupation': '?',
        'native-country': '?',
    }
)
load.load()
print(load.data.head(1))
```

**Parameters**

`filepath` (`str`, default=`None`, optional): The fullpath of dataset.

`method` (`str`, default=`None`, optional): The method for `Loader`. The only method for `Loader` is 'default', in which case there is no need to input `filepath`, and `Loader` will read the default dataset of `PETsARD` 'adult-income'. It is not necessary to set this if a `filepath` is provided.

`column_types` (`dict`, default=`None`, optional): The dictionary of column types and their corresponding column names, formatted as `{type: [colname]}`. Only the following types are supported (case-insensitive):

- 'category': The column(s) will be treated as categorical.
- 'datetime': The column(s) will be treated as datetime.

`header_names` (`list`, default=`None`, optional): Specifies a list of headers for the data without header.

`na_values` (`str | list | dict`, default=`None`, optional): The values to be recognized as `NA/NaN`. If a `dict` passed, `NA` values can be specified per-column. The format is `{colname: na_values}`. In the default setting, it will adopt the default checking in `pandas` only. Check [pandas document](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html) for details.

## `load()`

Read and load the data.

## `self.config`

The configuration of `Loader` module:

- `filepath` (`str`): The file path for the actual local data.
  - When using [benchmark dataset](PETsARD/docs/usage/06_benchmark-datasets/), it will be replaced by the filename of the data actually downloaded and saved.
- `method` (`str`): Same as input.
- `file_ext` (`str`): The file extension of the local data.
- `benchmark` (`bool`): Indicates whether it is a [benchmark dataset](PETsARD/docs/usage/06_benchmark-datasets/).
- `dtypes` (`dict`): The dictionary of column names and their types as format.
- `column_types` (`dict`, optional), `header_name` (`list`, optional), `na_values` (`str | list | dict`, optional): Same as input.

The following parameters are exclusive to using a benchmark dataset. See [benchmark dataset](PETsARD/docs/usage/06_benchmark-datasets/).

- `filepath_raw` (`str`): Keep original filepath input by user.
- `benchmark_name` (`str`): The name of benchmark dataset by user.
- `benchmark_filename` (`str`): The filename of benchmark dataset.
- `benchmark_access` (`str`): The access type of benchmark dataset.
- `benchmark_region_name` (`str`): The Amazon region name of benchmark dataset.
- `benchmark_bucket_name` (`str`): The Amazon bucket name of benchmark dataset.
- `benchmark_sha256` (`str`): The SHA-256 value of benchmark dataset.

## `self.loader`

The instantiated loader itself.

## `self.data`

The loaded data is stored in `self.data` in the format of `pd.DataFrame`.

## `self.metadata.metadata`

The metadata is stored in `self.metadata.metadata` in the format of nested `dict`. See the page ["Metadata"](PETsARD/docs/usage/05_metadata/).
