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

進階詮釋資料管理系統，提供全面的欄位分析、架構操作和詮釋資料轉換功能。系統採用三層階層架構：**Metadata**（多表格資料集）→ **Schema**（單表格結構）→ **Field**（包含統計資料和型態資訊的欄位層級詮釋資料）。支援函數式程式設計模式和管線式處理，適用於複雜的資料工作流程。

## 設計概述

Metadater 採用四層架構設計，結合函數式程式設計原則，提供清晰、可組合且易於使用的詮釋資料管理介面。我們將複雜的 23 個公開介面簡化為 8 個核心介面，大幅降低使用複雜度。

**四層架構**：`Metadata → Schema → Field → Types`

### 三層架構設計

#### 📊 Metadata 層 (多表格資料集)
```
職責：管理多個表格組成的資料集
使用場景：關聯式資料庫、多表格分析
主要類型：Metadata, MetadataConfig
```

#### 📋 Schema 層 (單表格結構) - 最常用
```
職責：管理單一 DataFrame 的結構描述  
使用場景：單表格分析、資料預處理
主要類型：SchemaMetadata, SchemaConfig
```

#### 🔍 Field 層 (單欄位分析)
```
職責：管理單一欄位的詳細分析
使用場景：欄位級別的深度分析  
主要類型：FieldMetadata, FieldConfig
```

## 核心設計原則

### 1. 不可變資料結構
- 所有資料型別都使用 `@dataclass(frozen=True)`
- 更新操作返回新的物件實例
- 支援函數式的資料轉換

```python
# 舊方式 (可變)
field_metadata.stats = new_stats

# 新方式 (不可變)
field_metadata = field_metadata.with_stats(new_stats)
```

### 2. 純函數
- 所有核心業務邏輯都是純函數
- 相同輸入總是產生相同輸出
- 無副作用，易於測試和推理

### 3. 統一命名規範
| 動詞 | 用途 | 範例 |
|------|------|------|
| **create** | 建立新物件 | `create_metadata`, `create_schema`, `create_field` |
| **analyze** | 分析和推斷 | `analyze_dataset`, `analyze_dataframe`, `analyze_series` |
| **validate** | 驗證和檢查 | `validate_metadata`, `validate_schema`, `validate_field` |

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
    compute_stats=True,
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


## 函數式程式設計功能

### 函數組合
```python
from petsard.metadater import compose, pipe

# 定義處理步驟
def step1(data): return process_data_1(data)
def step2(data): return process_data_2(data)
def step3(data): return process_data_3(data)

# 組合函數
process_pipeline = compose(step3, step2, step1)
result = process_pipeline(input_data)

# 或使用管道風格
result = pipe(input_data, step1, step2, step3)
```

### 管道處理
```python
from petsard.metadater import FieldPipeline

# 建立處理管道
pipeline = (FieldPipeline()
           .with_stats(enabled=True)
           .with_logical_type_inference(enabled=True)
           .with_dtype_optimization(enabled=True))

# 處理欄位
result = pipeline.process(field_data, initial_metadata)
```

## 設計效益

### 1. API 複雜度大幅降低
| 指標 | 重構前 | 重構後 | 改善 |
|------|--------|--------|------|
| 公開介面數量 | 23 個 | 8 個 | -65% |
| 認知負荷 | 高 (超過 7±2) | 中 (符合原則) | ✅ |
| 學習曲線 | 陡峭 | 平緩 | ✅ |

### 2. 架構清晰度提升
| 層級 | 重構前 | 重構後 | 改善 |
|------|--------|--------|------|
| **Metadata** | 職責不明確 | 多表格管理 | ✅ 職責清晰 |
| **Schema** | 與 Field 混淆 | 單表格管理 | ✅ 邊界明確 |
| **Field** | 功能重疊 | 單欄位管理 | ✅ 功能專一 |

### 3. 函數式程式設計效益
- **可測試性**: 純函數易於單元測試，不需要複雜的 mock 設定
- **可組合性**: 小的函數可以組合成複雜功能，靈活的配置和客製化
- **可維護性**: 清楚的職責分離，不可變資料結構避免意外修改
- **效能**: 不可變資料結構支援快取，純函數支援記憶化
- **型別安全**: 強型別檢查，編譯時期錯誤檢查

## 向後相容性

```python
# 使用新的統一 API
schema = Metadater.create_schema(df, "my_schema")
field = Metadater.create_field(series, "field_name")
```

## `__init__.py` 中的可用工具

Metadater 模組提供了一套完整的工具，分為不同類別：

### 核心介面 (8 個介面)

- **`Metadater`**：提供統一詮釋資料操作的主要類別
- **`Metadata`**, **`SchemaMetadata`**, **`FieldMetadata`**：核心類型
- **`MetadataConfig`**, **`SchemaConfig`**, **`FieldConfig`**：設定類型
- **`safe_round`**：工具函數

### 函數式 API 工具

- **`analyze_field()`**：分析個別欄位資料，產生完整的詮釋資料
- **`analyze_dataframe_fields()`**：分析 DataFrame 中的所有欄位，可選擇性提供欄位設定
- **`create_field_analyzer()`**：使用部分應用建立具有特定設定的自訂欄位分析器
- **`compose()`**：函數組合工具，用於建立複雜的處理管線
- **`pipe()`**：管線工具，用於串接操作
- **`FieldPipeline`**：可設定的欄位處理管線，支援方法串接

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