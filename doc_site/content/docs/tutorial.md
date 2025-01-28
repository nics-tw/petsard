---
title: Tutorial
type: docs
weight: 1
prev: docs
sidebar:
  open: true
---

## Basic Usage

Click the right button to run this example in Colab [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/628-guide---tutorial/demo/basic-usage.ipynb)


### Case 1: Default Synthesis

The simplest way to generate privacy-enhanced synthetic data.
Current default synthesis uses Gaussian Copula from SDV.

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


### Case 2: Default Synthesis and Default Evaluation

Default synthesis with default evaluation.
Current default evaluation uses SDMetrics Quality Report.

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


### Case 3: External Synthesis with Default Evaluation

External synthesis with default evaluation.