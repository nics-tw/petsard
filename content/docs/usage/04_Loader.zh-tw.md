---
title: "Loader"
draft: false
weight: 15
toc: true
---

`Loader` 模組將資料寫入記憶體，供後續使用。

```python
from PETsARD import Loader


load = Loader('data.csv')
load.load()
```

# `Loader`

只要提供檔案路徑即可初始化 `Loader`。您也可以加入其他參數以達到客製化的目的。

```Python
from PETsARD import Loader


load = Loader(
    filepath='benchmark/adult-income.csv',
    method=None,
    column_types={
        'category': [
            'workclass',
            'education',
            'marital-status',
            'occupation',
            'relationship',
            'race',
            'gender',
            'native-country',
            'income',
        ],
        'datetime': [],
    },
    header_names=None,
    na_values={
        'workclass': '?',
        'occupation': '?',
        'native-country': '?',
    }
)
load.load()
print(load.data.head(1))
```

**參數**

`filepath` (`str`, default=`None`, optional): 資料集完整路徑。

`method` (`str`, default=`None`, optional): `Loader` 的方法。`Loader` 唯一的方法為 'default'，此時不用輸入 `filepath`，`Loader` 將會讀取 `PETsARD` 預設的資料集 'adult-income'。有給定 `filepath` 時不用設定。

`column_types` (`dict`, default=`None`, optional): 指定欄位類型及其對應欄位名稱的字典，格式為 `{type: [colname]}`。只支援以下類型（不區分大小寫）：

- 'category': 欄位將被視為類別型。
- 'datetime': 欄位將被視為日期時間型。

`header_names` (`list`, default=`None`, optional): 為沒有標題的數據指定一個標題列表。

`na_values` (`str | list | dict`, default=`None`, optional): 視為 `NA/NaN` 的值，如果輸入的是一個 `dict`，則可以針對各欄位指定被視為 `NA/NaN` 的值，格式為 `{colname: na_values}`。預設情況下它僅會採用 `pandas` 的預設值。詳見 [pandas 文件](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html)。

## `load()`

讀取與載入資料。

## `self.config`

`Loader` 模組的參數：

- `filepath` (`str`): 實際本地端資料的檔案路徑。
  - 使用[基準資料集](PETsARD/zh-tw/docs/usage/06_benchmark-datasets/)時會被實際下載存檔的檔名取代。
- `method` (`str`): 與輸入相同。
- `file_ext` (`str`): 本地端資料的副檔名。
- `benchmark` (`bool`): 是否為[基準資料集](PETsARD/zh-tw/docs/usage/06_benchmark-datasets/)。
- `dtypes` (`dict`): 各欄位格式的字典。
- `column_types` (`dict`, optional), `header_name` (`list`, optional), `na_values` (`str | list | dict`, optional): 與輸入相同。

以下的參數為使用基準資料集獨有。見[基準資料集頁面](PETsARD/zh-tw/docs/usage/06_benchmark-datasets/)。

- `filepath_raw` (`str`): 保留使用者輸入的原始檔案路徑。
- `benchmark_name` (`str`): 使用者指定的基準資料集名稱。
- `benchmark_filename` (`str`): 基準資料集的檔案名稱。
- `benchmark_access` (`str`): 基準資料集的存取類型。
- `benchmark_region_name` (`str`): 基準資料集所在的亞馬遜地區名稱。
- `benchmark_bucket_name` (`str`): 基準資料集的亞馬遜桶名稱。
- `benchmark_sha256` (`str`): 基準資料集的SHA-256校驗值。

## `self.loader`

被實例化的讀取器本身。

## `self.data`

已寫入的資料會以 `pd.DataFrame` 的格式存於 `self.data`。

## `self.metadata.metadata`

元資料以巢狀 `dict` 存於 `self.metadata.metadata`。詳見 ["Metadata"](PETsARD/zh-tw/docs/usage/05_metadata/) 頁面。
