---
title: Reporter
type: docs
weight: 60
prev: docs/api/describer
next: docs/api/adapter
---


```python
Reporter(method, **kwargs)
```

用於產生實驗結果檔案與評估報告。

## 參數

- `method` (str)：報告產生方式
  - 'save_data'：將資料集儲存為 CSV
    - 需要額外參數：
      - `source` (str | List[str])：目標模組或實驗名稱
  - 'save_report'：產生評估報告
    - 需要額外參數：
      - `granularity` (str | List[str])：報告詳細度
        - 單一粒度：'global'、'columnwise'、'pairwise'、'details'、'tree'
        - 多重粒度：['global', 'columnwise'] 或 ['details', 'tree']
      - `eval` (str | List[str], optional)：目標評估實驗名稱
  - 'save_timing'：儲存時間資訊
    - 可選額外參數：
      - `time_unit` (str)：時間單位（'seconds'、'minutes'、'hours'、'days'）
      - `module` (str | List[str])：依特定模組過濾
- `output` (str, optional)：輸出檔案名稱前綴
  - 預設值：'petsard'

## 範例

```python
from petsard import Reporter


# 儲存合成資料
reporter = Reporter('save_data', source='Synthesizer')
reporter.create({('Synthesizer', 'exp1'): synthetic_df})
reporter.report()  # 產生：petsard_Synthesizer[exp1].csv

# 產生評估報告（單一粒度）
reporter = Reporter('save_report', granularity='global')
reporter.create({('Evaluator', 'eval1_[global]'): results})
reporter.report()  # 產生：petsard[Report]_[global].csv

# 產生評估報告（多重粒度）
reporter = Reporter('save_report', granularity=['global', 'columnwise'])
reporter.create({
    ('Evaluator', 'eval1_[global]'): global_results,
    ('Evaluator', 'eval1_[columnwise]'): columnwise_results
})
reporter.report()  # 為每個粒度產生個別報告

# 使用新粒度類型產生評估報告
reporter = Reporter('save_report', granularity=['details', 'tree'])
reporter.create({
    ('Evaluator', 'eval1_[details]'): details_results,
    ('Evaluator', 'eval1_[tree]'): tree_results
})
reporter.report()  # 產生詳細和樹狀結構報告

# 儲存時間資訊
reporter = Reporter('save_timing', time_unit='minutes', module=['Loader', 'Synthesizer'])
reporter.create({'timing_data': timing_df})
reporter.report()  # 產生：petsard_timing_report.csv
```

## 方法

### `create(data)`

使用函式化設計模式初始化報告資料。

**參數**

- `data` (dict)：報告資料，其中：
  - 鍵：實驗元組 (模組名稱, 實驗名稱, ...)
  - 值：要報告的資料 (pd.DataFrame)
  - 可選用 'exist_report' 鍵來合併先前結果
  - save_timing 模式：使用 'timing_data' 鍵搭配時間 DataFrame

**回傳值**

- `dict | pd.DataFrame | None`：準備用於報告的處理後資料
  - save_data 模式：處理後的 DataFrame 字典
  - save_report 模式：包含粒度特定結果的字典
  - save_timing 模式：包含時間資訊的 DataFrame
  - 無資料處理時回傳 None

### `report(processed_data)`

使用函式化設計模式產生並儲存 CSV 格式報告。

**參數**

- `processed_data`：來自 `create()` 方法的輸出

**輸出檔名格式：**
- save_data 模式：`{output}_{module-expt_name-pairs}.csv`
- save_report 模式：`{output}[Report]_{eval}_[{granularity}].csv`
- save_timing 模式：`{output}_timing_report.csv`

## 粒度類型

### 傳統粒度
- `global`：整體摘要統計
- `columnwise`：逐欄分析
- `pairwise`：欄位間成對關係

### 新粒度類型 (v2.0+)
- `details`：詳細分解與額外指標
- `tree`：階層樹狀結構分析

## 多粒度支援

Reporter 現在支援在單一操作中處理多個粒度：

```python
# 同時處理多個粒度
reporter = Reporter('save_report', granularity=['global', 'columnwise', 'details'])
result = reporter.create(evaluation_data)
reporter.report(result)  # 為每個粒度產生個別報告
```

## 函式化設計

Reporter 使用函式化的「拋出再拋回」設計模式：
- `create()` 處理資料但不將其儲存在實例變數中
- `report()` 接收處理後的資料並產生輸出檔案
- 不維護內部狀態，減少記憶體使用量