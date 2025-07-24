# Reporter Module Functional Design

## 🎯 模組職責

Reporter 模組負責實驗結果的匯出和報告生成，支援多種粒度的評估報告和資料匯出功能。

## 📁 模組結構

```
petsard/reporter/
├── __init__.py           # 模組匯出介面
├── reporter.py          # 主要報告器和相關類別
└── utils.py             # 工具函數
```

## 🔧 核心設計原則

1. **統一介面**: 透過 Reporter 類別提供統一的報告生成介面
2. **多粒度支援**: 支援 global, columnwise, pairwise 三種報告粒度
3. **Metadater 整合**: 使用 Metadater 的公開介面進行資料處理
4. **實驗追蹤**: 支援複雜的實驗命名和結果比較

## 📋 公開 API

### Reporter 類別
```python
class Reporter:
    def __init__(self, method: str, **kwargs)
    def create(self, data: dict) -> None
    def report(self) -> None
```

### ReporterSaveData 類別
```python
class ReporterSaveData(BaseReporter):
    def __init__(self, config: dict)
    def create(self, data: dict) -> None
    def report(self) -> None
```

### ReporterSaveReport 類別
```python
class ReporterSaveReport(BaseReporter):
    def __init__(self, config: dict)
    def create(self, data: dict) -> None
    def report(self) -> None
```

### ReporterSaveTiming 類別
```python
class ReporterSaveTiming(BaseReporter):
    def __init__(self, config: dict)
    def create(self, data: dict) -> None
    def report(self) -> None
```

### 工具函數
```python
def convert_full_expt_tuple_to_name(expt_tuple: tuple) -> str
def convert_full_expt_name_to_tuple(expt_name: str) -> tuple
def convert_eval_expt_name_to_tuple(expt_name: str) -> tuple
def full_expt_tuple_filter(full_expt_tuple: tuple, method: str, target: Union[str, List[str]]) -> tuple
```

## 🔄 與其他模組的互動

### 輸入依賴
- **Evaluator**: 接收評估結果 (global, columnwise, pairwise)
- **Synthesizer**: 接收合成資料
- **Processor**: 接收處理後的資料

### 輸出介面
- **檔案系統**: 生成 CSV 報告檔案
- **使用者**: 提供結構化的實驗結果

### 內部依賴
- **Metadater**: 使用公開介面進行資料處理
  - `safe_round` 函數
- **Utils**: 使用核心工具函數 (如需要)
  - `petsard.utils.load_external_module` (如有外部模組載入需求)

## 🎯 設計模式

### 1. Strategy Pattern
- **用途**: 支援不同的報告生成策略
- **實現**: ReporterSaveData 和 ReporterSaveReport 兩種策略

### 2. Template Method Pattern
- **用途**: 定義報告生成的通用流程
- **實現**: BaseReporter 定義抽象流程，子類實現具體邏輯

### 3. Factory Pattern
- **用途**: 根據 method 參數建立對應的報告器
- **實現**: Reporter 類別根據配置建立具體的報告器

## 📊 功能特性

### 1. 資料匯出 (save_data)
- 支援多種資料來源過濾
- 自動檔案命名
- CSV 格式匯出
- 空值處理

### 2. 評估報告 (save_report)
- 三種粒度支援：
  - **Global**: 整體評估結果
  - **Columnwise**: 逐欄位評估結果
  - **Pairwise**: 欄位間相關性評估
- 實驗結果合併
- 多評估器結果整合

### 3. 時間報告 (save_timing)
- 統一計時系統整合
- 時間精度轉換：
  - **seconds**: 秒（預設）
  - **minutes**: 分鐘
  - **hours**: 小時
  - **days**: 天
- 模組過濾支援
- DataFrame 格式輸出
- 自動時間單位標記

### 4. 實驗命名系統
- 結構化實驗命名規範
- 模組-實驗名稱對應
- 評估粒度標記
- 實驗結果追蹤

### 4. 資料合併邏輯
- 智慧型 DataFrame 合併
- 共同欄位識別 (包含 'column', 'column1', 'column2')
- 資料型別一致性檢查
- 衝突解決機制

## 🔒 封裝原則

### 對外介面
- 簡潔的 Reporter 類別介面
- 統一的配置參數格式
- 清楚的錯誤訊息

### 內部實現
- 隱藏複雜的資料合併邏輯
- 封裝實驗命名規則
- 統一的檔案操作

## 🚀 使用範例

```python
# 資料匯出
reporter = Reporter('save_data', source='Synthesizer')
reporter.create({('Synthesizer', 'exp1'): synthetic_df})
reporter.report()  # 生成: petsard_Synthesizer[exp1].csv

# 評估報告
reporter = Reporter('save_report', granularity='global')
reporter.create({('Evaluator', 'eval1_[global]'): results})
reporter.report()  # 生成: petsard[Report]_[global].csv

# 多實驗比較
reporter = Reporter('save_report', granularity='columnwise', eval=['eval1', 'eval2'])
reporter.create({
    ('Evaluator', 'eval1_[columnwise]'): results1,
    ('Evaluator', 'eval2_[columnwise]'): results2
})
reporter.report()  # 生成: petsard[Report]_eval1-eval2_[columnwise].csv

# 時間報告
reporter = Reporter('save_timing', time_unit='minutes')
reporter.create({'timing_data': timing_df})
reporter.report()  # 生成: petsard_timing.csv

# 時間報告 - 模組過濾
reporter = Reporter('save_timing', module='Loader', time_unit='seconds')
reporter.create({'timing_data': timing_df})
reporter.report()  # 生成: petsard_timing.csv (只包含 Loader 模組)
```

## 📈 架構特點

### 技術特點
- 使用 `petsard.metadater.safe_round` 進行數值處理
- 使用 `petsard.utils.load_external_module` 載入外部模組 (如需要)
- 內部使用 Metadater 同時保持向後相容
- 完善的 columnwise 和 pairwise 資料合併邏輯
- 模組化的外部模組載入功能

### 設計特點
- 增強的共同欄位識別邏輯
- 完善的資料型別一致性處理
- 優化的合併順序和結果格式
- 完善的錯誤處理和驗證

## 📈 模組效益

1. **統一報告**: 標準化的實驗結果格式
2. **多粒度分析**: 支援不同層級的評估檢視
3. **實驗追蹤**: 完整的實驗歷程記錄
4. **自動化**: 減少手動報告生成工作
5. **可擴展**: 易於添加新的報告格式和功能

這個設計確保 Reporter 模組提供清晰的公開介面，透過 Metadater 的公開 API 進行資料處理，為 PETsARD 系統提供完整的實驗結果報告功能。