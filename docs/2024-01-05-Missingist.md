# Missingist

`Missingist` deal with the missing values in a dataset. We provide four methods to cope with them.

## Drop the missing values

Drop the corresponding rows with missing values in any column.

```python
from PETsARD.Processor.Missingist import Missingist_Drop

missingist = Missingist_Drop()
```

## Fill the missing values with the mean

Fill the missing values with the mean value of the corresponding column.

```python
from PETsARD.Processor.Missingist import Missingist_Mean

missingist = Missingist_Mean()
```

## Fill the missing values with the median

Fill the missing values with the median value of the corresponding column.

```python
from PETsARD.Processor.Missingist import Missingist_Median

missingist = Missingist_Median()
```

## Fill the missing values with a predefined value

Fill the missing values with a predefined value for the corresponding column.

```python
from PETsARD.Processor.Missingist import Missingist_Simple

missingist = Missingist_Simple(value=0.0)
```

### Parameters
`value` (`float`): The value to be imputed.

### Outputs
None.