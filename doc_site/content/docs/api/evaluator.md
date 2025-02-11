---
title: Evaluator
type: docs
weight: 57
prev: docs/api/constrainer
next: docs/api/reporter
---


```python
Evaluator(method, custom_method=None, **kwargs)
```

Synthetic data quality evaluator providing privacy risk metrics, data quality assessment, and machine learning utility analysis.

## Parameters

- `method` (str): Evaluation method (case-insensitive):

  - Privacy Risk Assessment (Anonymeter):
    - 'anonymeter-singlingout': Singling out risk
    - 'anonymeter-linkability': Linkability risk
    - 'anonymeter-inference': Inference risk

  - Data Quality Assessment (SDMetrics):
    - 'sdmetrics-diagnosticreport': Data validity report
    - 'sdmetrics-qualityreport': Data quality report

  - Machine Learning Utility Assessment (MLUtility):
    - 'mlutility-regression': Regression utility
    - 'mlutility-classification': Classification utility
    - 'mlutility-cluster': Clustering utility

  - 'default': Uses 'sdmetrics-qualityreport'

- `custom_method` (dict, optional): Custom evaluation method

  - `filepath` (str): Evaluation method file path
  - `method` (str): Evaluation method name

## Examples

```python
from petsard import Evaluator


# Privacy risk assessment
eval = Evaluator('anonymeter-singlingout', n_attacks=2000)
eval.create({
    'ori': train_data,
    'syn': synthetic_data,
    'control': test_data
})
eval.eval()
privacy_risk = eval.get_global()

# Data quality assessment
eval = Evaluator('sdmetrics-qualityreport')
eval.create({
    'ori': train_data,
    'syn': synthetic_data
})
eval.eval()
quality_score = eval.get_global()
```

## Methods

### `create()`

```python
eval.create(data)
```

**Parameters**

- `data` (dict): Evaluation data
  - For Anonymeter and MLUtility:
    - 'ori': Original data used for synthesis (pd.DataFrame)
    - 'syn': Synthetic data (pd.DataFrame)
    - 'control': Control data not used for synthesis (pd.DataFrame)
  - For SDMetrics:
    - 'ori': Original data (pd.DataFrame)
    - 'syn': Synthetic data (pd.DataFrame)

**Returns**

None

### `eval()`

Perform evaluation.

**Parameters**

None

**Returns**

None. Results stored in `result` attribute.

### `get_global()`

Get global evaluation results.

**Parameters**

None

**Returns**

- pd.DataFrame: Single row dataframe representing overall dataset evaluation

### `get_columnwise()`

Get column-wise evaluation results.

**Parameters**

None

**Returns**

- pd.DataFrame: Each row represents evaluation results for one column

### `get_pairwise()`

取得欄位配對評估結果。

**Parameters**

None

**Returns**

- pd.DataFrame: Each row represents evaluation results for a column pair

## Attributes

- `result`: Evaluation results
- `config`: Evaluator configuration containing `method` and `method_code`