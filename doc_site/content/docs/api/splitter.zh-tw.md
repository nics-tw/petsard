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

用於實驗目的，使用函數式程式設計模式將資料分割為訓練集和驗證集。設計用於支援如 Anonymeter 的隱私評估任務，多次分割可降低合成資料評估的偏誤。對於不平衡的資料集，建議使用較大的 `num_samples`。

此模組採用函數式方法，使用純函數和不可變資料結構，回傳 `(split_data, metadata_dict, train_indices)` 元組以與其他 PETsARD 模組保持一致性。增強的重疊控制功能允許精確管理樣本重疊比率，防止產生相同樣本並控制多次分割間的訓練資料重複使用。

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
- `max_overlap_ratio` (float, optional)：樣本間允許的最大重疊比率
  - 預設值：1.0（100% - 允許完全重疊）
  - 必須介於 0 和 1 之間
  - 設為 0.0 表示樣本間無重疊
- `max_attempts` (int, optional)：抽樣的最大嘗試次數
  - 預設值：30
  - 當重疊控制啟用時使用

## 範例

```python
from petsard import Splitter

# 使用函數式 API 的基本用法
splitter = Splitter(num_samples=5, train_split_ratio=0.8)
split_data, metadata_dict, train_indices = splitter.split(data=df)

# 存取分割結果
train_df = split_data[1]['train']  # 第一次分割的訓練集
val_df = split_data[1]['validation']  # 第一次分割的驗證集
train_metadata = metadata_dict[1]['train']  # 訓練集元資料
train_idx_set = train_indices[0]  # 第一個樣本的訓練索引

# 重疊控制 - 嚴格模式（最大 10% 重疊）
strict_splitter = Splitter(
    num_samples=3,
    train_split_ratio=0.7,
    max_overlap_ratio=0.1,  # 最大 10% 重疊
    max_attempts=30
)
split_data, metadata_dict, train_indices = strict_splitter.split(data=df)

# 避免與現有樣本重疊
existing_indices = [set(range(0, 10)), set(range(15, 25))]
new_split_data, new_metadata, new_indices = splitter.split(
    data=df,
    exist_train_indices=existing_indices
)

# 函數式程式設計方法
def create_non_overlapping_splits(data, num_samples=3):
    """建立具有控制重疊的分割"""
    splitter = Splitter(
        num_samples=num_samples,
        max_overlap_ratio=0.2,  # 最大 20% 重疊
        random_state=42
    )
    return splitter.split(data=data)

# 使用函數
splits, metadata, indices = create_non_overlapping_splits(df)
```

## 方法

### `split()`

```python
split_data, metadata_dict, train_indices = splitter.split(
    data=None,
    exist_train_indices=None
)
```

使用函數式程式設計模式執行資料分割，具備增強的重疊控制功能。

**參數**

- `data` (pd.DataFrame, optional)：要分割的資料集
  - 若 `method='custom_data'` 則不需提供
- `exist_train_indices` (list[set], optional)：要避免重疊的現有訓練索引集合列表
  - 預設值：無
  - 每個集合包含來自先前分割的訓練索引

**回傳值**

- `split_data` (dict)：包含所有分割結果的字典
  - 格式：`{sample_num: {'train': pd.DataFrame, 'validation': pd.DataFrame}}`
- `metadata_dict` (dict)：包含每個分割的詮釋資料字典
  - 格式：`{sample_num: {'train': SchemaMetadata, 'validation': SchemaMetadata}}`
- `train_indices` (list[set])：每個樣本的訓練索引集合列表
  - 格式：`[{indices_set1}, {indices_set2}, ...]`

**範例**

```python
# 基本分割
splitter = Splitter(num_samples=3, train_split_ratio=0.8)
split_data, metadata_dict, train_indices = splitter.split(data=df)

# 存取分割資料
train_df = split_data[1]['train']  # 第一次分割的訓練集
val_df = split_data[1]['validation']  # 第一次分割的驗證集
train_meta = metadata_dict[1]['train']  # 訓練詮釋資料
train_idx = train_indices[0]  # 第一個樣本的訓練索引

# 避免與現有樣本重疊
existing_samples = [{0, 1, 2, 5}, {10, 11, 15, 20}]
new_data, new_meta, new_indices = splitter.split(
    data=df,
    exist_train_indices=existing_samples
)
```

## 屬性

- `config`：設定字典，包含：
  - 若 `method=None`：
    - `num_samples` (int)：重複抽樣次數
    - `train_split_ratio` (float)：分割比例
    - `random_state` (int | float | str)：隨機種子
    - `max_overlap_ratio` (float)：最大重疊比率
    - `max_attempts` (int)：最大抽樣嘗試次數
  - 若 `method='custom_data'`：
    - `method` (str)：載入方法
    - `filepath` (dict)：資料檔案路徑
    - 其他 Loader 設定

## 重疊控制功能

### 拔靴法抽樣與重疊管理

Splitter 使用拔靴法（bootstrap sampling）生成多個訓練/驗證分割，同時控制樣本間的重疊：

1. **完全一致檢查**：防止產生相同的樣本
2. **重疊比率控制**：限制樣本間重疊索引的百分比
3. **可配置嘗試次數**：允許在約束條件內多次嘗試尋找有效樣本

### 使用場景

- **隱私評估**：多個非重疊分割用於穩健的 Anonymeter 評估
- **交叉驗證**：控制重疊進行統計驗證
- **偏誤降低**：多個有限重疊的樣本以降低評估偏誤

### 最佳實務

- 使用 `max_overlap_ratio=0.0` 產生完全無重疊的樣本
- 使用 `max_overlap_ratio=0.2` 進行適度重疊控制（最大 20%）
- 對於更嚴格的重疊要求，增加 `max_attempts`
- 使用 `exist_train_indices` 避免與先前產生的樣本重疊

**注意**：函數式 API 直接從 `split()` 方法回傳 `(split_data, metadata_dict, train_indices)` 元組，而非將其儲存為實例屬性。此方法遵循函數式程式設計原則，使用不可變資料結構並支援純函數組合。