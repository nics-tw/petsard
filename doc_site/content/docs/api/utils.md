---
title: Utils
type: docs
weight: 65
prev: docs/api/status
next: docs/api
---

```python
petsard.utils
```

Core utility functions for the PETsARD system, providing essential tools for external module loading and other common operations.

## Design Overview

The Utils module provides general-purpose utility functions that are used across the PETsARD system. It follows the principle of separation of concerns, providing core functionality without domain-specific logic.

### Key Principles

1. **Generality**: Provides universal utility functions without specific domain logic
2. **Independence**: Does not depend on other PETsARD modules, serving as a foundational tool layer
3. **Extensibility**: Supports customizable behavior through parameters
4. **Error Handling**: Provides comprehensive error capture and reporting mechanisms

## Functions

### `load_external_module()`

```python
load_external_module(module_path, class_name, logger, required_methods=None, search_paths=None)
```

Load external Python module and return the module instance and class.

**Parameters**

- `module_path` (str): Path to the external module (relative or absolute)
- `class_name` (str): Name of the class to load from the module
- `logger` (logging.Logger): Logger for recording messages
- `required_methods` (dict[str, list[str]], optional): Dictionary mapping method names to required parameter names
- `search_paths` (list[str], optional): Additional search paths to try when resolving the module path

**Returns**

- `Tuple[Any, Type]`: A tuple containing the module instance and the class

**Raises**

- `FileNotFoundError`: If the module file does not exist
- `ConfigError`: If the module cannot be loaded or doesn't contain the specified class

## Usage Examples

### Basic Usage

```python
import logging
from petsard.utils import load_external_module

# Setup logger
logger = logging.getLogger(__name__)

# Load module from current directory
try:
    module, cls = load_external_module(
        module_path='my_module.py',
        class_name='MyClass',
        logger=logger
    )
    instance = cls(config={'param': 'value'})
except Exception as e:
    logger.error(f"Loading failed: {e}")
```

### Advanced Usage with Custom Search Paths

```python
import logging
from petsard.utils import load_external_module

logger = logging.getLogger(__name__)

# Custom search paths
search_paths = [
    '/path/to/custom/modules',
    './external_modules',
    '../shared_modules'
]

try:
    module, cls = load_external_module(
        module_path='advanced_module.py',
        class_name='AdvancedClass',
        logger=logger,
        search_paths=search_paths,
        required_methods={
            '__init__': ['config'],
            'process': ['data'],
            'validate': []
        }
    )
    instance = cls(config={'advanced': True})
except Exception as e:
    logger.error(f"Loading failed: {e}")
```

## Path Resolution Logic

### Default Search Order

1. **Direct path**: Use the provided module_path as-is
2. **Current working directory**: os.path.join(cwd, module_path)
3. **Custom paths**: All paths in the search_paths parameter

### Resolution Rules

- If it's an absolute path and the file exists, use it directly
- Try each search path in order
- Stop at the first existing file found
- If none found, raise FileNotFoundError

## Architecture Benefits

### 1. Separation of Concerns
- **Core functionality**: Focuses on general module loading logic
- **No domain-specific logic**: Does not contain demo or other specific-purpose hard-coding

### 2. Extensibility
- **Parameterized design**: Control behavior through parameters
- **Custom search paths**: Support arbitrary search path configurations
- **Optional method validation**: Optional interface validation functionality

### 3. Error Handling
- **Detailed error information**: Provides specific failure reasons
- **Search path reporting**: Lists all attempted paths
- **Layered error handling**: Different types of errors have different handling

### 4. Logging
- **Debug information**: Detailed debug logs
- **Error recording**: Complete error logs
- **Progress tracking**: Loading process progress recording

## Collaboration with Demo Utils

### Division of Responsibilities
- **petsard.utils**: Provides general core functionality
- **demo.utils**: Provides demo-specific search paths and logic

### Collaboration Pattern
```python
# Implementation of demo.utils.load_demo_module
def load_demo_module(module_path, class_name, logger, required_methods=None):
    # Generate demo-specific search paths
    demo_search_paths = _get_demo_search_paths(module_path)
    
    # Use core functionality for loading
    return load_external_module(
        module_path=module_path,
        class_name=class_name,
        logger=logger,
        required_methods=required_methods,
        search_paths=demo_search_paths
    )
```

## Benefits

1. **Modular Design**: Clear separation of responsibilities, core functionality separated from specific purposes
2. **Reusability**: General utility functions can be used by multiple modules
3. **Maintainability**: Centralized utility functions are easy to maintain and update
4. **Testability**: Independent functions are easy to unit test
5. **Extensibility**: Parameterized design supports multiple use cases

This design ensures the Utils module provides stable, general tool support while maintaining clean and modular architectural principles.