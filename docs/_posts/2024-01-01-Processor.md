The `Processor` module is responsible for managing preprocessing and postprocessing procedures during experiments. This component facilitates easy data handling, including tasks such as encoding categorical data, handling missing data, excluding outliers, and scaling data. This guide will walk you through the creation and manipulation of a processor instance from the `Processor` class.

`Processor` 模組負責在實驗期間管理資料前處理和後處理（還原）的過程。此元件可進行多種數據處理，包括為類別資料進行編碼、處理缺失值、排除異常值以及標準化資料等任務。本指南將引導您建立和操作 `Processor` 類的物件。


```Python
from PETsARD import Processor


proc = Processor(metadata=load.metadata)
proc.fit(data=load.data)
transformed_data = proc.transform(data=load.data)
print(transformed_data.head(1))

# synthetic_data = ...

inverse_transformed_data = proc.inverse_transform(data=synthetic_data)
print(inverse_transformed_data.head(1))
```


# `Processor`

Once you have an instance of metadata built from the `Loader` class, you can create a `Processor`. The `config` parameter is optional, allowing you to customise procedures. Upon creation, the processor analyses the metadata to determine the necessary preprocessing and postprocessing procedures. If a `config` is passed, the processor will overwrite default settings and follow the procedures specified in the `config`.

創建 `Processor` 類別的物件之前，必須要有利用 `Loader` 建立的 metadata 物件。在 `Processor` 參數中，`config` 參數不是必須的，其功能為自訂處理流程。此物件會分析 metadata 以確定所需的前處理和後處理流程。如果有給予 `config`，物件會覆寫預設值，並依照 `config` 中自訂的流程執行。

```python
proc = Processor(
    metadata=load.metadata, # required
    config=None
)
```

**Parameters**

`metadata` (`Metadata`): The data schema used for creating the processor and inferring appropriate data processing procedures. 用於推論前處理及後處理流程的數據架構。
    - Note that the requirement is for the `Metadata` type itself, not `Metadata.metadata` as a dictionary. See the [Metadata page](https://nics-tw.github.io/PETsARD/Metadata.html) for more information. 需注意的是這裡所需要的是 `Metadata` 類型本身，而非字典形式的 `Metadata.metadata`。可參閱 [Metadata 頁面](https://nics-tw.github.io/PETsARD/Metadata.html)

`config` (`dict`, default=`None`): User-defined procedures containing information about the components to be used in each column. 針對每個欄位的自定義處理流程。


## `config`


`config` is a nested `dict` defining the processing proceures. The structure is shown below:

`config` 是一個定義處理流程的巢狀 `dict`，結構如下：

```Python
{
    processor_type: {
        col_name: processor_obj
    }
}
```


Noted that `processor_obj` can be an initialised object from processing submodules or a class name (see "Available Processor Types").

其中 `processor_obj` 可以是來自子模組中已初始化的物件，或者是類別名稱（詳見 "Available Processor Types"）。


## `get_config()`


Use this method to access the configuration of procedures to be done during the transformation/inverse transform process. It is summarised by the processor types (e.g., missing, outlier, encoder, scaler, discretizing) and columns, storing all data processing objects for user access.

使用此方法取得在轉換/逆轉換過程中的設定檔。此設定檔依據處理類型（例如：missing、outlier、encoder、scaler、discretizing）與欄位進行整理，並呈現給使用者使用，使用者可以直接透過此方法存取儲存在內的處理物件。


```Python
proc.get_config(
    col=None,
    print_config=False
)
```

```plain_text
{'missing': {
    'gen': <PETsARD.processor.missing.MissingDrop at 0x28afa7d90>,
    'age': <PETsARD.processor.missing.MissingSimple at 0x28af374f0>
    },
 'outlier': {
    'gen': None,
    'age': <PETsARD.processor.outlier.OutlierLOF at 0x28afa72b0>
    },
 'encoder': {
    'gen': <PETsARD.processor.encoder.EncoderOneHot at 0x28afa6f80>,
    'age': None
    },
 'scaler': {
    'gen': None,
    'age': <PETsARD.processor.scaler.ScalerMinMax at 0x28afa6ec0>},
 'discretizing': {
    'gen': <PETsARD.processor.encoder.EncoderLabel at 0x28afa4910>,
    'age': <PETsARD.processor.discretizing.DiscretizingKBins at 0x28afa7310>
    }
}
```


**Parameters**


`col` (`list`, default=`None`): The columns the user wants to get the config from. If the list is empty, all columns from the metadata will be selected. 欲取用的欄位。若沒有輸入則視為選擇所有的欄位。

`print_config()` (`bool`, default=`False`): Whether the result should be printed. 是否需列印結果。


**Outputs**


(`dict`): The config with selected columns. 含有選定欄位的設定檔。


## `update_config()`

Update part of the config.

更改部分設定檔。

```Python
proc.update_config(config=config)
```


**Parameters**


`config` (`dict`): The `dict` with the same format as the config class. 與設定檔格式相同的 `dict` 輸入。


## `get_changes()`


Compare the differences between the current config and the default config. See "Available Processor Types" to know more about the default config.

比較目前設定檔與預設設定檔之間的差異。詳見 "Available Processor Types" 以了解預設設定檔的內容。


```Python
proc.get_changes()
```

**Outputs**

(`pandas.DataFrame`): A dataframe recording the differences bewteen the current config and the default config. 記錄當前設定檔與預設設定檔兩者差異的資料表。


## `fit()`


Learn the structure of the data.

學習資料整體結構。


```python
proc.fit(
    data=data,
    sequence=None
)
```


**Parameters**


`data` (`pandas.DataFrame`): The data to be fitted. 用來學習的資料。

`sequence` (`list`, default=`None`): The processing sequence, allowing users to skip procedures and alter the execution order. Avaliable procedures: `'missing'`, `'outlier'`, `'encoder'`, `'scaler'`, `'discretizing'`. `['missing', 'outlier', 'encoder', 'scaler']` is the default sequence if the user doesn't pass a sequence to the method. Noted that `'discretizing'` and `'encoder'` cannot be used in a sequence at the same time, and `'discretizing'` must be the last element if it exists in a sequence. 處理流程，可允許用戶跳過特定流程或改變執行順序。可用的流程選項： `'missing'`、`'outlier'`、`'encoder'`、`'scaler'`、`'discretizing'`。若用戶未指定流程，則使用 `['missing', 'outlier', 'encoder', 'scaler']` 作為預設序列。此外，`'discretizing'` 與 `'encoder'` 不能在序列中同時存在，且如果 `'discretizing'` 存在，其必須為最後一個元素。


## `transform()`


Conduct the data preprocessing procedure.

進行資料前處理。


```Python
transformed_data = proc.transform(data=data)
```


**Parameters**


`data` (`pandas.DataFrame`): The data to be transformed. 要轉換的資料。


**Outputs**


(`pandas.DataFrame`): The data after transformation. 轉換完成的資料。


## `inverse_transform()`


Conduct the data postprocessing procedure.

進行資料後處理。


```Python
inverse_transformed = proc.inverse_transform(data=data)
```


**Parameters**


`data` (`pandas.DataFrame`): The data to be inverse transformed. 要轉換的資料。


**Outputs**


(`pandas.DataFrame`): The data after inverse transformation. 轉換完成的資料。


# Available Processor Types


In this section, we provide a comprehensive list of supported processor types and their associated classes to facilitate thorough customization. You have the option to specify the processor classes for `config` either by initializing an object or by directly entering the class name (outlined below). The former approach offers flexibility for customization, while the latter offers simplicity of use.

我們列出所有目前支援的處理類型及相關類別，以提供細部的調整。若要在 `config` 使用這些處理類型，可以創造一個對應物件放入，或者直接填入類別名稱（詳見下文）。前者提供更多客製化的彈性，而後者則方便使用。


<div class="table-wrapper" markdown="block">

| Submodule | Processor Type | Class | Alias (class name) |
|:---:|:---:|:---:|:---:|
| `encoder` | Encoder | `EncoderUniform` | 'encoder_uniform' |
| `encoder` | Encoder | `EncoderLabel` | 'encoder_label' |
| `encoder` | Encoder | `EncoderOneHot` | 'encoder_onehot' |
| `missing` | MissingHandler | `MissingMean` | 'missing_mean' |
| `missing` | MissingHandler | `MissingMedian` | 'missing_median' |
| `missing` | MissingHandler | `MissingSimple` | 'missing_simple' |
| `missing` | MissingHandler | `MissingDrop` | 'missing_drop' |
| `outlier` | OutlierHandler | `OutlierZScore` | 'outlier_zscore' |
| `outlier` | OutlierHandler | `OutlierIQR` | 'outlier_iqr' |
| `outlier` | OutlierHandler | `OutlierIsolationForest` | 'outlier_isolationforest' |
| `outlier` | OutlierHandler | `OutlierLOF`| 'outlier_lof' |
| `scaler` | Scaler | `ScalerStandard` | 'scaler_standard' |
| `scaler` | Scaler | `ScalerZeroCenter` | 'scaler_zerocenter' |
| `scaler` | Scaler | `ScalerMinMax` | 'scaler_minmax' |
| `scaler` | Scaler | `ScalerLog` | 'scaler_log' |
| `discretizing` | Discretizing | `DiscretizingKBins` | 'discretizing_kbins' |

</div>


The following processors represent the default ones assigned based on `'inder_dtype'` in the `metadata`. See [Metadata](https://nics-tw.github.io/PETsARD/Metadata.html) page for details.

預設的處理類型如下，會根據 `metadata` 中的 `'inder_dtype'` 不同而有所調整。詳見 [Metadata](https://nics-tw.github.io/PETsARD/Metadata.html) 頁面。


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


## Encoder


The `encoder` submodule transforms categorical data into numerical format, a requirement for many modeling procedures.

`encoder` 子模組將類別資料轉換為連續型資料，方便套用大多數的模型。


### `EncoderUniform`

Applying uniform encoders during data processing, as suggested by [datacebo](https://datacebo.com/blog/improvement-uniform-encoder/), can enhance the performance of generative algorithms compared to other encoders. The concept is straightforward: map each category to a specific range in the uniform distribution, with ranges determined by the relative proportion of each category in the data. Major categories occupy larger areas under the distribution.

[datacebo](https://datacebo.com/blog/improvement-uniform-encoder/) 認為在資料處理過程中使用 Uniform encoder 來處理類別資料，可以提升生成模型的表現。Uniform encoder 的概念非常直觀：將每個類別映射到 Uniform distribution 中的特定範圍，範圍由資料中各類別的比例決定，因此較常見的類別會對應到較大的範圍。


Advantages of using a uniform encoder:

1. The variable's distribution converts from discrete to continuous, facilitating modeling.
2. The range of the new distribution is fixed, allowing easy conversion of any value between 0 and 1 to a category.
3. The mapping relationship retains information about the original distribution, a valuable property for sampling. More frequent categories are more likely to be sampled due to their larger areas under the distribution.

相較於其他類型的處理方式，使用 Uniform encoder 有以下優勢：

1. 變數的分布從離散轉換為連續，有助於建模。
2. 新分配的範圍固定，可將任何介於 0 和 1 之間的值輕鬆轉換為類別變數。
3. 映射關係保留原始資料分配的訊息，有助於進行抽樣。由於出現頻率較高的類別其分配下的面積較大，因此更有可能被抽樣，反映出原始資料的樣態。


A toy example demonstrates the output of a uniform encoder:

Assuming a categorical variable with three categories, 'a', 'b', and 'c', and associated proportions of 1:3:1, respectively. The mapping relationship is as follows:

    {
        'a': [0.0, 0.2),
        'b': [0.2, 0.8),
        'c': [0.8, 1.0]
    }

After transformation by the uniform encoder, data belonging to category 'a' will be assigned a random value between 0.0 (inclusive) and 0.2 (exclusive), data in category 'b' between 0.2 (inclusive) and 0.8 (exclusive), and data in category 'c' between 0.8 (inclusive) and 1.0 (inclusive).

To inverse transform numerical data to categorical data, simply check the range in which the value falls and convert it back to the corresponding category using the mapping relationship.


以下是 Uniform encoder 的簡易範例：

假設一個具有三個類別 'a'、'b' 和 'c'的類別變數，其資料比例為 1:3:1。則映射關係如下：

    {
        'a': [0.0, 0.2),
        'b': [0.2, 0.8),
        'c': [0.8, 1.0]
    }

經過 Uniform encoder 的轉換後，類別 'a' 會用介於 0.0（包含）和 0.2（不包含）之間的隨機值取代，類別 'b' 會用介於 0.2（包含）和 0.8（不包含）之間的隨機值取代，類別 'c' 則會用介於 0.8（包含）和 1.0（包含）之間的隨機值取代。

而要將連續型變數反轉為類別資料，只需檢查其值所處的範圍，然後使用映射關係將其轉換回相應的類別即可。


### `EncoderLabel`

Transform categorical data into numerical data by assigning a series of integers (1, 2, 3,...) to the categories.

將類別變數對應到一系列的整數 (1, 2, 3,...) 藉此達到轉換為連續型資料的目的。


### `EncoderOneHot`

Transform categorical data into a one-hot numeric data.

將類別變數對應到一系列的 one-hot 數值資料。


## MissingHandler

The `missing` submodule handles missing values in a dataset.

`missing` 子模組處理數據集中的缺失值。


### `MissingDrop`

This method involves dropping the rows containing missing values in any column.

捨棄任何含有缺失值的列。


### `MissingMean`

Missing values are filled with the mean value of the corresponding column.

將缺失值用該欄的平均值填入。


### `MissingMedian`

Missing values are filled with the median value of the corresponding column.

將缺失值用該欄的中位數填入。


### `MissingSimple`

Missing values are filled with a predefined value for the corresponding column.

將缺失值用指定的值填入。


**Parameters**

`value` (`float`, default=`0.0`): The value to be imputed. 要填入的自訂值。


## OutlierHandler


The `outlier` submodule is designed to identify and remove data classified as outliers.

`outlier` 子模組旨在識別並刪除被歸類為異常值的數據。


### `OutlierZScore`

This method classifies data as outliers if the absolute value of the z-score is greater than 3.

此方法將 z 分數的絕對值大於 3 的資料歸類為異常值。


### `OutlierIQR`

Data outside the range of 1.5 times the interquartile range (IQR) is determined as an outlier.

在此方法中，超過 1.5 倍四分位距（IQR）範圍的資料會被視為異常值。


### `OutlierIsolationForest`

This method uses `IsolationForest` from `sklearn` to identify outliers. It is a global transformation, meaning that if any column uses the isolation forest as an outlierist, it will overwrite the entire config and apply isolation forest to all outlierists.

此方法使用 `sklearn` 的 `IsolationForest` 進行異常值識別。這是一種全域轉換，意即只要設定檔中有任何欄位使用此方法作為異常值處理器，它將覆寫整個設定檔並將此方法應用於所有欄位。


### `OutlierLOF`

This method uses `LocalOutlierFactor` from `sklearn` to identify outliers. It is a global transformation, meaning that if any column uses the isolation forest as an outlierist, it will overwrite the entire config and apply isolation forest to all outlierists.

此方法使用 `sklearn` 的 `LocalOutlierFactor` 進行異常值識別。這是一種全域轉換，意即只要設定檔中有任何欄位使用此方法作為異常值處理器，它將覆寫整個設定檔並將此方法應用於所有欄位。


## Scaler


The `scaler` submodule is designed to standardise and scale data using various methods.

`scaler` 子模組旨在使用各種方法對數據進行標準化和縮放。


### `ScalerStandard`

This method applies `StandardScaler` from the `sklearn` library, transforming the data to have a mean of 0 and a standard deviation of 1.

此方法使用 `sklearn` 中的 `StandardScaler`，將資料轉換為平均值為 0、標準差為 1 的樣態。

### `ScalerZeroCenter`

Utilising `StandardScaler` from `sklearn`, this method centres the transformed data around a mean of 0.

利用 `sklearn` 中的 `StandardScaler`，將資料轉換為平均值為 0 的樣態。


### `ScalerMinMax`

By applying `MinMaxScaler` from `sklearn`, this method scales the data to fit within the range [0, 1].

利用 `sklearn` 中的 `MinMaxScaler`，將資料轉換至 [0, 1] 的範圍。


### `ScalerLog`


This method requires the input data to be positive. It applies log transformation to mitigate the impact of extreme values.

此方法僅能在資料為正的情形可用，可用於減緩極端值對整體資料的影響。


## Discretizing


The `discretizing` submodule is designed to transform continuous data into categorical types, which is useful for some synthetic methods (e.g., `mwem` offered by `smartnoise`).

`discretizing` 子模組可將連續資料轉換為類別資料，適用於部分合成資料方法，如 `smartnoise` 的 `mwem` 。


### `DiscretizingKBins`


Discretize continuous data into k bins (k intervals).

將連續資料切分為 k 個類別（k 個區間）。


**Parameters**

`n_bins` (`int`, default=`5`): The value k, the number of bins. k 值，即為類別數。
