---
title: Metadater
type: docs
weight: 53
prev: docs/api/loader
next: docs/api/splitter
---


```python
Metadater()
```

詮釋資料管理系統，提供欄位分析、架構操作和詮釋資料轉換功能。採用三層架構：**Metadata**（多表格資料集）→ **Schema**（單表格結構）→ **Field**（欄位層級詮釋資料）。

## 架構設計

### 📊 Metadata 層 (多表格資料集)
- **職責**：管理多個表格組成的資料集
- **使用場景**：關聯式資料庫、多表格分析
- **主要類型**：`Metadata`, `MetadataConfig`

### 📋 Schema 層 (單表格結構) - 最常用
- **職責**：管理單一 DataFrame 的結構描述
- **使用場景**：單表格分析、資料預處理
- **主要類型**：`SchemaMetadata`, `SchemaConfig`

### 🔍 Field 層 (單欄位分析)
- **職責**：管理單一欄位的詳細分析
- **使用場景**：欄位級別的深度分析
- **主要類型**：`FieldMetadata`, `FieldConfig`

## 參數

無

## 基本使用方式

### 最常用的使用方式
```python
from petsard.metadater import Metadater

# Schema 層：分析單表格 (最常用)
schema = Metadater.create_schema(df, "my_data")
schema = Metadater.analyze_dataframe(df, "my_data")  # 語意更清楚

# Field 層：分析單欄位
field = Metadater.create_field(df['age'], "age")
field = Metadater.analyze_series(df['email'], "email")  # 語意更清楚
```

### 進階使用
```python
# Metadata 層：分析多表格資料集
tables = {"users": user_df, "orders": order_df}
metadata = Metadater.analyze_dataset(tables, "ecommerce")

# 配置化分析
from petsard.metadater import SchemaConfig, FieldConfig

config = SchemaConfig(
    schema_id="my_schema",
    optimize_dtypes=True,
    infer_logical_types=True
)
schema = Metadater.create_schema(df, "my_data", config)
```

## 方法

### `create_schema()`

```python
Metadater.create_schema(dataframe, schema_id, config=None)
```

從 DataFrame 建立架構詮釋資料，自動進行欄位分析。

**參數**

- `dataframe` (pd.DataFrame)：輸入的 DataFrame
- `schema_id` (str)：架構識別碼
- `config` (SchemaConfig, 可選)：架構設定

**回傳值**

- `SchemaMetadata`：包含欄位詮釋資料和關聯性的完整架構

### `analyze_dataframe()`

```python
Metadater.analyze_dataframe(dataframe, schema_id, config=None)
```

分析 DataFrame 結構並產生完整的架構詮釋資料。

**參數**

- `dataframe` (pd.DataFrame)：要分析的輸入 DataFrame
- `schema_id` (str)：架構識別碼
- `config` (SchemaConfig, 可選)：分析設定

**回傳值**

- `SchemaMetadata`：包含欄位詮釋資料的完整架構分析

### `create_field()`

```python
Metadater.create_field(series, field_name, config=None)
```

從 pandas Series 建立詳細的欄位詮釋資料。

**參數**

- `series` (pd.Series)：輸入的資料序列
- `field_name` (str)：欄位名稱
- `config` (FieldConfig, 可選)：欄位特定設定

**回傳值**

- `FieldMetadata`：包含統計資料和型態資訊的完整欄位詮釋資料

### `analyze_series()`

```python
Metadater.analyze_series(series, field_name, config=None)
```

分析序列資料並產生完整的欄位詮釋資料。

**參數**

- `series` (pd.Series)：要分析的輸入資料序列
- `field_name` (str)：欄位名稱
- `config` (FieldConfig, 可選)：分析設定

**回傳值**

- `FieldMetadata`：包含統計資料和型態資訊的詳細欄位分析

### `analyze_dataset()`

```python
Metadater.analyze_dataset(tables, metadata_id, config=None)
```

分析多個表格並產生完整的詮釋資料。

**參數**

- `tables` (dict[str, pd.DataFrame])：表格名稱對應 DataFrame 的字典
- `metadata_id` (str)：詮釋資料識別碼
- `config` (MetadataConfig, 可選)：詮釋資料設定

**回傳值**

- `Metadata`：包含所有架構資訊的完整詮釋資料物件


## 可用工具

### 核心類型
- **`Metadater`**：主要操作類別
- **`Metadata`**, **`SchemaMetadata`**, **`FieldMetadata`**：資料類型
- **`MetadataConfig`**, **`SchemaConfig`**, **`FieldConfig`**：設定類型

## 範例

### 基本欄位分析

```python
from petsard.metadater import Metadater
import pandas as pd

# 建立範例資料
data = pd.Series([1, 2, 3, 4, 5, None, 7, 8, 9, 10], name="numbers")

# 使用新介面分析欄位
field_metadata = Metadater.analyze_series(
    series=data,
    field_name="numbers"
)

print(f"欄位: {field_metadata.name}")
print(f"資料型態: {field_metadata.data_type}")
print(f"可為空值: {field_metadata.nullable}")
if field_metadata.stats:
    print(f"統計資料: {field_metadata.stats.row_count} 列, {field_metadata.stats.na_count} 空值")
```

### 架構分析

```python
from petsard.metadater import Metadater, SchemaConfig
import pandas as pd

# 建立範例 DataFrame
df = pd.DataFrame({
    'id': [1, 2, 3, 4, 5],
    'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
    'email': ['alice@test.com', 'bob@test.com', 'charlie@test.com', 'diana@test.com', 'eve@test.com'],
    'age': [25, 30, 35, 28, 32],
})

# 分析 DataFrame
schema = Metadater.analyze_dataframe(
    dataframe=df,
    schema_id="user_data"
)

print(f"架構: {schema.name}")
print(f"欄位數: {len(schema.fields)}")
for field_name, field_metadata in schema.fields.items():
    print(f"  {field_name}: {field_metadata.data_type.value}")
```

### 多表格分析

```python
from petsard.metadater import Metadater
import pandas as pd

# 建立多個表格
tables = {
    'users': pd.DataFrame({
        'id': [1, 2, 3], 
        'name': ['Alice', 'Bob', 'Charlie']
    }),
    'orders': pd.DataFrame({
        'order_id': [101, 102], 
        'user_id': [1, 2]
    })
}

# 分析資料集
metadata = Metadater.analyze_dataset(
    tables=tables,
    metadata_id="ecommerce"
)

print(f"詮釋資料: {metadata.metadata_id}")
print(f"架構數: {len(metadata.schemas)}")
```

這個重新設計的 Metadater 提供了清晰、可組合且易於使用的詮釋資料管理解決方案，同時保持了功能的完整性和擴展性。