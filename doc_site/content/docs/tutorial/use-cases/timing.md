---
title: Timing
type: docs
weight: 36
prev: docs/tutorial/use-cases/benchmark-datasets
next: docs/tutorial/use-cases
---


When developing and optimizing privacy-preserving data synthesis workflows, you might need to:
  - Monitor execution time for each module in your pipeline
  - Identify performance bottlenecks in your workflow
  - Compare execution times across different configurations
  - Generate timing reports for performance analysis

PETsARD provides built-in timing analysis capabilities that automatically track execution time for each module and step in your workflow. This helps you understand where time is being spent and optimize your pipeline accordingly.

Click the below button to run this example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/use-cases/timing.ipynb)

```yaml
---
Loader:
  data:
    filepath: 'benchmark/adult-income.csv'
Synthesizer:
  default:
    method: 'default'
Evaluator:
  default:
    method: 'default'
Reporter:
  save_timing:
    method: 'save_timing'
    time_unit: 'seconds'
...
```

## Getting Timing Information

After running your workflow, you can access timing information in several ways:

### 1. Using the Executor API

```python
from petsard import Executor

# Run your workflow
executor = Executor('config.yaml')
executor.run()

# Get timing data as a DataFrame
timing_data = executor.get_timing()
print(timing_data)
```

### 2. Saving Timing Reports

You can configure the Reporter to automatically save timing data:

```yaml
Reporter:
  save_timing:
    method: 'save_data'
    data_type: 'timing'
    filepath: 'output/timing_report.csv'
```

## Timing Data Format

The timing data includes the following information:

- **record_id**: Unique timing record identifier
- **module_name**: Name of the executed module (e.g., 'Loader', 'Synthesizer')
- **experiment_name**: Name of the experiment configuration
- **step_name**: Name of the execution step (e.g., 'run', 'fit', 'sample')
- **start_time**: Execution start time (ISO format)
- **end_time**: Execution end time (ISO format)
- **duration_seconds**: Execution duration in seconds (rounded to 2 decimal places by default)
- **duration_precision**: Number of decimal places for duration_seconds (default: 2)

## Performance Analysis Tips

1. **Identify Bottlenecks**: Look for modules with the longest duration_seconds
2. **Compare Configurations**: Run the same workflow with different parameters and compare timing results
3. **Monitor Trends**: Track timing data over multiple runs to identify performance trends
4. **Optimize Workflows**: Use timing insights to optimize module configurations and data processing steps

## Example Analysis

```python
import pandas as pd

# Load timing data
timing_data = executor.get_timing()

# Analyze execution times by module
module_times = timing_data.groupby('module_name')['duration_seconds'].sum()
print("Total execution time by module:")
print(module_times.sort_values(ascending=False))

# Find the slowest operations
slowest_ops = timing_data.nlargest(5, 'duration_seconds')
print("\nSlowest operations:")
print(slowest_ops[['module_name', 'step_name', 'duration_seconds']])
```

This timing analysis capability helps you build more efficient and optimized privacy-preserving data synthesis workflows.