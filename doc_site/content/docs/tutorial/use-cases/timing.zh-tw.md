---
title: 計時
type: docs
weight: 36
prev: docs/tutorial/use-cases/benchmark-datasets
next: docs/tutorial/use-cases
---


在開發和優化隱私保護資料合成流程時，您可能需要：
  - 監控管線中每個模組的執行時間
  - 識別工作流程中的效能瓶頸
  - 比較不同配置下的執行時間
  - 產生時間報告進行效能分析

PETsARD 提供內建的時間分析功能，自動追蹤工作流程中每個模組和步驟的執行時間。這有助於您了解時間花費在哪裡，並相應地優化您的管線。

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/use-cases/timing.ipynb)

```yaml
---
Loader:
  data:
    filepath: 'benchmark/adult-income.csv'
Synthesizer:
  default:
    method: 'default'
Evaluator:
  default:
    method: 'default'
Reporter:
  save_timing:
    method: 'save_timing'
    time_unit: 'seconds'
...
```

## 取得時間資訊

執行工作流程後，您可以透過多種方式存取時間資訊：

### 1. 使用 Executor API

```python
from petsard import Executor

# 執行您的工作流程
executor = Executor('config.yaml')
executor.run()

# 以 DataFrame 格式取得時間資料
timing_data = executor.get_timing()
print(timing_data)
```

### 2. 儲存時間報告

您可以配置 Reporter 自動儲存時間資料：

```yaml
Reporter:
  save_timing:
    method: 'save_data'
    data_type: 'timing'
    filepath: 'output/timing_report.csv'
```

## 時間資料格式

時間資料包含以下資訊：

- **record_id**：唯一的時間記錄識別碼
- **module_name**：執行的模組名稱（如 'Loader', 'Synthesizer'）
- **experiment_name**：實驗配置名稱
- **step_name**：執行步驟名稱（如 'run', 'fit', 'sample'）
- **start_time**：執行開始時間（ISO 格式）
- **end_time**：執行結束時間（ISO 格式）
- **duration_seconds**：執行持續時間（秒，預設四捨五入至 2 位小數）
- **duration_precision**：duration_seconds 的小數位數精度（預設：2）

## 效能分析技巧

1. **識別瓶頸**：尋找 duration_seconds 最長的模組
2. **比較配置**：使用不同參數執行相同工作流程並比較時間結果
3. **監控趨勢**：追蹤多次執行的時間資料以識別效能趨勢
4. **優化工作流程**：使用時間洞察來優化模組配置和資料處理步驟

## 範例分析

```python
import pandas as pd

# 載入時間資料
timing_data = executor.get_timing()

# 按模組分析執行時間
module_times = timing_data.groupby('module_name')['duration_seconds'].sum()
print("各模組總執行時間：")
print(module_times.sort_values(ascending=False))

# 找出最慢的操作
slowest_ops = timing_data.nlargest(5, 'duration_seconds')
print("\n最慢的操作：")
print(slowest_ops[['module_name', 'step_name', 'duration_seconds']])
```

這個時間分析功能幫助您建立更高效且優化的隱私保護資料合成工作流程。