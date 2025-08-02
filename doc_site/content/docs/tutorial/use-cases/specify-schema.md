---
title: Specify Data Schema
type: docs
weight: 16
prev: docs/tutorial/use-cases
next: docs/tutorial/use-cases/data-description
---

When processing real-world data, we often encounter data quality issues: custom missing value markers (like '?' or 'unknown'), identifiers that need to preserve leading zeros, inconsistent numerical precision, etc. Traditional data loading methods rely on pandas' automatic type inference, but often make incorrect judgments when dealing with complex data.

The `schema` parameter in `Loader` allows you to precisely specify the data type, missing value definitions, and numerical precision for each field during the data loading phase, ensuring data quality is guaranteed from the source.

Click the button below to run the example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/tutorial/use-cases/specify-schema.ipynb)

```yaml
---
Loader:
  data:
    filepath: 'benchmark/adult-income.csv'
  data-w-schema:
    filepath: 'benchmark/adult-income.csv'
    schema:
      # Global parameters
      optimize_dtypes: true
      nullable_int: 'force'

      # Field parameters
      fields:
        # Numeric fields
        age:
          type: 'int'
        fnlwgt:
          type: 'int'
        # String fields
        gender:
          type: 'str'
          category_method: 'force'
        # Fields with custom missing values
        native-country:
          type: 'str'
          na_values: '?'
        workclass:
          type: 'str'
          na_values: '?'
        occupation:
          type: 'str'
          na_values: '?'
Describer:
  summary:
    method: 'default'
Reporter:
  save_report_columnwise:
    method: 'save_report'
    granularity: 'columnwise'
...
```

## Configuration Overview

### Two-Layer Architecture Design

The above YAML configuration adopts a two-layer architecture design, separating field definitions from global parameters:

**Field Definitions (`fields`)**:
- Each field explicitly specifies its logical type (`logical_type`)
- For example: `logical_type: 'string'` indicates this is a string type, `logical_type: 'category'` indicates categorical data
- Fields in `fields` can be arranged in any order, no need to correspond to the field order in the data table
- Only specify the fields you care about; unspecified fields will automatically undergo type inference

**Global Parameters**:
- Global control parameters can be set at the `schema` level, such as `compute_stats`, `optimize_dtypes`, etc.
- Global parameters affect the entire data loading and processing process
- Individual field parameters can override global settings

**Custom Missing Value Handling**:
- Missing value handling can be controlled through global or field-level parameters
- This is very useful for handling non-standard missing value markers in real-world data
- Can be set individually for each field, providing more precise missing value handling

## Global Parameters

### Processing Control Parameters

#### `optimize_dtypes` (bool, default: `true`)
Full-table memory optimization, automatically optimizes data types to save memory.

- `true`: Automatically converts int64 → int32, float64 → float32, etc.
- `false`: Maintains original types

#### `sample_size` (int, default: `null`)
Sample size for type inference.

- `null`: Uses all data
- Positive integer: Uses specified sample count (validates not exceeding actual data count)

### Inference Control Parameters

#### `infer_logical_types` (bool, default: `false`)
Full-table logical type inference, will override individual field `logical_type` settings.

⚠️ **Note**: Will error if used simultaneously with individual field `logical_type` settings.

#### `leading_zeros` (str, default: `"never"`)
Leading character handling method:

- `"never"`: Don't handle leading characters
- `"num-auto"`: Convert to string to preserve when numeric types have leading characters
- `"leading_n"`: Pad to specified digits (e.g., `"leading_5"` pads to 5 digits)

⚠️ **Important**: This setting treats all non-numeric fields as `str`, so `datetime` related fields will be treated as strings.

#### `nullable_int` (str, default: `"force"`)
Integer NULL handling method:

- `"force"`: Automatically converts int type to NULL-supporting Int64
- `"never"`: Automatically converts to float when encountering NULL

### Descriptive Parameters

- **`schema_id`** (str): Schema unique identifier
- **`name`** (str): Schema human-readable name
- **`description`** (str): Schema description

## Field-Level Parameters

### `logical_type` (str, default: `"never"`)
Individual field logical type inference:

- `"never"`: Don't infer logical type
- `"infer"`: Automatically infer logical type
- Specified type: Such as `"email"`, `"phone"`, `"url"`, etc.

```yaml
schema:
  fields:
    email:
      type: 'str'
      logical_type: 'email'
    phone:
      type: 'str'
      logical_type: 'phone'
```

### `leading_zeros` (Field Level)
Individual fields can override global `leading_zeros` setting:

```yaml
schema:
  leading_zeros: "never"  # Global setting
  fields:
    user_id:
      type: 'int'
      leading_zeros: "leading_8"  # Override global setting, pad to 8 digits
```

## Schema Five Core Functions

### 1. Type Control (`type`)
Precisely specify the basic data type for each field, avoiding pandas automatic inference errors:

- `'int'`: Integer type
- `'float'`: Floating-point type
- `'str'`: String type
- `'bool'`: Boolean type
- `'datetime'`: Date-time type

**Semantic Type (`logical_type`)**:
Used to specify the semantic meaning of fields, such as:
- `'email'`: Email address
- `'phone'`: Phone number
- `'url'`: URL
- `'infer'`: Automatically infer semantic type

### 2. Memory Optimization (`category_method`)
Intelligently determine whether to convert fields to categorical type to save memory:

- `str-auto` (default): Only use ASPL judgment for string type fields
- `auto`: Use ASPL judgment for all type fields
- `force`: Force conversion to categorical type
- `never`: Never convert to categorical type

**ASPL Judgment Mechanism**: When `ASPL = Sample Count / Unique Value Count ≥ 100`, convert to categorical type.

### 3. Numerical Precision Control (`precision`)
Control the decimal places of floating-point numbers to ensure consistent numerical format:

- Only applies to `float` type: `precision: 2`
- **Note**: Using `precision` with `int` type will cause an error

### 4. Categorical Variable Optimization
Intelligent classification judgment based on Zhu et al. (2024) research:

- **Theoretical Basis**: Ensures each category has sufficient sample count to support effective encoding
- **Avoids Problems**: Prevents performance issues caused by sparse categories
- **Memory Benefits**: Can save 50-90% memory usage

### 5. Date Type Reading
Supports flexible date-time handling:

#### Date Precision Control (`datetime_precision`)
- `s` (default): Second-level precision
- `ms`: Millisecond-level precision
- `us`: Microsecond-level precision
- `ns`: Nanosecond-level precision

#### Date Format Parsing (`datetime_format`)
- `auto` (default): Automatically detect format
- Custom format: Use Python strftime format strings

**Common Date Formats Supported by Python**:
- `%Y-%m-%d`: 2024-01-15
- `%Y/%m/%d`: 2024/01/15
- `%d/%m/%Y`: 15/01/2024
- `%Y-%m-%d %H:%M:%S`: 2024-01-15 14:30:00
- `%Y-%m-%dT%H:%M:%S`: 2024-01-15T14:30:00 (ISO 8601)

### Missing Value Definition (`na_values`)
Supports custom missing value markers for various data types:

- Single value: `na_values: '?'`
- Multiple values:
  ```yaml
  na_values:
    - '?'
    - 'unknown'
    - 'N/A'
  ```
- Define individually for each field, providing precise missing value handling

## Storage Advantages and Usage Scenarios for Categorical Types

### Storage Advantages

**Memory Efficiency**:
- Categorical type stores repeated string values only once, using integer indices for reference
- For fields with many repeated values, can save 50-90% memory usage
- Example: 10 million records with only 10 different region names

**Computational Efficiency**:
- Grouping operations (groupby) and comparison operations are faster
- Sorting operations can be optimized using categorical order
- String comparisons converted to integer comparisons

### When to Use Categorical Types

**Recommended Usage**:
- String fields with many repeated values (such as gender, region, status)
- Ordered categorical data (such as ratings: low, medium, high)
- Integer-encoded categorical data (such as status codes: 1, 2, 3)
- Fields where unique value count is much smaller than total data volume

**Not Recommended Usage**:
- Fields with many unique values (such as user ID, transaction ID)
- Fields requiring frequent string operations
- Fields with frequent numerical calculations
- Temporary or one-time analysis data

### Design Philosophy

Our design treats categorical processing as a storage optimization strategy, not a basic data type:
- `type: 'string', category_method: force` clearly expresses "force convert string type to categorical data"
- `type: 'int', category_method: force` expresses "force convert integer type to categorical data"
- `category_method: str-auto` by default only performs intelligent judgment on string types, avoiding unnecessary conversions
- Conceptually similar to Pandas' `category[dtype]` but provides more fine-grained control

## Practical Effects

After using the new `schema` parameter, you will get:

1. **Precise Type Control**: Avoid pandas automatic inference errors
2. **Unified Missing Value Handling**: Correctly identify custom markers like `'?'` as missing values
3. **Consistent Numerical Format**: Unify numerical precision through `precision` parameter
4. **Intelligent Memory Optimization**: Selectively optimize storage through `category_method`
5. **Reproducible Data Processing**: Clear schema definitions ensure consistent loading results every time
6. **Clear Conceptual Separation**: Data types and storage optimization are separated for clearer concepts

By precisely specifying the data table schema, you can ensure data meets expected formats from the loading stage, laying a solid foundation for subsequent preprocessing, synthesis, and evaluation. The new two-layer architecture design makes concepts clearer and usage more flexible.

## References

Zhu, W., Qiu, R., & Fu, Y. (2024). Comparative study on the performance of categorical variable encoders in classification and regression tasks. *arXiv preprint arXiv:2401.09682*. https://arxiv.org/abs/2401.09682