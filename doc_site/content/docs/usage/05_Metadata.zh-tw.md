---
title: "Metadata"
draft: false
weight: 16
toc: true
---

`Metadata` 是 `Loader` 模組的延伸功能，記錄資料集的特性及提供 `Processor` 初始化的必需元素。`Metadata` 的使用範例如下。

```Python
from petsard.loader import Metadata


metadata = Metadata()
metadata.build_metadata(df)
```

## `Metadata`

如果您使用 `PETsARD` 中的 `Loader`，恭喜您！您已經有元資料了，可於 `Loader.metadata.metadata` 中存取。否則，您需要使用此模組來創建元資料。初始化此類別不需要任何參數。

```Python
metadata = Metadata()
```

### `build_metadata()`

Read the dataset and build the metadata.

**參數**

`data` (`pd.DataFrame`): 生成元資料的資料集。

### `to_sdv()`

在 `sdv` 套件中，許多類別需要由 `sdv` 定義的元資料才能使用。這個函式提供將 `Metadata` 內的元資料轉換成 `sdv` 可接受的元資料格式。

**輸出**

`sdv_metadata` (dict): `sdv` 可接受的元資料格式。

### `self.metadata`

元資料以巢狀 `dict` 存於 `self.metadata`。它記錄了每個欄位的特性 (`'col'`)，包含資料型別 (`'dtype'`，與 `pandas` 的資料型別相同)、`NA` 比例 (`'na_percentage'`)、推論資料型別 (`'inder_dtype'`，值會是下列之一： 'numerical', 'categorical', 'datetime', 'object')。它也記錄整個資料集的特性 (`'global'`)，包含資料集的資料筆數與欄位數 (`'row_num'` and `'col_num'`)、`NA` 比例 (`'na_percentage'`)。以下是 `self.metadata` 的結構與範例。

```Python
{
    'col': {
        col_name: {
            'dtype': dtype,
            'na_percentage': column_na_percentage,
            'infer_dtype': infer_dtype
        }, ...
    },
    'global': {
        'row_num': row_num,
        'col_num': col_num,
        'na_percentage': global_na_percentage
    }
}
```

```plain_text
{
    'col': {
        'age': {
            'dtype': dtype('int8'),
            'na_percentage': 0.0,
            'infer_dtype': 'numerical'
        },
        'workclass': {
            'dtype': CategoricalDtype(...),
            'na_percentage': 0.057307,
            'infer_dtype': 'categorical'
        }
    },
    'global': {
        'row_num': 48842,
        'col_num': 15,
        'na_percentage': 0.074117
    }
}
```
