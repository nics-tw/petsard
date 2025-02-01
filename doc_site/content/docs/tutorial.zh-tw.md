---
title: 教學
type: docs
weight: 11
prev: docs/get-started
sidebar:
  open: true
---

## 基本使用

請點擊右方按鈕在 Colab 中執行範例 [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/628-guide---tutorial/demo/basic-usage.ipynb)

您可以透過以下程式碼執行這些範例，只需要準備您的 YAML 設定檔：

```python
exec = Executor(config=yaml_path)
exec.run()
```


### 情境一：預設合成

產生隱私強化合成資料的最簡單方式。
目前的預測合成方式採用 SDV 的 Gaussian Copula。

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
    output: 'result'
    source: 'Synthesizer'
...
```


### 情境二：預設合成與預設評測

使用預設方式進行合成與評測。
目前的預設評測方式採用 SDMetrics 品質報告。

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
Postprocessor:
  demo:
    method: 'default'
Evaluator:
  demo:
    method: 'default' # 'sdmetrics-qualityreport'
Reporter:
  output:
    method: 'save_data'
    output: 'result'
    source: 'Synthesizer'
  save_report_global:
    method: 'save_report'
    output: 'evaluation'
    eval: 'demo'
    granularity: 'global'
...
```


### 情境三：外部合成與預設評測

使用預設方式評測外部合成資料。
讓使用者評估外部解決方案獲得的合成資料。

```yaml
---
Loader:
  data:
    filepath: 'benchmark/adult-income.csv'
Synthesizer:
  custom:
    method: 'custom_data'
    filepath: 'benchmark/adult-income_syn.csv'
Evaluator:
  demo:
    method: 'default'
Reporter:
  save_report_global:
    method: 'save_report'
    output: 'evaluation'
    eval: 'demo'
    granularity: 'global'
...
```