---
title: Evaluator
type: docs
weight: 58
prev: docs/api/constrainer
next: docs/api/describer
---


```python
Evaluator(method, **kwargs)
```

合成資料品質評測器。提供隱私風險度量、資料品質評測及機器學習效用分析。

## 參數

- `method` (`str`)：評測方法，不分大小寫：

  - 隱私風險評測 (Anonymeter)：
    - 'anonymeter-singlingout'：指認性風險
    - 'anonymeter-linkability'：連結性風險
    - 'anonymeter-inference'：推斷性風險

  - 資料品質評測 (SDMetrics)：
    - 'sdmetrics-diagnosticreport'：資料效度報告
    - 'sdmetrics-qualityreport'：資料品質報告

  - 機器學習效用評測 (MLUtility)：
    - 'mlutility-classification'：分群效用
    - 'mlutility-regression'：迴歸效用
    - 'mlutility-cluster'：聚類效用

  - 'default'：使用 'sdmetrics-qualityreport'
  - 'stats：統計評測，比較合成前後的統計差異
  - 'custom_method' 自定義評測。需搭配：
    - `module_path` (str)：評測方法檔案路徑
    - `class_name` (str)：評測方法名稱

## 範例

```python
from petsard import Evaluator


eval_result: dict[str, pd.DataFrame] = None

# 隱私風險評測
eval = Evaluator('anonymeter-singlingout')
eval.create()
eval_result = eval.eval({
    'ori': train_data,
    'syn': synthetic_data,
    'control': test_data
})
privacy_risk: pd.DataFrame = eval_result['global']

# 資料品質評測
eval = Evaluator('sdmetrics-qualityreport')
eval.create()
eval_result = eval.eval({
    'ori': train_data,
    'syn': synthetic_data
})
quality_score: pd.DataFrame = eval_result['global']
```

## 方法

### `create()`

初始化評測器。

**參數**

無

**回傳值**

無

### `eval()`

```python
eval.eval(data)
```

執行評測。

**參數**

- `data` (dict)：評測用資料
  - Anonymeter 與 MLUtility 需要：
    - 'ori'：用於合成的原始資料 (pd.DataFrame)
    - 'syn'：合成資料 (pd.DataFrame)
    - 'control'：未用於合成的對照資料 (pd.DataFrame)
  - SDMetrics 需要：
    - 'ori'：原始資料 (pd.DataFrame)
    - 'syn'：合成資料 (pd.DataFrame)

**回傳值**

`(dict[str, pd.DataFrame])`，依照模組不同：
  - 'global'：表示整體資料集評測結果的單列資料框
  - 'columnwise'：表示各欄位評測結果，每列代表一個欄位的評測結果
  - 'pairwise'：表示欄位對評測結果，每列代表一組欄位配對的評測結果
  - 'details'：其他細節資訊

## 屬性

- - `config` (`EvaluatorConfig`)：評測器設定，包含 `method` 和 `method_code`

## 附錄：支援評測方式

### 支援評測方式

評測器支援三大類的評測方式：

- **隱私風險評測** (Privacy Risk Assessment) 用於評測合成資料的隱私保護程度。包括：
  - **指認性風險** (Singling Out Risk)：評測是否能從資料中識別出特定個體
  - **連結性風險** (Linkability Risk)：評測是否能連結不同資料集中的相同個體
  - **推斷性風險** (Inference Risk)：評測是否能從已知資訊推斷出其他屬性

- **資料保真評測** (Data Fidelity Assessment) 用於評測合成資料的保真性。包括：
  - **診斷報告** (Diagnostic Report)：檢驗資料結構與基本特性
  - **品質報告** (Quality Report)：評測統計分布的相似度

- **資料效用評測** (Data Utility Assessment) 用於評測合成資料的實用價值。包括：
  - **分群效用** (Classification Utility)：比較分群模型效能
  - **迴歸效用** (Regression Utility)：比較迴歸模型效能
  - **聚類效用** (Clustering Utility)：比較聚類結果

- **統計評測** (Statistical Assessment) 用於比較合成前後的統計差異
  - **統計量比較** (Statistical Comparison)：比較如均值、標準差、中位數等統計量
  - **分布比較** (Distribution Comparison)：比較如 Jensen-Shannon 散度等分布差異

- **自定義評測** (Custom Assessment) 用於整合使用者自定義的評測方法。

| 評測類型 | 評測方式 | 方法名稱 |
| :---: | :---: | :---: |
| 隱私風險評測 | 指認性風險 | anonymeter-singlingout |
| 隱私風險評測 | 連結性風險 | anonymeter-linkability |
| 隱私風險評測 | 推斷性風險 | anonymeter-inference |
| 資料保真評測 | 診斷報告 | sdmetrics-diagnosticreport |
| 資料保真評測 | 品質報告 | sdmetrics-qualityreport |
| 資料效用評測 | 分群效用 | mlutility-classification |
| 資料效用評測 | 迴歸效用 | mlutility-regression |
| 資料效用評測 | 聚類效用 | mlutility-cluster |
| 統計評測 | 統計量比較 | stats |
| 自定義評測 | 自定義方法 | custom_method |

### 隱私風險評測

#### 指認性風險評測

評測是否能從資料中識別出特定個體的紀錄。評測結果為 0 到 1 的分數，數字越大代表隱私的風險越高。

**參數**

- 'n_attacks' (`int`, default=2000)：攻擊嘗試次數（不重複查詢數）
- 'n_cols' (`int`, default=3)：每次查詢使用的欄位數
- 'max_attempts' (`int`, default=500000)：尋找成功攻擊的最大嘗試次數

**回傳值**

- `pd.DataFrame`：包含以下欄位的評測結果資料框：
  - 'risk'：隱私風險分數 (0-1)
  - 'risk_CI_btm'：隱私風險信賴區間下界
  - 'risk_CI_top'：隱私風險信賴區間上界
  - 'attack_rate'：主要隱私攻擊成功率
  - 'attack_rate_err'：主要隱私攻擊成功率誤差
  - 'baseline_rate'：基線隱私攻擊成功率
  - 'baseline_rate_err'：基線隱私攻擊成功率誤差
  - 'control_rate'：控制組隱私攻擊成功率
  - 'control_rate_err'：控制組隱私攻擊成功率誤差


#### 連結性風險評測

評測是否能連結不同資料集中屬於同一個體的紀錄。評測結果為 0 到 1 的分數，數字越大代表隱私的風險越高。

**參數**

- 'n_attacks' (`int`, default=2000)：攻擊嘗試次數
- 'max_n_attacks' (`bool`, default=False)：是否強制使用最大攻擊次數
- 'aux_cols' (`Tuple[List[str], List[str]]`)：輔助資訊欄位，例如：
    ```python
    aux_cols = [
        ['性別', '郵遞區號'],  # 公開資料
        ['年齡', '疾病史']    # 私密資料
    ]
    ```
- 'n_neighbors' (`int`, default=10)：考慮的最近鄰居數量

**回傳值**

- `pd.DataFrame`：包含與指認性風險評測相同格式的評測結果資料框

#### 推斷性風險評測

評測是否能從已知資訊推斷出其他屬性。評測結果為 0 到 1 的分數，數字越大代表隱私的風險越高。

**參數**

- 'n_attacks' (`int`, default=2000)：攻擊嘗試次數
- 'max_n_attacks' (`bool`, default=False)：是否強制使用最大攻擊次數
- 'secret' (`str`)：要被推斷的欄位
- 'aux_cols' (`List[str]`, optional)：用於推斷的欄位，預設為除了 'secret' 以外的所有欄位

**回傳值**

- `pd.DataFrame`：包含與指認性風險評測相同格式的評測結果資料框

### 資料保真評測

#### 診斷報告

驗證合成資料的結構和基本特性。

**參數**

無

**回傳值**

- `pd.DataFrame`：包含以下欄位的評測結果資料框：
  - 'Score'：整體診斷分數
  - 'Data Validity'：資料效度分數
    - 'KeyUniqueness'：主鍵唯一性
    - 'BoundaryAdherence'：數值範圍符合度
    - 'CategoryAdherence'：類別符合度
  - 'Data Structure'：資料結構分數
    - 'Column Existence'：欄位存在性
    - 'Column Type'：欄位型態符合度

#### 品質報告

評測原始資料與合成資料間的統計相似度。

**參數**

無

**回傳值**

- `pd.DataFrame`：包含以下欄位的評測結果資料框：
  - 'Score'：整體效度分數
  - 'Column Shapes'：欄位分布相似度
    - 'KSComplement'：連續變數分布相似度
    - 'TVComplement'：類別變數分布相似度
  - 'Column Pair Trends'：欄位關係保持度
    - 'Correlation Similarity'：相關性保持度
    - 'Contingency Similarity'：列聯表相似度

### 資料效用評測

#### 分群效用評測

比較分群模型在原始資料與合成資料上的預測效能，使用邏輯迴歸、支援向量機、隨機森林、梯度提升（皆使用預設參數）。

**參數**

- 'target' (`str`)：分群目標欄位

**回傳值**

- `pd.DataFrame`：包含以下欄位的評測結果資料框：
  - 'ori_mean'：原始資料模型平均 F1 分數
  - 'ori_std'：原始資料模型 F1 標準差
  - 'syn_mean'：合成資料模型平均 F1 分數
  - 'syn_std'：合成資料模型 F1 標準差
  - 'diff'：合成資料相對於原始資料的進步值

#### 迴歸效用評測

比較迴歸模型在原始資料與合成資料上的預測效能，使用線性迴歸、隨機森林迴歸、梯度提升迴歸（皆使用預設參數）。

**參數**

- 'target' (`str`)：預測目標欄位（數值型）

**回傳值**

- `pd.DataFrame`：包含以下欄位的評測結果資料框：
  - 'ori_mean'：原始資料模型平均 R² 分數
  - 'ori_std'：原始資料模型 R² 標準差
  - 'syn_mean'：合成資料模型平均 R² 分數
  - 'syn_std'：合成資料模型 R² 標準差
  - 'diff'：合成資料相對於原始資料的進步值

#### 聚類效用評測

比較 K-means 聚類演算法（使用預設參數）在原始資料與合成資料上的分群結果。

**參數**

- 'n_clusters' (`list`, default=[4, 5, 6])：聚類數量清單

**回傳值**

- `pd.DataFrame`：包含以下欄位的評測結果資料框：
  - 'ori_mean'：原始資料平均輪廓係數
  - 'ori_std'：原始資料輪廓係數標準差
  - 'syn_mean'：合成資料平均輪廓係數
  - 'syn_std'：合成資料輪廓係數標準差
  - 'diff'：合成資料相對於原始資料的進步值

### 統計評測

統計評測比較合成前後資料的統計差異，支援多種統計方法如均值、標準差、中位數、最小值、最大值、唯一值數量與 Jensen-Shannon 散度。對於數值型與類別型資料皆提供適合的評測方式。

**參數**

- 'stats_method' (`list[str]`, default=["mean", "std", "median", "min", "max", "nunique", "jsdivergence"])：統計方法清單
- 'compare_method' (`str`, default="pct_change")：比較方法，可選 "diff"（差值）或 "pct_change"（百分比變化）
- 'aggregated_method' (`str`, default="mean")：彙總方法
- 'summary_method' (`str`, default="mean")：總結方法

**回傳值**

- `pd.DataFrame`：包含統計比較結果的資料框，包括：
  - 各欄位的統計量（原始與合成）
  - 兩者差異或百分比變化
  - 整體分數

### 自定義評測

允許使用者實作並整合自定義的評測方法，透過指定外部模組路徑與類別名稱來載入自定義的評測邏輯。

**參數**

- 'module_path' (`str`)：自定義評測模組的檔案路徑
- 'class_name' (`str`)：自定義評測類別名稱
- 其他參數視自定義評測器需求而定

**回傳值**

- 依照自定義評測器的實作而定，但必須遵循標準評測器介面，返回格式為 `dict[str, pd.DataFrame]`

**自定義評測器必須實作的方法**

- `__init__(config)`: 初始化方法
- `eval(data)`: 評測方法，接收資料字典並返回評測結果

**自定義評測器必須定義的屬性**

- `REQUIRED_INPUT_KEYS`: 必要的輸入資料鍵值清單
- `AVAILABLE_SCORES_GRANULARITY`: 支援的評測粒度清單（如 "global", "columnwise"）