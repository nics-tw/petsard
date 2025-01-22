---
title: 教學
type: docs
weight: 1
prev: docs
sidebar:
  open: true
---

## 基本使用

請點擊右方按鈕在 Colab 中執行範例 [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/628-guide---tutorial/demo/basic-usage.ipynb)

### 情境一：預設合成

產生隱私強化合成資料的最簡單方式：

```yaml
---
Loader:
    data:
        filepath: 'benchmark/adult-income.csv'
Synthesizer:
    demo:
        method: 'default'
Reporter:
    output:
        method: 'save_data'
        output: 'result'
        source: 'Synthesizer'
...
```

