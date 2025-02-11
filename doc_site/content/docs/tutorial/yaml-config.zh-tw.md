---
title: YAML 設定
type: docs
weight: 11
prev: docs/tutorial
next: docs/tutorial/default-synthesis
---

YAML 是一種人類可讀的資料序列化格式，PETsARD 使用它來進行實驗設定。本文件說明如何有效地組織您的 YAML 設定。

## 基本結構

PETsARD 的 YAML 設定採用三層架構：

```yaml
模組名稱:             # 第一層：模組
    實驗名稱:         # 第二層：實驗
        參數1: 數值   # 第三層：參數
        參數2: 數值
```

### 模組層級

最上層定義了按執行順序排列的處理模組：

- Loader：資料讀取
- Preprocessor：資料前處理
- Synthesizer：資料合成
- Postprocessor：資料後處理
- Constrainer：資料約束
- Evaluator：結果評估
- Reporter：報告產生

### 實驗層級

每個模組可以有多個實驗設定：

```yaml
Synthesizer:
    exp1_ctgan:        # 第一個實驗
        method: ctgan
        epochs: 100
    exp2_tvae:         # 第二個實驗
        method: tvae
        epochs: 200
```

### 參數層級

參數依照各模組的具體要求設定：

```yaml
Loader:
    demo_load:
        filepath: 'data/sample.csv'
        na_values:
            age: '?'
            income: 'unknown'
        column_types:
            category:
                - gender
                - occupation
```

## 執行流程

當定義多個實驗時，PETsARD 採用深度優先的順序執行：
```
Loader -> Preprocessor -> Synthesizer -> Postprocessor -> Constrainer -> Evaluator -> Reporter
```

例如：
```yaml
Loader:
    load_a:
        filepath: 'data1.csv'
    load_b:
        filepath: 'data2.csv'
Synthesizer:
    syn_ctgan:
        method: ctgan
    syn_tvae:
        method: tvae
```

這會產生四種實驗組合：
1. load_a + syn_ctgan
2. load_a + syn_tvae
3. load_b + syn_ctgan
4. load_b + syn_tvae

## 報告選項

Reporter 支援兩種方法：

### 資料儲存
```yaml
Reporter:
    save_data:
        method: 'save_data'
        source: 'Postprocessor'  # 要儲存數據的來源模組
```

### 報告產生
```yaml
Reporter:
    save_report:
        method: 'save_report'
        granularity: 'global'    # 報告詳細程度
```

## 最佳實踐

1. 使用有意義的實驗名稱
2. 依模組組織參數
3. 為實驗設定加上註解
4. 執行前驗證 YAML 語法
