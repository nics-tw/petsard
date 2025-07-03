# Metadater 模組功能設計

## 🎯 設計概述

Metadater 模組是 PETsARD 系統的核心基礎模組，採用三層架構設計，結合函數式程式設計原則，提供清晰、可組合且易於使用的元資料管理介面。我們將複雜的 23 個公開介面簡化為 9 個核心介面，大幅降低使用複雜度。

## 🏗️ 三層架構設計

### 📊 Metadata 層 (多表格資料集)
```
職責：管理多個表格組成的資料集
使用場景：關聯式資料庫、多表格分析
主要類型：Metadata, MetadataConfig
```

### 📋 Schema 層 (單表格結構) - 最常用
```
職責：管理單一 DataFrame 的結構描述
使用場景：單表格分析、資料預處理
主要類型：SchemaMetadata, SchemaConfig
```

### 🔍 Field 層 (單欄位分析)
```
職責：管理單一欄位的詳細分析
使用場景：欄位級別的深度分析
主要類型：FieldMetadata, FieldConfig
```

## 📁 模組結構

```
petsard/metadater/
├── __init__.py                    # 簡化的公開 API (9 個介面)
├── metadater.py                   # 統一的 Metadater 主類別
├── api.py                         # API 介面定義
├── datatype.py                    # 資料型別定義
├── utils.py                       # 工具函數
├── adapters/                      # 外部適配器
│   ├── __init__.py
│   └── sdv_adapter.py             # SDV 適配器
├── metadata/                      # Metadata 層 (多表格)
│   ├── __init__.py
│   ├── metadata_types.py          # Metadata, MetadataConfig
│   ├── metadata_ops.py            # MetadataOperations
│   └── metadata.py                # 核心實作
├── schema/                        # Schema 層 (單表格)
│   ├── __init__.py
│   ├── schema_types.py            # SchemaMetadata, SchemaConfig
│   ├── schema_ops.py              # SchemaOperations
│   ├── schema_functions.py        # create_schema_from_dataframe
│   ├── schema_meta.py             # Schema 元資料
│   └── validation.py              # 驗證函數
├── field/                         # Field 層 (單欄位)
│   ├── __init__.py
│   ├── field_types.py             # FieldMetadata, FieldConfig
│   ├── field_ops.py               # FieldOperations
│   ├── field_functions.py         # build_field_metadata
│   ├── field_meta.py              # Field 元資料
│   ├── type_inference.py          # 型別推斷
│   └── transformation.py          # 資料轉換
└── types/                         # 共用型別定義
    ├── __init__.py
    └── data_types.py              # DataType, LogicalType, safe_round
```

## 🔧 核心設計原則

### 1. 不可變資料結構 (Immutable Data)
- 所有資料型別都使用 `@dataclass(frozen=True)`
- 更新操作返回新的物件實例
- 支援函數式的資料轉換

```python
# 舊方式 (可變)
field_metadata.stats = new_stats

# 新方式 (不可變)
field_metadata = field_metadata.with_stats(new_stats)
```

### 2. 純函數 (Pure Functions)
- 所有核心業務邏輯都是純函數
- 相同輸入總是產生相同輸出
- 無副作用，易於測試和推理

```python
# 純函數範例
def calculate_field_stats(field_data: pd.Series, field_metadata: FieldMetadata) -> FieldStats:
    """純函數：計算欄位統計資料"""
    # 只依賴輸入參數，無副作用
    return FieldStats(...)
```

### 3. 統一命名規範
| 動詞 | 用途 | 範例 |
|------|------|------|
| **create** | 建立新物件 | `create_metadata`, `create_schema`, `create_field` |
| **analyze** | 分析和推斷 | `analyze_dataset`, `analyze_dataframe`, `analyze_series` |
| **validate** | 驗證和檢查 | `validate_metadata`, `validate_schema`, `validate_field` |

### 4. 三層分離原則
- **Metadata**: 多表格管理，職責清晰
- **Schema**: 單表格管理，邊界明確
- **Field**: 單欄位管理，功能專一

## 📋 公開 API 設計

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

# 工具函數 (1 個)
safe_round                       # 安全四捨五入
```

**改善效果**: 從 23 個介面減少到 8 個 (-65%)，符合認知負荷 7±2 原則

## 🚀 使用方式

### 基本使用 (最常用)
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

### 向後相容性
```python
# 舊的方法仍然可用，但建議使用新方法
schema = Metadater.create_schema_from_dataframe(df, "my_schema")  # 舊方法
schema = Metadater.create_schema(df, "my_schema")                 # 新方法 (推薦)

field = Metadater.build_field_metadata(series, "field_name")     # 舊方法  
field = Metadater.create_field(series, "field_name")             # 新方法 (推薦)
```

## 📊 資料型別系統

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

### 型別推斷邏輯

#### 1. 數值型別
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

#### 2. 文字型別
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

#### 3. 時間型別
```python
# 時間型別推斷
if series.dtype == 'datetime64[ns]':
    logical_type = 'datetime'
elif series.dtype == 'timedelta64[ns]':
    logical_type = 'duration'
```

## 🔧 統計計算功能

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

## 🔄 與其他模組的互動

### 輸出介面 (被其他模組使用)
- **Loader**: 使用 `create_schema_from_dataframe` 和 `safe_round`
- **Reporter**: 使用 `safe_round`
- **Processor**: 使用統計和驗證函數
- **Evaluator**: 使用統計計算和型別推斷
- **Constrainer**: 使用資料驗證和型別檢查

### 注意事項
- **外部模組載入**: `load_external_module` 函數已移至 `petsard.utils` 模組
- **Demo 特定功能**: demo 相關的模組載入由 `demo.utils.load_demo_module` 提供

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

## 📊 設計效益

### 1. API 複雜度大幅降低
| 指標 | 重構前 | 重構後 | 改善 |
|------|--------|--------|------|
| 公開介面數量 | 23 個 | 8 個 | -65% |
| 認知負荷 | 高 (超過 7±2) | 低 (符合原則) | ✅ |
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

## 🎯 重視的設計細節

### 1. MECE 原則遵循
- **Mutually Exclusive**: 三層架構職責不重疊
- **Collectively Exhaustive**: 涵蓋所有元資料管理需求
- 每個層級都有明確的邊界和職責

### 2. 認知負荷管理
- 遵循 7±2 認知負荷原則
- 從 23 個介面簡化為 9 個核心介面
- 統一的命名規範降低學習成本

### 3. 函數式設計模式
- 不可變資料結構確保資料一致性
- 純函數提供可預測的行為
- 函數組合支援靈活的處理流程

### 4. 型別安全
- 強型別檢查避免執行時錯誤
- 清晰的型別定義提升程式碼可讀性
- IDE 友好的自動完成和錯誤檢查

### 5. 效能考量
- 不可變結構支援快取和記憶化
- 純函數支援並行處理
- 管道處理避免中間資料複製

## 📋 遷移指南

### 對於新專案
直接使用新的介面：
```python
from petsard.metadater import Metadater

# 推薦使用
schema = Metadater.create_schema(df, "schema_id")
field = Metadater.create_field(series, "field_name")
```

### 對於現有專案
逐步遷移，舊介面仍可使用：
```python
from petsard.metadater import Metadater

# 現有程式碼仍可運行
schema = Metadater.create_schema_from_dataframe(df, "schema_id")

# 建議逐步改為
schema = Metadater.create_schema(df, "schema_id")
```

## 🧪 測試策略

新的架構更容易測試：

```python
def test_calculate_field_stats():
    # 純函數測試
    data = pd.Series([1, 2, 3])
    metadata = FieldMetadata(name="test", data_type=DataType.INT64)

    stats = calculate_field_stats(data, metadata)

    assert stats.row_count == 3
    assert stats.na_count == 0
```

## 🎉 結論

Metadater 模組的設計重視：
- **清晰的架構分層**: 三層架構確保職責分離
- **簡潔的使用介面**: 9 個核心介面降低學習成本
- **函數式設計原則**: 提升可測試性和可維護性
- **強型別安全**: 避免執行時錯誤
- **向後相容性**: 保護現有投資

這個設計提供了清晰、可組合且易於使用的元資料管理解決方案，同時保持了功能的完整性和擴展性，為整個 PETsARD 系統提供穩定、高效、統一的基礎服務。