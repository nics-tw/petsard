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

Execute pipeline according to configuration.

## Parameters

- `config` (str): Configuration filename

## Examples

```python
exec = Executor(config=yaml_path)
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

- `config`: Configuration contents (Config object)
- `sequence`: Execution order list
- `status`: Execution status (Status object)
- `result`: Results dictionary