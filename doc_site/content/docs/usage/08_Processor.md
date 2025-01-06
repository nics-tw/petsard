---
title: "Processor"
draft: false
weight: 19
toc: true
---

The `Processor` module is responsible for managing preprocessing and postprocessing procedures during experiments. This component facilitates easy data handling, including tasks such as encoding categorical data, handling missing data, excluding outliers, and scaling data. This guide will walk you through the creation and manipulation of a processor instance from the `Processor` class.

```Python
from petsard import Processor


proc = Processor(metadata=split.metadata)
proc.fit(data=load.data)
transformed_data = proc.transform(data=load.data)
print(transformed_data.head(1))

## synthetic_data = ...

inverse_transformed_data = proc.inverse_transform(data=synthetic_data)
print(inverse_transformed_data.head(1))
```

## `Processor`

Once you have an instance of metadata built from the `Loader` class, you can create a `Processor`. The `config` parameter is optional, allowing you to customise procedures. Upon creation, the processor analyses the metadata to determine the necessary preprocessing and postprocessing procedures. If a `config` is passed, the processor will overwrite default settings and follow the procedures specified in the `config`.

```Python
proc = Processor(
    metadata=split.metadata, # required
    config=None
)
```

**Parameters**

`metadata` (`Metadata`): The data schema used for creating the processor and inferring appropriate data processing procedures. If `Loader`/`Splitter` is used, it is recommended to get the metadata via last use module `Loader.metadata`/`Splitter.metadata`. Note that the requirement is for the `Metadata` type itself, not `Metadata.metadata` as a dictionary. See the [Metadata page](petsard/docs/usage/05_metadata/) for more information.

`config` (`dict`, default=`None`): User-defined procedures containing information about the components to be used in each column.

### `config`

`config` is a nested `dict` defining the processing proceures. The structure is shown below:

```Python
{
    processor_type: {
        col_name: processor_obj
    }
}
```

Noted that `processor_obj` can be an initialised object from processing submodules or a class name (see "Available Processor Types").

### `get_config()`

Use this method to access the configuration of procedures to be done during the transformation/inverse transform process. It is summarised by the processor types (e.g., missing, outlier, encoder, scaler, discretizing) and columns, storing all data processing objects for user access.

```Python
proc.get_config(
    col=None,
    print_config=False
)
```

```plain_text
{'missing': {
    'gen': <petsard.processor.missing.MissingDrop at 0x28afa7d90>,
    'age': <petsard.processor.missing.MissingSimple at 0x28af374f0>
    },
 'outlier': {
    'gen': None,
    'age': <petsard.processor.outlier.OutlierLOF at 0x28afa72b0>
    },
 'encoder': {
    'gen': <petsard.processor.encoder.EncoderOneHot at 0x28afa6f80>,
    'age': None
    },
 'scaler': {
    'gen': None,
    'age': <petsard.processor.scaler.ScalerMinMax at 0x28afa6ec0>},
 'discretizing': {
    'gen': <petsard.processor.encoder.EncoderLabel at 0x28afa4910>,
    'age': <petsard.processor.discretizing.DiscretizingKBins at 0x28afa7310>
    }
}
```

**Parameters**

`col` (`list`, default=`None`): The columns the user wants to get the config from. If the list is empty, all columns from the metadata will be selected.

`print_config()` (`bool`, default=`False`): Whether the result should be printed.

**Outputs**

(`dict`): The config with selected columns.

### `update_config()`

Update part of the config.

```Python
proc.update_config(config=config)
```

**Parameters**

`config` (`dict`): The `dict` with the same format as the config class.

### `get_changes()`

Compare the differences between the current config and the default config. See "Available Processor Types" to know more about the default config.

```Python
proc.get_changes()
```

**Outputs**

(`pandas.DataFrame`): A dataframe recording the differences bewteen the current config and the default config.

### `fit()`

Learn the structure of the data.

```Python
proc.fit(
    data=data,
    sequence=None
)
```

**Parameters**

`data` (`pandas.DataFrame`): The data to be fitted.
`sequence` (`list`, default=`None`): The processing sequence, allowing users to skip procedures and alter the execution order. Avaliable procedures: `'missing'`, `'outlier'`, `'encoder'`, `'scaler'`, `'discretizing'`. `['missing', 'outlier', 'encoder', 'scaler']` is the default sequence if the user doesn't pass a sequence to the method. Noted that `'discretizing'` and `'encoder'` cannot be used in a sequence at the same time, and `'discretizing'` must be the last element if it exists in a sequence.

### `transform()`

Conduct the data preprocessing procedure.

```Python
transformed_data = proc.transform(data=data)
```

**Parameters**

`data` (`pandas.DataFrame`): The data to be transformed.

**Outputs**

(`pandas.DataFrame`): The data after transformation.

### `inverse_transform()`

Conduct the data postprocessing procedure. Noted that it also transforms the data types to align with the metadata using the following rules, and raises an error for other cases.

| Original Data Type | Transformed Data Type | Action                          |
| ------------------ | --------------------- | ------------------------------- |
| `int`              | `float`               | Convert to `int` after rounding |
| `float`            | `int`                 | Convert to `float`              |
| `str` / `object`   | Any                   | Convert to `str` / `object`     |
| `datetime`         | `int` / `float`       | Convert to `datetime`           |

```Python
inverse_transformed = proc.inverse_transform(data=data)
```

**Parameters**

`data` (`pandas.DataFrame`): The data to be inverse transformed.

**Outputs**

(`pandas.DataFrame`): The data after inverse transformation.

## Available Processor Types

In this section, we provide a comprehensive list of supported processor types and their associated classes to facilitate thorough customization. You have the option to specify the processor classes for `config` either by initializing an object or by directly entering the class name (outlined below). The former approach offers flexibility for customization, while the latter offers simplicity of use.

<div class="table-wrapper" markdown="block">

|   Submodule    | Processor Type |          Class           |    Alias (class name)     |
| :------------: | :------------: | :----------------------: | :-----------------------: |
|   `encoder`    |    Encoder     |     `EncoderUniform`     |     'encoder_uniform'     |
|   `encoder`    |    Encoder     |      `EncoderLabel`      |      'encoder_label'      |
|   `encoder`    |    Encoder     |     `EncoderOneHot`      |     'encoder_onehot'      |
|   `missing`    | MissingHandler |      `MissingMean`       |      'missing_mean'       |
|   `missing`    | MissingHandler |     `MissingMedian`      |     'missing_median'      |
|   `missing`    | MissingHandler |      `MissingMode`       |      'missing_mode'       |
|   `missing`    | MissingHandler |     `MissingSimple`      |     'missing_simple'      |
|   `missing`    | MissingHandler |      `MissingDrop`       |      'missing_drop'       |
|   `outlier`    | OutlierHandler |     `OutlierZScore`      |     'outlier_zscore'      |
|   `outlier`    | OutlierHandler |       `OutlierIQR`       |       'outlier_iqr'       |
|   `outlier`    | OutlierHandler | `OutlierIsolationForest` | 'outlier_isolationforest' |
|   `outlier`    | OutlierHandler |       `OutlierLOF`       |       'outlier_lof'       |
|    `scaler`    |     Scaler     |     `ScalerStandard`     |     'scaler_standard'     |
|    `scaler`    |     Scaler     |    `ScalerZeroCenter`    |    'scaler_zerocenter'    |
|    `scaler`    |     Scaler     |      `ScalerMinMax`      |      'scaler_minmax'      |
|    `scaler`    |     Scaler     |       `ScalerLog`        |       'scaler_log'        |
| `discretizing` |  Discretizing  |   `DiscretizingKBins`    |   'discretizing_kbins'    |

</div>

The following processors represent the default ones assigned based on `'inder_dtype'` in the `metadata`. See [Metadata](petsard/docs/usage/05_metadata/) page for details.

```plain_text
{
    'missing': {
        'numerical': MissingMean,
        'categorical': MissingDrop,
        'datetime': MissingDrop,
        'object': MissingDrop
    },
    'outlier': {
        'numerical': OutlierIQR,
        'categorical': None,
        'datatime': OutlierIQR,
        'object': None
    },
    'encoder': {
        'numerical': None,
        'categorical': EncoderUniform,
        'datetime': None,
        'object': EncoderUniform
    },
    'scaler': {
        'numerical': ScalerStandard,
        'categorical': None,
        'datetime': ScalerStandard,
        'object': None
    },
    'discretizing': {
        'numerical': DiscretizingKBins,
        'categorical': EncoderLabel,
        'datetime': DiscretizingKBins,
        'object': EncoderLabel
    }
}
```

### Encoder

The `encoder` submodule transforms categorical data into numerical format, a requirement for many modeling procedures.

#### `EncoderUniform`

Applying uniform encoders during data processing, as suggested by [datacebo](https://datacebo.com/blog/improvement-uniform-encoder/), can enhance the performance of generative algorithms compared to other encoders. The concept is straightforward: map each category to a specific range in the uniform distribution, with ranges determined by the relative proportion of each category in the data. Major categories occupy larger areas under the distribution.

Advantages of using a uniform encoder:

1. The variable's distribution converts from discrete to continuous, facilitating modeling.
2. The range of the new distribution is fixed, allowing easy conversion of any value between 0 and 1 to a category.
3. The mapping relationship retains information about the original distribution, a valuable property for sampling. More frequent categories are more likely to be sampled due to their larger areas under the distribution.

A toy example demonstrates the output of a uniform encoder:

Assuming a categorical variable with three categories, 'a', 'b', and 'c', and associated proportions of 1:3:1, respectively. The mapping relationship is as follows:

    {
        'a': [0.0, 0.2),
        'b': [0.2, 0.8),
        'c': [0.8, 1.0]
    }

After transformation by the uniform encoder, data belonging to category 'a' will be assigned a random value between 0.0 (inclusive) and 0.2 (exclusive), data in category 'b' between 0.2 (inclusive) and 0.8 (exclusive), and data in category 'c' between 0.8 (inclusive) and 1.0 (inclusive).

To inverse transform numerical data to categorical data, simply check the range in which the value falls and convert it back to the corresponding category using the mapping relationship.

#### `EncoderLabel`

Transform categorical data into numerical data by assigning a series of integers (1, 2, 3,...) to the categories.

#### `EncoderOneHot`

Transform categorical data into a one-hot numeric data.

### MissingHandler

The `missing` submodule handles missing values in a dataset.

#### `MissingDrop`

This method involves dropping the rows containing missing values in any column.

#### `MissingMean`

Missing values are filled with the mean value of the corresponding column.

#### `MissingMedian`

Missing values are filled with the median value of the corresponding column.

#### `MissingMode`

Missing values are filled with the mode value of the corresponding column. If there are multiple modes, it will randomly fill in one of them.

#### `MissingSimple`

Missing values are filled with a predefined value for the corresponding column.

**Parameters**

`value` (`float`, default=`0.0`): The value to be imputed.

### OutlierHandler

The `outlier` submodule is designed to identify and remove data classified as outliers.

#### `OutlierZScore`

This method classifies data as outliers if the absolute value of the z-score is greater than 3.

#### `OutlierIQR`

Data outside the range of 1.5 times the interquartile range (IQR) is determined as an outlier.

#### `OutlierIsolationForest`

This method uses `IsolationForest` from `sklearn` to identify outliers. It is a global transformation, meaning that if any column uses the isolation forest as an outlierist, it will overwrite the entire config and apply isolation forest to all outlierists.

#### `OutlierLOF`

This method uses `LocalOutlierFactor` from `sklearn` to identify outliers. It is a global transformation, meaning that if any column uses the isolation forest as an outlierist, it will overwrite the entire config and apply isolation forest to all outlierists.

### Scaler

The `scaler` submodule is designed to standardise and scale data using various methods.

#### `ScalerStandard`

This method applies `StandardScaler` from the `sklearn` library, transforming the data to have a mean of 0 and a standard deviation of 1.

#### `ScalerZeroCenter`

Utilising `StandardScaler` from `sklearn`, this method centres the transformed data around a mean of 0.

#### `ScalerMinMax`

By applying `MinMaxScaler` from `sklearn`, this method scales the data to fit within the range [0, 1].

#### `ScalerLog`

This method requires the input data to be positive. It applies log transformation to mitigate the impact of extreme values.

### Discretizing

The `discretizing` submodule is designed to transform continuous data into categorical types, which is useful for some synthetic methods (e.g., `mwem` offered by `smartnoise`).

#### `DiscretizingKBins`

Discretize continuous data into k bins (k intervals).

**Parameters**

`n_bins` (`int`, default=`5`): The value k, the number of bins.
