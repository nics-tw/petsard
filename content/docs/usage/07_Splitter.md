---
title: "Splitter"
# description: "Guides lead a user through a specific task they want to accomplish, often with a sequence of steps."
# summary: ""
date: 2023-09-07T16:04:48+02:00
lastmod: 2023-09-07T16:04:48+02:00
draft: false
weight: 18
toc: true
---

The `Splitter` module is responsible for splitting data for experimental purpose. This module is for `anonymeter` type `Evaluator`, which requires splitting the data into two parts: control and experiment datasets. However, it can be used for other experimental requirements as well.

```Python
from PETsARD import Splitter


split = Splitter(
    num_samples=5,
    train_split_ratio=0.8
)
split.split(data=load.data, metadata=load.metadata)
print(split.data[1]['train'].head(1))
print(split.data[1]['validation'].head(1))
```

# `Splitter`

You can set different split methods as your requirements.

```Python
split = Splitter(
    num_samples=5,
    train_split_ratio=0.8,
    random_state=None
)
```

**Parameters**

`method` (`str`, default=`None`, optional): Supports loading existing split data, only accepting 'custom_data'.

`num_samples` (`int`, default=`1`, optional): Number of datasets will be generated. For example, if `num_samples=5`, there are 5 split datasets, and each of them contain control and experiment datasets.

`train_split_ratio` (`float`, default=`0.8`, optional): The proportion of the dataset to include in the experiment dataset. Hence, the proportion of the dataset to include in the control dataset is 1-`train_split_ratio`.

`random_state` (`int`, default=`None`, optional): Controls the random sampling for reproducible output.

## `split()`

```Python
split.split(
    data=load.data,
    metadata=load.metadata,
)
```

When using `split()` without setting `method` to `'custom_data'`, it is required to provide a `pd.DataFrame`. Perform index bootstrapping and split the data into train and validation sets using the generated index samples.

**Parameters**

`data` (`pd.DataFrame`): The data to be split.

`exclude_index` (`List[int]`, optional): The exist indeces to be excluded during the sampling process.

`metadata` (`Metadata`, optional): The metadata of data. Note that the requirement is for the `Metadata` type itself, not `Metadata.metadata` as a dictionary. See the [Metadata page](https://nics-tw.github.io/PETsARD/Metadata.html) for more information.

## `self.config`

The configuration of `Splitter` module:

- For standard usage, it contains `num_samples`, `train_split_ratio`, `random_state`.
- When the `method` is set to `'custom_data'`, it encompasses `method`, `filepath`, and the configuration of `Loader`.

## `self.data`

The split results are stored in `self.data` in the form of nested `dict`. The structure is shown below:

```Python
{
    sample_num: {
        'train': train_df,
        'validation': validation_df
    }, ...
}
```

- The key `sample_num` corresponds to the parameter `num_samples` during initialisation. For instance, if `num_samples=5`, the `self.data` will contain 5 elements with `sample_num` from `1` to `5`.
  - Noted that `sample_num` starts from `1` for clarity and ease of understanding.
- Within each element, the value is a `dict` with two keys: `'train'` and `'validation'`, representing the experiment and control datasets, respectively. Each of these keys corresponds to a `pd.DataFrame`, which is the split data.
