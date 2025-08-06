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

## 邏輯型態系統

Metadater 包含一套自主開發的**邏輯型態推斷系統**，超越基本資料型態，能識別資料中的語意意義。此系統自動檢測模式並驗證資料以指派適當的邏輯型態。

> **重要說明**：此邏輯型態系統是我們的自主開發實作。詳細的實現方法請查閱 Metadater 原始碼和本文件。

### 可用的邏輯型態

我們的系統專注於不與基本資料型態重疊的語意型態，提供清晰的職責分離：

#### 文字語意型態（需要 `string` 資料型態）
- **`email`**：具有格式驗證的電子郵件地址
- **`url`**：具有協定驗證的網址連結
- **`uuid`**：標準格式的 UUID 識別碼
- **`categorical`**：透過基數分析檢測的分類文字資料
- **`ip_address`**：具有模式驗證的 IPv4/IPv6 位址

#### 數值語意型態（需要數值資料型態）
- **`percentage`**：具有 0-100 範圍驗證的百分比數值
- **`currency`**：具有貨幣符號檢測的金額數值
- **`latitude`**：具有 -90 到 90 範圍驗證的緯度座標
- **`longitude`**：具有 -180 到 180 範圍驗證的經度座標

#### 識別碼型態
- **`primary_key`**：具有唯一性驗證的主鍵欄位

### 詳細檢測邏輯

每種邏輯型態使用特定的檢測模式、驗證規則和信心閾值：

#### 電子郵件檢測（`email`）
```
相容資料型態: string
模式: ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
信心閾值: 80% 的非空值必須符合模式
驗證方法: 完整的電子郵件格式正則表達式驗證
說明: 標準電子郵件地址格式驗證
```

#### 網址檢測（`url`）
```
相容資料型態: string
模式: ^https?://[^\s/$.?#].[^\s]*$
信心閾值: 80% 的非空值必須符合模式
驗證方法: 協定和網域結構驗證
說明: 具有 HTTP/HTTPS 協定驗證的網址
```

#### UUID 檢測（`uuid`）
```
相容資料型態: string
模式: ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$
信心閾值: 95% 的非空值必須符合模式
驗證方法: 標準 UUID 格式驗證
說明: 8-4-4-4-12 十六進位格式的 UUID 識別碼
```

#### IP 位址檢測（`ip_address`）
```
相容資料型態: string
模式: IPv4 和 IPv6 位址模式
信心閾值: 90% 的非空值必須符合模式
驗證方法: IPv4/IPv6 模式驗證
說明: 網路 IP 位址（IPv4 和 IPv6）
```

#### 分類檢測（`categorical`）
```
相容資料型態: string
驗證方法: ASPL（適應性統計模式學習）基數分析
邏輯: 使用平均每級樣本數（ASPL）閾值
閾值: 根據資料大小和分佈動態調整
說明: 透過基數分析檢測的分類資料，每個類別有足夠的樣本數
```

#### 百分比檢測（`percentage`）
```
相容資料型態: int8, int16, int32, int64, float32, float64, decimal
範圍驗證: 0 ≤ 數值 ≤ 100
信心閾值: 95% 的數值必須在有效範圍內
驗證方法: 數值範圍驗證與精度檢查
說明: 0-100 範圍內的百分比數值
```

#### 貨幣檢測（`currency`）
```
相容資料型態: float32, float64, decimal
驗證方法: 貨幣符號檢測和正值驗證
信心閾值: 80% 的數值必須符合貨幣模式
說明: 具有貨幣符號檢測的金額數值
```

#### 地理座標
```
緯度（latitude）:
  相容資料型態: float32, float64, decimal
  範圍驗證: -90 ≤ 數值 ≤ 90
  信心閾值: 95% 的數值必須在有效範圍內
  說明: 具有地理範圍驗證的緯度座標

經度（longitude）:
  相容資料型態: float32, float64, decimal
  範圍驗證: -180 ≤ 數值 ≤ 180
  信心閾值: 95% 的數值必須在有效範圍內
  說明: 具有地理範圍驗證的經度座標
```

#### 主鍵檢測（`primary_key`）
```
相容資料型態: int8, int16, int32, int64, string
驗證方法: 唯一性檢查（需要 100% 唯一值）
額外檢查: 非空值約束驗證
信心閾值: 100%（不允許重複）
說明: 具有唯一性保證的資料庫主鍵識別
```

### 型態相容性系統

系統維持基本資料型態和邏輯型態之間的嚴格相容性規則：

#### 相容組合 ✅
- `string` + `email`, `url`, `uuid`, `categorical`, `ip_address`
- `數值型態` + `percentage`, `currency`, `latitude`, `longitude`
- `int/string` + `primary_key`

#### 不相容組合 ❌
- `數值型態` + `email`, `url`, `uuid`, `ip_address`
- `string` + `percentage`, `currency`, `latitude`, `longitude`

### 設定選項

```python
from petsard.metadater import FieldConfig

# 停用邏輯型態推斷
config = FieldConfig(logical_type="never")

# 啟用自動推斷
config = FieldConfig(logical_type="infer")

# 強制指定邏輯型態（具有相容性驗證）
config = FieldConfig(logical_type="email")
```

### 錯誤處理和衝突解決

當 `type` 和 `logical_type` 不相容時，系統遵循以下優先順序：

1. **相容性檢查**：驗證指定的邏輯型態是否與資料型態相容
2. **警告產生**：記錄關於不相容性的詳細警告
3. **自動回退**：回退到基於資料模式的自動推斷
4. **優先級系統**：資料型態約束優先於邏輯型態提示

警告訊息範例：
```
WARNING: Logical type 'email' is not compatible with data type 'int64' for field 'user_id'.
Falling back to automatic inference.
```

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