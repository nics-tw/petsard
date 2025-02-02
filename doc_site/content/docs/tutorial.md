---
title: Tutorial
type: docs
weight: 11
prev: docs/get-started
sidebar:
  open: true
---

## Basic Usage

Click the below button to run this example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/628-guide---tutorial/demo/basic-usage.ipynb)

You can run these examples by executing the following code with your YAML config file:

```python
exec = Executor(config=yaml_path)
exec.run()
```


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
    output: 'result'
    source: 'Synthesizer'
  save_report_global:
    method: 'save_report'
    output: 'evaluation'
    eval: 'demo'
    granularity: 'global'
...
```

#### Evaluation Overview

The evaluation of synthetic data requires balancing three key aspects:
1. Protection - assessing security level
2. Fidelity - measuring similarity with original data
3. Utility - evaluating practical performance

> Note: These three aspects often involve trade-offs. Higher protection might lead to lower fidelity, and high fidelity might result in lower protection.

#### Evaluation Parameters

1. `Splitter`:
  - `num_samples: 1`: At least one validation group for evaluating privacy protection. This split is essential for Anonymeter to assess privacy risks by comparing training and testing data
  - `train_split_ratio: 0.8`: Split the dataset with 80% for training and 20% for testing, which is a common practice for cross-validation

2. `Evaluator`:
  - For linkability risk, `aux_cols` groups variables based on domain knowledge, such as personal demographic information and employment-related data
  - For inference risk, choose the most sensitive field (income) as the `secret` column
  - For classification utility, use the main `target` variable (income) that aligns with the actual analysis goal

#### Evaluation Process

Follow these steps to evaluate your synthetic data:

1. **Data Validity Diagnosis** (using SDMetrics)
  - Goal: Ensure schema consistency
  - Standard: Diagnosis score should reach 1.0
  - Why: Valid data is the foundation for all subsequent analysis

2. **Privacy Protection Assessment** (using Anonymeter)
  - Goal: Verify privacy protection level
  - Standard: Risk score should be below 0.09
  - Evaluates: Singling out, linkability, and inference risks
  > Note: A risk score of 0.0 does NOT mean zero risk. Always implement additional protection measures.

3. **Application-Specific Assessment**

  Based on your use case, focus on either:

  A. No Specific Task (Data Release Scenario):
  - Focus on Data Fidelity (using SDMetrics)
  - Standard: Fidelity score above 0.75
  - Measures: Distribution similarity and correlation preservation

  B. Specific Task (Model Training Scenario):
  - Focus on Data Utility
  - Standards vary by task type:
    * Classification: ROC AUC > 0.8
    * Clustering: Silhouette > 0.5
    * Regression: Adjusted R² > 0.7
  > Note: ROC AUC (Receiver Operating Characteristic Area Under Curve) measures the model's ability to distinguish between classes


### Case 3: External Synthesis with Default Evaluation

External synthesis with default evaluation.
Enabling users to evaluate synthetic data from external solutions.

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