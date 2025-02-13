---
title: Data Preprocessing
type: docs
weight: 20
prev: docs/tutorial/use-cases/data-description
next: docs/tutorial/use-cases/comparing-synthesizers
sidebar:
  open: false
---


Ensuring the quality of source data before synthesis is crucial. High-quality input data not only improves the synthesis results but also reduces potential technical issues during the synthesis process. `PETsARD` provides comprehensive data preprocessing tools to help you enhance data quality:

> **Important Note**: CAPE's default preprocessing pipeline performs missing value handling and outlier processing before encoding and scaling operations. Users are advised to modify this default processing order only for experimental purposes and when fully familiar with their technical process details and objectives. `PETsARD` does not guarantee the effectiveness of data preprocessing when the default order is altered.

## Information Modification

### [Handling Missing Values](./handling-missing)

- Handle missing and incomplete values in data
- Ensure data completeness through deletion, statistical imputation, and custom imputation methods
- Provide customized options for different data fields and types

<!-- [Handling Outlier](./handling-outliers) -->
### Handling Outliers (WIP)

- Identify and handle abnormal or extreme values
- Prevent outliers from affecting model learning
- Provide multiple outlier detection and processing strategies

## Representation Transformation

### [Encoding Categorical Variables](./encoding-category)

- Convert categorical data to numerical format
- Support various encoding methods to preserve data characteristics
- Ensure synthetic algorithms can effectively process all data types

<!-- [Discretizing Continuous Values](./discretizing-continuous) -->
### Discretizing Continuous Values (WIP)

- Convert continuous values into discrete intervals
- Reduce data complexity
- Provide multiple grouping strategy options

<!-- [Scaling Numerical Features](./scaling-numeric) -->
### Scaling Numerical Features (WIP)

- Unify value ranges across different columns
- Improve model convergence performance
- Support various standardization and normalization methods

## Appx.: Available Process type

Following CAPE team's preprocessing taxonomy, `PETsARD` subdivides data preprocessing operations into two main types and provides support for both:

- **Information Modification** enhances data quality by addressing data imperfections. This includes:
  - **Missing handling**: completing missing data points
  - **Outlier handling**: smoothing data noise

- **Representation Transformation** changes how data is represented while preserving the original information. This includes:
  - **Encoding**: converting categorical data to numerical representation
  - **Discretizing**: continuous values to discrete representation
  - **Scaling**: remapping numerical ranges

The following table lists all preprocessing methods supported by `PETsARD`. You can learn how to use each method through the tutorial examples, or visit [Processor](../../../api/processor/) for detailed technical implementation.

| Process type | Process method | Parameters |
| :---: | :---: | :---: |
| Missing | `MissingMean`   | 'missing_mean'   |
| Missing | `MissingMedian` | 'missing_median' |
| Missing | `MissingMode`   | 'missing_mode'   |
| Missing | `MissingSimple` | 'missing_simple' |
| Missing | `MissingDrop`   | 'missing_drop'   |
| Outlier | `OutlierZScore`          | 'outlier_zscore'          |
| Outlier | `OutlierIQR`             | 'outlier_iqr'             |
| Outlier | `OutlierIsolationForest` | 'outlier_isolationforest' |
| Outlier | `OutlierLOF`             | 'outlier_lof'             |
| Encoding | `EncoderUniform` | 'encoder_uniform' |
| Encoding | `EncoderLabel`   | 'encoder_label'   |
| Encoding | `EncoderOneHot`  | 'encoder_onehot'  |
| Discretizing | `DiscretizingKBins` | 'discretizing_kbins' |
| Scaling | `ScalerStandard`   | 'scaler_standard'   |
| Scaling | `ScalerZeroCenter` | 'scaler_zerocenter' |
| Scaling | `ScalerMinMax`     | 'scaler_minmax'     |
| Scaling | `ScalerLog`        | 'scaler_log'        |
| Scaling | `ScalerTimeAnchor` | 'scaler_timeanchor' |