---
title: Metadater
type: docs
weight: 58
prev: docs/api/loader
next: docs/api/metadata
---


```python
Metadater()
```

Advanced metadata management system that provides comprehensive field analysis, schema operations, and metadata transformations. The system operates on a three-tier hierarchy: **Metadata** (top-level container for multiple datasets) → **Schema** (structure definition for individual datasets) → **Field** (column-level metadata with statistics and type information). Supports functional programming patterns and pipeline-based processing for complex data workflows.

## Parameters

None

## Examples

```python
from petsard import Metadater
import pandas as pd

# Initialize Metadater
metadater = Metadater()

# Build metadata from multiple datasets
datasets = {
    'users': pd.DataFrame({'id': [1, 2, 3], 'name': ['Alice', 'Bob', 'Charlie']}),
    'orders': pd.DataFrame({'order_id': [101, 102], 'user_id': [1, 2]})
}

metadata = metadater.build_metadata_from_datasets(datasets)

# Create schema configuration
config = metadater.create_schema_config(
    column_types={'id': 'int', 'name': 'str'},
    descriptions={'id': 'User identifier', 'name': 'User full name'}
)

# Apply field configuration
aligned_data = metadater.apply_field_config(df, schema)

# Convert metadata to DataFrame for analysis
metadata_df = metadater.get_metadata_to_dataframe(metadata)
```

## Methods

### `build_metadata_from_datasets()`

```python
metadater.build_metadata_from_datasets(datasets, config=None)
```

Build comprehensive metadata from multiple DataFrames with optional configuration.

**Parameters**

- `datasets` (dict[str, pd.DataFrame]): Dictionary mapping schema names to DataFrames
- `config` (MetadataConfig | dict, optional): Configuration for metadata generation

**Returns**

- `Metadata`: Complete metadata object containing all schema information

### `build_field_from_series()`

```python
metadater.build_field_from_series(series, field_name, config=None)
```

Create detailed field metadata from a pandas Series.

**Parameters**

- `series` (pd.Series): Input data series
- `field_name` (str): Name for the field
- `config` (FieldConfig, optional): Field-specific configuration

**Returns**

- `FieldMetadata`: Comprehensive field metadata including statistics and type information

### `build_schema_from_dataframe()`

```python
metadater.build_schema_from_dataframe(data, config=None)
```

Generate schema metadata from DataFrame with automatic field analysis.

**Parameters**

- `data` (pd.DataFrame): Input DataFrame
- `config` (SchemaConfig, optional): Schema configuration settings

**Returns**

- `SchemaMetadata`: Complete schema with field metadata and relationships

### `apply_field_config()`

```python
metadater.apply_field_config(data, schema)
```

Apply field configurations to align data with schema requirements.

**Parameters**

- `data` (pd.DataFrame): Input DataFrame to transform
- `schema` (SchemaMetadata): Target schema configuration

**Returns**

- `pd.DataFrame`: Transformed DataFrame aligned with schema

### `validate_against_schema()`

```python
metadater.validate_against_schema(data, schema)
```

Validate DataFrame against schema requirements and return validation results.

**Parameters**

- `data` (pd.DataFrame): DataFrame to validate
- `schema` (SchemaMetadata): Schema to validate against

**Returns**

- `dict`: Validation results with violations and warnings

### `create_schema_config()`

```python
metadater.create_schema_config(column_types=None, cast_errors=None, descriptions=None)
```

Create configuration dictionary for schema metadata generation.

**Parameters**

- `column_types` (dict[str, str], optional): Column name to type mappings
- `cast_errors` (dict[str, str], optional): Error handling strategies per column
- `descriptions` (dict[str, str], optional): Column descriptions

**Returns**

- `dict`: Configuration dictionary for schema operations

### `get_metadata_to_dataframe()`

```python
metadater.get_metadata_to_dataframe(metadata)
```

Convert Metadata object to DataFrame for analysis and visualization.

**Parameters**

- `metadata` (Metadata): Metadata object to convert

**Returns**

- `pd.DataFrame`: Tabular representation of metadata

### `get_schema_to_dataframe()`

```python
metadater.get_schema_to_dataframe(schema)
```

Convert SchemaMetadata to DataFrame format.

**Parameters**

- `schema` (SchemaMetadata): Schema metadata to convert

**Returns**

- `pd.DataFrame`: Schema information in tabular format

### `get_fields_to_dataframe()`

```python
metadater.get_fields_to_dataframe(schema)
```

Extract field information from schema as DataFrame with detailed statistics.

**Parameters**

- `schema` (SchemaMetadata): Schema containing field metadata

**Returns**

- `pd.DataFrame`: Comprehensive field analysis with statistics and properties

## Attributes

- `field_ops`: FieldOperations instance for field-level operations
- `schema_ops`: SchemaOperations instance for schema-level operations  
- `metadata_ops`: MetadataOperations instance for metadata-level operations
- `CONFIG_KEYS`: List of supported configuration keys ['column_types', 'cast_errors', 'descriptions']

## Advanced Processing Features

Metadater provides advanced field processing capabilities through functional APIs and pipeline-based workflows:

### FieldPipeline

`FieldPipeline` enables chaining multiple field processing steps in a configurable pipeline:

```python
from petsard.metadater import FieldPipeline, analyze_field

# Create a processing pipeline
pipeline = (FieldPipeline()
    .with_stats(enabled=True)                    # Calculate field statistics
    .with_logical_type_inference(enabled=True)   # Infer logical types (email, phone, etc.)
    .with_dtype_optimization(enabled=True))      # Optimize pandas dtypes

# Create initial metadata
initial_metadata = analyze_field(data, "field_name", compute_stats=False)

# Process through pipeline
final_metadata = pipeline.process(data, initial_metadata)
```

### Functional Field Analysis

```python
from petsard.metadater import (
    analyze_field, 
    analyze_dataframe_fields,
    create_field_analyzer,
    compose
)

# Direct field analysis
field_metadata = analyze_field(
    field_data=series,
    field_name="column_name",
    compute_stats=True,
    infer_logical_type=True
)

# Custom analyzer with specific settings
fast_analyzer = create_field_analyzer(
    compute_stats=False,
    sample_size=100
)

# Analyze entire DataFrame
field_metadata_dict = analyze_dataframe_fields(
    data=df, 
    field_configs=field_configs
)