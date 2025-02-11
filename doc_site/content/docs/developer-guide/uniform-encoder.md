---
title: Uniform Encoder
type: docs
weight: 83
prev: docs/developer-guide/benchmark-datasets
next: docs/developer-guide/anonymeter
---

When converting categorical variables to continuous values, the Uniform Encoder can provide better performance for generative models. This method, proposed by [datacebo](https://datacebo.com/), maps each category to a specific range in a uniform distribution, with the range size determined by the relative proportion of each category in the data.

## Principles

**Core Concepts**

- Map discrete categories to [0,1] interval
- Determine mapping ranges based on category frequencies
- Generate random values within ranges as encoded results

**Advantages**

1. Converts discrete distributions to continuous, facilitating modeling
2. Fixed value range [0,1], simplifying category restoration
3. Preserves original distribution information, with more frequent categories having larger sampling probabilities

## Implementation Example

Consider a categorical variable with three categories 'a', 'b', 'c', appearing in proportions 1:3:1:

```python
mapping = {
   'a': [0.0, 0.2),  # 20% range
   'b': [0.2, 0.8),  # 60% range
   'c': [0.8, 1.0]   # 20% range
}
```

**Encoding Process**

- Category 'a' → Random value in [0.0, 0.2)
- Category 'b' → Random value in [0.2, 0.8)
- Category 'c' → Random value in [0.8, 1.0]

**Restoration Process**

- Check which range contains the value
- Map back to corresponding category

## Usage Guidelines

- Best suited for features with fewer categories
- Particularly effective for imbalanced category distributions
- Can be combined with other preprocessing methods (e.g., scaling)

## References

- [Improving Synthetic Data Quality with the Uniform Encoder](https://datacebo.com/blog/improvement-uniform-encoder/)

## Appx.: Available Evaluation Methods

### Available Evaluation Methods

The evaluator supports three main types of evaluation methods:

- **Privacy Risk Assessment** evaluates the level of privacy protection in synthetic data. Including:
  - **Singling Out Risk**: Assesses the ability to identify specific individuals in the data
  - **Linkability Risk**: Assesses the ability to link records of the same individual across different datasets
  - **Inference Risk**: Assesses the ability to infer attributes from known information

- **Data Fidelity Assessment** evaluates the fidelity of synthetic data. Including:
  - **Diagnostic Report**: Examines data structure and basic properties
  - **Quality Report**: Evaluates statistical distribution similarity

- **Data Utility Assessment** evaluates the practical value of synthetic data. Including:
  - **Classification Utility**: Compares classification model performance
  - **Regression Utility**: Compares regression model performance
  - **Clustering Utility**: Compares clustering results

| Assessment Type | Method | Method Name |
| :---: | :---: | :---: |
| Privacy Risk Assessment | Singling Out Risk | anonymeter-singlingout |
| Privacy Risk Assessment | Linkability Risk | anonymeter-linkability |
| Privacy Risk Assessment | Inference Risk | anonymeter-inference |
| Data Fidelity Assessment | Diagnostic Report | sdmetrics-diagnosticreport |
| Data Fidelity Assessment | Quality Report | sdmetrics-qualityreport |
| Data Utility Assessment | Classification Utility | mlutility-classification |
| Data Utility Assessment | Regression Utility | mlutility-regression |
| Data Utility Assessment | Clustering Utility | mlutility-cluster |

### Privacy Risk Assessment

#### Singling Out Risk Assessment

Evaluates the ability to identify records of specific individuals in the data. Results are scored from 0 to 1, where higher numbers indicate greater privacy risk.

**Parameters**

- n_attacks (int, default=2000): Number of attack attempts (unique queries)
- n_cols (int, default=3): Number of columns used per query
- max_attempts (int, default=500000): Maximum attempts to find successful attacks

**Returns**

- pd.DataFrame: Evaluation results dataframe containing:
  - risk: Privacy risk score (0-1)
  - risk_CI_btm: Privacy risk confidence interval lower bound
  - risk_CI_top: Privacy risk confidence interval upper bound
  - attack_rate: Main privacy attack success rate
  - attack_rate_err: Main privacy attack success rate error
  - baseline_rate: Baseline privacy attack success rate
  - baseline_rate_err: Baseline privacy attack success rate error
  - control_rate: Control group privacy attack success rate
  - control_rate_err: Control group privacy attack success rate error

#### Linkability Risk Assessment

Evaluates the ability to link records belonging to the same individual across different datasets. Results are scored from 0 to 1, where higher numbers indicate greater privacy risk.

**Parameters**

- n_attacks (int, default=2000): Number of attack attempts
- max_n_attacks (bool, default=False): Whether to force maximum number of attacks
- aux_cols (Tuple[List[str], List[str]]): Auxiliary information columns, for example:
    ```python
    aux_cols = [
        ['gender', 'zip_code'],  # public data
        ['age', 'medical_history']  # private data
    ]
    ```
- n_neighbors (int, default=10): Number of nearest neighbors to consider

**Returns**

- pd.DataFrame: Evaluation results dataframe in the same format as singling out risk assessment

#### Inference Risk Assessment

Evaluates the ability to infer attributes from known information. Results are scored from 0 to 1, where higher numbers indicate greater privacy risk.

**Parameters**

- n_attacks (int, default=2000): Number of attack attempts
- max_n_attacks (bool, default=False): Whether to force maximum number of attacks
- secret (str): Column to be inferred
- aux_cols (List[str], optional): Columns used for inference, defaults to all columns except secret

**Returns**

- pd.DataFrame: Evaluation results dataframe in the same format as singling out risk assessment

### Data Fidelity Assessment

#### Diagnostic Report

Validates synthetic data structure and basic properties.

**Parameters**

None

**Returns**

- pd.DataFrame: Evaluation results dataframe containing:
  - Score: Overall diagnostic score
  - Data Validity: Data validity score
    - KeyUniqueness: Primary key uniqueness
    - BoundaryAdherence: Numeric range compliance
    - CategoryAdherence: Category compliance
  - Data Structure: Data structure score
    - Column Existence: Column presence
    - Column Type: Column type compliance

#### Quality Report

Evaluates statistical similarity between original and synthetic data.

**Parameters**

None

**Returns**

- pd.DataFrame: Evaluation results dataframe containing:
  - Score: Overall quality score
  - Column Shapes: Column distribution similarity
    - KSComplement: Continuous variable distribution similarity
    - TVComplement: Categorical variable distribution similarity
  - Column Pair Trends: Column relationship preservation
    - Correlation Similarity: Correlation preservation
    - Contingency Similarity: Contingency table similarity

### Data Utility Assessment

#### Classification Utility Assessment

Compares classification model performance between original and synthetic data using logistic regression, support vector machine, random forest, and gradient boosting (all with default parameters).

**Parameters**

- target (str): Classification target column

**Returns**

- pd.DataFrame: Evaluation results dataframe containing:
  - ori_mean: Original data model average F1 score
  - ori_std: Original data model F1 score standard deviation
  - syn_mean: Synthetic data model average F1 score
  - syn_std: Synthetic data model F1 score standard deviation
  - diff: Synthetic data improvement over original data

#### Regression Utility Assessment

Compares regression model performance between original and synthetic data using linear regression, random forest regression, and gradient boosting regression (all with default parameters).

**Parameters**

- target (str): Prediction target column (numeric)

**Returns**

- pd.DataFrame: Evaluation results dataframe containing:
  - ori_mean: Original data model average R² score
  - ori_std: Original data model R² score standard deviation
  - syn_mean: Synthetic data model average R² score
  - syn_std: Synthetic data model R² score standard deviation
  - diff: Synthetic data improvement over original data

#### Clustering Utility Assessment

Compares K-means clustering algorithm (with default parameters) results between original and synthetic data.

**Parameters**

- n_clusters (list, default=[4, 5, 6]): List of cluster counts

**Returns**

- pd.DataFrame: Evaluation results dataframe containing:
  - ori_mean: Original data average silhouette score
  - ori_std: Original data silhouette score standard deviation
  - syn_mean: Synthetic data average silhouette score
  - syn_std: Synthetic data silhouette score standard deviation
  - diff: Synthetic data improvement over original data