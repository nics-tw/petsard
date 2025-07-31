# Loader Module Functional Design

## 🎯 模組職責

Loader 模組負責統一的資料載入介面，支援多種資料格式和來源，並提供資料分割和基準資料集管理功能。

## 📁 模組結構

```
petsard/loader/
├── __init__.py           # 模組匯出介面
├── loader.py            # 主要載入器
├── metadata.py          # 詮釋資料處理 (整合 Metadater)
├── splitter.py          # 資料分割器
└── benchmarker.py       # 基準資料集管理
```

## 🔧 核心設計原則

1. **統一介面**: 載入操作回傳 `(data, metadata)` 元組，分割操作回傳 `(split_data, metadata_dict, train_indices)` 三元組
2. **函數式設計**: 使用純函數和不可變資料結構，避免副作用
3. **Metadater 整合**: 內部使用 Metadater 進行詮釋資料管理
4. **向後相容**: 保持現有 API 不變
5. **重疊控制**: 支援精確的樣本重疊管理和拔靴法抽樣

## 📋 公開 API

### Loader 類別
```python
class Loader:
    def __init__(self, filepath: str, **kwargs)
    def load(self) -> Tuple[pd.DataFrame, SchemaMetadata]
```

### Metadata 類別
```python
class Metadata:
    def __init__(self)
    def build_metadata(self, data: pd.DataFrame) -> None
    def set_col_infer_dtype(self, col: str, dtype: str) -> None
```

### Splitter 類別
```python
class Splitter:
    def __init__(self, num_samples: int, train_split_ratio: float,
                 max_overlap_ratio: float = 1.0, max_attempts: int = 30, **kwargs)
    def split(self, data: pd.DataFrame = None,
              exist_train_indices: list[set] = None) -> Tuple[Dict, Dict, List[Set]]
```

### Benchmarker 類別
```python
class BaseBenchmarker:
    def download(self) -> None
    def verify_file(self) -> bool
```

## 🔄 與其他模組的互動

### 輸入依賴
- **檔案系統**: 讀取各種格式的資料檔案
- **網路**: 下載基準資料集

### 輸出介面
- **Processor**: 提供 `(data, metadata)` 給資料前處理
- **Synthesizer**: 提供 `(data, metadata)` 給資料合成
- **Evaluator**: 提供分割後的資料給評估

### 內部依賴
- **Metadater**: 用於詮釋資料生成和管理
  - `Metadater.create_schema_from_dataframe()`
  - `safe_round` 函數

## 🎯 設計模式

### 1. Adapter Pattern
- **用途**: 支援多種檔案格式 (CSV, Excel, JSON)
- **實現**: 不同格式使用不同的載入邏輯

### 2. Factory Pattern
- **用途**: 根據檔案類型建立對應的載入器
- **實現**: 自動檢測檔案副檔名並選擇載入方法

### 3. Strategy Pattern
- **用途**: 支援不同的資料分割策略
- **實現**: 可配置的分割方法和參數

## 📊 功能特性

### 1. 檔案格式支援
- CSV 檔案載入
- Excel 檔案載入
- 自定義分隔符支援
- 編碼自動檢測

### 2. 詮釋資料管理
- 自動型別推斷
- 統計資訊計算
- 與 Metadater 整合
- 向後相容的 API

### 3. 資料分割
- 訓練/驗證集分割
- 多樣本支援
- 拔靴法（Bootstrap）抽樣
- 重疊控制機制
- 函數式三元組回傳格式
- 詮釋資料更新

### 4. 基準資料集
- 自動下載
- SHA256 驗證
- 快取管理
- 配置檔案支援

## 🔒 封裝原則

### 對外介面
- 只暴露必要的公開方法
- 統一的回傳格式 `(data, metadata)`
- 清楚的錯誤處理

### 內部實現
- 隱藏 Metadater 的複雜性
- 封裝檔案操作細節
- 統一的配置管理

## 🚀 使用範例

```python
# 基本載入
loader = Loader('data.csv')
data, metadata = loader.load()

# 資料分割（函數式 API）
splitter = Splitter(num_samples=5, train_split_ratio=0.8)
split_data, metadata_dict, train_indices = splitter.split(data=data)

# 重疊控制分割
overlap_splitter = Splitter(
    num_samples=3,
    train_split_ratio=0.8,
    max_overlap_ratio=0.2,  # 最大 20% 重疊
    max_attempts=30
)
split_data, metadata_dict, train_indices = overlap_splitter.split(data=data)

# 避免與現有樣本重疊
existing_indices = [set(range(0, 10)), set(range(15, 25))]
new_split_data, new_metadata, new_indices = splitter.split(
    data=data,
    exist_train_indices=existing_indices
)

# 詮釋資料操作
meta = Metadata()
meta.build_metadata(data)
meta.set_col_infer_dtype('column_name', 'categorical')
```

## 📈 效益

1. **統一介面**: 簡化資料載入流程
2. **自動化**: 減少手動配置需求
3. **可擴展**: 易於添加新的檔案格式支援
4. **可靠性**: 內建驗證和錯誤處理
5. **效能**: 最佳化的載入和處理流程

這個設計確保 Loader 模組提供清晰的公開介面，同時內部整合 Metadater 的強大功能，為整個 PETsARD 系統提供穩定的資料載入基礎。