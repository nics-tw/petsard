---
title: Metadater
type: docs
weight: 58
prev: docs/api/loader
next: docs/api/metadata
---


```python
Metadater()
```

進階詮釋資料管理系統，提供全面的欄位分析、架構操作和詮釋資料轉換功能。系統採用三層階層架構：**Metadata**（多個資料集的頂層容器）→ **Schema**（個別資料集的結構定義）→ **Field**（包含統計資料和型態資訊的欄位層級詮釋資料）。支援函數式程式設計模式和管線式處理，適用於複雜的資料工作流程。

## 參數

無

## 範例

```python
from petsard import Metadater
import pandas as pd

# 初始化 Metadater
metadater = Metadater()

# 從多個資料集建立詮釋資料
datasets = {
    'users': pd.DataFrame({'id': [1, 2, 3], 'name': ['Alice', 'Bob', 'Charlie']}),
    'orders': pd.DataFrame({'order_id': [101, 102], 'user_id': [1, 2]})
}

metadata = metadater.build_metadata_from_datasets(datasets)

# 建立架構設定
config = metadater.create_schema_config(
    column_types={'id': 'int', 'name': 'str'},
    descriptions={'id': '使用者識別碼', 'name': '使用者全名'}
)

# 套用欄位設定
aligned_data = metadater.apply_field_config(df, schema)

# 將詮釋資料轉換為 DataFrame 進行分析
metadata_df = metadater.get_metadata_to_dataframe(metadata)
```

## 方法

### `build_metadata_from_datasets()`

```python
metadater.build_metadata_from_datasets(datasets, config=None)
```

從多個 DataFrame 建立完整的詮釋資料，可選擇性地提供設定。

**參數**

- `datasets` (dict[str, pd.DataFrame])：架構名稱對應 DataFrame 的字典
- `config` (MetadataConfig | dict, 可選)：詮釋資料產生的設定

**回傳值**

- `Metadata`：包含所有架構資訊的完整詮釋資料物件

### `build_field_from_series()`

```python
metadater.build_field_from_series(series, field_name, config=None)
```

從 pandas Series 建立詳細的欄位詮釋資料。

**參數**

- `series` (pd.Series)：輸入的資料序列
- `field_name` (str)：欄位名稱
- `config` (FieldConfig, 可選)：欄位特定設定

**回傳值**

- `FieldMetadata`：包含統計資料和型態資訊的完整欄位詮釋資料

### `build_schema_from_dataframe()`

```python
metadater.build_schema_from_dataframe(data, config=None)
```

從 DataFrame 產生架構詮釋資料，自動進行欄位分析。

**參數**

- `data` (pd.DataFrame)：輸入的 DataFrame
- `config` (SchemaConfig, 可選)：架構設定

**回傳值**

- `SchemaMetadata`：包含欄位詮釋資料和關聯性的完整架構

### `apply_field_config()`

```python
metadater.apply_field_config(data, schema)
```

套用欄位設定以使資料符合架構需求。

**參數**

- `data` (pd.DataFrame)：要轉換的輸入 DataFrame
- `schema` (SchemaMetadata)：目標架構設定

**回傳值**

- `pd.DataFrame`：與架構對齊的轉換後 DataFrame

### `validate_against_schema()`

```python
metadater.validate_against_schema(data, schema)
```

根據架構需求驗證 DataFrame 並回傳驗證結果。

**參數**

- `data` (pd.DataFrame)：要驗證的 DataFrame
- `schema` (SchemaMetadata)：驗證依據的架構

**回傳值**

- `dict`：包含違規和警告的驗證結果

### `create_schema_config()`

```python
metadater.create_schema_config(column_types=None, cast_errors=None, descriptions=None)
```

建立架構詮釋資料產生的設定字典。

**參數**

- `column_types` (dict[str, str], 可選)：欄位名稱到型態的對應
- `cast_errors` (dict[str, str], 可選)：各欄位的錯誤處理策略
- `descriptions` (dict[str, str], 可選)：欄位描述

**回傳值**

- `dict`：架構操作的設定字典

### `get_metadata_to_dataframe()`

```python
metadater.get_metadata_to_dataframe(metadata)
```

將 Metadata 物件轉換為 DataFrame 以進行分析和視覺化。

**參數**

- `metadata` (Metadata)：要轉換的詮釋資料物件

**回傳值**

- `pd.DataFrame`：詮釋資料的表格表示

### `get_schema_to_dataframe()`

```python
metadater.get_schema_to_dataframe(schema)
```

將 SchemaMetadata 轉換為 DataFrame 格式。

**參數**

- `schema` (SchemaMetadata)：要轉換的架構詮釋資料

**回傳值**

- `pd.DataFrame`：表格格式的架構資訊

### `get_fields_to_dataframe()`

```python
metadater.get_fields_to_dataframe(schema)
```

從架構中提取欄位資訊作為包含詳細統計資料的 DataFrame。

**參數**

- `schema` (SchemaMetadata)：包含欄位詮釋資料的架構

**回傳值**

- `pd.DataFrame`：包含統計資料和屬性的完整欄位分析

## 屬性

- `field_ops`：用於欄位層級操作的 FieldOperations 實例
- `schema_ops`：用於架構層級操作的 SchemaOperations 實例
- `metadata_ops`：用於詮釋資料層級操作的 MetadataOperations 實例
- `CONFIG_KEYS`：支援的設定鍵值清單 ['column_types', 'cast_errors', 'descriptions']

## 進階處理功能

Metadater 透過函數式 API 和管線式工作流程提供進階欄位處理能力：

### FieldPipeline

`FieldPipeline` 能夠在可設定的管線中串接多個欄位處理步驟：

```python
from petsard.metadater import FieldPipeline, analyze_field

# 建立處理管線
pipeline = (FieldPipeline()
    .with_stats(enabled=True)                    # 計算欄位統計資料
    .with_logical_type_inference(enabled=True)   # 推斷邏輯型態（電子郵件、電話等）
    .with_dtype_optimization(enabled=True))      # 最佳化 pandas 資料型態

# 建立初始詮釋資料
initial_metadata = analyze_field(data, "field_name", compute_stats=False)

# 透過管線處理
final_metadata = pipeline.process(data, initial_metadata)
```

### 函數式欄位分析

```python
from petsard.metadater import (
    analyze_field, 
    analyze_dataframe_fields,
    create_field_analyzer,
    compose
)

# 直接欄位分析
field_metadata = analyze_field(
    field_data=series,
    field_name="column_name",
    compute_stats=True,
    infer_logical_type=True
)

# 具有特定設定的自訂分析器
fast_analyzer = create_field_analyzer(
    compute_stats=False,
    sample_size=100
)

# 分析整個 DataFrame
field_metadata_dict = analyze_dataframe_fields(
    data=df, 
    field_configs=field_configs
)