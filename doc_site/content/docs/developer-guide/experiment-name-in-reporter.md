---
title: Experiment Naming in Reporter
type: docs
weight: 87
prev: docs/developer-guide/logging-configuration
next: docs/developer-guide/test-coverage
---

# Experiment Naming in Reporter

This document explains the experiment naming system used in PETsARD's Reporter module, including the traditional tuple-based approach and the new naming strategy support.

Click the below button to run this example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/developer-guide/experiment-name-in-reporte.ipynb)

## Overview

PETsARD uses experiment names to identify and organize different experimental configurations. The Reporter module supports two naming strategies that can be controlled via the `naming_strategy` parameter:

1. **TRADITIONAL**: Maintains backward compatibility with the existing tuple-based system
2. **COMPACT**: Provides a new, more readable naming convention

## Naming Strategy Parameter

The Reporter class now accepts a `naming_strategy` parameter to control output filename formats:

```python
from petsard.reporter import Reporter

# Traditional naming (default)
reporter = Reporter('save_report', granularity='global', naming_strategy='traditional')

# Compact naming
reporter = Reporter('save_report', granularity='global', naming_strategy='compact')
```

## Traditional Naming System

### Tuple Format

The traditional system uses tuples to represent experiment configurations:

```python
from petsard.reporter import Reporter

# Single module experiment
experiment_key = ('Synthesizer', 'exp1')

# Multi-module experiment
experiment_key = ('Loader', 'default', 'Synthesizer', 'exp1')
```

### Granularity Support

For Reporter operations, granularity can be specified using bracket notation:

```python
# With granularity
experiment_key = ('Reporter', 'exp1_[global]')
experiment_key = ('Reporter', 'exp1_[columnwise]')
experiment_key = ('Reporter', 'exp1_[pairwise]')
```

### File Naming Convention

Traditional naming generates files like:
- `petsard_Synthesizer[exp1].csv`
- `petsard[Report]_eval1_[global].csv`

### Using with Reporter

```python
from petsard.reporter import Reporter

# Traditional naming strategy
reporter = Reporter('save_report', granularity='global', naming_strategy='traditional')
reporter.create({('Evaluator', 'eval1_[global]'): results})
reporter.report()  # Generates: petsard[Report]_eval1_[global].csv

# Compact naming strategy
reporter = Reporter('save_report', granularity='global', naming_strategy='compact')
reporter.create({('Evaluator', 'eval1_[global]'): results})
reporter.report()  # Generates: petsard_eval1_global.csv
```

## ExperimentConfig System

### Basic Usage

The new ExperimentConfig class provides a more structured approach:

```python
from petsard.reporter import ExperimentConfig, NamingStrategy

# Create experiment configuration
config = ExperimentConfig(
    module="Synthesizer",
    exp_name="exp1", 
    data=your_data,
    naming_strategy=NamingStrategy.COMPACT
)

# Use with Reporter
reporter = Reporter.create(config={'method': 'save_report'})
result = reporter.create({config.traditional_tuple: your_data})
```

### Naming Strategies

#### TRADITIONAL Strategy

Maintains complete backward compatibility:

```python
config = ExperimentConfig(
    module="Synthesizer",
    exp_name="exp1",
    data=data,
    naming_strategy=NamingStrategy.TRADITIONAL
)

print(config.filename)  # petsard_Synthesizer-exp1.csv
```

#### COMPACT Strategy

Provides cleaner, more readable names:

```python
config = ExperimentConfig(
    module="Synthesizer", 
    exp_name="exp1",
    data=data,
    naming_strategy=NamingStrategy.COMPACT
)

print(config.filename)  # petsard_Sy.exp1.csv
```

### Module Abbreviations

The COMPACT strategy uses these abbreviations:

| Module | Abbreviation |
|--------|-------------|
| Loader | Ld |
| Splitter | Sp |
| Processor | Pr |
| Synthesizer | Sy |
| Constrainer | Cn |
| Evaluator | Ev |
| Reporter | Rp |

### Granularity Support

ExperimentConfig supports multiple granularity levels:

```python
# Single granularity
config = ExperimentConfig(
    module="Reporter",
    exp_name="exp1", 
    data=data,
    granularity="global"
)

# Multiple granularities (using with_granularity)
configs = [
    config.with_granularity("global"),
    config.with_granularity("columnwise"), 
    config.with_granularity("pairwise")
]
```

### Granularity Abbreviations

In COMPACT mode, granularities are abbreviated:

| Granularity | Abbreviation |
|------------|-------------|
| global | G |
| columnwise | C |
| pairwise | P |
| details | D |
| tree | T |

### Advanced Features

#### Iteration Support

For multiple executions of the same experiment:

```python
config = ExperimentConfig(
    module="Splitter",
    exp_name="exp1",
    data=data,
    iteration=2
)

print(config.compact_name)  # Sp.exp1.i2
```

#### Parameter Tracking

Store additional experiment parameters:

```python
config = ExperimentConfig(
    module="Synthesizer",
    exp_name="exp1", 
    data=data,
    parameters={"epochs": 100, "lr": 0.001}
)

# Add more parameters
config = config.with_parameters(batch_size=32)
```

#### Conversion from Traditional Format

Convert existing tuple-based configurations:

```python
# From traditional tuple
traditional_tuple = ('Synthesizer', 'exp1_[global]')
config = ExperimentConfig.from_traditional_tuple(
    traditional_tuple, 
    data=your_data,
    naming_strategy=NamingStrategy.COMPACT
)
```

## File Naming Examples

### Traditional Strategy Examples

```python
# Basic save_data
('Synthesizer', 'exp1') → petsard_Synthesizer[exp1].csv

# Save_report with granularity
('Evaluator', 'eval1_[global]') → petsard[Report]_eval1_[global].csv
('Evaluator', 'eval1_[columnwise]') → petsard[Report]_eval1_[columnwise].csv

# Save_timing
timing_data → petsard_timing_report.csv
```

### COMPACT Strategy Examples

```python
# Basic save_data
('Synthesizer', 'exp1') → petsard_Synthesizer_exp1.csv

# Save_report with granularity
('Evaluator', 'eval1_[global]') → petsard_eval1_global.csv
('Evaluator', 'eval1_[columnwise]') → petsard_eval1_columnwise.csv

# Save_timing (unchanged)
timing_data → petsard_timing_report.csv
```

### Comparison Table

| Method | Traditional Format | Compact Format |
|--------|-------------------|----------------|
| save_data | `petsard_Synthesizer[exp1].csv` | `petsard_Synthesizer_exp1.csv` |
| save_report | `petsard[Report]_eval1_[global].csv` | `petsard_eval1_global.csv` |
| save_timing | `petsard_timing_report.csv` | `petsard_timing_report.csv` |

## Migration Guide

### From Traditional to ExperimentConfig

1. **Identify existing tuple usage**:
   ```python
   # Old way
   experiment_key = ('Synthesizer', 'exp1')
   ```

2. **Create equivalent ExperimentConfig**:
   ```python
   # New way
   config = ExperimentConfig(
       module="Synthesizer",
       exp_name="exp1",
       data=your_data
   )
   ```

3. **Use traditional_tuple for compatibility**:
   ```python
   # Use with existing Reporter code
   reporter_data = {config.traditional_tuple: your_data}
   ```

### Gradual Migration Strategy

1. **Phase 1**: Use ExperimentConfig with TRADITIONAL strategy
2. **Phase 2**: Switch to COMPACT strategy for new experiments  
3. **Phase 3**: Migrate existing experiments to COMPACT as needed

## Best Practices

### Naming Conventions

1. **Use descriptive experiment names**:
   ```python
   # Good
   config = ExperimentConfig(module="Synthesizer", exp_name="ctgan_v2", data=data)
   
   # Avoid
   config = ExperimentConfig(module="Synthesizer", exp_name="exp1", data=data)
   ```

2. **Include version information when relevant**:
   ```python
   config = ExperimentConfig(module="Synthesizer", exp_name="ctgan_v2_tuned", data=data)
   ```

3. **Use consistent naming across related experiments**:
   ```python
   base_config = ExperimentConfig(module="Synthesizer", exp_name="ctgan_baseline", data=data)
   tuned_config = base_config.with_parameters(epochs=200).with_exp_name("ctgan_tuned")
   ```

### Strategy Selection

- **Use TRADITIONAL** for:
  - Existing projects requiring backward compatibility
  - Integration with legacy systems
  - When file naming consistency is critical

- **Use COMPACT** for:
  - New projects
  - When file readability is important
  - Experiments with many variations

### Performance Considerations

- ExperimentConfig objects are immutable and can be safely cached
- Use `with_*` methods to create variations efficiently
- The `unique_id` property provides consistent hashing for deduplication

## Integration with Reporter

### Basic Reporter Usage

```python
from petsard.reporter import Reporter, ExperimentConfig

# Create configuration
config = ExperimentConfig(
    module="Evaluator",
    exp_name="privacy_metrics",
    data=evaluation_data,
    granularity="global"
)

# Create reporter
reporter = Reporter.create({'method': 'save_report'})

# Process data
data_dict = {config.traditional_tuple: evaluation_data}
processed = reporter.create(data_dict)
result = reporter.report(processed)
```

### Multi-Granularity Reporting

```python
# Create base configuration
base_config = ExperimentConfig(
    module="Evaluator", 
    exp_name="utility_metrics",
    data=evaluation_data
)

# Generate multiple granularity reports
granularities = ["global", "columnwise", "pairwise"]
data_dict = {}

for gran in granularities:
    config = base_config.with_granularity(gran)
    data_dict[config.traditional_tuple] = evaluation_data

# Process all at once
processed = reporter.create(data_dict)
result = reporter.report(processed)
```

## Troubleshooting

### Common Issues

1. **Import Error**:
   ```python
   # Correct import
   from petsard.reporter import ExperimentConfig, NamingStrategy
   ```

2. **Invalid Module Name**:
   ```python
   # Valid modules only
   valid_modules = ["Loader", "Splitter", "Processor", "Synthesizer", 
                   "Constrainer", "Evaluator", "Reporter"]
   ```

3. **Granularity Format**:
   ```python
   # Correct granularity specification
   config = ExperimentConfig(
       module="Reporter",
       exp_name="exp1", 
       data=data,
       granularity="global"  # Not "GLOBAL" or "[global]"
   )
   ```

### Debugging Tips

1. **Check configuration validity**:
   ```python
   try:
       config = ExperimentConfig(module="InvalidModule", exp_name="test", data=data)
   except ValueError as e:
       print(f"Configuration error: {e}")
   ```

2. **Verify file naming**:
   ```python
   config = ExperimentConfig(module="Synthesizer", exp_name="test", data=data)
   print(f"Traditional: {config.traditional_name}")
   print(f"Compact: {config.compact_name}")
   print(f"Filename: {config.filename}")
   ```

3. **Compare strategies**:
   ```python
   traditional = ExperimentConfig(
       module="Synthesizer", exp_name="test", data=data,
       naming_strategy=NamingStrategy.TRADITIONAL
   )
   compact = ExperimentConfig(
       module="Synthesizer", exp_name="test", data=data, 
       naming_strategy=NamingStrategy.COMPACT
   )
   
   print(f"Traditional: {traditional.filename}")
   print(f"Compact: {compact.filename}")
