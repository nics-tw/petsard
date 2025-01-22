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

The simplest way to generate privacy-enhanced synthetic data:

```yaml
---
Loader:
    data:
        filepath: 'benchmark/adult-income.csv'
Synthesizer:
    demo:
        method: 'default'
Reporter:
    output:
        method: 'save_data'
        output: 'result'
        source: 'Synthesizer'
...
```

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/628-guide---tutorial/demo/basic-usage.ipynb)