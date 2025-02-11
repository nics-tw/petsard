---
title: 外部合成與預設評測
type: docs
weight: 14
prev: docs/tutorial/default-synthesis-default-evaluation
next: docs/tutorial/use-cases
---


使用預設方式評測外部合成資料。
讓使用者評估外部解決方案獲得的合成資料。

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/external-synthesis-default-evaluation.ipynb)

```yaml
---
Splitter:
  custom:
    method: 'custom_data'
    filepath:
      ori: 'benchmark/adult-income_ori.csv'
      control: 'benchmark/adult-income_control.csv'
Synthesizer:
  custom:
    method: 'custom_data'
    filepath: 'benchmark/adult-income_syn.csv'
Evaluator:
  demo-diagnostic:
    method: 'sdmetrics-diagnosticreport'
  demo-quality:
    method: 'sdmetrics-qualityreport'
  demo-singlingout:
    method: 'anonymeter-singlingout'
  demo-linkability:
    method: 'anonymeter-linkability'
    aux_cols:
      -
        - 'age'
        - 'marital-status'
        - 'relationship'
        - 'gender'
      -
        - 'workclass'
        - 'educational-num'
        - 'occupation'
        - 'income'
  demo-inference:
    method: 'anonymeter-inference'
    secret: 'income'
  demo-classification:
    method: 'mlutility-classification'
    target: 'income'
Reporter:
  save_report_global:
    method: 'save_report'
    granularity: 'global'
...
```

## 外部資料準備概觀

預先合成資料的評測需要注意三個關鍵組成：

1. 訓練集 - 用於生成合成資料
2. 測試集 - 用於隱私風險評估
3. 合成資料 - 僅基於訓練集產生

> 注意：如果同時使用訓練和測試資料來合成，會影響隱私評測的準確性

## 外部資料要求

1. `Splitter`（資料分割）：

- `method: 'custom_data'`：用於外部提供的預分割資料集
- `filepath`: 指向原始 (`ori`) 和控制 (`control`) 資料集
- 建議比例：除非有特殊理由，否則採用 80% 訓練、20% 測試

2. `Synthesizer`（資料合成）：

- `method: 'custom_data'`：用於外部生成的合成資料
- `filepath`：指向預先合成的資料集
- 必須僅使用資料的訓練部分來生成

3. `Evaluator`（資料評測）：

- 確保不同合成資料解決方案之間的公平比較
