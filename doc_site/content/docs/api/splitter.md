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

For experimental purposes, splits data into training and validation sets. Designed to support privacy evaluation tasks like Anonymeter, where multiple splits can reduce bias in synthetic data assessment. For imbalanced datasets, larger `num_samples` is recommended.

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


# Basic usage
split = Splitter(num_samples=5, train_split_ratio=0.8)
split.split(data=df)
train_df = split.data[1]['train'] # first split's training set
```

## Methods

### `split()`

```python
split.split(data, exclude_index=None, metadata=None)
```

Perform data splitting.

**Parameters**

- `data` (pd.DataFrame, optional): Dataset to be split
  - Not required if `method='custom_data'`
- `exclude_index` (list[int], optional): List of indices to exclude from sampling
  - Default: None
- `metadata` (Metadata, optional): Metadata object of the dataset
  - Default: None

**Returns**

None.

- Split results are stored in:
  - `Splitter.data`: Dictionary containing all split results
  - `Splitter.metadata`: Dataset metadata
- Access split data via:
  - `Splitter.data[sample_num]['train']`: Training set for specific sample
  - `Splitter.data[sample_num]['validation']`: Validation set for specific sample

## Attributes

- `data`: Split datasets dictionary
  - Format: `{sample_num: {'train': pd.DataFrame, 'validation': pd.DataFrame}}`
- `metadata`: Dataset metadata (Metadata object)
- `config`: Configuration dictionary containing:
  - If `method=None`:
    - `num_samples` (int): Resample times
    - `train_split_ratio` (float): Split ratio
    - `random_state` (int | float | str): Random seed
  - If `method='custom_data'`:
    - `method` (str): Loading method
    - `filepath` (dict): Data file paths
    - Additional Loader configurations