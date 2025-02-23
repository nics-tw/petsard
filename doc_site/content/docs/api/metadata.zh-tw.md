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

記錄資料集特性，包含資料型態、缺失值比例及資料集維度。提供型態推斷和 SDV 詮釋資料轉換功能。

## 參數

無

## 範例

```python
from petsard import Metadata


# 建立與產生詮釋資料
meta = Metadata()
meta.build_metadata(df)

# 存取詮釋資料
col_properties = meta.metadata['col']
dataset_properties = meta.metadata['global']

# 轉換為 SDV 格式
sdv_meta = meta.to_sdv()
```

## 方法

### `build_metadata()`

```python
meta.build_metadata(data)
```

從 DataFrame 建立詮釋資料並推斷資料型態。

**參數**

- `data` (pd.DataFrame)：輸入的 DataFrame

**回傳值**

無。更新 `metadata` 屬性

### `set_col_infer_dtype()`

```python
meta.set_col_infer_dtype(col, dtype)
```

設定特定欄位的推斷資料型態。

**參數**

- `col` (str)：欄位名稱
- `dtype` (str)：推斷的資料型態
  - 可用值：'numerical'、'categorical'、'datetime'、'object'

**回傳值**

無。更新欄位的 infer_dtype

### `to_sdv()`

將詮釋資料轉換為 SDV 相容格式。

**參數**

無。

**回傳值**

- dict：SDV 格式的詮釋資料

## 屬性

- `metadata`：巢狀字典，包含資料集特性：
  - `col`：各欄位特性
    - `dtype`：pandas 資料型態
    - `na_percentage`：NA 值比例
    - `infer_dtype`：推斷的資料型態（'numerical'、'categorical'、'datetime' 或 'object'）
  - `global`：整體資料集特性
    - `row_num`：資料列數
    - `col_num`：欄位數
    - `na_percentage`：整體 NA 值比例

