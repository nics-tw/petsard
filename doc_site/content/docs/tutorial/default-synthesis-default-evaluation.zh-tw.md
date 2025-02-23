---
title: 預設合成與預設評測
type: docs
weight: 13
prev: docs/tutorial/default-synthesis
next: docs/tutorial/external-synthesis-default-evaluation
---


使用預設方式進行合成與評測。
目前的預設評測方式採用 SDMetrics 品質報告。

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/default-synthesis-default-evaluation.ipynb)

```yaml
---
Loader:
  data:
    filepath: 'benchmark/adult-income.csv'
Splitter:
  demo:
    num_samples: 1
    train_split_ratio: 0.8
Preprocessor:
  demo:
    method: 'default'
Synthesizer:
  demo:
    method: 'default'
Postprocessor:
  demo:
    method: 'default'
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
  output:
    method: 'save_data'
    source: 'Synthesizer'
  save_report_global:
    method: 'save_report'
    granularity: 'global'
...
```

## 評測概觀

評估合成資料需要權衡三個關鍵面向：
1. 保護力 (Protection) - 評估安全程度
2. 保真度 (Fidelity) - 衡量與原始資料的相似程度
3. 實用性 (Utility) - 評估實際應用表現

> 注意：這三個面向通常存在取捨關係。較高的保護力可能導致較低的保真度，而高保真度可能降低保護程度。

## 評測參數

1. `Splitter`（資料分割）:
  - `num_samples: 1`：至少需要一組驗證組來評估隱私保護程度。這個分割對於 Anonymeter 來說是必要的，因為它需要比較訓練資料和測試資料來評估隱私風險
  - `train_split_ratio: 0.8`：使用 80% 的資料作為訓練集、20% 作為測試集，這是交叉驗證的常見做法

2. `Evaluator`（資料評測）:
  - 連結性風險評測中，`aux_cols` 依據領域知識將變數分組，例如個人人口統計資料和就業相關資料
  - 推斷性風險評測中，將最敏感的欄位（收入）設為 `secret` 欄位
  - 分類實用性評測中，使用主要的 `target` 變數（收入），這需要與實際分析目標一致

## 評測流程

依照以下步驟評估您的合成資料：

1. **資料有效性診斷**（使用 SDMetrics）
  - 目標：確保資料綱要一致性
  - 標準：診斷分數需達到 1.0
  - 原因：有效的資料是後續所有分析的基礎

2. **隱私保護力評測**（使用 Anonymeter）
  - 目標：驗證隱私保護程度
  - 標準：風險分數應低於 0.09
  - 評估：指認性風險 (Singling Out)、連結性風險 (Linkability) 及推斷性風險 (Inference)
  > 注意：風險分數 0.0 並不代表完全沒有風險。務必同時實施其他保護措施。

3. **應用場景評測**

  根據您的使用情境，著重於：

  A. 無特定任務（資料釋出情境）：
  - 著重於資料保真度（使用 SDMetrics）
  - 標準：保真度分數高於 0.75
  - 衡量：分布相似性和相關性保持程度

  B. 特定任務（模型訓練情境）：
  - 著重於資料實用性
  - 標準依任務類型而異：
    * 分群 (Classification)：ROC AUC > 0.8
    * 聚類 (Clustering)：輪廓係數 (Silhouette) > 0.5
    * 迴歸 (Regression)：調整後決定係數 (Adjusted R²) > 0.7
  > 注意：ROC AUC（受試者操作特徵曲線下面積）用於衡量模型區分不同類別的能力
