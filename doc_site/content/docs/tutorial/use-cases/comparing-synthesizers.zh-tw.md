---
title: 比較合成演算法
type: docs
weight: 30
prev: docs/tutorial/use-cases/data-preprocessing
next: docs/tutorial/use-cases/custom-synthesis
---


`PETsARD` 支援多種合成資料的方法。您可以在同一個實驗中，使用不同的演算法來合成資料，並比較其結果。

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/use-cases/comparing-synthesizers.ipynb)

```yaml
---
Loader:
  data:
    filepath: 'benchmark/adult-income.csv'
Preprocessor:
  demo:
    method: 'default'
Synthesizer:
  gaussian-copula:
    method: 'sdv-single_table-gaussiancopula'
  ctgan:
    method: 'sdv-single_table-ctgan'
  tvae:
    method: 'sdv-single_table-tvae'
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

## 可用的合成演算法

1. 高斯 Copula (`sdv-single_table-gaussiancopula`)

  - 主要利用變數間的相依關係來合成資料
  - 這是 `PETsARD` 的預設方法

2. CTGAN (`sdv-single_table-ctgan`)

  - 使用條件式生成對抗網路 (conditional generative adversarial networks, conditional GAN) 來合成資料
  - 特別關注類別變數的條件機率分布

3. TVAE (`sdv-single_table-tvae`)

  - 使用變分自編碼器 (variational autoencoders) 來合成資料
  - 關注資料的整體分布特徵

透過在同一個 YAML 設定檔中指定多個合成方法，您可以一次執行多種演算法，並使用相同的評估指標來比較它們的表現。