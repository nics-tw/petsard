---
title: 資料遺失值處理
type: docs
weight: 18
prev: docs/tutorial/special-cases/comparing-synthesizers
next: docs/tutorial/special-cases/benchmark-datasets
sidebar:
  open: true
---


在合成資料之前，您需要先處理資料中的遺失值。`PETsARD` 提供多種遺失值處理方法供您選擇。

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/handling-missing-values.ipynb)

```yaml
---
Loader:
  data:
    filepath: 'benchmark/adult-income.csv'
Preprocessor:
  drop:
    method: 'default'
    config:
      missing:
        age: 'missing_drop'      # Drop rows with missing values
        income: 'missing_drop'
  fill:
    method: 'default'
    config:
      missing:
        age: 'missing_mean'      # Fill with mean value
        workclass: 'missing_mode'  # Fill with mode
  simple:
    method: 'default'
    config:
      missing:
        age:
          method: 'missing_simple'  # Fill with specified value
          value: 0
Synthesizer:
  demo:
    method: 'default'
Postprocessor:
  demo:
    method: 'default'
Evaluator:
  demo-quality:
    method: 'sdmetrics-qualityreport'
Reporter:
  output:
    method: 'save_data'
    source: 'Synthesizer'
  save_report_global:
    method: 'save_report'
    granularity: 'global'
...
```

## 遺失值處理方法

1. 直接刪除 (`missing_drop`)

  - 刪除含有遺失值的資料列
  - 適用於遺失值較少的情況
  - 需注意可能損失重要資訊

2. 統計插補

  - 平均值插補 (`missing_mean`)：用該欄位的平均值填入
  - 中位數插補 (`missing_median`)：
  - 眾數插補 (`missing_mode`)：
  - 適用於不同資料型態：
    - 數值型資料可使用平均值或中位數
    - 類別型資料建議使用眾數

3. 自定義插補 (`missing_simple`)

  - 用指定的數值填補遺失值
  - 需要設定 `value` 參數
  - 適用於有特定業務邏輯的情況

您可以針對不同欄位使用不同的處理方法，只要在設定檔中指定相應的設定即可。