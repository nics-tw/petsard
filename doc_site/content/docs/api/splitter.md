---
title: Splitter
type: docs
weight: 54
prev: docs/api/metadater
next: docs/api/processor
---


```python
Splitter(
    method=None,
    num_samples=1,
    train_split_ratio=0.8,
    random_state=None,
    max_overlap_ratio=1.0,
    max_attempts=30
)
```

For experimental purposes, splits data into training and validation sets using functional programming patterns. Designed to support privacy evaluation tasks like Anonymeter, where multiple splits can reduce bias in synthetic data assessment. For imbalanced datasets, larger `num_samples` is recommended.

The module uses a functional approach with pure functions and immutable data structures, returning `(split_data, metadata_dict, train_indices)` tuples for consistency with other PETsARD modules. Enhanced overlap control functionality allows precise management of sample overlap ratios, preventing identical samples and controlling training data reuse across multiple splits.

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
- `max_overlap_ratio` (float, optional): Maximum allowed overlap ratio between samples
  - Default: 1.0 (100% - allows complete overlap)
  - Must be between 0 and 1
  - Set to 0.0 for no overlap between samples
- `max_attempts` (int, optional): Maximum number of attempts for sampling
  - Default: 30
  - Used when overlap control is active

## Examples

```python
from petsard import Splitter

# Basic usage with functional API
splitter = Splitter(num_samples=5, train_split_ratio=0.8)
split_data, metadata_dict, train_indices = splitter.split(data=df)

# Access split results
train_df = split_data[1]['train']  # First split's training set
val_df = split_data[1]['validation']  # First split's validation set
train_metadata = metadata_dict[1]['train']  # Training set metadata
train_idx_set = train_indices[0]  # First sample's training indices

# Overlap control - strict mode (max 10% overlap)
strict_splitter = Splitter(
    num_samples=3,
    train_split_ratio=0.7,
    max_overlap_ratio=0.1,  # Maximum 10% overlap
    max_attempts=30
)
split_data, metadata_dict, train_indices = strict_splitter.split(data=df)

# Avoid overlap with existing samples
existing_indices = [set(range(0, 10)), set(range(15, 25))]
new_split_data, new_metadata, new_indices = splitter.split(
    data=df,
    exist_train_indices=existing_indices
)

# Functional programming approach
def create_non_overlapping_splits(data, num_samples=3):
    """Create splits with controlled overlap"""
    splitter = Splitter(
        num_samples=num_samples,
        max_overlap_ratio=0.2,  # Max 20% overlap
        random_state=42
    )
    return splitter.split(data=data)

# Use the function
splits, metadata, indices = create_non_overlapping_splits(df)
```

## Methods

### `split()`

```python
split_data, metadata_dict, train_indices = splitter.split(
    data=None,
    exist_train_indices=None
)
```

Perform data splitting using functional programming patterns with enhanced overlap control.

**Parameters**

- `data` (pd.DataFrame, optional): Dataset to be split
  - Not required if `method='custom_data'`
- `exist_train_indices` (list[set], optional): List of existing training index sets to avoid overlap with
  - Default: None
  - Each set contains training indices from previous splits

**Returns**

- `split_data` (dict): Dictionary containing all split results
  - Format: `{sample_num: {'train': pd.DataFrame, 'validation': pd.DataFrame}}`
- `metadata_dict` (dict): Dictionary containing metadata for each split
  - Format: `{sample_num: {'train': SchemaMetadata, 'validation': SchemaMetadata}}`
- `train_indices` (list[set]): List of training index sets for each sample
  - Format: `[{indices_set1}, {indices_set2}, ...]`

**Examples**

```python
# Basic splitting
splitter = Splitter(num_samples=3, train_split_ratio=0.8)
split_data, metadata_dict, train_indices = splitter.split(data=df)

# Access split data
train_df = split_data[1]['train']  # First split's training set
val_df = split_data[1]['validation']  # First split's validation set
train_meta = metadata_dict[1]['train']  # Training metadata
train_idx = train_indices[0]  # First sample's training indices

# Avoid overlap with existing samples
existing_samples = [{0, 1, 2, 5}, {10, 11, 15, 20}]
new_data, new_meta, new_indices = splitter.split(
    data=df,
    exist_train_indices=existing_samples
)
```

## Attributes

- `config`: Configuration dictionary containing:
  - If `method=None`:
    - `num_samples` (int): Resample times
    - `train_split_ratio` (float): Split ratio
    - `random_state` (int | float | str): Random seed
    - `max_overlap_ratio` (float): Maximum overlap ratio
    - `max_attempts` (int): Maximum sampling attempts
  - If `method='custom_data'`:
    - `method` (str): Loading method
    - `filepath` (dict): Data file paths
    - Additional Loader configurations

## Overlap Control Features

### Bootstrap Sampling with Overlap Management

The Splitter uses bootstrap sampling (拔靴法) to generate multiple training/validation splits while controlling overlap between samples:

1. **Complete Identity Check**: Prevents generating identical samples
2. **Overlap Ratio Control**: Limits the percentage of overlapping indices between samples
3. **Configurable Attempts**: Allows multiple attempts to find valid samples within constraints

### Use Cases

- **Privacy Evaluation**: Multiple non-overlapping splits for robust Anonymeter assessment
- **Cross-Validation**: Controlled overlap for statistical validation
- **Bias Reduction**: Multiple samples with limited overlap to reduce evaluation bias

### Best Practices

- Use `max_overlap_ratio=0.0` for completely non-overlapping samples
- Use `max_overlap_ratio=0.2` for moderate overlap control (20% maximum)
- Increase `max_attempts` for stricter overlap requirements
- Use `exist_train_indices` to avoid overlap with previously generated samples

**Note**: The functional API returns `(split_data, metadata_dict, train_indices)` tuples directly from the `split()` method rather than storing them as instance attributes. This approach follows functional programming principles with immutable data structures and enables pure function composition.