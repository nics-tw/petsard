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
    schema_config=None
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
- `schema_config` (`SchemaConfig`, optional): Schema configuration object for advanced data processing
  - Default: None
  - Use `SchemaConfig` and `FieldConfig` objects to define field-level processing rules
  - Provides type-safe configuration with validation
  - Takes precedence over deprecated `column_types` and `na_values` parameters
  - **Conflict Detection**: If both `schema_config` and `column_types` define the same field, a `ConfigError` will be raised

## Examples

```python
from petsard import Loader


# Basic usage
load = Loader('data.csv')
data, meta = load.load()

# Using benchmark dataset
load = Loader('benchmark://adult-income')
data, meta = load.load()

# Using SchemaConfig for advanced field processing
from petsard.metadater import SchemaConfig, FieldConfig

fields = {
    'age': FieldConfig(
        type_hint='int',
        na_values=['unknown', 'N/A', '?']
    ),
    'salary': FieldConfig(
        type_hint='float',
        precision=2,
        na_values=['missing']
    ),
    'active': FieldConfig(
        type_hint='boolean'
    ),
    'category': FieldConfig(
        type_hint='category'
    )
}

schema_config = SchemaConfig(
    schema_id='my_schema',
    name='My Data Schema',
    fields=fields
)

load = Loader('data.csv', schema_config=schema_config)
data, meta = load.load()

# Conflict detection - this will raise ConfigError
try:
    load = Loader(
        'data.csv',
        column_types={'category': ['age']},  # Conflicts with schema_config
        schema_config=schema_config          # Both define 'age' field
    )
except ConfigError as e:
    print(f"Conflict detected: {e}")
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

- `config` (`LoaderConfig`): Configuration object containing：
  - `filepath` (`str`): Local data file path
  - `method` (`str`): Loading method
  - `file_ext` (`str`): File extension
  - `benchmark` (`bool`): Whether using benchmark dataset
  - `dtypes` (`dict`): Column data types
  - `column_types` (`dict`): User-defined column types (deprecated)
  - `header_names` (`list`): Column headers
  - `na_values` (`str` | `list` | `dict`): NA value definitions (deprecated)
  - `schema_config` (`SchemaConfig` | `None`): Schema configuration object
  - For benchmark datasets only:
    - `filepath_raw` (`str`): Original input filepath
    - `benchmark_name` (`str`): Benchmark dataset name
    - `benchmark_filename` (`str`): Benchmark dataset filename
    - `benchmark_access` (`str`): Benchmark dataset access type
    - `benchmark_region_name` (`str`): Amazon region name
    - `benchmark_bucket_name` (`str`): Amazon bucket name
    - `benchmark_sha256` (`str`): SHA-256 value of benchmark dataset