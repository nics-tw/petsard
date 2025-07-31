---
title: 基準資料集
type: docs
weight: 35
prev: docs/tutorial/use-cases/custom-evaluation
next: docs/tutorial/use-cases/timing
---


在開發隱私保護資料合成流程時，您可能會遇到這些問題：
  - 不確定資料的特性是否適合特定合成演算法
  - 不知道合成參數的設定是否合理
  - 需要一個可靠的參考標準來評估結果

此時，使用基準資料集進行測試是很好的做法。基準資料集的特性是已知的，且被廣泛使用於學術研究中，因此您可以：
  1. 先在基準資料集上測試您的合成流程
  2. 確認結果符合預期
  3. 再將相同的流程應用在您的資料上

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/use-cases/benchmark-datasets.ipynb)

```yaml
---
Loader:
  data:
    filepath: 'benchmark/adult-income.csv'
  benchmark:
    filepath: 'benchmark://adult-income'
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
  demo-quality:
    method: 'sdmetrics-qualityreport'
Reporter:
  save_report_global:
    method: 'save_report'
    granularity: 'global'
...
```

## 附錄：可用的基準資料集

目前 `PETsARD` 提供 **Adult Income Dataset** 作為基準資料集：

  - 檔名：adult-income
  - 來源：美國人口普查局 (U.S. Census Bureau)
  - 規模：48,842 筆資料，15 個欄位
  - 特性：
    - 混合數值與類別型特徵
    - 包含敏感資訊（收入）
    - 適合測試資料合成的隱私保護效果

## 基準資料集使用方式

  1. 在 `filepath` 中使用 `benchmark://` 指定要使用的基準資料集
  2. `PETsARD` 會自動下載並驗證資料集
  3. 後續的合成與評測流程與一般資料相同

詳細的基準資料集實現方式，請參考開發者手冊的[基準資料集維護](docs/developer-guide/benchmark-datasets/)。