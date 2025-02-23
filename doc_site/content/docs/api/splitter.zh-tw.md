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

用於實驗目的，將資料分割為訓練集和驗證集。設計用於支援如 Anonymeter 的隱私評估任務，多次分割可降低合成資料評估的偏誤。對於不平衡的資料集，建議使用較大的 `num_samples`。

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


# 基本用法
split = Splitter(num_samples=5, train_split_ratio=0.8)
split.split(data=df)
train_df = split.data[1]['train'] # 第一次分割的訓練集
```

## 方法

### `split()`

```python
split.split(data, exclude_index=None, metadata=None)
```

執行資料分割。

**參數**

- `data` (pd.DataFrame, optional)：要分割的資料集
  - 若 `method='custom_data'` 則不需提供
- `exclude_index` (list[int], optional)：要在抽樣時排除的索引列表
  - 預設值：無
- `metadata` (Metadata, optional)：資料集的 Metadata 物件
  - 預設值：無

**回傳值**

無

- 分割結果儲存於：
  - `Splitter.data`：包含所有分割結果的字典
  - `Splitter.metadata`：資料集詮釋資料
- 存取分割資料的方式：
  - `Splitter.data[sample_num]['train']`：特定樣本的訓練集
  - `Splitter.data[sample_num]['validation']`：特定樣本的驗證集

## 屬性

- `data`：分割資料集字典
  - 格式：`{sample_num: {'train': pd.DataFrame, 'validation': pd.DataFrame}}`
- `metadata`：資料集詮釋資料（Metadata 物件）
- `config`：設定字典，包含：
  - 若 `method=None`：
    - `num_samples` (int)：重複抽樣次數
    - `train_split_ratio` (float)：分割比例
    - `random_state` (int | float | str)：隨機種子
  - 若 `method='custom_data'`：
    - `method` (str)：載入方法
    - `filepath` (dict)：資料檔案路徑
    - 其他 Loader 設定