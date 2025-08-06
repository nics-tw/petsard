---
title: Reporter 中的實驗名稱
type: docs
weight: 87
prev: docs/developer-guide/logging-configuration
next: docs/developer-guide/test-coverage
---

PETsARD 採用統一的實驗命名規範，用於識別和追蹤實驗過程。本文件說明實驗命名格式和命名策略系統。

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/developer-guide/experiment-name-in-reporter.ipynb)

## 命名策略概述

Reporter 模組支援兩種命名策略，可透過 `naming_strategy` 參數控制：

1. **TRADITIONAL**：維持向後相容性的傳統命名格式
2. **COMPACT**：提供更簡潔易讀的命名格式

### 命名策略參數

Reporter 類別現在接受 `naming_strategy` 參數來控制輸出檔名格式：

```python
from petsard.reporter import Reporter

# 傳統命名（預設）
reporter = Reporter('save_report', granularity='global', naming_strategy='traditional')

# 簡潔命名
reporter = Reporter('save_report', granularity='global', naming_strategy='compact')
```

## 實驗名稱格式

### 實驗元組

`full_expt_tuple` 是一個由模組名稱和實驗名稱組成的元組：
```python
(module_name, experiment_name)
```

此格式主要用於 Reporter 系統識別和組織實驗結果。

### 實驗字串

`full_expt_name` 是將模組名稱和實驗名稱用連字號串接的字串：
```
{module_name}-{experiment_name}
```

此格式用於輸出檔案名稱：
```
# 合成資料檔案
petsard_Synthesizer-exp1.csv
petsard_Synthesizer-exp2_epsilon1.0.csv

# 評估報告檔案
petsard[Report]_Evaluator-eval1_[global].csv
petsard[Report]_Evaluator-eval1_[columnwise].csv
```

## 命名範例

### 資料合成實驗

```python
# 不同方法比較
reporter.create({
    ('Synthesizer', 'exp1_ctgan'): ctgan_results,
    ('Synthesizer', 'exp2_tvae'): tvae_results,
    ('Synthesizer', 'exp3_copula'): copula_results
})

# 輸出檔案：
# petsard_Synthesizer-exp1_ctgan.csv
# petsard_Synthesizer-exp2_tvae.csv
# petsard_Synthesizer-exp3_copula.csv
```

### 方法比較實驗

```python
# 不同方法比較
reporter.create({
    ('Synthesizer', 'exp1_method_a'): method_a_df,
    ('Synthesizer', 'exp2_method_b'): method_b_df,
    ('Synthesizer', 'exp3_baseline'): baseline_df
})

# 輸出檔案：
# petsard_Synthesizer-exp1_method_a.csv
# petsard_Synthesizer-exp2_method_b.csv
# petsard_Synthesizer-exp3_baseline.csv
```

### 評估實驗

```python
# 多層級評估
reporter.create({
    ('Evaluator', 'privacy_risk_[global]'): global_privacy,
    ('Evaluator', 'data_quality_[columnwise]'): column_quality,
    ('Evaluator', 'correlation_[pairwise]'): pair_correlation,
    ('Evaluator', 'detailed_analysis_[details]'): detailed_analysis,
    ('Evaluator', 'hierarchical_view_[tree]'): tree_analysis
})

# 輸出檔案：
# petsard[Report]_Evaluator-privacy_risk_[global].csv
# petsard[Report]_Evaluator-data_quality_[columnwise].csv
# petsard[Report]_Evaluator-correlation_[pairwise].csv
# petsard[Report]_Evaluator-detailed_analysis_[details].csv
# petsard[Report]_Evaluator-hierarchical_view_[tree].csv
```

## 命名建議

1. **模組名稱**
   - 使用標準模組名稱：'Synthesizer'、'Evaluator'、'Processor' 等
   - 注意大小寫需要完全匹配

2. **實驗名稱**
   - 使用有意義的前綴：'exp'、'eval'、'test' 等
   - 用底線分隔不同部分：方法名稱、參數設定等
   - 評估層級使用方括號：[global]、[columnwise]、[pairwise]

3. **參數編碼**
   - 參數名稱使用縮寫：method、batch、epoch 等
   - 數值使用簡潔表示：300、0.1 等
   - 多參數用底線連接：method_a_batch500

---

## 🚀 檔案命名格式 (v2.0)

### 設計目標

v2.0 引入了簡潔檔案命名格式，解決了原有命名的問題：

1. **簡潔易讀**: 使用模組簡寫和點號分隔，檔名更短更清晰
2. **參數追蹤**: 自動將實驗參數編碼到檔案名稱中
3. **多次執行**: 支援迭代編號，區分多次執行結果
4. **向後相容**: 保留原有格式，可選擇使用簡潔格式

### 兩種檔案命名格式

#### 1. 標準格式 (Traditional)
```
# 資料檔案
petsard_Synthesizer-baseline_experiment.csv
petsard_Evaluator-eval1_[global].csv

# 報告檔案
petsard[Report]_Evaluator-eval1_[global].csv
```

#### 2. 簡潔格式 (Compact)
```
# 基本格式：petsard_模組簡寫.實驗名稱.csv
petsard_Sy.baseline_experiment.csv

# 帶迭代（僅Splitter）：petsard_模組簡寫.實驗名稱.迭代.csv
petsard_Sp.train_test.i2.csv

# 帶粒度（僅Reporter）：petsard_模組簡寫.實驗名稱.粒度.csv
petsard_Ev.cross_validation.G.csv
```

### 模組簡寫對照表

| 模組名稱 | 簡寫 | 範例檔名 |
|---------|------|---------|
| Loader | Ld | `petsard_Ld.load_adult.csv` |
| Splitter | Sp | `petsard_Sp.train_test.csv` |
| Processor | Pr | `petsard_Pr.normalize.i1.csv` |
| Synthesizer | Sy | `petsard_Sy.ctgan_baseline.csv` |
| Constrainer | Cn | `petsard_Cn.privacy_check.csv` |
| Evaluator | Ev | `petsard_Ev.utility_eval.G.csv` |
| Reporter | Rp | `petsard_Rp.summary.csv` |

### 粒度簡寫對照表

| 粒度名稱 | 簡寫 | 範例檔名 |
|---------|------|---------|
| global | G | `petsard_Ev.privacy_eval.G.csv` |
| columnwise | C | `petsard_Ev.column_analysis.C.csv` |
| pairwise | P | `petsard_Ev.correlation.P.csv` |
| details | D | `petsard_Ev.detailed_report.D.csv` |
| tree | T | `petsard_Ev.hierarchical.T.csv` |

### 簡潔格式規則

簡潔格式只包含必要的資訊：

| 組件 | 適用模組 | 格式 | 範例 |
|------|---------|------|------|
| 模組簡寫 | 所有 | 2字符簡寫 | `Synthesizer` → `Sy` |
| 實驗名稱 | 所有 | 完整名稱 | `gaussian-copula` |
| 迭代編號 | 僅 Splitter | `i` + 數值 | `iteration: 2` → `i2` |
| 粒度簡寫 | 僅 Reporter | 1字符簡寫 | `global` → `G` |

### 檔案命名範例

#### 資料合成實驗
```
# 傳統格式
petsard_Synthesizer-ctgan_baseline.csv
petsard_Synthesizer-tvae_method_b.csv

# 簡潔格式
petsard_Sy.ctgan_baseline.csv
petsard_Sy.tvae_method_b.csv
```

#### 多次處理實驗
```
# 傳統格式（無法區分迭代）
petsard_Processor-normalize_step1.csv
petsard_Processor-encode_step2.csv

# 簡潔格式（清楚標示迭代）
petsard_Pr.data_pipeline.i1.norm.csv
petsard_Pr.data_pipeline.i2.enco.csv
```

#### 評估實驗
```
# 傳統格式
petsard_Evaluator-privacy_eval_[global].csv
petsard[Report]_Evaluator-privacy_eval_[global].csv

# 簡潔格式
petsard_Ev.privacy_eval.G.csv
petsard_Ev.utility_eval.C.csv
```

### 檔名解讀指南

#### Splitter 範例：`petsard_Sp.train_test.i2.csv`
- `petsard_` : 系統前綴
- `Sp` : Splitter 模組
- `train_test` : 實驗名稱
- `i2` : 第2次迭代（僅Splitter有）
- `.csv` : 檔案格式

#### Reporter 範例：`petsard_Ev.utility_eval.G.csv`
- `petsard_` : 系統前綴
- `Ev` : Evaluator 模組
- `utility_eval` : 實驗名稱
- `G` : global 粒度（僅Reporter有）
- `.csv` : 檔案格式

#### 一般模組範例：`petsard_Sy.gaussian-copula.csv`
- `petsard_` : 系統前綴
- `Sy` : Synthesizer 模組
- `gaussian-copula` : 實驗名稱
- `.csv` : 檔案格式

### 使用建議

1. **新專案**: 建議使用簡潔格式，檔名更短更清晰
2. **現有專案**: 可繼續使用標準格式，確保相容性
3. **複雜實驗**: 簡潔格式能更好地追蹤參數和迭代
4. **檔案管理**: 簡潔格式的點號分隔便於檔案排序和分類

### Reporter 使用方式

```python
from petsard.reporter import Reporter

# 傳統命名策略
reporter = Reporter('save_report', granularity='global', naming_strategy='traditional')
reporter.create({('Evaluator', 'eval1_[global]'): results})
reporter.report()  # 產生：petsard[Report]_eval1_[global].csv

# 簡潔命名策略
reporter = Reporter('save_report', granularity='global', naming_strategy='compact')
reporter.create({('Evaluator', 'eval1_[global]'): results})
reporter.report()  # 產生：petsard_eval1_global.csv

# 儲存資料範例
reporter = Reporter('save_data', source='Synthesizer', naming_strategy='compact')
reporter.create({('Synthesizer', 'exp1'): synthetic_data})
reporter.report()  # 產生：petsard_Synthesizer_exp1.csv
```

### 檔名格式比較

| 方法 | 傳統格式 | 簡潔格式 |
|------|---------|---------|
| save_data | `petsard_Synthesizer[exp1].csv` | `petsard_Synthesizer_exp1.csv` |
| save_report | `petsard[Report]_eval1_[global].csv` | `petsard_eval1_global.csv` |
| save_timing | `petsard_timing_report.csv` | `petsard_timing_report.csv` |

### 使用建議

1. **新專案**: 建議使用簡潔格式，檔名更短更清晰
2. **現有專案**: 可繼續使用標準格式，確保相容性
3. **複雜實驗**: 簡潔格式能更好地追蹤參數和迭代
4. **檔案管理**: 簡潔格式的點號分隔便於檔案排序和分類

所有檔案命名和格式轉換都由 Reporter 自動處理，用戶只需要專注於實驗邏輯。