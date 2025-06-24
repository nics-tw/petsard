---
title: Executor
type: docs
weight: 51
prev: docs/api
next: docs/api/loader
---


```python
Executor(
    config=None
)
```

Execute pipeline according to configuration with enhanced logging and configuration management.

## Parameters

- `config` (str): Configuration filename (YAML format)

## Configuration Options

The executor supports additional configuration options in the YAML file under the `Executor` section:

```yaml
Executor:
  log_output_type: "both"    # "stdout", "file", "both"
  log_level: "INFO"          # "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
  log_dir: "./logs"          # Directory for log files
  log_filename: "PETsARD_{timestamp}.log"  # Log filename template

# Your experiment configuration
Loader:
  load_data:
    method: "csv"
    path: "data.csv"
```

## Examples

### Basic Usage
```python
exec = Executor(config="config.yaml")
exec.run()
results = exec.get_result()
```

### With Custom Logging
```python
# config.yaml with executor settings
exec = Executor(config="config_with_logging.yaml")
exec.run()
```

## Methods

### `run()`

Execute pipeline according to configuration.

**Parameters**

None

**Returns**

None. Results are stored in `result` attribute

### `get_result()`

Retrieve experiment results.

**Parameters**

None

**Returns**

- dict: Dictionary containing all experiment results
  - Format: `{full_expt_name: result}`

## Attributes

- `executor_config`: Executor-specific configuration (ExecutorConfig object)
- `config`: Experiment configuration contents (Config object)
- `sequence`: Module execution order list
- `status`: Execution status tracking (Status object)
- `result`: Final results dictionary

## Configuration Classes

### ExecutorConfig

```python
@dataclass
class ExecutorConfig:
    log_output_type: str = "file"
    log_level: str = "INFO"
    log_dir: str = "."
    log_filename: str = "PETsARD_{timestamp}.log"
```

**Parameters:**
- `log_output_type`: Where to output logs ("stdout", "file", "both")
- `log_level`: Logging level ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
- `log_dir`: Directory for storing log files
- `log_filename`: Log file name template (supports {timestamp} placeholder)