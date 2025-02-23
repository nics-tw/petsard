---
title: Metadata
type: docs
weight: 59
prev: docs/api/reporter
next: docs/api/describer
---


```python
Metadata()
```

Captures dataset properties including data types, missing value percentages, and dataset dimensions. Provides utilities for type inference and SDV metadata conversion.

## Parameters

None

## Examples

```python
from petsard import Metadata


# Create and build metadata
meta = Metadata()
meta.build_metadata(df)

# Access metadata
col_properties = meta.metadata['col']
dataset_properties = meta.metadata['global']

# Convert for SDV
sdv_meta = meta.to_sdv()
```

## Methods

### `build_metadata()`

```python
meta.build_metadata(data)
```

Create metadata from DataFrame and infer data types.

**Parameters**

- `data` (pd.DataFrame): Input DataFrame

**Returns**

None. Updates `metadata` attribute

### `set_col_infer_dtype()`

```python
meta.set_col_infer_dtype(col, dtype)
```

Set the inferred data type for a specific column.

**Parameters**

- `col` (str): Column name
- `dtype` (str): Inferred data type
  - Values: 'numerical', 'categorical', 'datetime', 'object'

**Returns**

None. Updates column's infer_dtype

### `to_sdv()`

Convert metadata to SDV compatible format.

**Parameters**

None.

**Returns**

- dict: SDV formatted metadata

## Attributes

- `metadata`: Nested dictionary containing dataset properties:
  - `col`: Per-column properties
    - `dtype`: pandas data type
    - `na_percentage`: Proportion of NA values
    - `infer_dtype`: Inferred data type ('numerical', 'categorical', 'datetime', or 'object')
  - `global`: Dataset-wide properties
    - `row_num`: Number of rows
    - `col_num`: Number of columns
    - `na_percentage`: Overall proportion of NA values
