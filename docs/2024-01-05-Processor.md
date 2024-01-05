# Processor

The `Processor` module is responsible for managing preprocessing and postprocessing procedures during experiments. This component facilitates easy data handling, including tasks such as encoding categorical data, handling missing data, excluding outliers, and scaling data. This guide will walk you through the creation and manipulation of a processor instance from the `Processor` class.

`Processor` 模組負責在實驗期間管理資料前處理和後處理（還原）的過程。此元件可進行多種數據處理，包括為類別資料進行編碼、處理缺失值、排除異常值以及標準化資料等任務。本指南將引導您建立和操作 `Processor` 類的物件。

```python
from PETsARD.Processor.Base import Processor

processor = Processor(metadata)

processor.fit(data)

transformed_data = processor.transform(data)

inverse_transformed_data = processor.inverse_transform(synthetic_data)
```



## `Processor` Creation

Once you have an instance of metadata built from the `Metadata` class, you can create a `Processor`. The `config` parameter is optional, allowing you to customise procedures. Upon creation, the processor analyses the metadata to determine the necessary preprocessing and postprocessing procedures. If a `config` is passed, the processor will overwrite default settings and follow the procedures specified in the `config`.

創建 `Processor` 類別的物件之前，必須要有利用 `Metadata` 建立的 metadata 物件。在 `Processor` 參數中，`config` 參數不是必須的，其功能為自訂處理流程。此物件會分析 metadata 以確定所需的前處理和後處理流程。如果有給予 `config`，物件會覆寫預設值，並依照 `config` 中自訂的流程執行。

```python
processor = Processor(
    metadata, # required
    config=None
)
```

### Parameters

`metadata`: The data schema used for creating the processor and inferring appropriate data processing procedures. 

`config` (`dict`): User-defined procedures containing information about the components to be used in each column.

---

`metadata`: 用於推論前處理及後處理流程的數據架構。

`config` (`dict`): 針對每個欄位的自定義處理流程。

### `get_config`

Use this method to access the configuration of procedures to be done during the transformation/inverse transform process. It is summarised by the processor types (missingist, outlierist, encoder, scaler) and columns, storing all data processing objects for user access.

使用此方法取得在轉換/逆轉換過程中的設定檔。此設定檔依據處理類型（missingist、outlierist、encoder、scaler）與欄位進行整理，並呈現給使用者使用，使用者可以直接透過此方法存取儲存在內的處理物件。

```python
processor.get_config(
    col=None,
    print_config=False
)
```

```python
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
`col` (`list`): The columns the user wants to get the config from. If the list is empty, all columns from the metadata will be selected.

`print_config` (`bool`, default=False): Whether the result should be printed.

---
`col` (`list`): 欲取用的欄位。若沒有輸入則視為選擇所有的欄位。

`print_config` (`bool`, default=False): 是否需列印結果。


#### Outputs
(`dict`): The config with selected columns.

---
(`dict`): 含有選定欄位的設定檔。

### `set_config`

Edit the whole config. To maintain the structure of the config, it fills the unspecified processors with `None`. If you don't want to do this, use `update_config` instead.

編輯整份設定檔。為了保持設定檔的結構，會將未指定的處理器設為 `None`。如果您不想這樣做，請改用 `update_config`。

```python
processor.set_config(config)
```

#### Parameters
`config` (`dict`): The dict with the same format as the config class.

---
`config` (`dict`): 與設定檔格式相同的 `dict` 輸入。

### `update_config`

Update part of the config.

更改部分設定檔。

```python
processor.update_config(config)
```

#### Parameters
`config` (`dict`): The dict with the same format as the config class.

---
`config` (`dict`): 與設定檔格式相同的 `dict` 輸入。

### `get_changes`

Compare the differences between the current config and the default config.

比較目前設定檔與預設設定檔之間的差異。

```python
processor.get_changes()
```

#### Outputs
(`pandas.DataFrame`): A dataframe recording the differences bewteen the current config and the default config.

---
(`pandas.DataFrame`): 記錄兩者差異的資料表。

## Data Processing

### `fit`

Learn the structure of the data.

學習資料整體結構。

```python
processor.fit(
    data,
    sequence=None
)
```

#### Parameters
`data` (`pandas.DataFrame`): The data to be fitted.

`sequence` (`list`): The processing sequence, allowing users to skip procedures and alter the execution order. Avaliable procedures: 'missingist', 'outlierist', 'encoder', 'scaler'. This is the default sequence if the user doesn't pass a sequence to the method.

---
`data` (`pandas.DataFrame`): 用來學習的資料。

`sequence` (`list`): 處理流程，可允許用戶跳過特定流程或改變執行順序。可用的流程選項：'missingist'、'outlierist'、'encoder'、'scaler'。若用戶未指定流程，則使用此作為預設序列。

### `transform`

Conduct the data preprocessing procedure.

進行資料前處理。

```python
transformed = processor.transform(data)
```

#### Parameters
`data` (`pandas.DataFrame`): The data to be transformed.

---
`data` (`pandas.DataFrame`): 要轉換的資料。

#### Outputs
(`pandas.DataFrame`): The data after transformation.

---
(`pandas.DataFrame`): 轉換完成的資料。

### `inverse_transform`

Conduct the data postprocessing procedure.

進行資料後處理。

```python
inverse_transformed = processor.inverse_transform(data)
```

#### Parameters
`data` (`pandas.DataFrame`): The data to be inverse transformed.

---
`data` (`pandas.DataFrame`): 要轉換的資料。

#### Outputs
(`pandas.DataFrame`): The data after inverse transformation.

---
(`pandas.DataFrame`): 轉換完成的資料。