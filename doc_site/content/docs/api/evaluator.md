---
title: Evaluator
type: docs
weight: 58
prev: docs/api/constrainer
next: docs/api/describer
---


```python
Evaluator(method, **kwargs)
```

Synthetic data quality evaluator providing privacy risk metrics, data quality assessment, and machine learning utility analysis.

## Parameters

- `method` (`str`): Evaluation method (case-insensitive):

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
  - 'stats': Statistical evaluation, comparing the statistical differences before and after synthesis
  - 'custom_method': Custom evaluation method. To be used with:
    - `module_path` (str): Evaluation method file path
    - `class_name` (str): Evaluation method name

## Examples

```python
from petsard import Evaluator


eval_result: dict[str, pd.DataFrame] = None

# Privacy risk assessment
eval = Evaluator('anonymeter-singlingout')
eval.create()
eval_result = eval.eval({
    'ori': train_data,
    'syn': synthetic_data,
    'control': test_data
})
privacy_risk: pd.DataFrame = eval_result['global']

# Data quality assessment
eval = Evaluator('sdmetrics-qualityreport')
eval.create()
eval_result = eval.eval({
    'ori': train_data,
    'syn': synthetic_data
})
quality_score: pd.DataFrame = eval_result['global']
```

## Methods

### `create()`

Initial evaluator

**Parameters**

None

**Returns**

None

### `eval()`

```python
eval.eval(data)
```

Perform evaluation.

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

`(dict[str, pd.DataFrame])`, varies by module:
  - 'global': Single row dataframe representing overall dataset evaluation results
  - 'columnwise': Column-level evaluation results, each row representing evaluation results for one column
  - 'pairwise': Column pair evaluation results, each row representing evaluation results for a pair of columns
  - 'details': Other detailed information

## Attributes

- `config` (`EvaluatorConfig`): Evaluator configuration containing `method` and `method_code`

## Appendix: Supported Evaluation Methods

### Supported Evaluation Methods

The evaluator supports three major categories of evaluation methods:

- **Privacy Risk Assessment** used to evaluate the privacy protection level of synthetic data. Including:
  - **Singling Out Risk**: Evaluates whether specific individuals can be identified from the data
  - **Linkability Risk**: Evaluates whether the same individual can be linked across different datasets
  - **Inference Risk**: Evaluates whether other attributes can be inferred from known information

- **Data Fidelity Assessment** used to evaluate the fidelity of synthetic data. Including:
  - **Diagnostic Report**: Examines data structure and basic characteristics
  - **Quality Report**: Evaluates the similarity of statistical distributions

- **Data Utility Assessment** used to evaluate the practical value of synthetic data. Including:
  - **Classification Utility**: Compares classification model performance
  - **Regression Utility**: Compares regression model performance
  - **Clustering Utility**: Compares clustering results

- **Statistical Assessment** used to compare statistical differences before and after synthesis. Including:
  - **Statistical Comparison**: Compares statistical measures such as mean, standard deviation, median, etc.
  - **Distribution Comparison**: Compares distribution differences such as Jensen-Shannon divergence

- **Custom Assessment** used to integrate user-defined evaluation methods.

| Evaluation Type | Evaluation Method | Method Name |
| :---: | :---: | :---: |
| Privacy Risk Assessment | Singling Out Risk | anonymeter-singlingout |
| Privacy Risk Assessment | Linkability Risk | anonymeter-linkability |
| Privacy Risk Assessment | Inference Risk | anonymeter-inference |
| Data Fidelity Assessment | Diagnostic Report | sdmetrics-diagnosticreport |
| Data Fidelity Assessment | Quality Report | sdmetrics-qualityreport |
| Data Utility Assessment | Classification Utility | mlutility-classification |
| Data Utility Assessment | Regression Utility | mlutility-regression |
| Data Utility Assessment | Clustering Utility | mlutility-cluster |
| Statistical Assessment | Statistical Comparison | stats |
| Custom Assessment | Custom Method | custom_method |

### Privacy Risk Assessment

#### Singling Out Risk Assessment

Evaluates whether specific individual records can be identified from the data. The evaluation result is a score from 0 to 1, with higher numbers representing greater privacy risk.

**Parameters**

- 'n_attacks' (`int`, default=2000): Number of attack attempts (unique queries)
- 'n_cols' (`int`, default=3): Number of columns used in each query
- 'max_attempts' (`int`, default=500000): Maximum number of attempts to find successful attacks

**Returns**

- `pd.DataFrame`: Evaluation result dataframe containing the following columns:
  - 'risk': Privacy risk score (0-1)
  - 'risk_CI_btm': Lower bound of privacy risk confidence interval
  - 'risk_CI_top': Upper bound of privacy risk confidence interval
  - 'attack_rate': Main privacy attack success rate
  - 'attack_rate_err': Error of main privacy attack success rate
  - 'baseline_rate': Baseline privacy attack success rate
  - 'baseline_rate_err': Error of baseline privacy attack success rate
  - 'control_rate': Control group privacy attack success rate
  - 'control_rate_err': Error of control group privacy attack success rate

#### Linkability Risk Assessment

Evaluates whether records belonging to the same individual can be linked across different datasets. The evaluation result is a score from 0 to 1, with higher numbers representing greater privacy risk.

**Parameters**

- 'n_attacks' (`int`, default=2000): Number of attack attempts
- 'max_n_attacks' (`bool`, default=False): Whether to force using the maximum number of attacks
- 'aux_cols' (`Tuple[List[str], List[str]]`): Auxiliary information columns, for example:
    ```python
    aux_cols = [
        ['gender', 'zip_code'],  # Public data
        ['age', 'medical_history']    # Private data
    ]
    ```
- 'n_neighbors' (`int`, default=10): Number of nearest neighbors to consider

**Returns**

- `pd.DataFrame`: Evaluation result dataframe in the same format as the singling out risk assessment

#### Inference Risk Assessment

Evaluates whether other attributes can be inferred from known information. The evaluation result is a score from 0 to 1, with higher numbers representing greater privacy risk.

**Parameters**

- 'n_attacks' (`int`, default=2000): Number of attack attempts
- 'max_n_attacks' (`bool`, default=False): Whether to force using the maximum number of attacks
- 'secret' (`str`): The attribute to be inferred
- 'aux_cols' (`List[str]`, optional): Columns used for inference, defaults to all columns except the 'secret'

**Returns**

- `pd.DataFrame`: Evaluation result dataframe in the same format as the singling out risk assessment

### Data Fidelity Assessment

#### Diagnostic Report

Validates the structure and basic characteristics of synthetic data.

**Parameters**

None

**Returns**

- `pd.DataFrame`: Evaluation result dataframe containing the following columns:
  - 'Score': Overall diagnostic score
  - 'Data Validity': Data validity score
    - 'KeyUniqueness': Primary key uniqueness
    - 'BoundaryAdherence': Numerical range compliance
    - 'CategoryAdherence': Category compliance
  - 'Data Structure': Data structure score
    - 'Column Existence': Column existence
    - 'Column Type': Column type compliance

#### Quality Report

Evaluates the statistical similarity between original and synthetic data.

**Parameters**

None

**Returns**

- `pd.DataFrame`: Evaluation result dataframe containing the following columns:
  - 'Score': Overall validity score
  - 'Column Shapes': Column distribution similarity
    - 'KSComplement': Continuous variable distribution similarity
    - 'TVComplement': Categorical variable distribution similarity
  - 'Column Pair Trends': Column relationship preservation
    - 'Correlation Similarity': Correlation preservation
    - 'Contingency Similarity': Contingency table similarity

### Data Utility Assessment

#### Classification Utility Assessment

Compares the prediction performance of classification models on original and synthetic data, using logistic regression, support vector machines, random forests, and gradient boosting (all with default parameters).

**Parameters**

- 'target' (`str`): Classification target column

**Returns**

- `pd.DataFrame`: Evaluation result dataframe containing the following columns:
  - 'ori_mean': Original data model average F1 score
  - 'ori_std': Original data model F1 standard deviation
  - 'syn_mean': Synthetic data model average F1 score
  - 'syn_std': Synthetic data model F1 standard deviation
  - 'diff': Improvement value of synthetic data relative to original data

#### Regression Utility Assessment

Compares the prediction performance of regression models on original and synthetic data, using linear regression, random forest regression, and gradient boosting regression (all with default parameters).

**Parameters**

- 'target' (`str`): Prediction target column (numerical)

**Returns**

- `pd.DataFrame`: Evaluation result dataframe containing the following columns:
  - 'ori_mean': Original data model average R² score
  - 'ori_std': Original data model R² standard deviation
  - 'syn_mean': Synthetic data model average R² score
  - 'syn_std': Synthetic data model R² standard deviation
  - 'diff': Improvement value of synthetic data relative to original data

#### Clustering Utility Assessment

Compares the clustering results of K-means clustering algorithm (with default parameters) on original and synthetic data.

**Parameters**

- 'n_clusters' (`list`, default=[4, 5, 6]): List of cluster numbers

**Returns**

- `pd.DataFrame`: Evaluation result dataframe containing the following columns:
  - 'ori_mean': Original data average silhouette coefficient
  - 'ori_std': Original data silhouette coefficient standard deviation
  - 'syn_mean': Synthetic data average silhouette coefficient
  - 'syn_std': Synthetic data silhouette coefficient standard deviation
  - 'diff': Improvement value of synthetic data relative to original data

### Statistical Evaluation

Statistical evaluation compares statistical differences before and after data synthesis, supporting various statistical methods such as mean, standard deviation, median, minimum, maximum, number of unique values, and Jensen-Shannon divergence. It provides appropriate evaluation methods for both numerical and categorical data.

**Parameters**

- 'stats_method' (`list[str]`, default=["mean", "std", "median", "min", "max", "nunique", "jsdivergence"]): List of statistical methods
- 'compare_method' (`str`, default="pct_change"): Comparison method, options include "diff" (difference) or "pct_change" (percentage change)
- 'aggregated_method' (`str`, default="mean"): Aggregation method
- 'summary_method' (`str`, default="mean"): Summary method

**Return Value**

- `pd.DataFrame`: Dataframe containing statistical comparison results, including:
  - Statistical measures for each column (original and synthetic)
  - Differences or percentage changes between them
  - Overall score

### Custom Evaluation

Allows users to implement and integrate custom evaluation methods by specifying external module paths and class names to load custom evaluation logic.

**Parameters**

- 'module_path' (`str`): File path to the custom evaluation module
- 'class_name' (`str`): Name of the custom evaluation class
- Other parameters depending on the requirements of the custom evaluator

**Return Value**

- Depends on the implementation of the custom evaluator, but must follow the standard evaluator interface, returning a format of `dict[str, pd.DataFrame]`

**Required Methods for Custom Evaluators**

- `__init__(config)`: Initialization method
- `eval(data)`: Evaluation method that receives a data dictionary and returns evaluation results

**Required Attributes for Custom Evaluators**

- `REQUIRED_INPUT_KEYS`: List of required input data keys
- `AVAILABLE_SCORES_GRANULARITY`: List of supported evaluation granularities (such as "global", "columnwise")