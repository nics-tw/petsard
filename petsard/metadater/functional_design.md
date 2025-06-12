# Metadater Functional Programming 重構設計

## 🎯 設計原則

1. **Pure Functions**: 所有核心功能都是純函數，無副作用
2. **Immutable Data**: 使用不可變資料結構
3. **Function Composition**: 透過函數組合建立複雜功能
4. **Type Safety**: 強型別檢查和清晰的介面
5. **Separation of Concerns**: 清楚分離資料、操作和配置

## 📁 新的檔案結構

```
petsard/metadater/
├── __init__.py                 # 主要匯出介面
├── types/                      # 型別定義
│   ├── __init__.py
│   ├── data_types.py          # 基礎資料型別
│   ├── field_types.py         # 欄位相關型別
│   ├── schema_types.py        # Schema 相關型別
│   └── metadata_types.py      # Metadata 相關型別
├── core/                       # 核心純函數
│   ├── __init__.py
│   ├── field_functions.py     # 欄位處理純函數
│   ├── schema_functions.py    # Schema 處理純函數
│   ├── type_inference.py      # 型別推斷純函數
│   ├── validation.py          # 驗證純函數
│   └── transformation.py      # 轉換純函數
├── builders/                   # 建構器 (Builder Pattern)
│   ├── __init__.py
│   ├── field_builder.py       # 欄位建構器
│   ├── schema_builder.py      # Schema 建構器
│   └── metadata_builder.py    # Metadata 建構器
├── adapters/                   # 適配器層
│   ├── __init__.py
│   ├── pandas_adapter.py      # Pandas 適配器
│   ├── legacy_adapter.py      # 舊版相容適配器
│   └── export_adapter.py      # 匯出適配器
├── utils/                      # 工具函數
│   ├── __init__.py
│   ├── functional_utils.py    # 函數式工具
│   ├── type_utils.py          # 型別工具
│   └── validation_utils.py    # 驗證工具
└── api.py                      # 高階 API 介面
```

## 🔧 核心設計概念

### 1. 型別系統 (types/)
- 使用 dataclass 和 TypedDict 定義不可變資料結構
- 清楚的型別階層和介面定義
- 支援泛型和聯合型別

### 2. 純函數核心 (core/)
- 所有業務邏輯都是純函數
- 輸入 -> 處理 -> 輸出，無副作用
- 易於測試和組合

### 3. 建構器模式 (builders/)
- 使用 Builder Pattern 建立複雜物件
- 支援鏈式呼叫和流暢介面
- 內部使用純函數組合

### 4. 適配器層 (adapters/)
- 處理外部系統整合
- 資料格式轉換
- 向後相容性支援

### 5. 高階 API (api.py)
- 提供簡潔的使用者介面
- 組合底層功能
- 隱藏複雜性

## 🚀 使用範例

```python
# 函數式風格的使用方式
from petsard.metadater import (
    build_field_metadata,
    build_schema_metadata,
    infer_field_type,
    validate_schema,
    transform_data
)

# 1. 純函數方式
field_meta = build_field_metadata(
    data=series,
    config=field_config,
    type_inference=infer_field_type,
    validators=[validate_nullable, validate_range]
)

# 2. 函數組合方式
pipeline = compose(
    partial(transform_data, schema=schema),
    partial(validate_schema, strict=True),
    partial(build_schema_metadata, config=config)
)
result = pipeline(dataframe)

# 3. Builder 方式
schema = (SchemaBuilder()
    .with_id("user_data")
    .add_field("name", StringField().nullable(False))
    .add_field("age", IntField().range(0, 150))
    .with_validation(strict=True)
    .build())
```

## 📊 效益

1. **可測試性**: 純函數易於單元測試
2. **可組合性**: 函數可以靈活組合
3. **可維護性**: 清楚的職責分離
4. **效能**: 不可變資料結構支援快取和最佳化
5. **型別安全**: 編譯時期錯誤檢查
6. **並行處理**: 純函數天然支援並行處理

## 🔄 遷移策略

1. **階段一**: 建立新的型別系統和核心函數
2. **階段二**: 實作建構器和適配器
3. **階段三**: 建立高階 API 和向後相容層
4. **階段四**: 逐步遷移現有程式碼
5. **階段五**: 移除舊的實作和清理

這個設計將讓 metadater 更加模組化、可測試和易於維護，同時保持向後相容性。