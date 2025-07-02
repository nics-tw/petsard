# Config 模組功能設計文件

## 🎯 模組職責

Config 模組負責管理 PETsARD 執行器的配置和狀態管理，提供統一的配置解析、流程控制和狀態追蹤功能。

## 📋 核心功能

### 1. 配置管理 (Config)
- **YAML 配置解析**: 解析實驗配置檔案
- **模組流程控制**: 管理模組執行順序和依賴關係
- **動態配置轉換**: 處理特殊配置如 Splitter 的多樣本配置
- **配置驗證**: 檢查配置格式的正確性

### 2. 狀態管理 (Status)
- **執行狀態追蹤**: 追蹤各模組的執行狀態和結果
- **元資料管理**: 統一管理各模組產生的元資料
- **結果儲存**: 儲存和檢索各模組的執行結果
- **依賴關係處理**: 管理模組間的資料依賴關係

## 🏗️ 架構設計

### 設計模式
- **Queue Pattern**: 使用佇列管理模組執行流程
- **State Pattern**: 管理執行器的不同狀態
- **Observer Pattern**: 追蹤模組執行狀態變化

### 核心類別

#### Config 類別
```python
class Config:
    """實驗配置管理器"""
    
    def __init__(self, config: dict)
    def _set_flow(self) -> Tuple[queue.Queue, queue.Queue, queue.Queue]
    def _splitter_handler(self, config: dict) -> dict
```

#### Status 類別
```python
class Status:
    """執行狀態管理器"""
    
    def put(self, module: str, expt: str, operator: BaseOperator)
    def get_result(self, module: str) -> Union[dict, pd.DataFrame]
    def get_metadata(self, module: str = "Loader") -> SchemaMetadata
    def set_metadata(self, module: str, metadata: SchemaMetadata)
```

## 🔄 與 Metadater 整合

### 元資料類型遷移
- **舊版**: `petsard.loader.Metadata`
- **新版**: `petsard.metadater.SchemaMetadata`

### 整合優勢
- **統一介面**: 使用 Metadater 的標準化元資料格式
- **型別安全**: 強型別檢查和驗證
- **功能增強**: 更豐富的元資料操作功能

## 📊 公開 API

### Config 類別 API
```python
# 建立配置物件
config = Config(yaml_config_dict)

# 取得執行流程
config.config      # 模組操作器佇列
config.module_flow # 模組名稱佇列
config.expt_flow   # 實驗名稱佇列
config.sequence    # 模組執行順序
```

### Status 類別 API
```python
# 狀態管理
status.put(module, expt, operator)           # 儲存模組狀態
status.get_result(module)                    # 取得模組結果
status.get_metadata(module)                  # 取得模組元資料
status.set_metadata(module, metadata)        # 設定模組元資料

# 流程控制
status.get_pre_module(curr_module)           # 取得前一個模組
status.get_full_expt(module)                 # 取得完整實驗配置

# 特殊功能
status.get_synthesizer()                     # 取得合成器
status.get_processor()                       # 取得處理器
status.get_report()                          # 取得報告
```

## 🔧 使用範例

### 基本使用
```python
from petsard.config import Config, Status

# 載入配置
with open('config.yaml', 'r') as f:
    yaml_config = yaml.safe_load(f)

# 建立配置和狀態管理器
config = Config(yaml_config)
status = Status(config)

# 執行流程
while config.config.qsize() > 0:
    operator = config.config.get()
    module = config.module_flow.get()
    expt = config.expt_flow.get()
    
    # 執行模組
    operator.run(operator.set_input(status))
    status.put(module, expt, operator)
```

### 元資料管理
```python
# 取得和設定元資料
metadata = status.get_metadata("Loader")
status.set_metadata("Preprocessor", processed_metadata)

# 檢查模組依賴
pre_module = status.get_pre_module("Synthesizer")
if pre_module:
    input_data = status.get_result(pre_module)
```

## 🧪 測試策略

### 單元測試
- 配置解析正確性測試
- 狀態管理功能測試
- 元資料操作測試
- 錯誤處理測試

### 整合測試
- 完整工作流程測試
- 模組間依賴關係測試
- 多實驗配置測試

## 🔮 未來發展

### 功能增強
- **並行執行支援**: 支援模組並行執行
- **配置驗證增強**: 更嚴格的配置格式檢查
- **狀態持久化**: 支援執行狀態的儲存和恢復
- **動態配置**: 支援執行時配置修改

### 效能最佳化
- **記憶體管理**: 最佳化大型資料集的記憶體使用
- **快取機制**: 實作智慧快取減少重複計算
- **流程最佳化**: 自動最佳化模組執行順序

## 📝 注意事項

### 設計原則
1. **單一職責**: Config 負責配置，Status 負責狀態
2. **依賴注入**: 透過介面注入依賴，提高可測試性
3. **錯誤處理**: 完善的錯誤檢查和異常處理
4. **向後相容**: 保持與舊版 API 的相容性

### 最佳實踐
1. **配置驗證**: 在執行前驗證所有配置參數
2. **狀態一致性**: 確保狀態管理的一致性和正確性
3. **資源管理**: 適當管理記憶體和系統資源
4. **日誌記錄**: 完整記錄配置和狀態變化