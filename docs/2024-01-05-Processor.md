# Processor

The `Processor` is responsible for preprocessing and postprocessing procedures during the experiment. With the component, you can deal with the data at ease, including encoding categorical data, dealing with missing data, excluding outliers, and scaling data. The guide will go through creating, manipulating the processor instance from `Processor` class.

```{python}
from PETsARD.Processor.Base import Processor

processor = Processor(metadata)

processor.fit(data)

transformed_data = processor.transform(data)

inverse_transformed_data = processor.inverse_transform(synthetic_data)
```



## `Processor` Creation

Once you have the metadata instance built from the class `Metadata`, you are ready for creating a `processor`. The config is optional, which allows you to determine the procedures to be done at your own. When the `processor` is created, it will analyse the metadata and determine what kinds of pre/postprocessing procedures should be done. If a `config` is passed, the `processor` will overwrite the default settings and follow the pre/postprocessing procedures in the `config`.

```{python}
processor = Processor(
    metadata, # required
    config=None
)
```

### Parameters

`metadata`: The data schema. Used for creating processor and inferring the appropriate data processing procedures.

`config` (`dict`): The user-defined procedures, containing the information about the components to be used in each column.

### `get_config`

Use this method to access what procedures will be done during transformation/inverse transform process, which we called it config. It will be summarised by the processor types (missingist, outlierist, encoder, scaler) and the columns. It also stores all the data processing objects, which allows users to access the attributes of the objects.

```{python}
processor.get_config(
    col=None,
    print_config=False
)
```

```{python}
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
`col` (`list`): The columns the user want to get the config from. If the list is empty, all columns from the metadata will be selected.

`print_config` (`bool`, default=False): Whether the result should be printed.

#### Outputs
(`dict`): The config with selected columns.

### `set_config`

Edit the whole config. To keep the structure of the config, it fills the unspecified preprocessors with `None`. If you don't want to do this, use `update_config` instead.

```{python}
processor.set_config(config)
```

#### Parameters
`config` (`dict`): The dict with the same format as the config class.

#### Outputs
None.

### `update_config`

Update part of the config.

```{python}
processor.update_config(config)
```

#### Parameters
`config` (`dict`): The dict with the same format as the config class.

#### Outputs
None.

### `get_changes`

Compare the differences between the current config and the default config.

```{python}
processor.get_changes()
```

#### Parameters
None.

#### Outputs
(`pandas.DataFrame`): A dataframe recording the differences bewteen the current config and the default config.

## Data Processing

### `fit`

Learn the structure of the data.

```{python}
processor.fit(
    data,
    sequence=None
)
```

#### Parameters
`data` (`pandas.DataFrame`): The data to be fitted.

`sequence` (`list`): The processing sequence, allowing users to skip the procedures and alter the execution order. Avaliable procedures: 'missingist', 'outlierist', 'encoder', 'scaler'. This is the default sequence if the user doesn't pass a sequence to the method.

#### Outputs
None.

### `transform`

Conduct the data preprocessing procedure.

```{python}
transformed = processor.transform(data)
```

#### Parameters
`data` (`pandas.DataFrame`): The data to be transformed.

#### Outputs
(`pandas.DataFrame`): The data after transformation.

### `inverse_transform`

Conduct the data postprocessing procedure.

```{python}
inverse_transformed = processor.inverse_transform(data)
```

#### Parameters
`data` (`pandas.DataFrame`): The data to be inverse transformed.

#### Outputs
(`pandas.DataFrame`): The data after inverse transformation.