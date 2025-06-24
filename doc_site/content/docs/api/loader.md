---
title: Loader
type: docs
weight: 52
prev: docs/api/executor
next: docs/api/metadater
---


```python
Loader(
    filepath=None,
    method=None,
    column_types=None,
    header_names=None,
    na_values=None
)
```

Module for loading tabular data.

## Parameters

- `filepath` (`str`, optional): Path to the dataset file. Cannot be used with `method`
  - Default: None
  - If using benchmark dataset, format as `benchmark://{dataset_name}`
- `method` (`str`, optional): Loading method. Cannot be used with `filepath`
  - Default: None
  - Values: 'default'- loads PETsARD's default dataset 'adult-income'
- `column_types` (`dict`, optional): Column type definitions
  - Default: None
  - Format: `{type: [colname]}`
  - Available types (case-insensitive):
    - 'category': Categorical columns
    - 'datetime': Datetime columns
- `header_names` (`list`, optional): Column names for data without headers
  - Default: None
- `na_values` (`str` | `list` | `dict`, optional): Values to be recognized as NA/NaN
  - Default: None
  - If str or list: Apply to all columns
  - If dict: Apply per-column with format `{colname: na_values}`
  - Example: `{'workclass': '?', 'age': [-1]}`

## Examples

```python
from petsard import Loader


# Basic usage
load = Loader('data.csv')
load.load()

# Using benchmark dataset
load = Loader('benchmark://adult-income')
load.load()
```

## Methods

### `load()`

Read and load the data.

**Parameters**

None.

**Return**

- `data` (`pd.DataFrame`): Loaded DataFrame
- `metadata` (`SchemaMetadata`): Dataset schema metadata with field information and statistics

```python
loader = Loader('data.csv')
data, metadata = loader.load() # get loaded DataFrame
```

## Attributes

- `config` (`LoaderConfig`): Configuration dictionary containing：
  - `filepath` (`str`): Local data file path
  - `method` (`str`): Loading method
  - `file_ext` (`str`): File extension
  - `benchmark` (`bool`): Whether using benchmark dataset
  - `dtypes` (`dict`): Column data types
  - `column_types` (`dict`): User-defined column types
  - `header_names` (`list`): Column headers
  - `na_values` (`str` | `list` | `dict`): NA value definitions
  - For benchmark datasets only:
    - `filepath_raw` (`str`): Original input filepath
    - `benchmark_name` (`str`): Benchmark dataset name
    - `benchmark_filename` (`str`): Benchmark dataset filename
    - `benchmark_access` (`str`): Benchmark dataset access type
    - `benchmark_region_name` (`str`): Amazon region name
    - `benchmark_bucket_name` (`str`): Amazon bucket name
    - `benchmark_sha256` (`str`): SHA-256 value of benchmark dataset