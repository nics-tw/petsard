---
title: Operator
type: docs
weight: 61
prev: docs/api/reporter
next: docs/api/config
---

```python
petsard.operator
```

The Operator module provides wrapper classes that standardize the execution interface for all PETsARD pipeline components. Each operator encapsulates a specific module (Loader, Synthesizer, etc.) and provides consistent methods for configuration, execution, and result retrieval.

## Design Overview

The Operator system follows a decorator pattern, wrapping core modules with standardized interfaces for pipeline execution. This design ensures consistent behavior across all pipeline components while maintaining flexibility for module-specific functionality.

### Key Principles

1. **Standardization**: All operators implement the same base interface for consistent pipeline execution
2. **Encapsulation**: Each operator wraps its corresponding module, handling configuration and execution details
3. **Error Handling**: Comprehensive error logging and exception handling across all operators
4. **Metadata Management**: Consistent metadata handling using the Metadater system

## Base Classes

### `BaseOperator`

```python
BaseOperator(config)
```

Abstract base class defining the standard interface for all operators.

**Parameters**
- `config` (dict): Configuration parameters for the operator

**Methods**
- `run(input)`: Execute the operator's functionality
- `set_input(status)`: Configure input data from pipeline status
- `get_result()`: Retrieve the operator's output data
- `get_metadata()`: Retrieve metadata associated with the output

## Operator Classes

### `LoaderOperator`

```python
LoaderOperator(config)
```

Wraps the Loader module for data loading operations.

**Configuration Parameters**
- `filepath` (str): Path to the data file
- `method` (str, optional): Loading method ('default' for benchmark data)
- `column_types` (dict, optional): Column type specifications
- `header_names` (list, optional): Custom header names
- `na_values` (str/list/dict, optional): Custom NA value definitions

**Key Methods**
- `get_result()`: Returns loaded DataFrame
- `get_metadata()`: Returns SchemaMetadata for the loaded data

### `SplitterOperator`

```python
SplitterOperator(config)
```

Wraps the Splitter module for data splitting operations.

**Configuration Parameters**
- `train_split_ratio` (float): Ratio for training data (default: 0.8)
- `num_samples` (int): Number of split samples (default: 1)
- `random_state` (int/float/str, optional): Random seed
- `method` (str, optional): 'custom_data' for loading pre-split data

**Key Methods**
- `get_result()`: Returns dict with 'train' and 'validation' DataFrames
- `get_metadata()`: Returns updated SchemaMetadata with split information

### `PreprocessorOperator`

```python
PreprocessorOperator(config)
```

Wraps the Processor module for data preprocessing operations.

**Configuration Parameters**
- `method` (str): Processing method ('default' or 'custom')
- `sequence` (list, optional): Custom processing sequence
- `config` (dict, optional): Processor-specific configuration

**Key Methods**
- `get_result()`: Returns preprocessed DataFrame
- `get_metadata()`: Returns updated SchemaMetadata

### `SynthesizerOperator`

```python
SynthesizerOperator(config)
```

Wraps the Synthesizer module for synthetic data generation.

**Configuration Parameters**
- `method` (str): Synthesis method (e.g., 'sdv')
- `model` (str): Model type (e.g., 'GaussianCopula')
- Additional parameters specific to the chosen method

**Key Methods**
- `get_result()`: Returns synthetic DataFrame

### `PostprocessorOperator`

```python
PostprocessorOperator(config)
```

Wraps the Processor module for data postprocessing operations.

**Configuration Parameters**
- `method` (str): Processing method ('default' or custom)

**Key Methods**
- `get_result()`: Returns postprocessed DataFrame

### `ConstrainerOperator`

```python
ConstrainerOperator(config)
```

Wraps the Constrainer module for applying data constraints.

**Configuration Parameters**
- `field_combinations` (list): Field combination constraints
- `target_rows` (int, optional): Target number of rows
- `sampling_ratio` (float, optional): Sampling ratio for resampling
- `max_trials` (int, optional): Maximum resampling attempts

**Key Methods**
- `get_result()`: Returns constrained DataFrame

### `EvaluatorOperator`

```python
EvaluatorOperator(config)
```

Wraps the Evaluator module for data quality assessment.

**Configuration Parameters**
- `method` (str): Evaluation method (e.g., 'sdmetrics')
- Additional parameters specific to the chosen method

**Key Methods**
- `get_result()`: Returns dict of evaluation results by metric type

### `DescriberOperator`

```python
DescriberOperator(config)
```

Wraps the Describer module for descriptive data analysis.

**Configuration Parameters**
- `method` (str): Description method
- Additional parameters specific to the chosen method

**Key Methods**
- `get_result()`: Returns dict of descriptive analysis results

### `ReporterOperator`

```python
ReporterOperator(config)
```

Wraps the Reporter module for result export and reporting.

**Configuration Parameters**
- `method` (str): Report method ('save_data' or 'save_report')
- `source` (str/list): Source modules for data export
- `granularity` (str): Report granularity ('global', 'columnwise', 'pairwise')
- `output` (str, optional): Output filename prefix

**Key Methods**
- `get_result()`: Returns generated report data

## Usage Examples

### Basic Operator Usage

```python
from petsard.operator import LoaderOperator

# Create and configure operator
config = {"filepath": "data.csv"}
loader_op = LoaderOperator(config)

# Set input (typically done by Executor)
input_data = loader_op.set_input(status)

# Execute operation
loader_op.run(input_data)

# Retrieve results
data = loader_op.get_result()
metadata = loader_op.get_metadata()
```

### Pipeline Integration

```python
from petsard.config import Config
from petsard.executor import Executor

# Operators are typically used through Config and Executor
config_dict = {
    "Loader": {"load_data": {"filepath": "data.csv"}},
    "Synthesizer": {"synth": {"method": "sdv", "model": "GaussianCopula"}},
    "Evaluator": {"eval": {"method": "sdmetrics"}}
}

config = Config(config_dict)
executor = Executor(config)
executor.run()
```

## Architecture Benefits

### 1. Consistent Interface
- **Standardized methods**: All operators implement the same base interface
- **Predictable behavior**: Consistent execution patterns across all modules

### 2. Error Handling
- **Comprehensive logging**: Detailed logging for debugging and monitoring
- **Exception management**: Consistent error handling and reporting

### 3. Pipeline Integration
- **Status management**: Seamless integration with the Status system
- **Data flow**: Standardized data passing between pipeline stages

### 4. Modularity
- **Separation of concerns**: Each operator handles one specific functionality
- **Extensibility**: Easy to add new operators for new modules

The Operator system provides the foundation for PETsARD's modular pipeline architecture, ensuring consistent and reliable execution across all data processing stages.