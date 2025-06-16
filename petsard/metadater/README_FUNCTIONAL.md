# Metadater Functional Programming 重構

## 🎯 概述

這個重構將 PETsARD 的 metadater 模組從物件導向設計轉換為更加 functional programming 的架構，提供更好的可組合性、可測試性和可維護性。

## 📁 新的架構

```
petsard/metadater/
├── types/                      # 不可變型別定義
│   ├── data_types.py          # 基礎資料型別 (DataType, LogicalType)
│   ├── field_types.py         # 欄位型別 (FieldConfig, FieldMetadata, FieldStats)
│   ├── schema_types.py        # Schema 型別 (SchemaConfig, SchemaMetadata)
│   └── metadata_types.py      # Metadata 型別 (Metadata, MetadataConfig)
├── core/                       # 純函數核心
│   ├── field_functions.py     # 欄位處理純函數
│   ├── schema_functions.py    # Schema 處理純函數
│   ├── type_inference.py      # 型別推斷純函數
│   ├── validation.py          # 驗證純函數
│   └── transformation.py      # 轉換純函數
├── api.py                      # 高階函數式 API
├── examples.py                 # 使用範例
└── README_FUNCTIONAL.md        # 說明文件
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

### 3. 函數組合 (Function Composition)
- 支援函數組合和管道操作
- 可以靈活組合小的函數來建立複雜功能

```python
# 函數組合範例
process_field = compose(
    optimize_field_dtype,
    infer_field_logical_type,
    calculate_field_stats
)
```

### 4. 高階函數 (Higher-Order Functions)
- 使用 partial application 建立配置化的函數
- 支援函數作為參數和返回值

```python
# 高階函數範例
fast_analyzer = create_field_analyzer(
    compute_stats=False,
    sample_size=100
)
```

## 🚀 使用方式

### 基本欄位分析

```python
from petsard.metadater import analyze_field
import pandas as pd

# 建立資料
data = pd.Series([1, 2, 3, None, 5], name="numbers")

# 分析欄位
field_metadata = analyze_field(
    field_data=data,
    field_name="numbers",
    compute_stats=True,
    infer_logical_type=True
)

print(f"資料型別: {field_metadata.data_type}")
print(f"統計資料: {field_metadata.stats}")
```

### 自訂分析器

```python
from petsard.metadater import create_field_analyzer

# 建立自訂分析器
fast_analyzer = create_field_analyzer(
    compute_stats=False,  # 跳過統計計算以提升速度
    infer_logical_type=True,
    sample_size=100
)

# 使用自訂分析器
metadata = fast_analyzer(data, "field_name", None)
```

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

### DataFrame 分析

```python
from petsard.metadater import analyze_dataframe_fields, create_schema_from_dataframe

# 分析整個 DataFrame
field_metadata_dict = analyze_dataframe_fields(
    data=df,
    field_configs={"email": FieldConfig(logical_type="email")}
)

# 建立 Schema
schema = create_schema_from_dataframe(
    data=df,
    schema_id="user_data",
    config=SchemaConfig(schema_id="user_data", compute_stats=True)
)
```

## 📊 效益

### 1. 可測試性
- 純函數易於單元測試
- 不需要複雜的 mock 設定
- 測試覆蓋率更高

### 2. 可組合性
- 小的函數可以組合成複雜功能
- 靈活的配置和客製化
- 支援函數式程式設計模式

### 3. 可維護性
- 清楚的職責分離
- 不可變資料結構避免意外修改
- 更容易推理和除錯

### 4. 效能
- 不可變資料結構支援快取
- 純函數支援記憶化
- 更好的並行處理支援

### 5. 型別安全
- 強型別檢查
- 編譯時期錯誤檢查
- 更好的 IDE 支援

## 🔄 遷移指南

### 從舊 API 遷移

```python
# 舊方式
from petsard.metadater import Metadater
metadater = Metadater()
field_metadata = metadater.build_field_from_series(data, "field_name")

# 新方式
from petsard.metadater import analyze_field
field_metadata = analyze_field(data, "field_name")
```

### 向後相容性
- 舊的 API 仍然可用，但標記為 deprecated
- 提供 legacy adapter 進行格式轉換
- 逐步遷移策略

## 🧪 測試

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

## 📚 範例

完整的使用範例請參考 `examples.py` 檔案，包含：
- 基本欄位分析
- 自訂分析器
- 函數組合
- 管道處理
- DataFrame 分析
- 驗證功能

## 🎉 結論

這個 functional programming 重構提供了：
- 更清晰的程式碼結構
- 更好的可測試性和可維護性
- 更靈活的組合和配置能力
- 更強的型別安全性
- 更好的效能潛力

同時保持向後相容性，讓現有程式碼可以逐步遷移到新的架構。