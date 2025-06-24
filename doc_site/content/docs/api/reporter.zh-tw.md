---
title: Reporter
type: docs
weight: 60
prev: docs/api/describer
next: docs/api/operator
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
      - `granularity` (str)：報告詳細度（'global'、'columnwise'、'pairwise'）
      - `eval` (str | List[str], optional)：目標評估實驗名稱
- `output` (str, optional)：輸出檔案名稱前綴
  - 預設值：'petsard'

## 範例

```
from petsard import Reporter


# 儲存合成資料
reporter = Reporter('save_data', source='Synthesizer')
reporter.create({('Synthesizer', 'exp1'): synthetic_df})
reporter.report()  # 產生：petsard_Synthesizer[exp1].csv

# 產生評估報告
reporter = Reporter('save_report', granularity='global')
reporter.create({('Evaluator', 'eval1_[global]'): results})
reporter.report()  # 產生：petsard[Report]_[global].csv
```

## 方法

### `create()`

初始化報告資料。

**參數**

- `data` (dict)：報告資料，其中：
  - 鍵：實驗元組 (模組名稱, 實驗名稱, ...)
  - 值：要報告的資料 (pd.DataFrame)
  - 可選用 'exist_report' 鍵來合併先前結果

### `report()`

產生並儲存 CSV 格式報告。輸出檔名格式：
- save_data 模式：`{output}_{module-expt_name-pairs}.csv`
- save_report 模式：`{output}[Report]_{eval}_[{granularity}].csv`

## 屬性
- `result`：報告結果
  - save_data 模式：DataFrame 字典
  - save_report 模式：報告的詮釋資料與內容
- `config`：報告器設定