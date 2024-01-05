# Processor

The `Processor` module is responsible for managing preprocessing and postprocessing procedures during experiments. This component facilitates easy data handling, including tasks such as encoding categorical data, handling missing data, excluding outliers, and scaling data. This guide will walk you through the creation and manipulation of a processor instance from the `Processor` class.

```python
from PETsARD.Processor.Base import Processor

processor = Processor(metadata)

processor.fit(data)

transformed_data = processor.transform(data)

inverse_transformed_data = processor.inverse_transform(synthetic_data)
```



## `Processor` Creation

Once you have an instance of metadata built from the `Metadata` class, you can create a `Processor`. The `config` parameter is optional, allowing you to customise procedures. Upon creation, the processor analyses the metadata to determine the necessary preprocessing and postprocessing procedures. If a `config` is passed, the processor will overwrite default settings and follow the procedures specified in the `config`.

```python
processor = Processor(
    metadata, # required
    config=None
)
```

### Parameters

`metadata`: The data schema used for creating the processor and inferring appropriate data processing procedures.

`config` (`dict`): User-defined procedures containing information about the components to be used in each column.

### `get_config`

Use this method to access the configuration of procedures to be done during the transformation/inverse transform process. It summarises the processor types (missingist, outlierist, encoder, scaler) and columns, storing all data processing objects for user access.

```python
processor.get_config(
    col=None,
    print_config=False
)
```

```python
{'missingist': {'gen': <PETsARD.Processor.Missingist.Missingist_Drop at 0x14715dcc0>,
  'age': <PETsARD.Processor.Missingist.Missingist_Simple at 0x14715f9d0>,
  },
 'outlierist': {'gen': None,
  'age': <PETsARD.Processor.Outlierist.Outlierist_LOF at 0x14715c670>,
  },
 'encoder': {'gen': <PETsARD.Processor.Encoder.Encoder_Uniform at 0x14715c1f0>,
  'age': None
  },
 'scaler': {'gen': None,
  'age': <PETsARD.Processor.Scaler.Scaler_MinMax at 0x14715d300>
  }
}
```

#### Parameters
`col` (`list`): The columns the user wants to get the config from. If the list is empty, all columns from the metadata will be selected.

`print_config` (`bool`, default=False): Whether the result should be printed.

#### Outputs
(`dict`): The config with selected columns.

### `set_config`

Edit the whole config. To maintain the structure of the config, it fills the unspecified preprocessors with `None`. If you don't want to do this, use `update_config` instead.

```python
processor.set_config(config)
```

#### Parameters
`config` (`dict`): The dict with the same format as the config class.

#### Outputs
None.

### `update_config`

Update part of the config.

```python
processor.update_config(config)
```

#### Parameters
`config` (`dict`): The dict with the same format as the config class.

#### Outputs
None.

### `get_changes`

Compare the differences between the current config and the default config.

```python
processor.get_changes()
```

#### Parameters
None.

#### Outputs
(`pandas.DataFrame`): A dataframe recording the differences bewteen the current config and the default config.

## Data Processing

### `fit`

Learn the structure of the data.

```python
processor.fit(
    data,
    sequence=None
)
```

#### Parameters
`data` (`pandas.DataFrame`): The data to be fitted.

`sequence` (`list`): The processing sequence, allowing users to skip procedures and alter the execution order. Avaliable procedures: 'missingist', 'outlierist', 'encoder', 'scaler'. This is the default sequence if the user doesn't pass a sequence to the method.

#### Outputs
None.

### `transform`

Conduct the data preprocessing procedure.

```python
transformed = processor.transform(data)
```

#### Parameters
`data` (`pandas.DataFrame`): The data to be transformed.

#### Outputs
(`pandas.DataFrame`): The data after transformation.

### `inverse_transform`

Conduct the data postprocessing procedure.

```python
inverse_transformed = processor.inverse_transform(data)
```

#### Parameters
`data` (`pandas.DataFrame`): The data to be inverse transformed.

#### Outputs
(`pandas.DataFrame`): The data after inverse transformation.