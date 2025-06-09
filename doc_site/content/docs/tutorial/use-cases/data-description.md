---
title: Data Description
type: docs
weight: 16
prev: docs/tutorial/use-cases
next: docs/tutorial/use-cases/data-preprocessing
---


Before data synthesizing, you might want to understand your data first. `PETsARD` provides a description module that analyzes your data at three different granularities.

Click the below button to run this example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/use-cases/data-description.ipynb)

```yaml
---
Loader:
  data:
    filepath: 'benchmark/adult-income.csv'
Describer:
  summary:
    method: 'default'
Reporter:
  save_report_global:
    method: 'save_report'
    granularity: 'global'
  save_report_columnwise:
    method: 'save_report'
    granularity: 'columnwise'
  save_report_pairwise:
    method: 'save_report'
    granularity: 'pairwise'
...
```

## Statistics at Three Granularities

1. Global Statistics (`global`)

  - Provides basic information about the entire dataset
  - Includes total row count, column count, and missing value count

2. Column Statistics (`columnwise`)

  - Individual statistics for each column
  - Numerical columns: mean, median, standard deviation, min/max values, quartiles, etc.
  - Categorical columns: number of categories, missing value count

3. Pairwise Statistics (`pairwise`)

  - Analyzes relationships between columns
  - Primarily provides correlation coefficients between numerical columns