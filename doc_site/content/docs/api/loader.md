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
- `schema` (`SchemaConfig` | `dict` | `str`, optional): Schema definition for data processing
  - Default: None
  - **SchemaConfig object**: Direct schema configuration object
  - **Dict**: Inline schema definition that will be converted to SchemaConfig
  - **String**: Path to external YAML schema file (e.g., `'my_schema.yaml'`)
  - Supports all schema parameters: `optimize_dtypes`, `nullable_int`, `fields`, etc.
  - Takes precedence over deprecated `column_types` and `na_values` parameters
  - **Conflict Detection**: If both `schema` and `column_types` define the same field, a `ConfigError` will be raised
  - **External Schema File Benefits**:
    - **Reusability**: Same schema can be used across multiple components (Loader, Metadater, Splitter, Synthesizer)
    - **Maintainability**: Centralized schema definitions for easier updates
    - **Evaluation Convenience**: Direct use in evaluation processes for consistency
    - **Version Control**: Independent schema versioning and evolution tracking

## Examples

```python
from petsard import Loader


# Basic usage
load = Loader('data.csv')
data, meta = load.load()

# Using benchmark dataset
load = Loader('benchmark://adult-income')
data, meta = load.load()

# Using external schema file (recommended)
load = Loader('data.csv', schema='my_schema.yaml')
data, meta = load.load()

# Using inline schema definition
schema_dict = {
    'optimize_dtypes': True,
    'nullable_int': 'force',
    'fields': {
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
            'type': 'bool'
        },
        'category': {
            'type': 'str',
            'category_method': 'force'
        }
    }
}
load = Loader('data.csv', schema=schema_dict)
data, meta = load.load()

# For advanced schema configuration, refer to Metadater API documentation

# Conflict detection - this will raise ConfigError
try:
    load = Loader(
        'data.csv',
        column_types={'category': ['age']},  # Conflicts with schema
        schema=schema_dict                   # Both define 'age' field
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
  - `column_types` (`dict`): User-defined column types (deprecated)
  - `header_names` (`list`): Column headers
  - `na_values` (`str` | `list` | `dict`): NA value definitions (deprecated)
  - `schema` (`SchemaConfig` | `None`): Schema configuration object
  - `schema_path` (`str` | `None`): Path to schema file if loaded from YAML file
  - File path components:
    - `dir_name` (`str`): Directory name
    - `base_name` (`str`): Base filename with extension
    - `file_name` (`str`): Filename without extension
    - `file_ext` (`str`): File extension
    - `file_ext_code` (`int`): File extension code for internal processing
  - `benchmarker_config` (`BenchmarkerConfig` | `None`): Benchmark dataset configuration (handles all benchmark-related operations)