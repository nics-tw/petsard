---
title: Experiment Name in Reporter
type: docs
weight: 87
prev: docs/developer-guide/logging-configuration
next: docs/developer-guide/test-coverage
---

PETsARD adopts a standardized naming convention for identifying and tracking experiments. This document explains the two main naming formats and their usage.

## Experiment Name Formats

### Experiment Tuple

`full_expt_tuple` is a tuple consisting of a module name and an experiment name:
```python
(module_name, experiment_name)
```

This format is primarily used when creating reports:
```python
# Basic usage
reporter.create({
    ('Synthesizer', 'exp1'): df_synthetic,
    ('Evaluator', 'eval1_[global]'): df_results
})

# Multiple experiment comparison
reporter.create({
    ('Synthesizer', 'exp1_epsilon0.1'): df_low_privacy,
    ('Synthesizer', 'exp2_epsilon1.0'): df_high_privacy,
    ('Synthesizer', 'exp3_epsilon5.0'): df_baseline
})

# Different evaluation levels
reporter.create({
    ('Evaluator', 'eval1_[global]'): global_results,
    ('Evaluator', 'eval1_[columnwise]'): column_results,
    ('Evaluator', 'eval1_[pairwise]'): pair_results
})
```

### Experiment String

`full_expt_name` is a string that concatenates the module name and experiment name with a hyphen:
```
{module_name}-{experiment_name}
```

This format is used for output filenames:
```
# Synthetic data files
petsard_Synthesizer-exp1.csv
petsard_Synthesizer-exp2_epsilon1.0.csv

# Evaluation report files
petsard[Report]_Evaluator-eval1_[global].csv
petsard[Report]_Evaluator-eval1_[columnwise].csv
```

## Naming Examples

### Data Synthesis Experiments

```python
# Comparing different methods
reporter.create({
    ('Synthesizer', 'exp1_ctgan'): ctgan_results,
    ('Synthesizer', 'exp2_tvae'): tvae_results,
    ('Synthesizer', 'exp3_copula'): copula_results
})

# Output files:
# petsard_Synthesizer-exp1_ctgan.csv
# petsard_Synthesizer-exp2_tvae.csv
# petsard_Synthesizer-exp3_copula.csv
```

### Privacy Parameter Experiments

```python
# Privacy parameter adjustment
reporter.create({
    ('Synthesizer', 'exp1_eps0.1_delta1e-5'): low_privacy_df,
    ('Synthesizer', 'exp2_eps1.0_delta1e-5'): med_privacy_df,
    ('Synthesizer', 'exp3_eps10.0_delta1e-5'): high_privacy_df
})

# Output files:
# petsard_Synthesizer-exp1_eps0.1_delta1e-5.csv
# petsard_Synthesizer-exp2_eps1.0_delta1e-5.csv
# petsard_Synthesizer-exp3_eps10.0_delta1e-5.csv
```

### Evaluation Experiments

```python
# Multi-level evaluation
reporter.create({
    ('Evaluator', 'privacy_risk_[global]'): global_privacy,
    ('Evaluator', 'data_quality_[columnwise]'): column_quality,
    ('Evaluator', 'correlation_[pairwise]'): pair_correlation
})

# Output files:
# petsard[Report]_Evaluator-privacy_risk_[global].csv
# petsard[Report]_Evaluator-data_quality_[columnwise].csv
# petsard[Report]_Evaluator-correlation_[pairwise].csv
```

## Naming Guidelines

1. **Module Names**
   - Use standard module names: 'Synthesizer', 'Evaluator', 'Processor', etc.
   - Case sensitivity must match exactly

2. **Experiment Names**
   - Use meaningful prefixes: 'exp', 'eval', 'test', etc.
   - Separate different parts with underscores: method names, parameter settings, etc.
   - Use square brackets for evaluation levels: [global], [columnwise], [pairwise]

3. **Parameter Encoding**
   - Use abbreviations for parameter names: eps (epsilon), del (delta), etc.
   - Use concise representation for values: 1e-5, 0.1, etc.
   - Connect multiple parameters with underscores: eps0.1_del1e-5
