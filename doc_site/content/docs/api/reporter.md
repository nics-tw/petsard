---
title: Reporter
type: docs
weight: 60
prev: docs/api/describer
next: docs/api/operator
---


```python
Reporter(method, **kwargs)
```

Generates output files for experiment results and evaluation reports.

## Parameters

- `method` (str): Report generation method
  - 'save_data': Save dataset to CSV
    - Additional parameter required:
      - `source` (str | List[str]): Target module or experiment name
  - 'save_report': Generate evaluation report
    - Additional parameters required:
      - `granularity` (str): Report detail level ('global', 'columnwise', 'pairwise')
      - `eval` (str | List[str], optional): Target evaluation experiment name
- `output` (str, optional): Output filename prefix
  - Default: 'petsard'

## Examples

```python
from petsard import Reporter


# Save synthetic data
reporter = Reporter('save_data', source='Synthesizer')
reporter.create({('Synthesizer', 'exp1'): synthetic_df})
reporter.report()  # Creates: petsard_Synthesizer[exp1].csv

# Generate evaluation report
reporter = Reporter('save_report', granularity='global')
reporter.create({('Evaluator', 'eval1_[global]'): results})
reporter.report()  # Creates: petsard[Report]_[global].csv
```

## Methods

### `create()`

Initialize reporter with data.

**Parameters**

- `data` (dict): Report data where:
  - Keys: Experiment tuples (module_name, experiment_name, ...)
  - Values: Data to be reported (pd.DataFrame)
  - Optional 'exist_report' key for merging with previous results

### `report()`

Generate and save report as CSV. Output filename format:
- For save_data: `{output}_{module-expt_name-pairs}.csv`
- For save_report: `{output}[Report]_{eval}_[{granularity}].csv`

## Attributes
- `result`: Report results
  - For save_data: Dictionary of DataFrames
  - For save_report: Report metadata and content
- `config`: Reporter configuration