---
title: 日誌設定
type: docs
weight: 86
prev: docs/developer-guide/mpuccs
next: docs/developer-guide/experiment-name-in-reporter
---

## 日誌設定

日誌配置在 YAML 配置檔案的 `Executor` 部分指定。

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/developer-guide/logging-configuration.ipynb)

```yaml
---
Executor:
  log_output_type: both # 日誌輸出位置：stdout, file, 或 both。預設為 file
  log_level: DEBUG      # 日誌詳細程度：DEBUG, INFO, WARNING, ERROR, CRITICAL。預設為 INFO
  log_dir: demo_logs    # 日誌檔案目錄（如不存在則自動建立）。預設為 .，即工作目錄
  log_filename: PETsARD_demo_{timestamp}.log # 日誌檔案名稱模板。預設為 "PETsARD_{timestamp}.log"
# ... 後面省略
...
```

這四個參數都是可選的，您可以根據需求選擇使用。此外，`Executor` 在 YAML 檔案中的位置順序並不會影響其功能。

### 輸出目標 (log_output_type)

- `stdout`：日誌輸出到控制台
- `file`：日誌寫入檔案
- `both`：日誌同時輸出到控制台和寫入檔案

### 日誌檔案命名 (log_filename)

檔案名中的 `{timestamp}` 佔位符將替換為當前日期和時間。如不想要日期可省略。
