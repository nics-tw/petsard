# Metadater Module Functional Design

## 🎯 模組職責

Metadater 模組是 PETsARD 系統的核心基礎模組，負責元資料管理、資料型別推斷、統計計算、外部模組載入等基礎功能，為其他模組提供統一的資料處理和工具函數介面。

## 📁 重構後的模組結構 (2025/6/19)

```
petsard/metadater/
├── __init__.py                    # 簡化的公開 API (9 個介面)
├── metadater.py                   # 統一的 Metadater 主類別
├── utils.py                       # 工具函數
├── metadata/                      # Metadata 層 (多表格)
│   ├── __init__.py
│   ├── metadata_types.py          # Metadata, MetadataConfig
│   ├── metadata_ops.py            # MetadataOperations
│   └── metadata.py                # 舊版相容
├── schema/                        # Schema 層 (單表格)
│   ├── __init__.py
│   ├── schema_types.py            # SchemaMetadata, SchemaConfig
│   ├── schema_ops.py              # SchemaOperations
│   ├── schema_functions.py        # create_schema_from_dataframe
│   └── validation.py              # 驗證函數
├── field/                         # Field 層 (單欄位)
│   ├── __init__.py
│   ├── field_types.py             # FieldMetadata, FieldConfig
│   ├── field_ops.py               # FieldOperations
│   ├── field_functions.py         # build_field_metadata
│   ├── type_inference.py          # 型別推斷
│   └── transformation.py          # 資料轉換
└── types/                         # 共用型別定義
    ├── __init__.py
    └── data_types.py              # DataType, LogicalType, safe_round
```

## 🔧 核心設計原則

1. **函數式設計**: 採用函數式程式設計範式，提供純函數介面
2. **統一介面**: 為整個 PETsARD 系統提供統一的基礎功能介面
3. **型別安全**: 強化資料型別推斷和驗證機制
4. **效能優化**: 高效的統計計算和資料處理

## 📋 重構後的公開 API

### 統一的 Metadater 類別
```python
class Metadater:
    # Metadata 層 (多表格資料集)
    @classmethod
    def create_metadata(metadata_id: str, config: MetadataConfig = None) -> Metadata
    @classmethod
    def analyze_dataset(tables: Dict[str, pd.DataFrame], metadata_id: str, config: MetadataConfig = None) -> Metadata
    
    # Schema 層 (單表格結構) - 最常用
    @classmethod
    def create_schema(dataframe: pd.DataFrame, schema_id: str, config: SchemaConfig = None) -> SchemaMetadata
    @classmethod
    def analyze_dataframe(dataframe: pd.DataFrame, schema_id: str, config: SchemaConfig = None) -> SchemaMetadata
    
    # Field 層 (單欄位分析)
    @classmethod
    def create_field(series: pd.Series, field_name: str, config: FieldConfig = None) -> FieldMetadata
    @classmethod
    def analyze_series(series: pd.Series, field_name: str, config: FieldConfig = None) -> FieldMetadata
```

### 簡化的公開介面 (在 __init__.py 中匯出)
```python
# 主要介面 (1 個)
Metadater

# 核心類型 (6 個)
Metadata, MetadataConfig          # 多表格層級
SchemaMetadata, SchemaConfig      # 單表格層級
FieldMetadata, FieldConfig        # 單欄位層級

# 工具函數 (2 個)
load_external_module             # 動態載入外部模組
safe_round                       # 安全四捨五入
```

**改善效果**: 從 23 個介面減少到 9 個 (-61%)，符合認知負荷 7±2 原則

### 結構描述格式
```python
{
    'columns': {
        'column_name': {
            'dtype': 'int64',
            'logical_type': 'integer',
            'nullable': True,
            'unique': False,
            'statistics': {
                'min': 0,
                'max': 100,
                'mean': 50.5,
                'std': 28.87
            }
        }
    },
    'shape': (1000, 5),
    'memory_usage': 40000,
    'creation_timestamp': '2025-06-19T09:52:00Z'
}
```

## 🔄 與其他模組的互動

### 輸出介面 (被其他模組使用)
- **Loader**: 使用 `create_schema_from_dataframe` 和 `safe_round`
- **Reporter**: 使用 `safe_round` 和 `load_external_module`
- **Synthesizer**: 使用 `load_external_module`
- **Processor**: 使用統計和驗證函數
- **Evaluator**: 使用統計計算和型別推斷
- **Constrainer**: 使用資料驗證和型別檢查

### 輸入依賴
- **標準函式庫**: pandas, numpy, importlib 等
- **無其他 PETsARD 模組依賴**: 作為基礎模組，不依賴其他 PETsARD 模組

## 🎯 設計模式

### 1. Utility Pattern
- **用途**: 提供靜態工具函數
- **實現**: 靜態方法和獨立函數

### 2. Factory Pattern
- **用途**: 動態建立外部模組實例
- **實現**: `load_external_module` 函數

### 3. Strategy Pattern
- **用途**: 支援不同的型別推斷策略
- **實現**: 可配置的型別推斷邏輯

### 4. Singleton Pattern
- **用途**: 確保配置和快取的一致性
- **實現**: 模組層級的快取機制

## 📊 功能特性

### 1. 元資料管理
- **結構描述生成**: 從 DataFrame 自動生成完整的結構描述
- **型別推斷**: 智慧型資料型別推斷和邏輯型別對應
- **統計摘要**: 自動計算描述性統計資訊
- **記憶體分析**: 分析資料記憶體使用情況

### 2. 資料型別系統
- **物理型別**: pandas 原生資料型別 (int64, float64, object 等)
- **邏輯型別**: 業務邏輯型別 (integer, decimal, categorical, datetime 等)
- **型別轉換**: 安全的型別轉換和驗證
- **型別相容性**: 檢查型別相容性和轉換可行性

### 3. 統計計算
- **描述性統計**: 均值、中位數、標準差、分位數等
- **分佈分析**: 分佈形狀、偏度、峰度分析
- **缺失值分析**: 缺失值模式和統計
- **唯一值分析**: 唯一值計數和比例

### 4. 資料驗證
- **結構驗證**: 檢查資料結構是否符合結構描述
- **型別驗證**: 驗證資料型別正確性
- **範圍驗證**: 檢查數值範圍合理性
- **品質評估**: 整體資料品質評分

### 5. 外部模組管理
- **動態載入**: 安全地載入外部 Python 模組
- **類別實例化**: 動態建立外部類別實例
- **錯誤處理**: 完善的載入錯誤處理機制
- **相容性檢查**: 檢查外部模組相容性

## 🔒 封裝原則

### 對外介面
- **簡潔 API**: 僅匯出必要的公開函數
- **一致命名**: 統一的函數命名規範
- **型別提示**: 完整的型別註解

### 內部實現
- **模組化**: 功能按類別分離到不同檔案
- **快取機制**: 內部快取提高效能
- **錯誤處理**: 統一的錯誤處理策略

## 🚀 重構後的使用範例

```python
from petsard.metadater import Metadater, safe_round, load_external_module

# === 最常用：Schema 層 (單表格分析) ===
# 建立資料結構描述
schema = Metadater.create_schema(df, "my_schema")
print(f"結構描述 ID: {schema.schema_id}")
print(f"欄位數量: {len(schema.fields)}")

# 分析 DataFrame (語意更清楚的別名)
schema = Metadater.analyze_dataframe(df, "customer_data")
for field in schema.fields:
    print(f"{field.name}: {field.data_type} ({field.logical_type})")

# === Field 層 (單欄位分析) ===
# 分析單一欄位
field = Metadater.create_field(df['age'], "age")
print(f"欄位統計: {field.stats}")

# 分析 Series (語意更清楚的別名)
field = Metadater.analyze_series(df['email'], "email")
print(f"邏輯型別: {field.logical_type}")

# === Metadata 層 (多表格資料集) ===
tables = {
    "customers": customer_df,
    "orders": order_df,
    "products": product_df
}
metadata = Metadater.analyze_dataset(tables, "ecommerce_dataset")
print(f"資料集包含 {len(metadata.schemas)} 個表格")

# === 工具函數 ===
# 安全四捨五入
rounded_value = safe_round(3.14159, 2)  # 3.14
rounded_value = safe_round(None, 2)     # None (安全處理)

# 動態載入外部模組
try:
    CustomClass = load_external_module('my_package.custom_module', 'CustomClass')
    instance = CustomClass(param1='value1')
except Exception as e:
    print(f"載入失敗: {e}")
```

### 向後相容性
```python
# 舊的方法仍然可用，但建議使用新方法
schema = Metadater.create_schema_from_dataframe(df, "my_schema")  # 舊方法
schema = Metadater.create_schema(df, "my_schema")                 # 新方法 (推薦)
```

## 📊 型別推斷邏輯

### 1. 數值型別
```python
# 整數型別推斷
if series.dtype in ['int8', 'int16', 'int32', 'int64']:
    logical_type = 'integer'
elif series.dtype in ['uint8', 'uint16', 'uint32', 'uint64']:
    logical_type = 'positive_integer'

# 浮點型別推斷
elif series.dtype in ['float16', 'float32', 'float64']:
    if series.apply(lambda x: x == int(x) if pd.notna(x) else True).all():
        logical_type = 'integer'  # 實際上是整數
    else:
        logical_type = 'decimal'
```

### 2. 文字型別
```python
# 類別型別推斷
if series.dtype == 'object':
    unique_ratio = series.nunique() / len(series)
    if unique_ratio < 0.1:  # 低唯一值比例
        logical_type = 'categorical'
    elif series.str.match(r'^\d{4}-\d{2}-\d{2}$').any():
        logical_type = 'date'
    elif series.str.match(r'^[\w\.-]+@[\w\.-]+\.\w+$').any():
        logical_type = 'email'
    else:
        logical_type = 'text'
```

### 3. 時間型別
```python
# 時間型別推斷
if series.dtype == 'datetime64[ns]':
    logical_type = 'datetime'
elif series.dtype == 'timedelta64[ns]':
    logical_type = 'duration'
```

## 🔧 統計計算函數

### 1. 數值統計
```python
def calculate_numerical_stats(series: pd.Series) -> dict:
    return {
        'count': series.count(),
        'mean': series.mean(),
        'std': series.std(),
        'min': series.min(),
        'max': series.max(),
        'median': series.median(),
        'q25': series.quantile(0.25),
        'q75': series.quantile(0.75),
        'skewness': series.skew(),
        'kurtosis': series.kurtosis()
    }
```

### 2. 類別統計
```python
def calculate_categorical_stats(series: pd.Series) -> dict:
    value_counts = series.value_counts()
    return {
        'count': series.count(),
        'unique': series.nunique(),
        'top': value_counts.index[0] if len(value_counts) > 0 else None,
        'freq': value_counts.iloc[0] if len(value_counts) > 0 else 0,
        'distribution': value_counts.to_dict()
    }
```

## 🔍 資料品質評估

### 品質指標
```python
def check_data_quality(df: pd.DataFrame) -> dict:
    return {
        'completeness': 1 - df.isnull().sum().sum() / (df.shape[0] * df.shape[1]),
        'uniqueness': df.nunique().sum() / (df.shape[0] * df.shape[1]),
        'consistency': calculate_consistency_score(df),
        'validity': calculate_validity_score(df),
        'overall_score': calculate_overall_quality_score(df)
    }
```

### 異常檢測
```python
def detect_anomalies(df: pd.DataFrame) -> dict:
    anomalies = {}
    for col in df.select_dtypes(include=[np.number]).columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        anomalies[col] = df[(df[col] < lower_bound) | (df[col] > upper_bound)].index.tolist()
    return anomalies
```

## 📈 架構重構 (2025/6/19)

### 主要更新
- **公開 API 標準化**: 在 `__init__.py` 中明確定義公開介面
- **函數遷移**: 從 `petsard.util` 遷移核心函數
  - `safe_round` 函數
  - `load_external_module` 函數
- **向後相容性**: 確保其他模組的無縫遷移
- **效能最佳化**: 改善統計計算和型別推斷效能

### 設計改善
- 採用靜態方法設計提高模組化程度
- 增強錯誤處理和異常管理
- 改善記憶體使用效率
- 加強型別安全和驗證機制

## 🔍 架構問題分析與改善 (2025/6/19)

### 三層架構現狀分析

根據正確的三層架構定義：
- **Metadata**: 多表格層級 (datasets)
- **Schema**: 單表格層級 (dataframe)
- **Field**: 欄位層級 (column)

#### 目前公開 API 暴露問題分析表

| 類別 | 函數/類型 | 層級 | 暴露必要性 | 問題 |
|------|-----------|------|------------|------|
| **主要介面** | `Metadater` | 統一 | ✅ 必要 | 無 |
| **高階 API** | `create_schema_from_dataframe` | Schema | ✅ 必要 | 無 |
| **中階 API** | `analyze_field` | Field | ⚠️ 重疊 | 與 `build_field_metadata` 功能重複 |
| **中階 API** | `analyze_dataframe_fields` | Schema | ⚠️ 混淆 | 返回 Field 字典，層級不清 |
| **低階 API** | `build_field_metadata` | Field | ❌ 內部 | 應隱藏的實作細節 |
| **低階 API** | `calculate_field_stats` | Field | ❌ 內部 | 應隱藏的實作細節 |
| **工具 API** | `compose`, `pipe` | 工具 | ❌ 過技術 | 函數式編程概念，使用者不需要 |
| **管道 API** | `FieldPipeline` | Field | ❌ 複雜 | 增加學習成本 |

#### 三層架構 MECE 合規性檢查表

| 層級 | 類型定義 | 操作函數 | 職責邊界 | MECE 問題 |
|------|----------|----------|----------|-----------|
| **Metadata** | ✅ `Metadata` | ❌ 缺少專用函數 | ✅ 多 Schema 管理 | 缺少操作介面 |
| **Schema** | ✅ `SchemaMetadata` | ✅ `create_schema_from_dataframe` | ✅ 單 DataFrame 管理 | 命名不一致 |
| **Field** | ✅ `FieldMetadata` | ❌ `build` vs `analyze` 混淆 | ✅ 單欄位管理 | 功能重疊 |

#### 命名規範一致性分析表

| 功能 | 目前命名 | 層級 | 問題 | 建議命名 |
|------|----------|------|------|----------|
| 建立欄位元資料 | `build_field_metadata` | Field | `build` vs `create` 不一致 | `create_field_metadata` |
| 分析欄位 | `analyze_field` | Field | 與 `build_field_metadata` 100% 重疊 | 移除，統一使用 `create_field_metadata` |
| 建立結構描述 | `create_schema_from_dataframe` | Schema | ✅ 命名正確 | 保持 |
| 分析多欄位 | `analyze_dataframe_fields` | Schema? | 返回 Field 字典，層級混淆 | `create_schema_fields` |

#### 功能重疊度分析表

| 功能組 | 函數 1 | 函數 2 | 重疊度 | 建議處理 |
|--------|--------|--------|--------|----------|
| 欄位分析 | `analyze_field` | `build_field_metadata` | 100% | 保留 `build_field_metadata`，移除 `analyze_field` |
| 欄位分析器 | `create_field_analyzer` | 直接呼叫 `build_field_metadata` | 90% | 移除包裝函數 |
| 統計計算 | `create_stats_calculator` | `calculate_field_stats` | 100% | 移除工廠函數 |

### 建議的新架構設計

#### 簡化後的公開 API 對比表

| 項目 | 目前 | 建議 | 改善 |
|------|------|------|------|
| 公開函數數量 | 23 個 | 9 個 | -61% |
| 認知負荷 | 高 (超過 7±2 原則) | 中 (符合認知負荷) | ✅ |
| 學習曲線 | 陡峭 | 平緩 | ✅ |
| 抽象層次 | 混亂 (高低階混合) | 清晰 (統一高階) | ✅ |

#### 建議的資料夾結構對比表

| 層級 | 目前結構 | 建議結構 | 改善 |
|------|----------|----------|------|
| **組織方式** | 技術分類 (`core/`, `types/`) | 業務分類 (`metadata/`, `schema/`, `field/`) | ✅ 符合三層架構 |
| **Metadata** | 散佈在 `types/metadata_types.py` | 集中在 `metadata/` 資料夾 | ✅ 職責集中 |
| **Schema** | 散佈在 `types/schema_types.py` | 集中在 `schema/` 資料夾 | ✅ 職責集中 |
| **Field** | 散佈在 `core/field_functions.py` | 集中在 `field/` 資料夾 | ✅ 職責集中 |

#### 統一命名規範對比表

| 動詞 | 目前使用 | 建議用途 | 範例 |
|------|----------|----------|------|
| **create** | 部分使用 | 建立新物件 | `create_metadata`, `create_schema`, `create_field` |
| **build** | 與 create 混用 | 組裝複雜結構 | `build_pipeline`, `build_config` |
| **analyze** | 與 build 重疊 | 分析和推斷 | `analyze_dataset`, `analyze_dataframe`, `analyze_series` |
| **validate** | 少量使用 | 驗證和檢查 | `validate_metadata`, `validate_schema` |
| **optimize** | 正確使用 | 優化和改善 | `optimize_dtypes`, `optimize_memory` |

### 詳細分析報告

完整的架構分析和改善建議請參考：[`ARCHITECTURE_ANALYSIS.md`](./ARCHITECTURE_ANALYSIS.md)

該文件包含：
- 詳細的 MECE 合規性檢查表格
- 建議的新三層架構設計
- 統一的命名規範
- 簡化的公開 API 設計
- 分階段遷移策略
- 具體的行動項目檢查清單

### 關鍵改善建議

1. **重新組織資料夾結構**
   ```
   metadater/
   ├── metadata/    # 多表格層級
   ├── schema/      # 單表格層級
   ├── field/       # 單欄位層級
   └── utils.py
   ```

2. **統一 Metadater 類別介面**
   - Metadata 層: `create_metadata()`, `analyze_dataset()`
   - Schema 層: `create_schema()`, `analyze_dataframe()`
   - Field 層: `create_field()`, `analyze_series()`

3. **大幅簡化公開 API**
   - 從 23 個函數減少到 9 個核心介面
   - 隱藏所有內部實作細節
   - 提供統一的高階抽象

## � 效益

1. **統一基礎**: 為整個系統提供統一的基礎功能
2. **型別安全**: 強化資料型別管理和驗證
3. **效能優化**: 高效的統計計算和資料處理
4. **可維護性**: 集中管理基礎功能便於維護
5. **可擴展性**: 易於添加新的基礎功能和工具

這個設計確保 Metadater 模組作為 PETsARD 系統的核心基礎，提供穩定、高效、統一的基礎服務，支撐整個系統的正常運作。