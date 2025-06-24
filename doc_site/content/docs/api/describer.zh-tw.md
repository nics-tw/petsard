---
title: Describer
type: docs
weight: 59
prev: docs/api/evaluator
next: docs/api/reporter
---

```python
Describer(config)
```

用於產生敘述性統計分析。

## 參數

- `config` (dict)：敘述性統計設定
  - `method` (str)：操作名稱
    - 'default'：套用預設統計方法組合
  - `describe` (list)：要執行的統計方法列表
    - 可用值見下方統計方法表格
    - 百分位數需使用字典格式：`{'percentile': k}`

## 範例

```python
from petsard import Describer


# 使用預設敘述方法
desc = Describer(method='default')

# 自定義敘述方法
desc = Describer(
    method='default',
    describe_method=['mean', 'median', 'std', 'percentile'],
    percentile=0.95,
)

# 評測
desc.create()
desc_result: dict[str, pd.DataFrame] = desc.eval({'data': df})

# 取得結果
global_stats: pd.DataFrame = desc_result.get('global')      # 整體統計
column_stats: pd.DataFrame = desc_result.get('columnwise')  # 各欄位統計
pairwise_stats: pd.DataFrame = desc_result.get('pairwise')  # 欄位配對統計
```

## 方法

### `create()`

初始化描述器。

**參數**

無

**回傳值**

無

### `eval()`

執行敘述性統計分析。

**參數**

- `data` (dict)：要敘述的資料
  - 格式：`{'data': pd.DataFrame}`

**回傳值**

`(dict[str, pd.DataFrame])`，依照模組不同：
  - 'global'：表示整體資料集敘述結果的單列資料框
  - 'columnwise'：表示各欄位敘述結果，每列代表一個欄位的敘述結果
  - 'pairwise'：表示欄位對敘述結果，每列代表一組欄位配對的敘述結果

## 附錄：支援敘述方法

### 總覽

敘述性統計方法分為三種層級：
- 全域分析：計算整體資料特性（如資料筆數）
- 欄位分析：計算各欄位的統計量（如平均值、標準差）
- 配對分析：計算欄位間的關係（如相關係數）

### 支援敘述方法

| 分析層級 | 敘述方法 | 參數 | 描述 |
| :---: | :---: | :---: | :--- |
| 全域 | `DescriberRowCount` | 'row_count' | 計算資料列數 |
| 全域 | `DescriberColumnCount` | 'col_count' | 計算資料欄數 |
| 全域 | `DeescriberGlobalNA` | 'global_na_count' | 計算含 NA 的列數 |
| 欄位 | `DescriberMean` | 'mean' | 計算平均值 |
| 欄位 | `DescriberMedian` | 'median' | 計算中位數 |
| 欄位 | `DescriberStd` | 'std' | 計算標準差 |
| 欄位 | `DescriberVar` | 'var' | 計算變異數 |
| 欄位 | `DescriberMin` | 'min' | 計算最小值 |
| 欄位 | `DescriberMax` | 'max' | 計算最大值 |
| 欄位 | `DescriberKurtosis` | 'kurtosis' | 計算峰態係數 |
| 欄位 | `DescriberSkew` | 'skew' | 計算偏態係數 |
| 欄位 | `DescriberQ1` | 'q1' | 計算第一四分位數 |
| 欄位 | `DescriberQ3` | 'q3' | 計算第三四分位數 |
| 欄位 | `DescriberIQR` | 'iqr' | 計算四分位距 |
| 欄位 | `DescriberRange` | 'range' | 計算全距 |
| 欄位 | `DescriberPercentile` | 'percentile' | 計算自定義百分位數 |
| 欄位 | `DescriberColNA` | 'col_na_count' | 計算各欄位 NA 值數量 |
| 欄位 | `DescriberNUnique` | 'nunique' | 計算類別數量 |
| 配對 | `DescriberCov` | 'cov' | 計算共變異數 |
| 配對 | `DescriberCorr` | 'corr' | 計算相關係數 |