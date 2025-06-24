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
    random_state=None
)
```

用於實驗目的，使用函數式程式設計模式將資料分割為訓練集和驗證集。設計用於支援如 Anonymeter 的隱私評估任務，多次分割可降低合成資料評估的偏誤。對於不平衡的資料集，建議使用較大的 `num_samples`。

此模組採用函數式方法，使用純函數和不可變資料結構，回傳 `(data, metadata)` 元組以與其他 PETsARD 模組保持一致性。

## 參數

- `method` (str, optional)：載入已分割資料的方法
  - 預設值：無
  - 可用值：'custom_data' - 從檔案路徑載入分割資料
- `num_samples` (int, optional)：重複抽樣次數
  - 預設值：1
- `train_split_ratio` (float, optional)：訓練集的資料比例
  - 預設值：0.8
  - 必須介於 0 和 1 之間
- `random_state` (int | float | str, optional)：用於重現結果的隨機種子
  - 預設值：無

## 範例

```python
from petsard import Splitter


# 使用函數式 API 的基本用法
splitter = Splitter(num_samples=5, train_split_ratio=0.8)
split_data, split_metadata = splitter.split(data=df, metadata=metadata)

# 存取分割結果
train_df = split_data[1]['train']  # 第一次分割的訓練集
val_df = split_data[1]['validation']  # 第一次分割的驗證集

# 多次抽樣以降低偏誤
for sample_num in range(1, 6):  # 5 次抽樣
    train_set = split_data[sample_num]['train']
    val_set = split_data[sample_num]['validation']
    # 用於隱私評估...
```

## 方法

### `split()`

```python
data, metadata = split.split(data, exclude_index=None, metadata=None)
```

使用函數式程式設計模式執行資料分割。

**參數**

- `data` (pd.DataFrame, optional)：要分割的資料集
  - 若 `method='custom_data'` 則不需提供
- `exclude_index` (list[int], optional)：要在抽樣時排除的索引列表
  - 預設值：無
- `metadata` (SchemaMetadata, optional)：資料集的架構詮釋資料物件
  - 預設值：無

**回傳值**

- `data` (dict)：包含所有分割結果的字典
  - 格式：`{sample_num: {'train': pd.DataFrame, 'validation': pd.DataFrame}}`
- `metadata` (SchemaMetadata)：更新後包含分割資訊的架構詮釋資料

```python
splitter = Splitter(num_samples=3, train_split_ratio=0.8)
split_data, split_metadata = splitter.split(data=df, metadata=metadata)

# 存取分割資料
train_df = split_data[1]['train']  # 第一次分割的訓練集
val_df = split_data[1]['validation']  # 第一次分割的驗證集
```

## 屬性

- `config`：設定字典，包含：
  - 若 `method=None`：
    - `num_samples` (int)：重複抽樣次數
    - `train_split_ratio` (float)：分割比例
    - `random_state` (int | float | str)：隨機種子
  - 若 `method='custom_data'`：
    - `method` (str)：載入方法
    - `filepath` (dict)：資料檔案路徑
    - 其他 Loader 設定

**注意**：新的函數式 API 直接從 `split()` 方法回傳資料和詮釋資料，而非將其儲存為實例屬性。此方法遵循函數式程式設計原則，使用不可變資料結構。