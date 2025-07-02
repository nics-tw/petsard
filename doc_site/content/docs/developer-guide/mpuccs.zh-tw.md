---
title: mpUCCs 實驗性新功能
type: docs
weight: 85
prev: docs/developer-guide/anonymeter
next: docs/developer-guide/logging-configuration
math: true
---


## 概述

mpUCCs (Maximal Partial Unique Column Combinations，最大部分唯一欄位組合) 是 PETsARD 系統中的一個實驗性隱私風險評估工具，基於最大部分唯一欄位組合理論，提供比傳統指認性攻擊方法更準確和高效的隱私風險評估。

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/developer-guide/mpuccs.ipynb)

```yaml
---
Loader:
  data:
    filepath: 'benchmark/adult-income.csv'
Splitter:
  demo:
    num_samples: 1
    train_split_ratio: 0.8
Preprocessor:
  demo:
    method: 'default'
Synthesizer:
  demo:
    method: 'default'
Postprocessor:
  demo:
    method: 'default'
Evaluator:
  demo-mpuccs:
    method: 'mpuccs'
    n_cols:
      - 1
      - 2
      - 3
      - 4
      - 5
Reporter:
  output:
    method: 'save_data'
    source: 'Synthesizer'
  save_report_global:
    method: 'save_report'
    granularity: 'global'
...
```

## 理論基礎

### 核心概念

#### UCC (Unique Column Combinations，唯一欄位組合)
UCC 是指在資料集中的所有記錄上，此欄位組合的值都是唯一的，沒有重複。

**範例：**
對於門牌資料，地址是唯一值。而地址也可視為縣市、鄉鎮、道路、與門牌的唯一值組合。

#### pUCC (Partial Unique Column Combinations，部分唯一欄位組合)
pUCC 則是只有在特定條件或特定值的情況下才具有唯一性，而不是在全部資料集上都唯一。

**範例：**
在大部分情況，路街名、門牌號碼不是唯一的，因為在不同鄉鎮市具有許多重名的街道，只有 (1.) 特殊的道路名稱 或 (2.) 特殊的門牌號碼，才會是唯一值。

#### mpUCCs (Maximal Partial Unique Column Combinations，最大部分唯一欄位組合)
mpUCCs 指具有最大形式 (Maximal form) 的 pUCCs，意味著不存在比它更小的子集能達到相同的識別效果。

**範例：**
對於「忠孝東路」「一段」「1號」，由於其他縣市也有忠孝東路，精簡任何欄位屬性都無法達到唯一識別，此時即為 mpUCCs。

### 關鍵理論洞察

#### mpUCCs = QIDs (準識別符)
指認性攻擊的本質是：
1. 在合成資料中識別出一個獨特的欄位組合
2. 該組合在原始資料中也僅對應到一個獨特記錄

本質上可視為找 pUCC 之後，比對是否也為 pUCC。

#### 自包含匿名性 (Self-contained Anonymity)
當資料集中沒有任何特徵組合 (IDs + QIDs) 能唯一識別原始實體時，該資料集被視為匿名化。

**尋找 QIDs (Find-QIDs problem) 即為發現 mpUCCs！**

重複計算非最大形式的欄位組合會高估風險 - 此即指認性風險具集合意義的反面表述！

## 演算法實現

### Find-QIDs 問題的困難

1. 對於 k 個屬性，潛在的 QIDs 為 2^k - 1 組
2. 被證明為 W[2]-complete 問題 (Bläsius et al., 2017)
3. 問題沒有最優子結構，故沒辦法動態規劃

**範例：** 知道 {A, B} 跟 {B, C} 並沒有 pUCCs，並不等於 {A, B, C} 沒有。

### 我們的解決方案：啟發式貪婪基數優先演算法

#### 1. 以高基數欄位為優先
- 計算所有欄位的基數
- 對於數值型欄位，依最低精度四捨五入
- 欄位組合廣度優先：由少到多，高基數先進

#### 2. 對欄位跟值域組合做集合運算
- 運用 `collections.Counter` 抓僅有一筆的合成資料值域組合
- 比對出同樣值域組合且僅有一筆的原始資料
- 紀錄對應之原始與合成資料索引

#### 3. 剪枝策略
若該欄位組合所有值域組合都唯一且碰撞，則跳過其超集。

#### 4. 遮罩機制
對於已被高基數少欄位識別過的合成資料，該列不再碰撞。

#### 5. 基於條件熵的早停機制
我們基於過去對於功能相依 (Functional Dependencies) 的資訊熵研究 (Mandros et al., 2020)，提出以下的演算法：

**對於 k ≥ 2 的欄位組合：**

1. **欄位組合熵** H(XY) = entropy(Counter(syn_data[XY]) / syn_n_rows)
2. **條件熵** H(Y|X) = Σ p(X = x)*H(Y | X = x)，其中 x ∈ {pUCC, ¬pUCC}
3. **互資訊** I(X; Y) = H(Y) - H(Y|X)

**早停：** 如果互資訊為負，則後續繼承的欄位組合不再確認。

#### 6. Rényi 熵（α=2，碰撞熵）
我們使用 Rényi 熵而非 Shannon 熵，以更好地進行碰撞機率分析：

- **理論最大熵** = log(n_rows)
- **合成資料最大熵** = scipy.stats.entropy(Counter(syn_data))
- **欄位組合熵** = scipy.stats.entropy(Counter(syn_data[column_combos]))
- **正規化** = 合成資料最大熵 - 欄位組合熵

## 相較於 Anonymeter 的關鍵改進

### 1. 理論基礎
- **明確理論基礎**：mpUCCs = QIDs 提供堅實的數學基礎
- **避免風險高估**：專注於最大形式組合
- **集合論意義**：正確理解指認性風險的本質

### 2. 演算法優化
- **漸進式樹狀搜尋**：高效的欄位組合探索
- **基於熵的剪枝**：智能早停機制
- **基數優先處理**：高基數欄位優先處理
- **碰撞導向分析**：直接聚焦於實際隱私風險

### 3. 精度處理
- **自動數值精度檢測**：處理浮點數比較問題
- **日期時間精度支援**：適當處理時間資料
- **手動精度覆蓋**：允許自訂精度設定

### 4. 效能改進
- **更快執行**：在 adult-income 資料集上 5 分鐘 vs 12+ 分鐘
- **更好擴展性**：高效處理高維度資料
- **記憶體優化**：基於 Counter 的唯一性檢測

### 5. 全面進度追蹤
- **雙層進度條**：欄位層級和組合層級進度
- **詳細執行樹**：演算法決策的完整審計軌跡
- **剪枝統計**：優化決策的透明度

## 配置參數

```python
config = {
    'eval_method': 'mpuccs',
    'n_cols': None,                    # 目標組合大小 (None/int/list)
    'min_entropy_delta': 0.0,          # 最小熵增益閾值
    'field_decay_factor': 0.5,         # 欄位衰減因子
    'renyi_alpha': 2.0,                # Rényi 熵參數 (碰撞熵)
    'numeric_precision': None,          # 數值精度 (自動偵測或手動設定)
    'datetime_precision': None          # 日期時間精度 (自動偵測或手動設定)
}
```

### 參數詳解

#### `n_cols`
- `None`：評估從 1 到欄位數的所有組合大小
- `int`：僅評估特定組合大小
- `list`：評估特定組合大小（支援跳躍模式如 [1, 3]）

#### `min_entropy_delta`
- 繼續探索分支所需的最小熵增益
- 任何正值意味著只要有熵差異就會剪枝
- 較高值導致更積極的剪枝
- 預設：0.0（無基於熵的剪枝）

#### `field_decay_factor`
- 較大欄位組合的加權因子
- 反映在攻擊中使用更多欄位的實際困難度
- 預設：0.5（每增加一個欄位權重減半）

#### `renyi_alpha`
- Rényi 熵計算的 alpha 參數
- α=2 對應碰撞熵，適合隱私分析
- 預設：2.0

## 使用範例

### 基本使用
```python
from petsard.evaluator import Evaluator

# 初始化評估器
evaluator = Evaluator('mpuccs')
evaluator.create()

# 評估隱私風險
results = evaluator.eval({
    'ori': original_data,
    'syn': synthetic_data
})

# 存取結果
global_stats = results['global']
detailed_results = results['details']
tree_analysis = results['tree']
```

### 進階配置
```python
# 自訂配置
evaluator = Evaluator('mpuccs',
                     n_cols=[1, 2, 3],           # 僅 1, 2, 3 欄位組合
                     min_entropy_delta=0.1,      # 積極剪枝
                     field_decay_factor=0.3,     # 大組合強衰減
                     numeric_precision=2)         # 數值 2 位小數

evaluator.create()
results = evaluator.eval({
    'ori': original_data,
    'syn': synthetic_data
})
```

### 跳躍模式配置
```python
# 跳過 2 欄位組合，僅評估 1 和 3 欄位組合
evaluator = Evaluator('mpuccs', n_cols=[1, 3])
evaluator.create()
results = evaluator.eval({
    'ori': original_data,
    'syn': synthetic_data
})
```

## 輸出結果

### Global 結果
```python
{
    'total_syn_records': 1000,              # 合成資料總記錄數
    'total_ori_records': 1000,              # 原始資料總記錄數
    'total_identified': 150,                # 成功識別記錄數
    'identification_rate': 0.15,            # 基本識別率
    'weighted_identification_rate': 0.12,   # 加權識別率
    'total_combinations_checked': 45,       # 評估的組合總數
    'total_combinations_pruned': 12,        # 演算法剪枝的組合數
    'config_n_cols': '[1, 2, 3]',          # 使用的配置
    'config_min_entropy_delta': 0.1,       # 使用的熵閾值
    'config_field_decay_factor': 0.5,      # 使用的衰減因子
    'config_renyi_alpha': 2.0,             # Rényi alpha 參數
    'config_numeric_precision': 2,          # 應用的數值精度
    'config_datetime_precision': 'D'        # 應用的日期時間精度
}
```

### Details 結果
```python
[
    {
        'combo_size': 2,                    # 組合中的欄位數
        'syn_idx': 42,                      # 合成資料索引
        'field_combo': "('age', 'income')", # 使用的欄位組合
        'value_combo': "(25, 50000)",       # 造成碰撞的值
        'ori_idx': 123                      # 對應的原始資料索引
    },
    # ... 更多碰撞記錄
]
```

### Tree 結果
```python
[
    {
        'check_order': 1,                   # 處理順序
        'combo_size': 2,                    # 組合大小
        'field_combo': "('age', 'income')", # 欄位組合
        'base_combo': "('age',)",           # 熵計算的基礎組合
        'base_is_pruned': False,            # 基礎是否被剪枝
        'combo_entropy': 0.85,              # 正規化 Rényi 熵
        'base_entropy': 0.72,               # 基礎組合熵
        'entropy_gain': 0.13,               # 相對基礎的熵增益
        'is_pruned': False,                 # 此組合是否被剪枝
        'mpuccs_cnt': 5,                    # 找到的唯一組合數
        'mpuccs_collision_cnt': 3,          # 成功碰撞數
        'field_weighted': 0.5,              # 基於欄位的加權
        'total_weighted': 0.5,              # 應用的總加權
        'weighted_mpuccs_collision_cnt': 1.5 # 加權碰撞計數
    },
    # ... 更多樹節點
]
```

## 效能特性

### 計算複雜度
- **時間複雜度**：最壞情況 O(2^k)，但有顯著剪枝
- **空間複雜度**：O(n*k)，其中 n 為記錄數，k 為欄位數
- **實際效能**：由於剪枝，在真實資料集上為線性到次二次方

### 擴展性
- **欄位擴展性**：透過剪枝具有高度擴展性 - 能高效處理具有許多欄位的資料集
- **記錄擴展性**：在 100K+ 記錄的資料集上測試過
- **記憶體效率**：基於 Counter 的操作最小化記憶體使用

### 與 Anonymeter 的比較
| 指標 | Anonymeter | mpUCCs | 改進 |
|------|------------|--------|------|
| 執行時間 (adult-income, n_cols=3) | 12+ 分鐘 | 44 秒 | 16x 更快 |
| 指認性攻擊檢測 | ~1,000-2,000 (隨機抽樣) | 7,999 (完整評估) | 完整覆蓋 |
| 理論基礎 | 啟發式 | 數學理論 | 堅實理論 |
| 風險高估 | 高 | 低 | 準確評估 |
| 進度可見性 | 不支援 | 全面 | 完全透明 |
| 精度處理 | 不支援 | 自動 | 更好可用性 |

## 最佳實踐

### 1. 配置選擇
- 使用預設設定以獲得最佳結果

### 2. 資料前處理
- 確保原始和合成資料間的資料型別一致
- 考慮數值和日期時間欄位的適當精度
- 一致地移除或處理缺失值

### 3. 結果解釋
- 專注於 `weighted_identification_rate` 進行實際風險評估
- 檢查 `details` 結果以了解特定漏洞
- 使用 `tree` 結果了解演算法決策和優化

### 4. 效能優化
- 使用跳躍模式（`n_cols=[1, 3]`）專注於特定組合大小
- 如需要，考慮欄位選擇以降低維度

## 限制與未來工作

### 目前限制
1. **實驗狀態**：仍在積極開發和驗證中
2. **記憶體使用**：對於非常高維度的資料可能記憶體密集
3. **風險加權**：合乎學理的風險加權方式正在研究中，目前僅設定為 field_decay_factor = 0.5

### 未來增強
1. **分散式計算**：支援大資料集的平行處理（nice-to-have）

## 參考文獻

1. Abedjan, Z., & Naumann, F. (2011). Advancing the discovery of unique column combinations. In Proceedings of the 20th ACM international conference on Information and knowledge management (pp. 1565-1570).

2. Mandros, P., Kaltenpoth, D., Boley, M., & Vreeken, J. (2020). Discovering Functional Dependencies from Mixed-Type Data. In Proceedings of the 26th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining (pp. 1404-1414).

3. Bläsius, T., Friedrich, T., Lischeid, J., Meeks, K., & Schirneck, M. (2017). Efficiently enumerating hitting sets of hypergraphs arising in data profiling. In Proceedings of the 16th International Symposium on Experimental Algorithms (pp. 130-145).

## 支援與回饋

作為實驗性功能，mpUCCs 正在積極開發和改進中。我們歡迎回饋、錯誤報告和改進建議。請參考專案的問題追蹤器來報告問題或請求功能。