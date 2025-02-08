---
title: 資料約束
type: docs
weight: 12
prev: docs/tutorial/default-synthesis
next: docs/tutorial/advanced-synthesis
sidebar:
  open: true
---

透過欄位值規則、欄位組合和空值處理策略來約束合成資料。
目前的實作支援三種約束：欄位約束、欄位組合和空值群組。

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/data-constraining.ipynb)

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
    method: 'default'
Constrainer:
  demo:
    nan_groups:
      workclass: ('delete', 'occupation')  # 當 workclass 是空值時刪除整列
      occupation: ('erase', ['income'])    # 當 occupation 是空值時，把 income 設為空值
      income: ('copy', 'salary')          # 當 income 有值但 salary 是空值時，複製 income 的值到 salary
    field_constraints:
      - "age >= 18 & age <= 65"          # 年齡限制在 18-65 歲
      - "hours-per-week >= 20 & hours-per-week <= 60"  # 每週工時限制在 20-60 小時
    field_combinations:
      -
        - {'education': 'income'}         # 教育程度和收入的對應關係
        - {'Doctorate': ['>50K'], 'Masters': ['>50K', '<=50K']}  # 博士只能高收入，碩士可以高低收入
Postprocessor:
  demo:
    method: 'default'
Reporter:
  output:
    method: 'save_data'
    source: 'Constrainer'
...
```