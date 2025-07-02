# Executor 模組功能設計文件

## 🎯 模組職責

Executor 模組是 PETsARD 的核心執行引擎，負責協調和執行整個資料處理工作流程，包括配置管理、日誌系統、模組執行和結果收集。

## 📋 核心功能

### 1. 工作流程執行
- **順序執行**: 按照配置順序執行各個模組
- **狀態管理**: 追蹤和管理執行狀態
- **錯誤處理**: 處理執行過程中的異常情況
- **結果收集**: 收集和整理最終執行結果

### 2. 配置管理
- **YAML 配置載入**: 從檔案載入實驗配置
- **執行器配置**: 管理日誌、輸出等執行器特定設定
- **動態配置**: 支援執行時配置調整
- **配置驗證**: 驗證配置的完整性和正確性

### 3. 日誌系統
- **多輸出支援**: 支援 stdout、檔案或兩者同時輸出
- **日誌等級控制**: 支援多種日誌等級 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **格式化輸出**: 統一的日誌格式和時間戳記
- **動態重配置**: 支援執行時日誌配置調整

## 🏗️ 架構設計

### 設計模式
- **Command Pattern**: 將模組執行封裝為命令
- **Observer Pattern**: 監控執行狀態變化
- **Strategy Pattern**: 支援不同的執行策略
- **Template Method**: 定義執行流程模板

### 核心類別

#### ExecutorConfig 類別
```python
@dataclass
class ExecutorConfig(BaseConfig):
    """執行器配置"""
    log_output_type: str = "file"
    log_level: str = "INFO"
    log_dir: str = "."
    log_filename: str = "PETsARD_{timestamp}.log"
```

#### Executor 類別
```python
class Executor:
    """主要執行器"""
    
    def __init__(self, config: str)
    def run(self)
    def get_result(self)
    def _setup_logger(self, reconfigure=False)
    def _get_config(self, yaml_file: str) -> dict
    def _set_result(self, module: str)
```

## 🔄 執行流程

### 1. 初始化階段
```python
# 1. 載入執行器預設配置
executor_config = ExecutorConfig()

# 2. 設定日誌系統
_setup_logger()

# 3. 載入 YAML 配置
yaml_config = _get_config(config_file)

# 4. 建立配置和狀態物件
config = Config(yaml_config)
status = Status(config)
```

### 2. 執行階段
```python
# 按順序執行所有模組
while config.config.qsize() > 0:
    operator = config.config.get()
    module = config.module_flow.get()
    expt = config.expt_flow.get()
    
    # 執行模組
    operator.run(operator.set_input(status))
    status.put(module, expt, operator)
    
    # 收集結果
    _set_result(module)
```

### 3. 結果收集
```python
# 收集最終模組的結果
if module == sequence[-1]:
    full_expt = status.get_full_expt()
    full_expt_name = "_".join([f"{m}[{e}]" for m, e in full_expt.items()])
    result[full_expt_name] = status.get_result(module)
```

## 📊 公開 API

### Executor 類別 API
```python
# 建立執行器
executor = Executor('config.yaml')

# 執行工作流程
executor.run()

# 取得執行結果
results = executor.get_result()
```

### ExecutorConfig API
```python
# 配置選項
config = ExecutorConfig(
    log_output_type="both",      # "stdout", "file", "both"
    log_level="DEBUG",           # "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
    log_dir="./logs",           # 日誌檔案目錄
    log_filename="run_{timestamp}.log"  # 日誌檔案名稱模板
)
```

## 🔧 使用範例

### 基本使用
```python
from petsard.executor import Executor

# 建立並執行
executor = Executor('experiment_config.yaml')
executor.run()

# 取得結果
results = executor.get_result()
for expt_name, result in results.items():
    print(f"實驗 {expt_name} 完成")
    print(f"結果類型: {type(result)}")
```

### 自定義日誌配置
```yaml
# config.yaml
Executor:
  log_output_type: "both"
  log_level: "DEBUG"
  log_dir: "./experiment_logs"
  log_filename: "petsard_experiment_{timestamp}.log"

Loader:
  method: "csv"
  path: "data.csv"

Synthesizer:
  method: "sdv"
  model: "GaussianCopula"
```

### 程式化配置
```python
import yaml
from petsard.executor import Executor, ExecutorConfig

# 建立配置
config = {
    'Executor': {
        'log_output_type': 'file',
        'log_level': 'INFO',
        'log_dir': './logs'
    },
    'Loader': {'method': 'csv', 'path': 'data.csv'},
    'Synthesizer': {'method': 'sdv', 'model': 'GaussianCopula'}
}

# 儲存為檔案
with open('temp_config.yaml', 'w') as f:
    yaml.dump(config, f)

# 執行
executor = Executor('temp_config.yaml')
executor.run()
```

## 🧪 測試策略

### 單元測試
- 配置載入和驗證測試
- 日誌系統功能測試
- 執行流程控制測試
- 錯誤處理測試

### 整合測試
- 完整工作流程執行測試
- 多模組協調測試
- 配置檔案格式測試
- 日誌輸出驗證測試

### 效能測試
- 大型資料集執行測試
- 記憶體使用監控
- 執行時間分析

## 🔮 未來發展

### 功能增強
- **並行執行**: 支援模組並行執行以提升效能
- **斷點續執**: 支援從中斷點繼續執行
- **進度追蹤**: 提供執行進度的即時回饋
- **資源監控**: 監控 CPU、記憶體等系統資源使用

### 使用者體驗改善
- **互動式執行**: 支援互動式配置和執行
- **視覺化介面**: 提供 Web 或 GUI 介面
- **執行報告**: 生成詳細的執行報告
- **配置範本**: 提供常用配置範本

### 系統整合
- **雲端執行**: 支援雲端平台執行
- **容器化**: 支援 Docker 容器執行
- **API 服務**: 提供 REST API 介面
- **排程系統**: 整合任務排程系統

## 📝 注意事項

### 設計原則
1. **單一職責**: Executor 專注於執行協調，不處理具體業務邏輯
2. **可配置性**: 所有執行參數都可透過配置檔案調整
3. **錯誤恢復**: 提供適當的錯誤處理和恢復機制
4. **日誌完整**: 記錄完整的執行過程和狀態變化

### 最佳實踐
1. **配置驗證**: 執行前驗證所有配置參數
2. **資源管理**: 適當管理系統資源，避免記憶體洩漏
3. **異常處理**: 完善的異常捕獲和處理機制
4. **效能監控**: 監控執行效能，識別瓶頸

### 常見問題
1. **配置檔案格式錯誤**: 確保 YAML 格式正確
2. **模組依賴問題**: 確保模組執行順序正確
3. **記憶體不足**: 大型資料集需要適當的記憶體管理
4. **日誌檔案權限**: 確保日誌目錄有寫入權限