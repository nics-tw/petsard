---
title: Reporter
type: docs
weight: 60
prev: docs/api/describer
next: docs/api/adapter
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
      - `granularity` (str | List[str]): Report detail level
        - Single granularity: 'global', 'columnwise', 'pairwise', 'details', 'tree'
        - Multiple granularities: ['global', 'columnwise'] or ['details', 'tree']
      - `eval` (str | List[str], optional): Target evaluation experiment name
  - 'save_timing': Save timing information
    - Additional parameters optional:
      - `time_unit` (str): Time unit ('seconds', 'minutes', 'hours', 'days')
      - `module` (str | List[str]): Filter by specific modules
- `output` (str, optional): Output filename prefix
  - Default: 'petsard'

## Examples

```python
from petsard import Reporter


# Save synthetic data
reporter = Reporter('save_data', source='Synthesizer')
reporter.create({('Synthesizer', 'exp1'): synthetic_df})
reporter.report()  # Creates: petsard_Synthesizer[exp1].csv

# Generate evaluation report (single granularity)
reporter = Reporter('save_report', granularity='global')
reporter.create({('Evaluator', 'eval1_[global]'): results})
reporter.report()  # Creates: petsard[Report]_[global].csv

# Generate evaluation report (multiple granularities)
reporter = Reporter('save_report', granularity=['global', 'columnwise'])
reporter.create({
    ('Evaluator', 'eval1_[global]'): global_results,
    ('Evaluator', 'eval1_[columnwise]'): columnwise_results
})
reporter.report()  # Creates multiple reports for each granularity

# Generate evaluation report with new granularity types
reporter = Reporter('save_report', granularity=['details', 'tree'])
reporter.create({
    ('Evaluator', 'eval1_[details]'): details_results,
    ('Evaluator', 'eval1_[tree]'): tree_results
})
reporter.report()  # Creates detailed and tree-structured reports

# Save timing information
reporter = Reporter('save_timing', time_unit='minutes', module=['Loader', 'Synthesizer'])
reporter.create({'timing_data': timing_df})
reporter.report()  # Creates: petsard_timing_report.csv
```

## Methods

### `create(data)`

Initialize reporter with data using functional design pattern.

**Parameters**

- `data` (dict): Report data where:
  - Keys: Experiment tuples (module_name, experiment_name, ...)
  - Values: Data to be reported (pd.DataFrame)
  - Optional 'exist_report' key for merging with previous results
  - For save_timing: 'timing_data' key with timing DataFrame

**Returns**

- `dict | pd.DataFrame | None`: Processed data ready for reporting
  - For save_data: Dictionary of processed DataFrames
  - For save_report: Dictionary with granularity-specific results
  - For save_timing: DataFrame with timing information
  - Returns None if no data to process

### `report(processed_data)`

Generate and save report as CSV using functional design pattern.

**Parameters**

- `processed_data`: Output from `create()` method

**Output filename formats:**
- For save_data: `{output}_{module-expt_name-pairs}.csv`
- For save_report: `{output}[Report]_{eval}_[{granularity}].csv`
- For save_timing: `{output}_timing_report.csv`

## Granularity Types

### Traditional Granularities
- `global`: Overall summary statistics
- `columnwise`: Column-by-column analysis
- `pairwise`: Pairwise column relationships

### New Granularity Types (v2.0+)
- `details`: Detailed breakdown with additional metrics
- `tree`: Hierarchical tree-structured analysis

## Multi-Granularity Support

The Reporter now supports processing multiple granularities in a single operation:

```python
# Process multiple granularities simultaneously
reporter = Reporter('save_report', granularity=['global', 'columnwise', 'details'])
result = reporter.create(evaluation_data)
reporter.report(result)  # Generates separate reports for each granularity
```

## Functional Design

The Reporter uses a functional "throw out and throw back in" design pattern:
- `create()` processes data without storing it in instance variables
- `report()` takes the processed data and generates output files
- No internal state is maintained, reducing memory usage