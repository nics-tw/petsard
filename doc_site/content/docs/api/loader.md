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
    na_values=None,
    schema=None
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
- `column_types` (`dict`, optional): **⚠️ DEPRECATED in v2.0.0 - will be removed** Column type definitions
  - Default: None
  - Format: `{type: [colname]}`
  - Available types (case-insensitive):
    - 'category': Categorical columns
    - 'datetime': Datetime columns
- `header_names` (`list`, optional): Column names for data without headers
  - Default: None
- `na_values` (`str` | `list` | `dict`, optional): **⚠️ DEPRECATED in v2.0.0 - will be removed** Values to be recognized as NA/NaN
  - Default: None
  - If str or list: Apply to all columns
  - If dict: Apply per-column with format `{colname: na_values}`
  - Example: `{'workclass': '?', 'age': [-1]}`
- `schema` (`dict`, optional): Field schema configuration for advanced data processing
  - Default: None
  - Format: `{field_name: {config_options}}`
  - Available configuration options per field:
    - `'type'` (`str`): Data type hint for conversion
      - Supported types: 'int', 'integer', 'float', 'string', 'str', 'category', 'boolean', 'datetime', 'date'
    - `'na_values'` (`str` | `list`): Custom NA values for this specific field
    - `'precision'` (`int`): Decimal precision for numeric fields (≥ 0)
  - Example: `{'age': {'type': 'int', 'na_values': ['unknown', 'N/A']}, 'salary': {'type': 'float', 'precision': 2}}`
  - Takes precedence over deprecated `column_types` and `na_values` parameters

## Examples

```python
from petsard import Loader


# Basic usage
load = Loader('data.csv')
data, meta = load.load()

# Using benchmark dataset
load = Loader('benchmark://adult-income')
data, meta = load.load()

# Using schema for advanced field processing
schema_config = {
    'age': {
        'type': 'int',
        'na_values': ['unknown', 'N/A', '?']
    },
    'salary': {
        'type': 'float',
        'precision': 2,
        'na_values': ['missing']
    },
    'active': {
        'type': 'boolean'
    },
    'category': {
        'type': 'category'
    }
}

load = Loader('data.csv', schema=schema_config)
data, meta = load.load()

# Metadata takes precedence over deprecated parameters
load = Loader(
    'data.csv',
    column_types={'category': ['age']},  # This will be overridden
    schema={'age': {'type': 'int'}}    # This takes precedence
)
data, meta = load.load()
```

## Methods

### `load()`

Read and load the data.

**Parameters**

None.

**Return**

- `data` (`pd.DataFrame`): Loaded DataFrame
- `schema` (`SchemaMetadata`): Dataset schema schema with field information and statistics

```python
loader = Loader('data.csv')
data, meta = loader.load() # get loaded DataFrame
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