---
title: Processor
type: docs
weight: 35
prev: docs/api/splitter
next: docs/api/synthesizer
sidebar:
  open: true
---


```python
Processor(
    metadata,
    config=None
)
```

Create a data processor to manage data preprocessing and postprocessing workflows.

## Parameters

- `metadata` (Metadata): Data schema object providing column-level metadata and type information
  - Required
- `config` (dict, optional): Custom data processing configuration
  - Default: None
  - Used to override default processing procedures
  - Structure: `{processing type: {column name: processing method}}`

## Examples

```python
from petsard import Processor


# Basic usage
proc = Processor(metadata=split.metadata)

# Using custom configuration
    'missing': {'age': 'missing_mean'},
    'outlier': {'income': 'outlier_iqr'}
}
proc = Processor(metadata=split.metadata, config=custom_config)

# Data Transformation
proc.fit(data=load.data)
transformed_data = proc.transform(data=load.data)

# Restore to original type/format
inverse_transformed_data = proc.inverse_transform(data=synthetic_data)
```

## Methods

### `get_config()`

```python
proc.get_config(
    col=None,
    print_config=False
)
```

**Parameters**

- `col` (list, optional): Column names to retrieve configuration for
  - Default: None, retrieves configuration for all columns
- `print_config` (bool, optional): Whether to print the configuration
  - Default: False

**Returns**

- (dict): Dictionary containing processing procedure configurations

### `update_config()`

```python
proc.update_config(config)
```

Update the processor's configuration.

**Parameters**

- `config` (dict): New processing procedure configuration

**Returns**

None

### `get_changes()`

Compare current configuration with default configuration.

**Parameters**

None

**Returns**

- (pandas.DataFrame): Table recording configuration differences

### `fit()`

```python
proc.fit(
    data,
    sequence=None
)
```

Learn data structure and prepare transformation workflow.

**Parameters**

- `data` (pandas.DataFrame): Dataset used for learning
- `sequence` (list, optional): Custom processing flow order
  - Default: None
  - Available values: 'missing', 'outlier', 'encoder', 'scaler', 'discretizing'

**Returns**

None

### `transform()`

```python
proc.transform(data)
```

Perform data preprocessing transformation.

**Parameters**

- `data` (pandas.DataFrame): Dataset to be transformed

**Returns**

- (pandas.DataFrame): Transformed data

### `inverse_transform()`

```python
proc.inverse_transform(data)
```

Perform data postprocessing inverse transformation.

**Parameters**

- `data` (pandas.DataFrame): Dataset to be inverse transformed

**Returns**

- (pandas.DataFrame): Inverse transformed data

## Appx.: Available Process type

### Config Setting

**Format**

```python
config = {
    processor-type: {
        colname: processor-method
    }
}
```

**Examples**

This configuration customizes data processing methods for different columns. The age column uses mean for missing values, Z-score for outliers, min-max scaling, and K-bins discretization; gender column is one-hot encoded; income column uses interquartile range for outliers; and salary column is standardized.

```python
config = {
    'missing': {
        'age': 'missing_mean',
        'salary': 'missing_median'
    },
    'outlier': {
        'income': 'outlier_iqr',
        'age': 'outlier_zscore'
    },
    'encoder': {
        'gender': 'encoder_onehot',
        'city': 'encoder_label'
    },
    'scaler': {
        'salary': 'scaler_standard',
        'age': 'scaler_minmax'
    },
    'discretizing': {
        'age': 'discretizing_kbins'
    }
}
```

### Available Process type

Processor supports two main types of data processing:

- **Representation Transformation** changes how data is represented while preserving the original information. This includes:
  - **Encoding**: converting categorical data to numerical representation
  - **Discretizing**: continuous values to discrete representation
  - **Scaling**: remapping numerical ranges

- **Information Modification** enhances data quality by addressing data imperfections. This includes:
  - **Missing handling**: completing missing data points
  - **Outlier handling**: smoothing data noise

| Process type | Process method | Parameters |
| :---: | :---: | :---: |
| Encoding | `EncoderUniform` | 'encoder_uniform' |
| Encoding | `EncoderLabel`   | 'encoder_label'   |
| Encoding | `EncoderOneHot`  | 'encoder_onehot'  |
| Discretizing | `DiscretizingKBins` | 'discretizing_kbins' |
| Scaling | `ScalerStandard`   | 'scaler_standard'   |
| Scaling | `ScalerZeroCenter` | 'scaler_zerocenter' |
| Scaling | `ScalerMinMax`     | 'scaler_minmax'     |
| Scaling | `ScalerLog`        | 'scaler_log'        |
| Scaling | `ScalerTimeAnchor` | 'scaler_timeanchor' |
| Missing | `MissingMean`   | 'missing_mean'   |
| Missing | `MissingMedian` | 'missing_median' |
| Missing | `MissingMode`   | 'missing_mode'   |
| Missing | `MissingSimple` | 'missing_simple' |
| Missing | `MissingDrop`   | 'missing_drop'   |
| Outlier | `OutlierZScore`          | 'outlier_zscore'          |
| Outlier | `OutlierIQR`             | 'outlier_iqr'             |
| Outlier | `OutlierIsolationForest` | 'outlier_isolationforest' |
| Outlier | `OutlierLOF`             | 'outlier_lof'             |

#### Encoding

##### `EncoderUniform`

Mapping each category to a specific range within a uniform distribution, with the range size determined by the frequency of the category in the data.

##### `EncoderLabel`

Transform categorical data into numerical data by assigning a series of integers (1, 2, 3,…) to the categories.

##### `EncoderOneHot`

Transform categorical data into a one-hot numeric data.

#### Discretizing

##### `DiscretizingKBins`

Discretize continuous data into k bins (k intervals).

**Parameters**

- `n_bins` (int, default=5): The value k, the number of bins.

#### Scaling

##### `ScalerStandard`

Utilising `StandardScaler` from the `sklearn` library, transforming the data to have a mean of 0 and a standard deviation of 1.

##### `ScalerZeroCenter`

Utilising `StandardScaler` from `sklearn`, this method centres the transformed data around a mean of 0.

##### `ScalerMinMax`

By applying `MinMaxScaler` from `sklearn`, this method scales the data to fit within the range [0, 1].

##### `ScalerLog`

This method requires the input data to be positive. It applies log transformation to mitigate the impact of extreme values.

##### `ScalerTimeAnchor`

This method scales datetime data by calculating time differences from a reference time series. It provides two modes of scaling:

**Parameters**

- `reference` (str): The name of the reference column used for time difference calculation. Must be a datetime column.
- `unit` (str, default='D'): The unit of time difference calculation.
  - 'D': Days (default)
  - 'S': Seconds

**Examples**

```yaml
scaler:
    create_time:
      method: 'scaler_timeanchor'
      reference: 'event_time'
      unit: 'D'
```

#### Missing

##### `MissingMean`

Missing values are filled with the mean value of the corresponding column.

##### `MissingMedian`

Missing values are filled with the median value of the corresponding column.

##### `MissingMode`

Missing values are filled with the mode value of the corresponding column. If there are multiple modes, it will randomly fill in one of them.

##### `MissingSimple`

Missing values are filled with a predefined value for the corresponding column.

**Parameters**

- `value` (float, default=0.0): The value to be imputed.

##### `MissingDrop`

This method involves dropping the rows containing missing values in any column.

#### Outlier

##### `OutlierZScore`

This method classifies data as outliers if the absolute value of the z-score is greater than 3.

##### `OutlierIQR`

Data outside the range of 1.5 times the interquartile range (IQR) is determined as an outlier.

##### `OutlierIsolationForest`

This method uses `IsolationForest` from `sklearn` to identify outliers. It is a global transformation, meaning that if any column uses the isolation forest as an outlierist, it will overwrite the entire config and apply isolation forest to all outlierists.

##### `OutlierLOF`

This method uses `LocalOutlierFactor` from `sklearn` to identify outliers. It is a global transformation, meaning that if any column uses the isolation forest as an outlierist, it will overwrite the entire config and apply isolation forest to all outlierists.

### Default Processor method

This mapping defines default processing methods for different data types. Numerical types use mean imputation, interquartile range for outliers, standard scaling, and K-bins discretization; categorical types use drop missing values, uniform encoding, and label encoding.

```python
PROCESSOR_MAP: dict[str, dict[str, str]] = {
    "missing": {
        "numerical": MissingMean,
        "categorical": MissingDrop,
        "datetime": MissingDrop,
        "object": MissingDrop,
    },
    "outlier": {
        "numerical": OutlierIQR,
        "categorical": lambda: None,
        "datetime": OutlierIQR,
        "object": lambda: None,
    },
    "encoder": {
        "numerical": lambda: None,
        "categorical": EncoderUniform,
        "datetime": lambda: None,
        "object": EncoderUniform,
    },
    "scaler": {
        "numerical": ScalerStandard,
        "categorical": lambda: None,
        "datetime": ScalerStandard,
        "object": lambda: None,
    },
    "discretizing": {
        "numerical": DiscretizingKBins,
        "categorical": EncoderLabel,
        "datetime": DiscretizingKBins,
        "object": EncoderLabel,
    },
}
```