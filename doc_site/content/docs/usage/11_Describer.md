---
title: "Describer"
draft: false
weight: 22
toc: true
---

The `Describer` module is responsible for producing descriptive statistical analysis. You can specify describing method in `Describer` class and use it to analyse the data.

```Python
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

## `Describer`

To initialise a `Describer`, you must specify the describing methods used to assess the data, which are stored in a `dict`-like object called `config`. Within `config`, there are two keys: `method` and `describe`, representing the operation name and the describing methods, respectively. The structure is shown below. Noted that if `method` is set to `'default'`, the default set of describing methods will be applied, including `['row_count', 'col_count', 'global_na_count', 'mean', 'median', 'std', 'min', 'max', 'kurtosis', 'skew', 'q1', 'q3', 'col_na_count', 'nunique', 'corr']`. Please refer to the subsequent section for detailed explanations of each method and a comprehensive list of all available methods.

```Python
config = {
  'method': str,
  'describe': []
}
```

```Python
des = Describer(config=config)
```

**Parameters**

`config` (`dict`): The describing methods. The format is specified above.

### `create()`

Create a `Describer` object with the provided data. The data should be stored within a `dict`. Each dataset should adhere to the following structure: the key must be `'data'`, while the corresponding value represents the dataset itself in `pd.DataFrame` format.

```Python
data = {
  'data': pd.DataFrame
}

des.create(data)
```

**Parameters**

`data` (`dict`): The dictionary contains the data to be analysed, in the form of `pd.DataFrame`. The `key` of `data` is specified above.

### `eval()`

Analyse the dataset. To retrieve the result, see the following sections.

### `get_global()`

Get the global result of the descriptive analysis, presenting it as a single row where each property is stored in its respective column.

**Outputs**

(`pd.DataFrame`): The global result of the descriptive analysis.

### `get_columnwise()`

Get the column-wise result of the descriptive analysis, where each column represents a property and each row represents a column/variable in the dataset.

**Outputs**

(`pd.DataFrame`): The column-wise result of the descriptive analysis.

### `get_pairwise()`

Get the pairwise result of the descriptive analysis, where each column represents a property and each row represents a pair of columns/variables in the dataset.

**Outputs**

(`pd.DataFrame`): The pairwise result of the descriptive analysis.

## Available Describer Types

In this section, we provide a comprehensive list of supported describer types and their scope (used in `get_global`, `get_columnwise`, `get_pairwise`) and name used in `config`.

<div class="table-wrapper" markdown="block">

| Granularity |         Class          | Alias (used in `config`) |
| :---------: | :--------------------: | :----------------------: |
|   Global    |  `DescriberRowCount`   |       'row_count'        |
|   Global    | `DescriberColumnCount` |       'col_count'        |
|   Global    |  `DeescriberGlobalNA`  |    'global_na_count'     |
| Column-wise |    `DescriberMean`     |          'mean'          |
| Column-wise |   `DescriberMedian`    |         'median'         |
| Column-wise |     `DescriberStd`     |          'std'           |
| Column-wise |     `DescriberVar`     |          'var'           |
| Column-wise |     `DescriberMin`     |          'min'           |
| Column-wise |     `DescriberMax`     |          'max'           |
| Column-wise |  `DescriberKurtosis`   |        'kurtosis'        |
| Column-wise |    `DescriberSkew`     |          'skew'          |
| Column-wise |     `DescriberQ1`      |           'q1'           |
| Column-wise |     `DescriberQ3`      |           'q3'           |
| Column-wise |     `DescriberIQR`     |          'iqr'           |
| Column-wise |    `DescriberRange`    |         'range'          |
| Column-wise | `DescriberPercentile`  |       'percentile'       |
| Column-wise |    `DescriberColNA`    |      'col_na_count'      |
| Column-wise |   `DescriberNUnique`   |        'nunique'         |
|  Pairwise   |     `DescriberCov`     |          'cov'           |
|  Pairwise   |    `DescriberCorr`     |          'corr'          |

</div>

### `'row_count'`

Calculate the number of rows in the dataset.

### `'column_count'`

Calculate the number of columns in the dataset.

### `'global_na_count'`

Calculate the number of rows with `NA` in the dataset.

### `'mean'`

Calculate the mean of each numerical column in the dataset.

### `'median'`

Calculate the median of each numerical column in the dataset.

### `'std'`

Calculate the standard deviation of each numerical column in the dataset.

### `'var'`

Calculate the variance of each numerical column in the dataset.

### `'min'`

Calculate the minimum of each numerical column in the dataset.

計算資料集中各數值型欄位的最小值。

### `'max'`

Calculate the maximum of each numerical column in the dataset.

### `'kurtosis'`

Calculate the kurtosis of each numerical column in the dataset.

### `'skew'`

Calculate the skewness of each numerical column in the dataset.

### `'q1'`

Calculate the first quartile of each numerical column in the dataset.

### `'q3'`

Calculate the third quartile of each numerical column in the dataset.

### `'iqr'`

Calculate the interquartile range of each numerical column in the dataset.

### `'range'`

Calculate the range of each numerical column in the dataset.

### `'percentile'`

Calculate the `k`\*100 th-percentile of each numerical column in the dataset. The paramter `k` is needed and should be passed in the following structure: `{'percentile': k}`.

**Parameters**

`k` (`float`): The `k`\*100 th-percentile. Should be between 0 and 1.

### `'col_na_count'`

Calculate the number of NA in each column in the dataset.

### `'nunique'`

Calculate the number of unique values of each categorical column in the dataset.

### `'cov'`

Calculate the covariance matrix of the dataset.

### `'corr'`

Calculate the correlation matrix of the dataset.
