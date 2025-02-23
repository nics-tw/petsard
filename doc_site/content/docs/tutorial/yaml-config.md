---
title: YAML Configuration
type: docs
weight: 11
prev: docs/tutorial
next: docs/tutorial/default-synthesis
---

YAML is a human-readable data serialization format used by PETsARD for experiment configuration. This document explains how to structure your YAML configurations effectively.

## Basic Structure

YAML configurations in PETsARD follow a three-level hierarchy:

```yaml
ModuleName:           # First level: Module
    ExperimentName:   # Second level: Experiment
        param1: value # Third level: Parameters
        param2: value
```

### Module Level

The top level defines the processing modules in execution order:

- Loader: Data loading
- Preprocessor: Data preprocessing
- Synthesizer: Data synthesis
- Postprocessor: Data postprocessing
- Constrainer: Data constraining
- Evaluator: Result evaluation
- Reporter: Report generation

### Experiment Level

Each module can have multiple experiment configurations:

```yaml
Synthesizer:
    exp1_ctgan:        # First experiment
        method: ctgan
        epochs: 100
    exp2_tvae:         # Second experiment
        method: tvae
        epochs: 200
```

### Parameter Level

Parameters follow each module's specific requirements:

```yaml
Loader:
    demo_load:
        filepath: 'data/sample.csv'
        na_values:
            age: '?'
            income: 'unknown'
        column_types:
            category:
                - gender
                - occupation
```

## Execution Flow

When multiple experiments are defined, PETsARD executes them in a depth-first order:
```
Loader -> Preprocessor -> Synthesizer -> Postprocessor -> Constrainer -> Evaluator -> Reporter
```

For example:
```yaml
Loader:
    load_a:
        filepath: 'data1.csv'
    load_b:
        filepath: 'data2.csv'
Synthesizer:
    syn_ctgan:
        method: ctgan
    syn_tvae:
        method: tvae
```

This creates four experiment combinations:
1. load_a + syn_ctgan
2. load_a + syn_tvae
3. load_b + syn_ctgan
4. load_b + syn_tvae

## Reporting Options

Reporter supports two methods:

### Data Saving
```yaml
Reporter:
    save_data:
        method: 'save_data'
        source: 'Postprocessor'  # Module to save data from
```

### Report Generation
```yaml
Reporter:
    save_report:
        method: 'save_report'
        granularity: 'global'    # Report detail level
```

## Best Practices

1. Use meaningful experiment names
2. Keep parameters organized by module
3. Document experiment configurations
4. Validate YAML syntax before running