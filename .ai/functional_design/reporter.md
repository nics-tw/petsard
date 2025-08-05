# Reporter Module Functional Design

## 🎯 模組職責

Reporter 模組負責實驗結果的匯出和報告生成，採用函式化設計模式，支援多種粒度的評估報告和資料匯出功能。

## 📁 模組結構

```
petsard/reporter/
├── __init__.py                  # 模組匯出介面
├── base_reporter.py            # 基礎報告器抽象類別
├── reporter.py                 # 主要報告器工廠類別
├── reporter_save_data.py       # 資料匯出報告器
├── reporter_save_report.py     # 評估報告生成器
├── reporter_save_timing.py     # 時間報告生成器
└── utils.py                    # 工具函數
```

## 🔧 核心設計原則

1. **函式化設計**: 採用無狀態的函式化設計模式，避免記憶體累積
2. **多粒度支援**: 支援 global, columnwise, pairwise, details, tree 五種報告粒度
3. **靈活配置**: 支援 `str | list[str]` 的 granularity 配置
4. **Adapter 模式**: ReporterAdapter 適應函式化 Reporter，保持向後相容
5. **Metadater 整合**: 使用 Metadater 的公開介面進行資料處理
6. **實驗追蹤**: 支援複雜的實驗命名和結果比較

## 📋 公開 API

### Reporter 工廠類別
```python
class Reporter:
    def __init__(self, method: str, **kwargs)
    def create(self, data: dict) -> None
    def report(self) -> None
```

### BaseReporter 抽象類別
```python
class BaseReporter(ABC):
    def __init__(self, config: dict)
    
    @abstractmethod
    def report(self, data: dict) -> Any:
        """函式化報告生成方法"""
        pass
```

### 具體報告器類別
```python
class ReporterSaveData(BaseReporter):
    def report(self, data: dict) -> None:
        """函式化資料匯出"""
        pass

class ReporterSaveReport(BaseReporter):
    def report(self, data: dict) -> None:
        """函式化評估報告生成"""
        pass

class ReporterSaveTiming(BaseReporter):
    def report(self, data: dict) -> None:
        """函式化時間報告生成"""
        pass
```

### ReporterAdapter 相容性類別
```python
class ReporterAdapter:
    """適應函式化 Reporter 的相容性介面"""
    def __init__(self, reporter: BaseReporter)
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

### 1. 函式化設計模式
- **無狀態設計**: 完全消除 `self.result` 和 `self._processed_data`
- **記憶體優化**: 採用 "throw out and throw back in" 模式
- **純函數**: 所有 `report()` 方法都是純函數，無副作用
- **向後相容**: 透過 ReporterAdapter 保持現有 API 相容性

### 2. 多粒度支援增強
- **五種粒度類型**：
  - **GLOBAL=1**: 整體評估結果
  - **COLUMNWISE=2**: 逐欄位評估結果
  - **PAIRWISE=3**: 欄位間相關性評估
  - **DETAILS=4**: 詳細評估結果
  - **TREE=5**: 樹狀結構評估結果
- **靈活配置**: 支援 `str | list[str]` 的 granularity 參數
- **多粒度組合**: 可同時生成多種粒度的報告

### 3. 資料匯出 (save_data)
- 支援多種資料來源過濾
- 自動檔案命名
- CSV 格式匯出
- 空值處理
- 函式化資料處理

### 4. 評估報告 (save_report)
- 支援所有五種粒度
- 實驗結果合併
- 多評估器結果整合
- 函式化報告生成

### 5. 時間報告 (save_timing)
- 統一計時系統整合
- 時間精度轉換：
  - **seconds**: 秒（預設）
  - **minutes**: 分鐘
  - **hours**: 小時
  - **days**: 天
- 模組過濾支援
- DataFrame 格式輸出
- 自動時間單位標記

### 6. 實驗命名系統
- 結構化實驗命名規範
- 模組-實驗名稱對應
- 評估粒度標記
- 實驗結果追蹤

### 7. 資料合併邏輯
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

### 傳統介面（透過 ReporterAdapter）
```python
# 資料匯出
reporter = Reporter('save_data', source='Synthesizer')
reporter.create({('Synthesizer', 'exp1'): synthetic_df})
reporter.report()  # 生成: petsard_Synthesizer[exp1].csv

# 評估報告 - 單一粒度
reporter = Reporter('save_report', granularity='global')
reporter.create({('Evaluator', 'eval1_[global]'): results})
reporter.report()  # 生成: petsard[Report]_[global].csv

# 評估報告 - 多粒度支援
reporter = Reporter('save_report', granularity=['global', 'columnwise'])
reporter.create({
    ('Evaluator', 'eval1_[global]'): global_results,
    ('Evaluator', 'eval1_[columnwise]'): columnwise_results
})
reporter.report()  # 生成: petsard[Report]_eval1_[global-columnwise].csv

# 新增粒度類型
reporter = Reporter('save_report', granularity=['details', 'tree'])
reporter.create({
    ('Evaluator', 'eval1_[details]'): details_results,
    ('Evaluator', 'eval1_[tree]'): tree_results
})
reporter.report()  # 生成: petsard[Report]_eval1_[details-tree].csv

# 時間報告
reporter = Reporter('save_timing', time_unit='minutes')
reporter.create({'timing_data': timing_df})
reporter.report()  # 生成: petsard_timing.csv
```

### 函式化介面（直接使用）
```python
from petsard.reporter import ReporterSaveData, ReporterSaveReport, ReporterSaveTiming

# 函式化資料匯出
save_data_reporter = ReporterSaveData({'source': 'Synthesizer'})
save_data_reporter.report({('Synthesizer', 'exp1'): synthetic_df})

# 函式化評估報告
save_report_reporter = ReporterSaveReport({'granularity': ['global', 'columnwise']})
save_report_reporter.report({
    ('Evaluator', 'eval1_[global]'): global_results,
    ('Evaluator', 'eval1_[columnwise]'): columnwise_results
})

# 函式化時間報告
save_timing_reporter = ReporterSaveTiming({'time_unit': 'minutes'})
save_timing_reporter.report({'timing_data': timing_df})
```

### ReporterAdapter 相容性
```python
from petsard.reporter import ReporterSaveReport
from petsard.adapter import ReporterAdapter

# 建立函式化報告器
functional_reporter = ReporterSaveReport({'granularity': 'global'})

# 透過 Adapter 使用傳統介面
adapter = ReporterAdapter(functional_reporter)
adapter.create({('Evaluator', 'eval1_[global]'): results})
adapter.report()  # 內部調用函式化 report() 方法
```

## 📈 架構特點

### 技術特點
- **函式化設計**: 完全無狀態的純函數設計，避免記憶體累積
- **記憶體優化**: 採用 "throw out and throw back in" 模式
- **向後相容**: 透過 ReporterAdapter 保持現有 API 相容性
- **多粒度支援**: 支援 `str | list[str]` 的靈活配置
- **新增粒度類型**: 支援 DETAILS=4 和 TREE=5 兩種新粒度
- 使用 `petsard.metadater.safe_round` 進行數值處理
- 使用 `petsard.utils.load_external_module` 載入外部模組 (如需要)
- 內部使用 Metadater 同時保持向後相容
- 完善的 columnwise 和 pairwise 資料合併邏輯

### 設計特點
- **Adapter 模式**: ReporterAdapter 適應函式化 Reporter
- **工廠模式**: Reporter 類別根據 method 建立對應的報告器
- **策略模式**: 不同的報告生成策略（save_data, save_report, save_timing）
- 增強的共同欄位識別邏輯
- 完善的資料型別一致性處理
- 優化的合併順序和結果格式
- 完善的錯誤處理和驗證

## 🔄 架構演進

### 從有狀態到無狀態
```python
# 舊設計（有狀態）
class OldReporter:
    def __init__(self):
        self.result = {}  # 記憶體累積問題
        self._processed_data = {}  # 狀態管理複雜
    
    def create(self, data):
        self.result.update(data)  # 累積資料
    
    def report(self):
        # 使用 self.result 生成報告
        pass

# 新設計（無狀態）
class NewReporter(BaseReporter):
    def report(self, data: dict) -> None:
        # 純函數，無狀態，直接處理並輸出
        processed_data = self._process_data(data)
        self._generate_report(processed_data)
        # 資料處理完即釋放，無記憶體累積
```

### ReporterAdapter 相容性
```python
# 透過 Adapter 保持向後相容
class ReporterAdapter:
    def __init__(self, reporter: BaseReporter):
        self.reporter = reporter
        self._data = {}
    
    def create(self, data: dict):
        self._data.update(data)  # 暫存資料
    
    def report(self):
        self.reporter.report(self._data)  # 調用函式化方法
        self._data.clear()  # 清理暫存
```

## 📈 模組效益

1. **記憶體優化**: 函式化設計消除記憶體累積問題
2. **統一報告**: 標準化的實驗結果格式
3. **多粒度分析**: 支援五種不同層級的評估檢視
4. **靈活配置**: 支援單一或多重粒度組合
5. **實驗追蹤**: 完整的實驗歷程記錄
6. **向後相容**: 保持現有 API 不變
7. **自動化**: 減少手動報告生成工作
8. **可擴展**: 易於添加新的報告格式和功能

## 🎯 設計目標達成

✅ **記憶體優化**: 完全消除 `self.result` 和 `self._processed_data`
✅ **函式化設計**: 所有 `report()` 方法都是純函數
✅ **多粒度支援**: 支援 `str | list[str]` 配置和新粒度類型
✅ **向後相容**: 透過 ReporterAdapter 保持現有 API
✅ **架構清晰**: ReporterAdapter 適應函式化 Reporter

這個設計確保 Reporter 模組提供清晰的公開介面，採用現代化的函式化設計模式，同時保持向後相容性，為 PETsARD 系統提供高效能、低記憶體消耗的實驗結果報告功能。