---
title: 預設合成
type: docs
weight: 12
prev: docs/tutorial/yaml-config
next: docs/tutorial/default-synthesis-default-evaluation
---


產生隱私強化合成資料的最簡單方式。
目前的預測合成方式採用 SDV 的 Gaussian Copula。

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/default-synthesis.ipynb)

```yaml
---
Loader:
  data:
    filepath: 'benchmark/adult-income.csv'
Preprocessor:
  demo:
    method: 'default'
Synthesizer:
  demo:
    method: 'default' # sdv-single_table-gaussiancopula
Postprocessor:
  demo:
    method: 'default'
Reporter:
  output:
    method: 'save_data'
    source: 'Synthesizer'
...
```