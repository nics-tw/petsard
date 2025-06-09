---
title: Comparing Synthesizers
type: docs
weight: 30
prev: docs/tutorial/use-cases/data-preprocessing
next: docs/tutorial/use-cases/custom-synthesis
---


`PETsARD` supports multiple data synthesis methods. You can use different algorithms to synthesize data in the same experiment and compare their results.

Click the below button to run this example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/use-cases/comparing-synthesizers.ipynb)

```yaml
---
Loader:
  data:
    filepath: 'benchmark/adult-income.csv'
Preprocessor:
  demo:
    method: 'default'
Synthesizer:
  gaussian-copula:
    method: 'sdv-single_table-gaussiancopula'
  ctgan:
    method: 'sdv-single_table-ctgan'
  tvae:
    method: 'sdv-single_table-tvae'
Postprocessor:
  demo:
    method: 'default'
Evaluator:
  demo-quality:
    method: 'sdmetrics-qualityreport'
Reporter:
  output:
    method: 'save_data'
    source: 'Synthesizer'
  save_report_global:
    method: 'save_report'
    granularity: 'global'
...
```

## Available Synthesizers

1. Gaussian Copula (`sdv-single_table-gaussiancopula`)

  - Synthesizes data by modeling variable dependencies
  - This is `PETsARD`'s default method

2. CTGAN (`sdv-single_table-ctgan`)

  - Uses conditional generative adversarial networks (conditional GAN)
  - Focuses on conditional probability distributions of categorical variables

3. TVAE (`sdv-single_table-tvae`)

  - Uses variational autoencoders for synthesis
  - Focuses on overall data distribution patterns

By specifying multiple synthesis methods in a single YAML configuration file, you can run multiple algorithms at once and compare their performance using the same evaluation metrics.