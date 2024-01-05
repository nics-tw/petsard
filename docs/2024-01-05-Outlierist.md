# Outlierist

`Outlierist` removes the data classified as outliers. We provide four ways to identify outliers.

## `Outlierist_ZScore`: Identify outliers by z-score

If the absolute value of z-score is greater than 3, it will be classified as an outlier.

```python
from PETsARD.Processor.Outlierist import Outlierist_ZScore

outlierist = Outlierist_ZScore()
```

## `Outlierist_IQR`: Identify outliers by IQR

The data which is outside of the range of 1.5*IQR will be determined as an outlier.

```python
from PETsARD.Processor.Outlierist import Outlierist_IQR

outlierist = Outlierist_IQR()
```

## `Outlierist_IsolationForest`: Identify outliers by Isolation Forest

Identify the outliers using isolation forest from sklearn. It is a global transformation. That is, if any of the column uses isolation forest as an outlierist, it will overwrite the whole config and edit all outlierists to isolation forest.

```python
from PETsARD.Processor.Outlierist import Outlierist_IsolationForest

outlierist = Outlierist_IsolationForest()
```

## `Outlierist_LOF`: Identify outliers by Local Outlier Factor

Identify the outliers using local outlier factor from sklearn. It is a global transformation. That is, if any of the column uses local outlier factor as an outlierist, it will overwrite the whole config and edit all outlierists to local outlier factor.

```python
from PETsARD.Processor.Outlierist import Outlierist_LOF

outlierist = Outlierist_LOF()
```