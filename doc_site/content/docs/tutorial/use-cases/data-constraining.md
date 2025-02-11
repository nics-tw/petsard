---
title: Data Constraining
type: docs
weight: 31
prev: docs/tutorial/use-cases/comparing-synthesizers
next: docs/tutorial/use-cases/custom-evaluation
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
Postprocessor:
  demo:
    method: 'default'
Constrainer:
  demo:
    nan_groups:
      # Delete entire row when workclass is NA
      workclass: 'delete'
      # Set income to NA if occupation is NA
      occupation:
        'erase':
          - 'income'
      # Copy educational-num value to age when educational-num exists but age is NA
      age:
        'copy':
          'educational-num'
    field_constraints:
      - "age >= 18 & age <= 65" # age limits to 18~65
      - "hours-per-week >= 20 & hours-per-week <= 60" # hours per week limits to 20 ~ 60
    field_combinations:
      -
        - {'education': 'income'}
        - {'Doctorate': ['>50K'], 'Masters': ['>50K', '<=50K']}
Reporter:
  output:
    method: 'save_data'
    source: 'Constrainer'
...
```