---
title: "Describer"
draft: false
weight: 22
toc: true
---

`Describer` 模組負責產生敘述性統計分析。您可以在 `Describer` 類別中指定統計方法以分析資料。

```Python
from petsard import Describer


data = {"data": loader.data}

config = {
    'method': 'summary',
    'describe': ['mean', 'median', {'percentile': 0.01}, 'q1', 'corr',
                  'row_count', 'cov', 'col_count', 'global_na_count',
                  'std', 'var', 'min', 'max', 'range', 'skew', 'kurtosis','q3', 'iqr',
                  {'percentile': 0.95}, 'col_na_count', 'nunique', {'percentile': 0.85}]
}

des = Describer(config)
des.create(data)
des.eval()

des.get_global()
des.get_columnwise()
des.get_pairwise()
```

## `Describer`

使用 `Describer` 類別的物件之前，您需要指定敘述性統計方法，並將其存於 `dict` 形式的物件 `config`。在 `config` 中須包含兩個鍵：`method` 與 `describe`，分別代表操作名稱與統計方法。結構如下。值得注意的是，若將 `method` 名稱設為 `default`，則會自動套用預設的敘述性統計方法：`['row_count', 'col_count', 'global_na_count', 'mean', 'median', 'std', 'min', 'max', 'kurtosis', 'skew', 'q1', 'q3', 'col_na_count', 'nunique', 'corr']`，詳見後續章節以了解各方法的意涵及所有可用方法。

```Python
config = {
  'method': str,
  'describe': []
}
```

```Python
des = Describer(config=config)
```

**參數**

`config` (`dict`): 欲執行的敘述性統計方法，格式可見上述程式碼。

### `create()`

利用資料創建 `Describer`。資料集須以 `dict` 方式儲存。每個資料集須符合下述架構：鍵為 `'data'`；值為 `pd.DataFrame` 格式的資料集。

```Python
data = {
  'data': pd.DataFrame
}

des.create(data)
```

**參數**

`data` (`dict`): 欲分析的資料，存於字典中，需要是 `pd.DataFrame` 的格式。`data` 的 `key` 可見上述程式碼。

### `eval()`

分析資料集。取得結果的方法請詳見後續章節。

### `get_global()`

獲取全域敘述性統計的分析結果。只有一列，各屬性存於欄位中。

**輸出**

(`pd.DataFrame`): 全域敘述性統計的分析結果。

### `get_columnwise()`

獲取各欄位的敘述性統計分析結果。各屬性存於欄位中，而每列則代表資料集中的一個欄位/變數。

**輸出**

(`pd.DataFrame`): 各欄位的敘述性統計的分析結果。

### `get_pairwise()`

獲取各欄位兩兩組合的敘述性統計分析結果。各屬性存於欄位中，而每列則代表資料集中的兩個欄位/變數組合。

**輸出**

(`pd.DataFrame`): 各欄位兩兩組合的敘述性統計的分析結果。

## 可用的 Describer 類型

在此章節我們列出所有目前支援的敘述性分析類型，及其尺度（使用於 `get_global`、`get_columnwise`、`get_pairwise`）與用於 `config` 的名稱。

<div class="table-wrapper" markdown="block">

|             |           類           | 別名（在 `config` 中使用） |
| :---------: | :--------------------: | :------------------------: |
|   Global    |  `DescriberRowCount`   |        'row_count'         |
|   Global    | `DescriberColumnCount` |        'col_count'         |
|   Global    |  `DeescriberGlobalNA`  |     'global_na_count'      |
| Column-wise |    `DescriberMean`     |           'mean'           |
| Column-wise |   `DescriberMedian`    |          'median'          |
| Column-wise |     `DescriberStd`     |           'std'            |
| Column-wise |     `DescriberVar`     |           'var'            |
| Column-wise |     `DescriberMin`     |           'min'            |
| Column-wise |     `DescriberMax`     |           'max'            |
| Column-wise |  `DescriberKurtosis`   |         'kurtosis'         |
| Column-wise |    `DescriberSkew`     |           'skew'           |
| Column-wise |     `DescriberQ1`      |            'q1'            |
| Column-wise |     `DescriberQ3`      |            'q3'            |
| Column-wise |     `DescriberIQR`     |           'iqr'            |
| Column-wise |    `DescriberRange`    |          'range'           |
| Column-wise | `DescriberPercentile`  |        'percentile'        |
| Column-wise |    `DescriberColNA`    |       'col_na_count'       |
| Column-wise |   `DescriberNUnique`   |         'nunique'          |
|  Pairwise   |     `DescriberCov`     |           'cov'            |
|  Pairwise   |    `DescriberCorr`     |           'corr'           |

</div>

### `'row_count'`

計算資料集列數。

### `'column_count'`

計算資料集欄數。

### `'global_na_count'`

計算資料集中含有 `NA` 值的列數。

### `'mean'`

計算資料集中各數值型欄位的平均數。

### `'median'`

計算資料集中各數值型欄位的中位數。

### `'std'`

計算資料集中各數值型欄位的標準差。

### `'var'`

計算資料集中各數值型欄位的變異數。

### `'min'`

計算資料集中各數值型欄位的最小值。

### `'max'`

計算資料集中各數值型欄位的最大值。

### `'kurtosis'`

計算資料集中各數值型欄位的峰態係數。

### `'skew'`

計算資料集中各數值型欄位的偏態係數。

### `'q1'`

計算資料集中各數值型欄位的第一四分位數。

### `'q3'`

計算資料集中各數值型欄位的第三四分位數。

### `'iqr'`

計算資料集中各數值型欄位的四分位距。

### `'range'`

計算資料集中各數值型欄位的全距。

### `'percentile'`

計算資料集中各數值型欄位的第 `k`\*100 百分位數。使用此方法需給定 `k`，結構如下：`{'percentile': k}`。

**參數**

`k` (`float`): 第 `k`\*100 百分位數。需介於 0 到 1 之間。

### `'col_na_count'`

計算資料集中各欄位含有的 `NA` 值總數。

### `'nunique'`

計算資料集中各類別型欄位的類別個數。

### `'cov'`

計算資料集的共變異數矩陣。

### `'corr'`

計算資料集的相關性矩陣。
