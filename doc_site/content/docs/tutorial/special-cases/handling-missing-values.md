---
title: Handling Missing Values
type: docs
weight: 18
prev: docs/tutorial/special-cases/comparing-synthesizers
next: docs/tutorial/special-cases/benchmark-datasets
sidebar:
  open: true
---


Before synthesizing data, you need to handle missing values in your dataset. `PETsARD` offers several methods for handling missing values.

Click the below button to run this example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/handling-missing-values.ipynb)

```yaml
---
Loader:
  data:
    filepath: 'benchmark/adult-income.csv'
Preprocessor:
  drop:
    method: 'default'
    config:
      missing:
        age: 'missing_drop'      # Drop rows with missing values
        income: 'missing_drop'
  fill:
    method: 'default'
    config:
      missing:
        age: 'missing_mean'      # Fill with mean value
        workclass: 'missing_mode'  # Fill with mode
  simple:
    method: 'default'
    config:
      missing:
        age:
          method: 'missing_simple'  # Fill with specified value
          value: 0
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
  output:
    method: 'save_data'
    source: 'Synthesizer'
  save_report_global:
    method: 'save_report'
    granularity: 'global'
...
```

## Missing Value Handling Methods

1. Drop Missing Values (`missing_drop`)

  - Removes rows containing missing values
  - Suitable when missing values are rare
  - Note: May lose important information

2. Statistical Imputation

  - Mean imputation (`missing_mean`): Fill with column mean
  - Median imputation (`missing_median`): Fill with column median
  - Mode imputation (`missing_mode`): Fill with most frequent value
  - Suitable for different data types:
    - Use mean or median for numerical data
    - Use mode for categorical data

3. Custom Imputation (`missing_simple`)

  - Fill missing values with a specified value
  - Requires setting the `value` parameter
  - Suitable when specific business logic applies

You can use different methods for different columns by specifying the appropriate configuration in your settings file.