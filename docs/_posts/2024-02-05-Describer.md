The `describer` module is responsible for producing descriptive statistical analysis. You can specify describing method in `Describer` class and use it to analyse the data.

`describer` 模組負責產生敘述性統計分析。您可以在 `Describer` 類別中指定統計方法以分析資料。

```python
from PETsARD import Describer

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

# `Describer`

To initialise a `Describer`, you must specify the describing methods used to assess the data, which are stored in a `dict`-like object called `config`. Within `config`, there are two keys: `method` and `describe`, representing the operation name and the describing methods, respectively. The structure is shown below. Noted that if `method` is set to `'default'`, the default set of describing methods will be applied, including `['row_count', 'col_count', 'global_na_count', 'mean', 'median', 'std', 'min', 'max', 'kurtosis', 'skew', 'q1', 'q3', 'col_na_count', 'nunique', 'corr']`. Please refer to the subsequent section for detailed explanations of each method and a comprehensive list of all available methods.

使用 `Describer` 類別的物件之前，您需要指定敘述性統計方法，並將其存於 `dict` 形式的物件 `config`。在 `config` 中須包含兩個鍵：`method` 與 `describe`，分別代表操作名稱與統計方法。結構如下。值得注意的是，若將 `method` 名稱設為 `default`，則會自動套用預設的敘述性統計方法：`['row_count', 'col_count', 'global_na_count', 'mean', 'median', 'std', 'min', 'max', 'kurtosis', 'skew', 'q1', 'q3', 'col_na_count', 'nunique', 'corr']`，詳見後續章節以了解各方法的意涵及所有可用方法。


```python
config = {
  'method': str,
  'describe': []
}
```

```python
des = Describer(config)
```

**Parameters**

`config` (`dict`): The describing methods. The format is specified above. 欲執行的敘述性統計方法，格式可見上述程式碼。

## `create()`

Create a `Describer` object with the provided data. The data should be stored within a `dict`. Each dataset should adhere to the following structure: the key must be `'data'`, while the corresponding value represents the dataset itself in `pd.DataFrame` format.

利用資料創建 `Describer`。資料集須以 `dict` 方式儲存。每個資料集須符合下述架構：鍵為 `'data'`；值為 `pd.DataFrame` 格式的資料集。

```python
data = {
  'data': pd.DataFrame
}

des.create(data)
```

**Parameters**

`data` (`dict`): The dictionary contains the data to be analysed, in the form of `pd.DataFrame`. The `key` of `data` is specified above. 欲分析的資料，存於字典中，需要是 `pd.DataFrame` 的格式。`data` 的 `key` 可見上述程式碼。

## `eval()`

Analyse the dataset. To retrieve the result, see the following sections.

分析資料集。取得結果的方法請詳見後續章節。

## `get_global()`

Get the global result of the descriptive analysis, presenting it as a single row where each property is stored in its respective column.

獲取全域敘述性統計的分析結果。只有一列，各屬性存於欄位中。

**Outputs**

(`pd.DataFrame`): The global result of the descriptive analysis. 全域敘述性統計的分析結果。

## `get_columnwise()`

Get the column-wise result of the descriptive analysis, where each column represents a property and each row represents a column/variable in the dataset. 獲取各欄位的敘述性統計分析結果。各屬性存於欄位中，而每列則代表資料集中的一個欄位/變數。

**Outputs**

(`pd.DataFrame`): The column-wise result of the descriptive analysis. 各欄位的敘述性統計的分析結果。

## `get_pairwise()`

Get the pairwise result of the descriptive analysis, where each column represents a property and each row represents a pair of columns/variables in the dataset. 獲取各欄位兩兩組合的敘述性統計分析結果。各屬性存於欄位中，而每列則代表資料集中的兩個欄位/變數組合。

**Outputs**

(`pd.DataFrame`): The pairwise result of the descriptive analysis. 各欄位兩兩組合的敘述性統計的分析結果。

# Available Describer Types

In this section, we provide a comprehensive list of supported describer types and their scope (used in `get_global`, `get_columnwise`, `get_pairwise`) and name used in `config`.

在此章節我們列出所有目前支援的敘述性分析類型，及其尺度（使用於 `get_global`、`get_columnwise`、`get_pairwise`）與用於 `config` 的名稱。

| Scope | Class | Alias (used in `config`) |
|---|:---:|:---:|
| Global | `DescriberRowCount` | 'row_count' |
| Global | `DescriberColumnCount` | 'col_count' |
| Global | `DeescriberGlobalNA` | 'global_na_count' |
| Column-wise | `DescriberMean` | 'mean' |
| Column-wise | `DescriberMedian` | 'median' |
| Column-wise | `DescriberStd` | 'std' |
| Column-wise | `DescriberVar` | 'var' |
| Column-wise | `DescriberMin` | 'min' |
| Column-wise | `DescriberMax` | 'max' |
| Column-wise | `DescriberKurtosis` | 'kurtosis' |
| Column-wise | `DescriberSkew` | 'skew' |
| Column-wise | `DescriberQ1` | 'q1' |
| Column-wise | `DescriberQ3` | 'q3' |
| Column-wise | `DescriberIQR` | 'iqr' |
| Column-wise | `DescriberRange` | 'range' |
| Column-wise | `DescriberPercentile` | 'percentile' |
| Column-wise | `DescriberColNA` | 'col_na_count' |
| Column-wise | `DescriberNUnique` | 'nunique' |
| Pairwise | `DescriberCov` | 'cov' |
| Pairwise | `DescriberCorr` | 'corr' |

## `'row_count'`

Calculate the number of rows in the dataset.

計算資料集列數。

## `'column_count'`

Calculate the number of columns in the dataset.

計算資料集欄數。

## `'global_na_count'`

Calculate the number of rows with `NA` in the dataset.

計算資料集中含有 `NA` 值的列數。

## `'mean'`

Calculate the mean of each numerical column in the dataset.

計算資料集中各數值型欄位的平均數。

## `'median'`

Calculate the median of each numerical column in the dataset.

計算資料集中各數值型欄位的中位數。

## `'std'`

Calculate the standard deviation of each numerical column in the dataset.

計算資料集中各數值型欄位的標準差。

## `'var'`

Calculate the variance of each numerical column in the dataset.

計算資料集中各數值型欄位的變異數。

## `'min'`

Calculate the minimum of each numerical column in the dataset.

計算資料集中各數值型欄位的最小值。

## `'max'`

Calculate the maximum of each numerical column in the dataset.

計算資料集中各數值型欄位的最大值。

## `'kurtosis'`

Calculate the kurtosis of each numerical column in the dataset.

計算資料集中各數值型欄位的峰態係數。

## `'skew'`

Calculate the skewness of each numerical column in the dataset.

計算資料集中各數值型欄位的偏態係數。

## `'q1'`

Calculate the first quartile of each numerical column in the dataset.

計算資料集中各數值型欄位的第一四分位數。

## `'q3'`

Calculate the third quartile of each numerical column in the dataset.

計算資料集中各數值型欄位的第三四分位數。

## `'iqr'`

Calculate the interquartile range of each numerical column in the dataset.

計算資料集中各數值型欄位的四分位距。

## `'range'`

Calculate the range of each numerical column in the dataset.

計算資料集中各數值型欄位的全距。

## `'percentile'`

Calculate the `k`*100 th-percentile of each numerical column in the dataset. The paramter `k` is needed and should be passed in the following structure: `{'percentile': k}`.

計算資料集中各數值型欄位的第 `k`*100 百分位數。使用此方法需給定 `k`，結構如下：`{'percentile': k}`。

**Parameters**

`k` (`float`): The `k`\*100 th-percentile. Should be between 0 and 1. 第 `k`*100 百分位數。需介於 0 到 1 之間。

## `'col_na_count'`

Calculate the number of NA in each column in the dataset.

計算資料集中各欄位含有的 `NA` 值總數。

## `'nunique'`

Calculate the number of unique values of each categorical column in the dataset.

計算資料集中各類別型欄位的類別個數。

## `'cov'`

Calculate the covariance matrix of the dataset.

計算資料集的共變異數矩陣。

## `'corr'`

Calculate the correlation matrix of the dataset.

計算資料集的相關性矩陣。
