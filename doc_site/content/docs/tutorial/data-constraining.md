---
title: Data Constraining
type: docs
weight: 12
prev: docs/tutorial/default-synthesis
next: docs/tutorial/advanced-synthesis
sidebar:
  open: true
---

Constrain synthetic data through field value rules, field combinations, and NA handling strategies.
Current implementation supports three types of constraints: field constraints, field combinations, and NA groups.

Click the below button to run this example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/data-constraining.ipynb)

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
Constrainer:
  demo:
    nan_groups:
      workclass: ('delete', 'occupation')  # Delete row if workclass is NA
      occupation: ('erase', ['income'])    # Set income to NA if occupation is NA
      income: ('copy', 'salary')          # Copy income to salary if salary is NA
    field_constraints:
      - "age >= 18 & age <= 65"
      - "hours-per-week >= 20 & hours-per-week <= 60"
    field_combinations:
      -
        - {'education': 'income'}
        - {'Doctorate': ['>50K'], 'Masters': ['>50K', '<=50K']}
Postprocessor:
  demo:
    method: 'default'
Reporter:
  output:
    method: 'save_data'
    source: 'Constrainer'
...
```