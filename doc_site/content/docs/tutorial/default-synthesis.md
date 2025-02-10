---
title: Default Synthesis
type: docs
weight: 12
prev: docs/tutorial/yaml-config
next: docs/tutorial/default-synthesis-default-evaluation
---


The simplest way to generate privacy-enhanced synthetic data.
Current default synthesis uses Gaussian Copula from SDV.

Click the below button to run this example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/default-synthesis.ipynb)

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
    source: 'Synthesizer'
...
```