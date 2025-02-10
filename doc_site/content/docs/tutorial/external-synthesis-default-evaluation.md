---
title: External Synthesis with Default Evaluation
type: docs
weight: 14
prev: docs/tutorial/default-synthesis-default-evaluation
next: docs/tutorial/use-cases
---


External synthesis with default evaluation.
Enabling users to evaluate synthetic data from external solutions.

Click the below button to run this example in Colab:

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

## External Data Preparation Overview

Pre-synthesized data evaluation requires attention to three key components:

1. Training Set - used for synthetic data generation
2. Testing Set - for privacy risk evaluation
3. Synthetic Data - based only on the training set

> Note: Using both training and testing data for synthesis would affect the accuracy of privacy evaluation.

## External Data Requirements

1. `Splitter`:

- `method: 'custom_data'`: For pre-split datasets provided externally
- `filepath`: Points to original (`ori`) and control (`control`) datasets
- Recommended ratio: 80% training, 20% testing unless specific reasons otherwise

2. `Synthesizer`:

- `method: 'custom_data'`: For externally generated synthetic data
- `filepath`: Points to pre-synthesized dataset
- Must be generated using only the training portion of data

3. `Evaluator`:

- Ensures fair comparison between different synthetic data solutions
