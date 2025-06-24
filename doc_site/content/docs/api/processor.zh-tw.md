---
title: Processor
type: docs
weight: 55
prev: docs/api/splitter
next: docs/api/synthesizer
---


```python
Processor(
    metadata,
    config=None
)
```

建立資料處理器，管理資料的前處理與後處理流程。

## 參數

- `metadata` (Metadata): 資料架構物件，提供資料欄位的詮釋資料和型別資訊
  - 必填
- `config` (dict, optional): 自訂資料處理設定
  - 預設值：無
  - 用於覆寫預設的處理程序
  - 結構為 `{處理類型: {欄位名稱: 處理方式}}`

## 範例

```python
from petsard import Processor


# 基本用法
proc = Processor(metadata=split.metadata)

# 使用自定義設定
custom_config = {
    'missing': {'age': 'missing_mean'},
    'outlier': {'income': 'outlier_iqr'}
}
proc = Processor(metadata=split.metadata, config=custom_config)

# 資料前處理
proc.fit(data=load.data)
transformed_data = proc.transform(data=load.data)

# 還原到原始型態
proc.fit(data=load.data)
transformed_data = proc.transform(data=load.data)
```

## 方法

### `get_config()`

```python
proc.get_config(
    col=None,
    print_config=False
)
```

**參數**

- `col` (list, optional)：要取得設定的欄位名稱
  - 預設值：無，表示取得所有欄位
- `print_config` (bool, optional)：是否列印設定
  - 預設值：False

**回傳值**

- (dict): 包含處理程序設定的字典

### `update_config()`

```python
proc.update_config(config)
```

更新處理器的設定。

**參數**

- `config` (dict)：新的處理程序設定

**回傳值**

無

### `get_changes()`

比較當前設定與預設設定的差異。

**參數**

無

**回傳值**

- (pandas.DataFrame)：記錄設定差異的資料表

### `fit()`

```python
proc.fit(
    data,
    sequence=None
)
```

學習資料結構並準備轉換流程。

**參數**

- `data` (pandas.DataFrame)：用於學習的資料集
- `sequence` (list, optional)：自訂處理流程順序
  - 預設值：無
  - 可用值：'missing', 'outlier', 'encoder', 'scaler', 'discretizing'

**回傳值**

無

### `transform()`

```python
proc.transform(data)
```

執行資料前處理轉換。

**參數**

- `data` (pandas.DataFrame)：待轉換的資料集

**回傳值**

- (pandas.DataFrame): 轉換後的資料

### `inverse_transform()`

```python
proc.inverse_transform(data)
```

執行資料後處理還原轉換。

**參數**

- `data` (pandas.DataFrame)：待還原轉換的資料集

**回傳值**

- (pandas.DataFrame): 還原轉換後的資料

## 附錄：支援處理方式

### 預設處理方式

此映射定義了不同資料型別的預設處理方法。數值型別採用平均值填補、四分位距異常值處理、標準化縮放和K-bins離散化；類別型別則使用丟棄遺失值、均勻編碼和標籤編碼。

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

### Config 設定

`config` 是一個巢狀字典，用於自訂各欄位的處理程序。

**格式**

```python
config = {
    處理類型: {
        欄位名稱: 處理程序
    }
}
```

**範例**

這個設定檔為不同欄位客製化資料處理方法。年齡欄位使用平均值填補遺失值、Z-score處理異常值、最小-最大縮放和K-bins離散化；性別欄位採用One-Hot編碼；收入欄位使用四分位距處理異常值；工資欄位則使用標準化縮放。

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

### 遺失值

#### `MissingMean`

將缺失值用該欄的平均值填入。

#### `MissingMedian`

將缺失值用該欄的中位數填入。

#### `MissingMode`

將缺失值用該欄的眾數填入。如果有多個眾數會隨機填入。

#### `MissingSimple`

將缺失值用指定的值填入。

**參數**

- `value` (float, default=0.0)：要填入的自訂值。

#### `MissingDrop`

捨棄任何含有缺失值的列。

### 離群值

#### `OutlierZScore`

此方法將 z 分數的絕對值大於 3 的資料歸類為異常值。

#### `OutlierIQR`

在此方法中，超過 1.5 倍四分位距（IQR）範圍的資料會被視為異常值。

#### `OutlierIsolationForest`

此方法使用 `sklearn` 的 `LocalOutlierFactor` 進行異常值識別。這是一種全域轉換，意即只要設定檔中有任何欄位使用此方法作為異常值處理器，它將覆寫整個設定檔並將此方法應用於所有欄位。

#### `OutlierLOF`

此方法使用 `sklearn` 的 `LocalOutlierFactor` 進行異常值識別。這是一種全域轉換，意即只要設定檔中有任何欄位使用此方法作為異常值處理器，它將覆寫整個設定檔並將此方法應用於所有欄位。

### 編碼

#### `EncoderUniform`

將每個類別映射到均勻分布的特定範圍，範圍大小由資料中類別的出現頻率決定。

#### `EncoderLabel`

將類別變數對應到一系列的整數 (1, 2, 3,…) 藉此達到轉換為連續型資料的目的。

#### `EncoderOneHot`

將類別變數對應到一系列的獨熱編碼 (One-hot) 數值資料。

#### `EncoderDate`

將不標準的日期時間資料轉換為日期格式，支援各種日期格式，包含民國年等自訂曆法。

**參數**

- `input_format` (str, optional)：日期解析格式字串
  - 預設值：無（使用模糊解析）
  - 範例："%Y-%m-%d" 或 "%MinguoY-%m-%d"
- `date_type` (str, default="datetime")：轉換後的日期型別
  - "date"：僅日期（無時間）
  - "datetime"：日期和時間
  - "datetime_tz"：含時區的日期和時間
- `tz` (str, optional)：輸出日期的時區
  - 預設值：無
  - 範例："Asia/Taipei"
- `numeric_convert` (bool, default=False)：是否嘗試轉換數值型時間戳
- `invalid_handling` (str, default="error")：無效日期的處理方式
  - "error"：拋出錯誤
  - "erase"：替換為空值
  - "replace"：使用替換規則
- `invalid_rules` (list[dict[str, str]], optional)：無效日期的替換規則
  - 預設值：無

**範例**

```python
# 基本使用方式
config = {
    'encoder': {
        'created_at': 'encoder_date'
    }
}

# 使用民國年格式
config = {
    'encoder': {
        'doc_date': {
            'method': 'encoder_date',
            'input_format': '%MinguoY-%m-%d'
        }
    }
}

# 使用時區和無效日期處理
config = {
    'encoder': {
        'event_time': {
            'method': 'encoder_date',
            'date_type': 'datetime_tz',
            'tz': 'Asia/Taipei',
            'invalid_handling': 'erase'
        }
    }
}
```

### 尺度

#### `ScalerStandard`

利用 `sklearn` 中的 `StandardScaler`，將資料轉換為平均值為 0、標準差為 1 的樣態。

#### `ScalerZeroCenter`

利用 `sklearn` 中的 `StandardScaler`，將資料轉換為平均值為 0 的樣態。

#### `ScalerMinMax`

利用 `sklearn` 中的 `MinMaxScaler`，將資料轉換至 [0, 1] 的範圍。

#### `ScalerLog`

此方法僅能在資料為正的情形可用，可用於減緩極端值對整體資料的影響。

#### `ScalerTimeAnchor`

此方法透過計算與參考時間序列的時間差來縮放日期時間資料。提供兩種縮放模式：

**參數**

- `reference` (str)：用於計算時間差的參考欄位名稱。必須是日期時間型態的欄位。
- `unit` (str, default='D')：時間差計算的單位。
  - 'D'：天（預設）
  - 'S'：秒

**範例**

```yaml
scaler:
    create_time:
      method: 'scaler_timeanchor'
      reference: 'event_time'
      unit: 'D'
```

### 離散化

#### `DiscretizingKBins`

將連續資料切分為 k 個類別（k 個區間）。

**參數**

- `n_bins` (int, default=5)：k 值，即為類別數。