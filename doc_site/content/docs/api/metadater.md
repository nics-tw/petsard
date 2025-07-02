---
title: Metadater
type: docs
weight: 53
prev: docs/api/loader
next: docs/api/splitter
---


```python
Metadater()
```

Advanced metadata management system that provides comprehensive field analysis, schema operations, and metadata transformations. The system operates on a three-tier hierarchy: **Metadata** (multi-table datasets) → **Schema** (single table structure) → **Field** (column-level metadata with statistics and type information). Supports functional programming patterns and pipeline-based processing for complex data workflows.

## Design Overview

Metadater adopts a four-tier architecture design combined with functional programming principles, providing a clear, composable, and easy-to-use metadata management interface. We have simplified the complex 23 public interfaces to 9 core interfaces, significantly reducing usage complexity.

**Four-tier Architecture**: `Metadata → Schema → Field → Types`

### Three-Tier Architecture

#### 📊 Metadata Layer (Multi-table Datasets)
```
Responsibility: Managing datasets composed of multiple tables
Use Cases: Relational databases, multi-table analysis
Main Types: Metadata, MetadataConfig
```

#### 📋 Schema Layer (Single Table Structure) - Most Common
```
Responsibility: Managing structure description of individual DataFrames
Use Cases: Single table analysis, data preprocessing
Main Types: SchemaMetadata, SchemaConfig
```

#### 🔍 Field Layer (Single Column Analysis)
```
Responsibility: Managing detailed analysis of individual columns
Use Cases: Column-level deep analysis
Main Types: FieldMetadata, FieldConfig
```

## Core Design Principles

### 1. Immutable Data Structures
- All data types use `@dataclass(frozen=True)`
- Update operations return new object instances
- Support functional data transformations

```python
# Old way (mutable)
field_metadata.stats = new_stats

# New way (immutable)
field_metadata = field_metadata.with_stats(new_stats)
```

### 2. Pure Functions
- All core business logic consists of pure functions
- Same input always produces same output
- No side effects, easy to test and reason about

### 3. Unified Naming Convention
| Verb | Purpose | Examples |
|------|---------|----------|
| **create** | Create new objects | `create_metadata`, `create_schema`, `create_field` |
| **analyze** | Analyze and infer | `analyze_dataset`, `analyze_dataframe`, `analyze_series` |
| **validate** | Validate and check | `validate_metadata`, `validate_schema`, `validate_field` |

## Parameters

None

## Basic Usage

### Most Common Usage
```python
from petsard.metadater import Metadater

# Schema Layer: Analyze single table (most common)
schema = Metadater.create_schema(df, "my_data")
schema = Metadater.analyze_dataframe(df, "my_data")  # Clearer semantics

# Field Layer: Analyze single column
field = Metadater.create_field(df['age'], "age")
field = Metadater.analyze_series(df['email'], "email")  # Clearer semantics
```

### Advanced Usage
```python
# Metadata Layer: Analyze multi-table datasets
tables = {"users": user_df, "orders": order_df}
metadata = Metadater.analyze_dataset(tables, "ecommerce")

# Configured analysis
from petsard.metadater import SchemaConfig, FieldConfig

config = SchemaConfig(
    schema_id="my_schema",
    compute_stats=True,
    infer_logical_types=True
)
schema = Metadater.create_schema(df, "my_data", config)
```

## Methods

### `create_schema()`

```python
Metadater.create_schema(dataframe, schema_id, config=None)
```

Create schema metadata from DataFrame with automatic field analysis.

**Parameters**

- `dataframe` (pd.DataFrame): Input DataFrame
- `schema_id` (str): Schema identifier
- `config` (SchemaConfig, optional): Schema configuration settings

**Returns**

- `SchemaMetadata`: Complete schema with field metadata and relationships

### `analyze_dataframe()`

```python
Metadater.analyze_dataframe(dataframe, schema_id, config=None)
```

Analyze DataFrame structure and generate comprehensive schema metadata.

**Parameters**

- `dataframe` (pd.DataFrame): Input DataFrame to analyze
- `schema_id` (str): Schema identifier
- `config` (SchemaConfig, optional): Analysis configuration

**Returns**

- `SchemaMetadata`: Complete schema analysis with field metadata

### `create_field()`

```python
Metadater.create_field(series, field_name, config=None)
```

Create detailed field metadata from a pandas Series.

**Parameters**

- `series` (pd.Series): Input data series
- `field_name` (str): Name for the field
- `config` (FieldConfig, optional): Field-specific configuration

**Returns**

- `FieldMetadata`: Comprehensive field metadata including statistics and type information

### `analyze_series()`

```python
Metadater.analyze_series(series, field_name, config=None)
```

Analyze series data and generate comprehensive field metadata.

**Parameters**

- `series` (pd.Series): Input data series to analyze
- `field_name` (str): Name for the field
- `config` (FieldConfig, optional): Analysis configuration

**Returns**

- `FieldMetadata`: Detailed field analysis with statistics and type information

### `analyze_dataset()`

```python
Metadater.analyze_dataset(tables, metadata_id, config=None)
```

Analyze multiple tables and generate comprehensive metadata.

**Parameters**

- `tables` (dict[str, pd.DataFrame]): Dictionary mapping table names to DataFrames
- `metadata_id` (str): Metadata identifier
- `config` (MetadataConfig, optional): Metadata configuration

**Returns**

- `Metadata`: Complete metadata object containing all schema information


## Functional Programming Features

### Function Composition
```python
from petsard.metadater import compose, pipe

# Define processing steps
def step1(data): return process_data_1(data)
def step2(data): return process_data_2(data)
def step3(data): return process_data_3(data)

# Compose functions
process_pipeline = compose(step3, step2, step1)
result = process_pipeline(input_data)

# Or use pipeline style
result = pipe(input_data, step1, step2, step3)
```

### Pipeline Processing
```python
from petsard.metadater import FieldPipeline

# Create processing pipeline
pipeline = (FieldPipeline()
           .with_stats(enabled=True)
           .with_logical_type_inference(enabled=True)
           .with_dtype_optimization(enabled=True))

# Process field
result = pipeline.process(field_data, initial_metadata)
```

## Design Benefits

### 1. Significantly Reduced API Complexity
| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Public Interface Count | 23 | 8 | -65% |
| Cognitive Load | High (exceeds 7±2) | Medium (follows principle) | ✅ |
| Learning Curve | Steep | Gentle | ✅ |

### 2. Enhanced Architecture Clarity
| Layer | Before | After | Improvement |
|-------|--------|-------|-------------|
| **Metadata** | Unclear responsibility | Multi-table management | ✅ Clear responsibility |
| **Schema** | Confused with Field | Single table management | ✅ Clear boundaries |
| **Field** | Overlapping functions | Single column management | ✅ Focused functionality |

### 3. Functional Programming Benefits
- **Testability**: Pure functions are easy to unit test, no complex mock setup needed
- **Composability**: Small functions can be composed into complex functionality, flexible configuration and customization
- **Maintainability**: Clear separation of concerns, immutable data structures prevent accidental modifications
- **Performance**: Immutable data structures support caching, pure functions support memoization
- **Type Safety**: Strong type checking, compile-time error detection

## Backward Compatibility

```python
# Use the new unified API
schema = Metadater.create_schema(df, "my_schema")
field = Metadater.create_field(series, "field_name")
```

## Available Tools in `__init__.py`

The Metadater module provides a comprehensive set of tools organized into different categories:

### Core Interface (8 interfaces)

- **`Metadater`**: Primary class providing unified metadata operations
- **`Metadata`**, **`SchemaMetadata`**, **`FieldMetadata`**: Core types
- **`MetadataConfig`**, **`SchemaConfig`**, **`FieldConfig`**: Configuration types
- **`safe_round`**: Utility functions

### Functional API Tools

- **`analyze_field()`**: Analyze individual field data with comprehensive metadata generation
- **`analyze_dataframe_fields()`**: Analyze all fields in a DataFrame with optional field configurations
- **`create_field_analyzer()`**: Create custom field analyzer with specific settings using partial application
- **`compose()`**: Function composition utility for creating complex processing pipelines
- **`pipe()`**: Pipeline utility for chaining operations
- **`FieldPipeline`**: Configurable pipeline for field processing with method chaining

## Examples

### Basic Field Analysis

```python
from petsard.metadater import Metadater
import pandas as pd

# Create sample data
data = pd.Series([1, 2, 3, 4, 5, None, 7, 8, 9, 10], name="numbers")

# Analyze field using new interface
field_metadata = Metadater.analyze_series(
    series=data,
    field_name="numbers"
)

print(f"Field: {field_metadata.name}")
print(f"Data Type: {field_metadata.data_type}")
print(f"Nullable: {field_metadata.nullable}")
if field_metadata.stats:
    print(f"Stats: {field_metadata.stats.row_count} rows, {field_metadata.stats.na_count} nulls")
```

### Schema Analysis

```python
from petsard.metadater import Metadater, SchemaConfig
import pandas as pd

# Create sample DataFrame
df = pd.DataFrame({
    'id': [1, 2, 3, 4, 5],
    'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
    'email': ['alice@test.com', 'bob@test.com', 'charlie@test.com', 'diana@test.com', 'eve@test.com'],
    'age': [25, 30, 35, 28, 32],
})

# Analyze DataFrame
schema = Metadater.analyze_dataframe(
    dataframe=df,
    schema_id="user_data"
)

print(f"Schema: {schema.name}")
print(f"Fields: {len(schema.fields)}")
for field_name, field_metadata in schema.fields.items():
    print(f"  {field_name}: {field_metadata.data_type.value}")
```

### Multi-table Analysis

```python
from petsard.metadater import Metadater
import pandas as pd

# Create multiple tables
tables = {
    'users': pd.DataFrame({
        'id': [1, 2, 3], 
        'name': ['Alice', 'Bob', 'Charlie']
    }),
    'orders': pd.DataFrame({
        'order_id': [101, 102], 
        'user_id': [1, 2]
    })
}

# Analyze dataset
metadata = Metadater.analyze_dataset(
    tables=tables,
    metadata_id="ecommerce"
)

print(f"Metadata: {metadata.metadata_id}")
print(f"Schemas: {len(metadata.schemas)}")
```

This redesigned Metadater provides a clear, composable, and easy-to-use metadata management solution while maintaining functional completeness and extensibility.