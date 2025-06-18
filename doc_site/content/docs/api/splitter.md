---
title: Splitter
type: docs
weight: 53
prev: docs/api/loader
next: docs/api/processor
---


```python
Splitter(
    method=None,
    num_samples=1,
    train_split_ratio=0.8,
    random_state=None
)
```

For experimental purposes, splits data into training and validation sets using functional programming patterns. Designed to support privacy evaluation tasks like Anonymeter, where multiple splits can reduce bias in synthetic data assessment. For imbalanced datasets, larger `num_samples` is recommended.

The module uses a functional approach with pure functions and immutable data structures, returning `(data, metadata)` tuples for consistency with other PETsARD modules.

## Parameters

- `method` (str, optional): Loading method for existing split data
  - Default: None
  - Values: 'custom_data' - load split data from filepath
- `num_samples` (int, optional): Number of times to resample the data
  - Default: 1
- `train_split_ratio` (float, optional): Ratio of data for training set
  - Default: 0.8
  - Must be between 0 and 1
- `random_state` (int | float | str, optional): Seed for reproducibility
  - Default: None

## Examples

```python
from petsard import Splitter


# Basic usage with functional API
splitter = Splitter(num_samples=5, train_split_ratio=0.8)
split_data, split_metadata = splitter.split(data=df, metadata=metadata)

# Access split results
train_df = split_data[1]['train']  # First split's training set
val_df = split_data[1]['validation']  # First split's validation set

# Multiple samples for bias reduction
for sample_num in range(1, 6):  # 5 samples
    train_set = split_data[sample_num]['train']
    val_set = split_data[sample_num]['validation']
    # Use for privacy evaluation...
```

## Methods

### `split()`

```python
data, metadata = split.split(data, exclude_index=None, metadata=None)
```

Perform data splitting using functional programming patterns.

**Parameters**

- `data` (pd.DataFrame, optional): Dataset to be split
  - Not required if `method='custom_data'`
- `exclude_index` (list[int], optional): List of indices to exclude from sampling
  - Default: None
- `metadata` (SchemaMetadata, optional): Schema metadata object of the dataset
  - Default: None

**Returns**

- `data` (dict): Dictionary containing all split results
  - Format: `{sample_num: {'train': pd.DataFrame, 'validation': pd.DataFrame}}`
- `metadata` (SchemaMetadata): Updated schema metadata with split information

```python
splitter = Splitter(num_samples=3, train_split_ratio=0.8)
split_data, split_metadata = splitter.split(data=df, metadata=metadata)

# Access split data
train_df = split_data[1]['train']  # First split's training set
val_df = split_data[1]['validation']  # First split's validation set
```

## Attributes

- `config`: Configuration dictionary containing:
  - If `method=None`:
    - `num_samples` (int): Resample times
    - `train_split_ratio` (float): Split ratio
    - `random_state` (int | float | str): Random seed
  - If `method='custom_data'`:
    - `method` (str): Loading method
    - `filepath` (dict): Data file paths
    - Additional Loader configurations

**Note**: The new functional API returns data and metadata directly from the `split()` method rather than storing them as instance attributes. This approach follows functional programming principles with immutable data structures.