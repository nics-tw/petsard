# Outlierist

The `Outlierist` module is designed to identify and remove data classified as outliers. Four methods for identifying outliers are provided:

`Outlierist` 模組旨在識別並刪除被歸類為異常值的數據。此套件提供了四種識別異常值的方法：

## `Outlierist_ZScore`: Identify outliers by z-score

This method classifies data as outliers if the absolute value of the z-score is greater than 3.

此方法將 z 分數的絕對值大於 3 的資料歸類為異常值。

```python
from PETsARD.Processor.Outlierist import Outlierist_ZScore

outlierist = Outlierist_ZScore()
```

## `Outlierist_IQR`: Identify outliers by IQR

Data outside the range of 1.5 times the interquartile range (IQR) is determined as an outlier.

在此方法中，超過 1.5 倍四分位距（IQR）範圍的資料會被視為異常值。

```python
from PETsARD.Processor.Outlierist import Outlierist_IQR

outlierist = Outlierist_IQR()
```

## `Outlierist_IsolationForest`: Identify outliers by Isolation Forest

This method uses `IsolationForest` from sklearn to identify outliers. It is a global transformation, meaning that if any column uses the isolation forest as an outlierist, it will overwrite the entire config and apply isolation forest to all outlierists.

此方法使用 sklearn 的 `IsolationForest` 進行異常值識別。這是一種全域轉換，意即只要設定檔中有任何欄位使用此方法作為異常值處理器，它將覆寫整個設定檔並將此方法應用於所有欄位。

```python
from PETsARD.Processor.Outlierist import Outlierist_IsolationForest

outlierist = Outlierist_IsolationForest()
```

## `Outlierist_LOF`: Identify outliers by Local Outlier Factor

This method uses `LocalOutlierFactor` from sklearn to identify outliers. It is a global transformation, meaning that if any column uses the isolation forest as an outlierist, it will overwrite the entire config and apply isolation forest to all outlierists.

此方法使用 sklearn 的 `LocalOutlierFactor` 進行異常值識別。這是一種全域轉換，意即只要設定檔中有任何欄位使用此方法作為異常值處理器，它將覆寫整個設定檔並將此方法應用於所有欄位。

```python
from PETsARD.Processor.Outlierist import Outlierist_LOF

outlierist = Outlierist_LOF()
```