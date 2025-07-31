---
title: 資料描述
type: docs
weight: 16
prev: docs/tutorial/use-cases
next: docs/tutorial/use-cases/data-preprocessing
---


在資料合成之前，您可能會想先了解您的資料。`PETsARD` 提供描述模組，以三種不同的顆粒度分析您的資料。

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/use-cases/data-description.ipynb)

```yaml
---
Loader:
  data:
    filepath: 'benchmark/adult-income.csv'
Describer:
  summary:
    method: 'default'
Reporter:
  save_report_global:
    method: 'save_report'
    granularity: 'global'
  save_report_columnwise:
    method: 'save_report'
    granularity: 'columnwise'
  save_report_pairwise:
    method: 'save_report'
    granularity: 'pairwise'
...
```

## 三種顆粒度的統計資訊

1. 全域統計 (`global`)

  - 提供整個資料集的基本資訊
  - 包含總列數、總欄位數、缺失值數量

2. 欄位統計 (`columnwise`)

  - 針對每個欄位的個別統計
  - 數值型欄位：平均值、中位數、標準差、最大最小值、四分位數等
  - 類別型欄位：類別數量、遺失值數量

3. 配對統計 (`pairwise`)

  - 分析欄位之間的關係
  - 主要提供數值型欄位間的相關係數