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

合成資料產生器。支援多種合成方法並提供資料生成功能。

## 參數

- `method` (str)：合成方法
  - 'default'：使用 SDV-GaussianCopula
  - 'custom_data'：從檔案載入自定義資料
  - 'sdv-single_table-{method}'：使用 SDV 提供的方法
    - copulagan：CopulaGAN 生成模型
    - ctgan：CTGAN 生成模型
    - gaussiancopula：高斯耦合模型
    - tvae：TVAE 生成模型

## 範例

```python
from petsard import Synthesizer


# 使用 SDV 的 GaussianCopula
syn = Synthesizer(method='sdv-single_table-gaussiancopula')

# 使用預設方法
syn = Synthesizer(method='default')

# 合成
syn.create(metadata=metadata)
syn.fit_sample(data=df)
synthetic_data = syn.data_syn
```

## 方法

### `create()`

```python
syn.create(metadata)
```

建立合成器。

**參數**

- `metadata` (Metadata, optional)：資料集的 Metadata 物件

**回傳值**

無。初始化合成器物件

### `fit()`

```python
syn.fit(data=data)
```

訓練合成模型。

**參數**

- `data` (pd.DataFrame)：用於訓練的資料集

**回傳值**

無。更新合成器的內部狀態

### `sample()`

```python
syn.sample(
    sample_num_rows=None,
    reset_sampling=False,
    output_file_path=None
)
```

訓練合成模型。

**參數**

- `sample_num_rows` (int, optional)：要生成的資料列數
  - 預設值：無（使用原始資料列數）
- `reset_sampling` (bool, optional)：是否重置採樣狀態
  - 預設值：False
- `output_file_path` (str, optional): Output file path
  - 預設值：無

**回傳值**

無。生成的資料儲存於 `data_syn` 屬性

### `fit_sample()`

```python
syn.fit_sample(data, **kwargs)
```

Perform training and generation in sequence. Combines functionality of `fit()` and `sample()`.

**參數**

與 `sample()` 相同

**回傳值**

無。生成的資料儲存於 `data_syn` 屬性

## 屬性

- `data_syn`：生成的合成資料 (pd.DataFrame)
- `config`：設定字典，包含：
  - `method` (str)：合成方法名稱
  - `method_code` (int)：方法類型代碼
  - 各方法特定的其他參數
- `synthesizer`：實例化的合成器物件（用於 SDV 方法）
- `loader`：載入器物件（僅用於 'custom_data' 方法）