---
title: Synthesizer
type: docs
weight: 56
prev: docs/api/processor
next: docs/api/constrainer
---


```python
Synthesizer(
    method,
    **kwargs
)
```

Synthetic data generator supporting multiple synthesis methods.

## Parameters

- `method` (str): Synthesis method
  - 'default': Use SDV-GaussianCopula
  - 'custom_data': Load custom data from file
  - 'sdv-single_table-{method}': Use SDV provided methods
    - copulagan: CopulaGAN generative model
    - ctgan: CTGAN generative model
    - gaussiancopula: Gaussian Copula model
    - tvae: TVAE generative model

## Examples

```python
from petsard import Synthesizer


# Using SDV's GaussianCopula
syn = Synthesizer(method='sdv-single_table-gaussiancopula')

# Using default method
syn = Synthesizer(method='default')

# Synthesizng
syn.create(metadata=metadata)
syn.fit_sample(data=df)
synthetic_data = syn.data_syn
```

## Methods

### `create()`

```python
syn.create(data, metadata=None)
```

Initialize synthesizer.

**Parameters**

- `metadata` (Metadata, optional): Dataset's Metadata object
  - Default: None

**Returns**

None. Initializes the synthesizer object

### `fit()`

Train synthesis model.

```python
syn.fit(data=data)
```

**Parameters**

- `data` (pd.DataFrame): Training dataset

**Returns**

None. Updates synthesizer's internal state

### `sample()`

```python
syn.sample(
    sample_num_rows=None,
    reset_sampling=False,
    output_file_path=None
)
```

Generate synthetic data.

**Parameters**

- `sample_num_rows` (int, optional): Number of rows to generate
  - Default: None (use original data row count)
- `reset_sampling` (bool, optional): Whether to reset sampling state
  - Default: False
- `output_file_path` (str, optional): Output file path
  - Default: None

**Returns**

None. Generated data is stored in `data_syn` attribute

### `fit_sample()`

```python
syn.fit_sample(data, **kwargs)
```

依序執行訓練與生成。整合 `fit()` 和 `sample()` 的功能。

**Parameters**

Same as `sample()`

**Returns**

None. Generated data is stored in `data_syn` attribute

## Attributes

- `data_syn`: Generated synthetic data (pd.DataFrame)
- `config`: Configuration dictionary containing:
  - `method` (str): Synthesis method name
  - `method_code` (int): Method type code
  - Additional parameters specific to each method
- `synthesizer`: Instantiated synthesizer object (for SDV methods)
- `loader`: Loader object (for 'custom_data' method only)