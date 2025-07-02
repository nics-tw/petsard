---
title: Benchmark Datasets
type: docs
weight: 35
prev: docs/tutorial/use-cases/custom-evaluation
next: docs/tutorial/use-cases/timing
---


When developing privacy-preserving data synthesis workflows, you might face these challenges:
  - Unsure if your data characteristics suit specific synthesis algorithms
  - Uncertain about the appropriate synthesis parameters
  - Need a reliable reference standard for evaluation

Using benchmark datasets for testing is a good practice. Benchmark datasets have well-known characteristics and are widely used in academic research, allowing you to:
  1. Test your synthesis workflow on benchmark data first
  2. Verify results meet expectations
  3. Apply the same workflow to your data

Click the below button to run this example in Colab:

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

## Appx. Available Benchmark Dataset

Currently, `PETsARD` provides the **Adult Income Dataset** as a benchmark:

  - Name: adult-income
  - Source: U.S. Census Bureau
  - Scale: 48,842 records, 15 columns
  - Characteristics:
    - Mixed numerical and categorical features
    - Contains sensitive information (income)
    - Suitable for testing privacy protection in data synthesis

## Benchmark Datasets Usage

  1. Use `benchmark://` in `filepath` to specify the benchmark dataset
  2. `PETsARD` will automatically download and verify the dataset
  3. Subsequent synthesis and evaluation processes remain the same as with regular data

For detailed implementation of benchmark datasets, please refer to [Benchmark Dataset Maintenance](docs/developer-guide/benchmark-datasets/) in the Developer Guide.