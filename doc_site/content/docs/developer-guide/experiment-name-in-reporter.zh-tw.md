---
title: Reporter 中的實驗名稱
type: docs
weight: 87
prev: docs/developer-guide/logging-configuration
next: docs/developer-guide/test-coverage
---

PETsARD 採用統一的實驗命名規範，用於識別和追蹤實驗過程。本文件說明兩種主要的命名格式及其使用方式。

## 實驗名稱格式

### 實驗元組

`full_expt_tuple` 是一個由模組名稱和實驗名稱組成的元組：
```python
(module_name, experiment_name)
```

此格式主要用於建立報告時指定實驗：
```python
# 基本用法
reporter.create({
    ('Synthesizer', 'exp1'): df_synthetic,
    ('Evaluator', 'eval1_[global]'): df_results
})

# 多實驗比較
reporter.create({
    ('Synthesizer', 'exp1_epsilon0.1'): df_low_privacy,
    ('Synthesizer', 'exp2_epsilon1.0'): df_high_privacy,
    ('Synthesizer', 'exp3_epsilon5.0'): df_baseline
})

# 不同評估層級
reporter.create({
    ('Evaluator', 'eval1_[global]'): global_results,
    ('Evaluator', 'eval1_[columnwise]'): column_results,
    ('Evaluator', 'eval1_[pairwise]'): pair_results
})
```

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

### 隱私參數實驗

```python
# 隱私參數調整
reporter.create({
    ('Synthesizer', 'exp1_eps0.1_delta1e-5'): low_privacy_df,
    ('Synthesizer', 'exp2_eps1.0_delta1e-5'): med_privacy_df,
    ('Synthesizer', 'exp3_eps10.0_delta1e-5'): high_privacy_df
})

# 輸出檔案：
# petsard_Synthesizer-exp1_eps0.1_delta1e-5.csv
# petsard_Synthesizer-exp2_eps1.0_delta1e-5.csv
# petsard_Synthesizer-exp3_eps10.0_delta1e-5.csv
```

### 評估實驗

```python
# 多層級評估
reporter.create({
    ('Evaluator', 'privacy_risk_[global]'): global_privacy,
    ('Evaluator', 'data_quality_[columnwise]'): column_quality,
    ('Evaluator', 'correlation_[pairwise]'): pair_correlation
})

# 輸出檔案：
# petsard[Report]_Evaluator-privacy_risk_[global].csv
# petsard[Report]_Evaluator-data_quality_[columnwise].csv
# petsard[Report]_Evaluator-correlation_[pairwise].csv
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
   - 參數名稱使用縮寫：eps (epsilon)、del (delta) 等
   - 數值使用簡潔表示：1e-5、0.1 等
   - 多參數用底線連接：eps0.1_del1e-5