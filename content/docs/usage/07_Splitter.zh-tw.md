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

`Splitter` 模組可切分資料，用於進行實驗。開發動機是由於 `anonymeter` 類的 `Evaluator` 要求將資料分成兩部分：控制組與實驗組。但亦可用於其他實驗需求。

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

您可以依照需求自訂切分方法。

```Python
split = Splitter(
    num_samples=5,
    train_split_ratio=0.8,
    random_state=None
)
```

**參數**

`method` (`str`, default=`None`, optional): 支援讀取已存在的分割數據，僅接受 'custom_data'。

`num_samples` (`int`, default=`1`, optional): 產生的資料集數目。例如 `num_samples=5` 代表會產生 5 個切分資料集，每個資料集都包含控制組與實驗組的資料集。

`train_split_ratio` (`float`, default=`0.8`, optional): 實驗組資料集的資料佔比。因此控制組資料集的資料佔比為 1-`train_split_ratio`。

`random_state` (`int`, default=`None`, optional): 控制隨機切分過程，以便未來產生出相同切分結果的資料集。

## `split()`

```Python
split.split(
    data=load.data,
    metadata=load.metadata,
)
```

在並未將 `method` 設定為 `'custom_data'` 的情況下使用 `split()` 時，必須提供 `pd.DataFrame`。利用索引來進行拔靴法以生成多份資料集，並將資料集切分成訓練及驗證資料集。

**參數**

`data` (`pd.DataFrame`): 欲切分的資料集。

`exclude_index` (`List[int]`, optional): 在抽樣過程中欲排除的索引值。

`metadata` (`Metadata`, optional): 資料集的元資料。需注意的是這裡所需要的是 `Metadata` 類型本身，而非字典形式的 `Metadata.metadata`。可參閱 [Metadata 頁面](https://nics-tw.github.io/PETsARD/Metadata.html)

## `self.config`

`Splitter` 模組的參數：

- 在標準使用情況下，它包括 `num_samples`（樣本數量）、`train_split_ratio`（訓練集分割比例）與 `random_state`（隨機狀態）。
- 當 `method` 設為 `'custom_data'` 時，它包含 `method`（方法）、`filepath`（檔案路徑）以及其他 `Loader` 的配置。

## `self.data`

切分結果會以巢狀 `dict` 的形式存於 `self.data`。其結構如下：

```Python
{
    sample_num: {
        'train': train_df,
        'validation': validation_df
    }, ...
}
```

- 其中 `sample_num` 對應到初始化過程中的 `num_samples` 參數。例如當 `num_samples=5`，`self.data` 內會含有 5 個元素，其 `sample_num` 為 1 到 5。
  - 需要注意的是，`sample_num` 從 `1` 開始計數，以方便理解。
- 在每個元素中，其值皆為一個 `dict`，包含兩個鍵：`'train'`、`'validation'`，前者對應到實驗組資料集，後者對應到控制組資料集。其內部皆存放一個 `pd.DataFrame`，為切分後的資料集。
