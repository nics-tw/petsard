---
title: Describer
type: docs
weight: 59
prev: docs/api/evaluator
next: docs/api/reporter
---

```python
Describer(config)
```

Generate descriptive statistics for datasets.

## Parameters

- `config` (dict): Descriptive statistics configuration
 - `method` (str): Operation name
   - 'default': Use default set of statistics methods
 - `describe` (list): List of statistics methods to apply
   - See supported methods table below
   - For percentile, use dictionary format: `{'percentile': k}`

## Examples

```python
from petsard import Describer


# Using default descriptive methods
desc = Describer(method='default')

# Using custom descriptive methods
desc = Describer(
    method='default',
    describe_method=['mean', 'median', 'std', 'percentile'],
    percentile=0.95,
)

# Analysis
desc.create()
desc_result: dict[str, pd.DataFrame] = desc.eval({'data': df})

# Get results
global_stats: pd.DataFrame = desc_result.get('global')      # Global statistics
column_stats: pd.DataFrame = desc_result.get('columnwise')  # Column-wise statistics
pairwise_stats: pd.DataFrame = desc_result.get('pairwise')  # Pairwise statistics
```

## Methods

### `create()`

Initialize descriptor.

**Parameters**

None

**Returns**

None

### `eval()`

Perform descriptive statistical analysis.

**Parameters**

- `data` (dict): Data to analyze
  - Format: `{'data': pd.DataFrame}`

**Returns**

`(dict[str, pd.DataFrame])`, varies by module:
  - 'global': Single row dataframe representing overall dataset desciption results
  - 'columnwise': Column-level desciption results, each row representing desciption results for one column
  - 'pairwise': Column pair desciption results, each row representing desciption results for a pair of columns

## Appendix: Supported Methods

### Overview

Descriptive statistics are divided into three levels:
- Global analysis: Calculate overall dataset properties (e.g., row count)
- Column analysis: Calculate statistics for each column (e.g., mean, standard deviation)
- Pairwise analysis: Calculate relationships between columns (e.g., correlation)

### Supported Methods

| Level | Method | Parameter | Description |
| :---: | :---: | :---: | :--- |
| Global | `DescriberRowCount` | 'row_count' | Calculate number of rows |
| Global | `DescriberColumnCount` | 'col_count' | Calculate number of columns |
| Global | `DeescriberGlobalNA` | 'global_na_count' | Calculate rows containing NA |
| Column | `DescriberMean` | 'mean' | Calculate mean |
| Column | `DescriberMedian` | 'median' | Calculate median |
| Column | `DescriberStd` | 'std' | Calculate standard deviation |
| Column | `DescriberVar` | 'var' | Calculate variance |
| Column | `DescriberMin` | 'min' | Calculate minimum |
| Column | `DescriberMax` | 'max' | Calculate maximum |
| Column | `DescriberKurtosis` | 'kurtosis' | Calculate kurtosis |
| Column | `DescriberSkew` | 'skew' | Calculate skewness |
| Column | `DescriberQ1` | 'q1' | Calculate first quartile |
| Column | `DescriberQ3` | 'q3' | Calculate third quartile |
| Column | `DescriberIQR` | 'iqr' | Calculate interquartile range |
| Column | `DescriberRange` | 'range' | Calculate range |
| Column | `DescriberPercentile` | 'percentile' | Calculate custom percentile |
| Column | `DescriberColNA` | 'col_na_count' | Calculate NA count per column |
| Column | `DescriberNUnique` | 'nunique' | Calculate number of unique values |
| Pairwise | `DescriberCov` | 'cov' | Calculate covariance |
| Pairwise | `DescriberCorr` | 'corr' | Calculate correlation |