---
title: Config
type: docs
weight: 62
prev: docs/api/operator
next: docs/api/status
---

```python
Config(config)
```

The Config class manages experiment configuration and creates operator execution flows for the PETsARD pipeline. It parses configuration dictionaries, validates settings, and generates queues of operators for sequential execution.

## Design Overview

The Config system transforms declarative configuration into executable pipeline flows. It handles module sequencing, experiment naming, and operator instantiation while providing validation and error checking.

### Key Principles

1. **Declarative Configuration**: Define experiments through structured dictionaries
2. **Automatic Flow Generation**: Convert configuration into executable operator sequences
3. **Validation**: Comprehensive configuration validation and error reporting
4. **Flexibility**: Support for complex experiment configurations and custom naming

## Parameters

- `config` (dict): The configuration dictionary defining the experiment pipeline

## Configuration Structure

The configuration follows a hierarchical structure:

```python
{
    "ModuleName": {
        "experiment_name": {
            "parameter1": "value1",
            "parameter2": "value2"
        }
    }
}
```

### Example Configuration

```python
config_dict = {
    "Loader": {
        "load_data": {
            "filepath": "data.csv"
        }
    },
    "Splitter": {
        "split_data": {
            "train_split_ratio": 0.8,
            "num_samples": 3
        }
    },
    "Synthesizer": {
        "generate": {
            "method": "sdv",
            "model": "GaussianCopula"
        }
    },
    "Evaluator": {
        "evaluate": {
            "method": "sdmetrics"
        }
    },
    "Reporter": {
        "report": {
            "method": "save_report",
            "granularity": "global"
        }
    }
}
```

## Attributes

### Core Attributes

- `config` (queue.Queue): Queue of instantiated operators ready for execution
- `module_flow` (queue.Queue): Queue of module names corresponding to each operator
- `expt_flow` (queue.Queue): Queue of experiment names corresponding to each operator
- `sequence` (list): List of module names in execution order
- `yaml` (dict): The processed configuration dictionary

## Methods

### Configuration Processing

The Config class automatically processes the configuration during initialization:

1. **Validation**: Checks for invalid experiment naming patterns
2. **Splitter Expansion**: Handles multi-sample splitting configurations
3. **Operator Creation**: Instantiates operators for each experiment
4. **Flow Generation**: Creates execution queues using depth-first search

## Special Handling

### Splitter Configuration

The Config class provides special handling for Splitter configurations with multiple samples:

```python
# Original configuration
"Splitter": {
    "split_data": {
        "train_split_ratio": 0.8,
        "num_samples": 3
    }
}

# Automatically expanded to:
"Splitter": {
    "split_data_[3-1]": {"train_split_ratio": 0.8, "num_samples": 1},
    "split_data_[3-2]": {"train_split_ratio": 0.8, "num_samples": 1},
    "split_data_[3-3]": {"train_split_ratio": 0.8, "num_samples": 1}
}
```

### Experiment Naming Rules

- Experiment names cannot end with `_[xxx]` pattern (reserved for internal use)
- Each experiment name must be unique within its module
- Names are used for result tracking and reporting

## Usage Examples

### Basic Configuration

```python
from petsard.config import Config

# Simple pipeline configuration
config_dict = {
    "Loader": {
        "load_data": {"filepath": "benchmark://adult-income"}
    },
    "Synthesizer": {
        "generate": {"method": "sdv", "model": "GaussianCopula"}
    }
}

config = Config(config_dict)

# Access configuration attributes
print(f"Module sequence: {config.sequence}")
print(f"Number of operators: {config.config.qsize()}")
```

### Complex Multi-Module Configuration

```python
from petsard.config import Config

config_dict = {
    "Loader": {
        "load_benchmark": {"method": "default"},
        "load_custom": {"filepath": "custom_data.csv"}
    },
    "Preprocessor": {
        "preprocess": {"method": "default"}
    },
    "Splitter": {
        "split_train_test": {
            "train_split_ratio": 0.8,
            "num_samples": 5
        }
    },
    "Synthesizer": {
        "sdv_gaussian": {"method": "sdv", "model": "GaussianCopula"},
        "sdv_ctgan": {"method": "sdv", "model": "CTGAN"}
    },
    "Evaluator": {
        "evaluate_all": {"method": "sdmetrics"}
    },
    "Reporter": {
        "save_results": {
            "method": "save_data",
            "source": "Synthesizer"
        },
        "generate_report": {
            "method": "save_report",
            "granularity": "global"
        }
    }
}

config = Config(config_dict)
```

### Integration with Executor

```python
from petsard.config import Config
from petsard.executor import Executor

# Config is typically used with Executor
config = Config(config_dict)
executor = Executor(config)
executor.run()
```

## Validation and Error Handling

### Configuration Validation

The Config class performs several validation checks:

- **Naming validation**: Ensures experiment names don't use reserved patterns
- **Structure validation**: Verifies proper configuration hierarchy
- **Parameter validation**: Delegates to individual operators for parameter checking

### Error Types

- `ConfigError`: Raised for invalid configuration structures or naming violations
- Module-specific errors: Propagated from individual operator initialization

## Architecture Benefits

### 1. Separation of Concerns
- **Configuration parsing**: Handles structure and validation
- **Operator management**: Creates and organizes execution units
- **Flow control**: Manages execution sequence and dependencies

### 2. Flexibility
- **Multiple experiments**: Support for multiple experiments per module
- **Complex pipelines**: Handle arbitrary module combinations
- **Custom configurations**: Extensible parameter system

### 3. Validation
- **Early error detection**: Catch configuration issues before execution
- **Clear error messages**: Detailed feedback for debugging
- **Consistent validation**: Standardized validation across all modules

### 4. Integration
- **Executor compatibility**: Seamless integration with execution system
- **Status management**: Compatible with Status tracking system
- **Operator abstraction**: Clean interface to underlying operators

The Config system provides the foundation for PETsARD's flexible and robust experiment configuration, enabling complex data processing pipelines through simple declarative specifications.