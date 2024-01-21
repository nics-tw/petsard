# Missingist

The `Missingist` module handles missing values in a dataset, offering four methods for coping with them.

`Missingist` 模組處理數據集中的缺失值，並提供四種處理方法。

## `Missingist_Drop`: Drop the missing values

This method involves dropping the rows containing missing values in any column.

捨棄任何含有缺失值的列。

```python
from PETsARD.Processor.Missingist import Missingist_Drop

missingist = Missingist_Drop()
```

## `Missingist_Mean`: Fill the missing values with the mean

Missing values are filled with the mean value of the corresponding column.

將缺失值用該欄的平均值填入。

```python
from PETsARD.Processor.Missingist import Missingist_Mean

missingist = Missingist_Mean()
```

## `Missingist_Median`: Fill the missing values with the median

Missing values are filled with the median value of the corresponding column.

將缺失值用該欄的中位數填入。

```python
from PETsARD.Processor.Missingist import Missingist_Median

missingist = Missingist_Median()
```

## `Missingist_Simple`: Fill the missing values with a predefined value

Missing values are filled with a predefined value for the corresponding column.

將缺失值用指定的值填入。

```python
from PETsARD.Processor.Missingist import Missingist_Simple

missingist = Missingist_Simple(value=0.0)
```

### Parameters
`value` (`float`): The value to be imputed.

---
`value` (`float`): 要填入的自訂值。