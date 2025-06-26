---
title: Executor
type: docs
weight: 51
prev: docs/api
next: docs/api/loader
---


```python
Executor(
    config=None
)
```

實驗管線的執行器，根據設定檔執行一系列的操作，具備增強的日誌記錄和配置管理功能。

## 參數

- `config` (str)：設定檔名稱（YAML 格式）

## 配置選項

執行器支援在 YAML 檔案的 `Executor` 區段中設定額外的配置選項：

```yaml
Executor:
  log_output_type: "both"    # "stdout", "file", "both"
  log_level: "INFO"          # "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
  log_dir: "./logs"          # 日誌檔案目錄
  log_filename: "PETsARD_{timestamp}.log"  # 日誌檔案名稱模板

# 您的實驗配置
Loader:
  load_data:
    method: "csv"
    path: "data.csv"
```

## 範例

### 基本使用
```python
exec = Executor(config="config.yaml")
exec.run()
results = exec.get_result()
```

### 時間分析
```python
exec = Executor(config="config.yaml")
exec.run()

# 取得執行結果
results = exec.get_result()

# 取得時間資訊
timing_data = exec.get_timing()
print(timing_data)
# 顯示每個模組和步驟的執行時間
```

### 自定義日誌設定
```python
# 包含執行器設定的 config.yaml
exec = Executor(config="config_with_logging.yaml")
exec.run()
```

## 方法

### `run()`

根據設定檔執行實驗管線。

**參數**

無

**回傳值**

無。執行結果儲存於 `result` 屬性

### `get_result()`

取得實驗結果。

**參數**

無

**回傳值**

- dict：包含所有實驗結果的字典
  - 格式：`{full_expt_name: result}`

### `get_timing()`

取得所有模組的執行時間記錄。

**參數**

無

**回傳值**

- pandas.DataFrame：包含時間資訊的 DataFrame，欄位包括：
  - `record_id`：唯一的時間記錄識別碼
  - `module_name`：執行的模組名稱
  - `experiment_name`：實驗配置名稱
  - `step_name`：執行步驟名稱（如 'run', 'fit', 'sample'）
  - `start_time`：執行開始時間（ISO 格式）
  - `end_time`：執行結束時間（ISO 格式）
  - `duration_seconds`：執行持續時間（秒，預設四捨五入至 2 位小數）
  - `duration_precision`：duration_seconds 的小數位數精度（預設：2）
  - 其他來自執行上下文的欄位

## 屬性

- `executor_config`：執行器專用配置（ExecutorConfig 物件）
- `config`：實驗配置內容（Config 物件）
- `sequence`：模組執行順序列表
- `status`：執行狀態追蹤（Status 物件）
- `result`：最終結果字典

## 配置類別

### ExecutorConfig

```python
@dataclass
class ExecutorConfig:
    log_output_type: str = "file"
    log_level: str = "INFO"
    log_dir: str = "."
    log_filename: str = "PETsARD_{timestamp}.log"
```

**參數：**
- `log_output_type`：日誌輸出位置（"stdout", "file", "both"）
- `log_level`：日誌等級（"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"）
- `log_dir`：日誌檔案儲存目錄
- `log_filename`：日誌檔案名稱模板（支援 {timestamp} 佔位符）