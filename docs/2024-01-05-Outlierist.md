# Outlierist

The `Outlierist` module is designed to identify and remove data classified as outliers. Four methods for identifying outliers are provided:

## `Outlierist_ZScore`: Identify outliers by z-score

This method classifies data as outliers if the absolute value of the z-score is greater than 3.

```python
from PETsARD.Processor.Outlierist import Outlierist_ZScore

outlierist = Outlierist_ZScore()
```

## `Outlierist_IQR`: Identify outliers by IQR

Data outside the range of 1.5 times the interquartile range (IQR) is determined as an outlier.

```python
from PETsARD.Processor.Outlierist import Outlierist_IQR

outlierist = Outlierist_IQR()
```

## `Outlierist_IsolationForest`: Identify outliers by Isolation Forest

This method uses `IsolationForest` from sklearn to identify outliers. It is a global transformation, meaning that if any column uses the isolation forest as an outlierist, it will overwrite the entire config and apply isolation forest to all outlierists.

```python
from PETsARD.Processor.Outlierist import Outlierist_IsolationForest

outlierist = Outlierist_IsolationForest()
```

## `Outlierist_LOF`: Identify outliers by Local Outlier Factor

This method uses `LocalOutlierFactor` from sklearn to identify outliers. It is a global transformation, meaning that if any column uses the isolation forest as an outlierist, it will overwrite the entire config and apply isolation forest to all outlierists.

```python
from PETsARD.Processor.Outlierist import Outlierist_LOF

outlierist = Outlierist_LOF()
```