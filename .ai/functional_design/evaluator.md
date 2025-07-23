# Evaluator Module Functional Design

## 🎯 模組職責

Evaluator 模組負責評估合成資料的品質和隱私保護程度，提供多粒度的評估指標和全面的評估報告，確保合成資料的實用性和安全性。

## 📁 模組結構

```
petsard/evaluator/
├── __init__.py              # 模組匯出介面
├── evaluator.py            # 主要評估器類別
├── base_evaluator.py       # 基礎評估器抽象類別
├── metrics/                # 評估指標模組
│   ├── __init__.py
│   ├── statistical.py     # 統計指標
│   ├── privacy.py          # 隱私指標
│   ├── utility.py          # 效用指標
│   └── similarity.py       # 相似度指標
└── utils.py                # 評估工具函數
```

## 🔧 核心設計原則

1. **多粒度評估**: 支援 global、columnwise、pairwise 三種評估粒度
2. **指標豐富性**: 提供統計、隱私、效用等多維度評估指標
3. **可擴展性**: 易於添加新的評估指標和方法
4. **標準化輸出**: 統一的評估結果格式和報告結構

## 📋 公開 API

### Evaluator 類別
```python
class Evaluator:
    def __init__(self, granularity: str, **kwargs)
    def evaluate(self, original: pd.DataFrame, synthetic: pd.DataFrame) -> dict
    def get_supported_metrics(self) -> list
    def get_evaluation_summary(self) -> dict
```

### BaseEvaluator 抽象類別
```python
class BaseEvaluator(ABC):
    @abstractmethod
    def evaluate(self, original: pd.DataFrame, synthetic: pd.DataFrame) -> dict
    def validate_data(self, original: pd.DataFrame, synthetic: pd.DataFrame) -> bool
    def get_metric_descriptions(self) -> dict
```

### 指標類別
```python
class StatisticalMetrics:
    def calculate_distribution_similarity(self, original: pd.Series, synthetic: pd.Series) -> float
    def calculate_correlation_preservation(self, original: pd.DataFrame, synthetic: pd.DataFrame) -> float
    def calculate_statistical_tests(self, original: pd.Series, synthetic: pd.Series) -> dict

class PrivacyMetrics:
    def calculate_membership_inference_risk(self, original: pd.DataFrame, synthetic: pd.DataFrame) -> float
    def calculate_attribute_inference_risk(self, original: pd.DataFrame, synthetic: pd.DataFrame) -> float
    def calculate_reconstruction_risk(self, original: pd.DataFrame, synthetic: pd.DataFrame) -> float

class UtilityMetrics:
    def calculate_ml_utility(self, original: pd.DataFrame, synthetic: pd.DataFrame, task: str) -> dict
    def calculate_query_utility(self, original: pd.DataFrame, synthetic: pd.DataFrame) -> dict
    def calculate_downstream_task_performance(self, original: pd.DataFrame, synthetic: pd.DataFrame) -> dict
```

## 🔄 與其他模組的互動

### 輸入依賴
- **Synthesizer**: 接收合成資料
- **Processor**: 接收原始和處理後的資料
- **Loader**: 接收資料元資料和結構描述

### 輸出介面
- **Reporter**: 提供評估結果供報告生成
- **使用者**: 提供評估摘要和建議
- **檔案系統**: 儲存詳細評估報告

### 內部依賴
- **Utils**: 使用核心工具函數進行外部模組載入
  - `petsard.utils.load_external_module` 提供通用的外部模組載入功能
- **Demo Utils**: 使用 demo 特定的模組載入功能 (優先選擇)
  - `demo.utils.load_demo_module` 提供 demo 目錄的智能搜索
- **Metadater**: 使用公開介面進行資料分析
  - 統計計算和資料驗證
  - 型別推斷和結構分析

## 🎯 設計模式

### 1. Strategy Pattern
- **用途**: 支援不同的評估策略和指標
- **實現**: 可插拔的評估指標實現

### 2. Template Method Pattern
- **用途**: 定義評估流程的通用步驟
- **實現**: BaseEvaluator 定義抽象評估流程

### 3. Composite Pattern
- **用途**: 組合多個評估指標
- **實現**: MetricComposite 類別管理指標集合

### 4. Observer Pattern
- **用途**: 監控評估進度和結果
- **實現**: 評估事件通知機制

## 📊 功能特性

### 1. 多粒度評估

#### Global 評估
- **整體統計**: 資料集層級的統計指標
- **分佈比較**: 整體資料分佈相似度
- **隱私風險**: 整體隱私洩露風險評估
- **效用評估**: 整體資料效用評估

#### Columnwise 評估
- **逐欄位分析**: 每個欄位的詳細評估
- **型別特定指標**: 針對不同資料型別的專門指標
- **缺失值分析**: 缺失值模式比較
- **異常值檢測**: 異常值分佈比較

#### Pairwise 評估
- **欄位間相關性**: 兩兩欄位間的相關性保持
- **聯合分佈**: 雙變數聯合分佈比較
- **條件分佈**: 條件機率分佈分析
- **交互效應**: 欄位間交互作用保持

### 2. 評估指標體系

#### 統計指標
- **分佈相似度**: KS 檢定、Wasserstein 距離、Jensen-Shannon 散度
- **統計矩**: 均值、變異數、偏度、峰度比較
- **相關性**: 皮爾森、斯皮爾曼、肯德爾相關係數
- **假設檢定**: t 檢定、卡方檢定、Mann-Whitney U 檢定

#### 隱私指標
- **成員推斷攻擊**: 評估原始資料成員身份洩露風險
- **屬性推斷攻擊**: 評估敏感屬性推斷風險
- **重建攻擊**: 評估原始記錄重建風險
- **差分隱私**: 差分隱私保證程度評估
- **mpUCCs 指認性攻擊**: 基於最大部分唯一欄位組合的指認性風險評估

#### 效用指標
- **機器學習效用**: 使用合成資料訓練模型的效能
- **查詢效用**: SQL 查詢結果一致性
- **下游任務效能**: 特定應用任務效能比較
- **資料探索**: 資料探索和分析結果一致性

### 3. 品質評估
- **完整性檢查**: 資料完整性和一致性驗證
- **合理性驗證**: 合成資料的合理性檢查
- **範圍驗證**: 數值範圍和約束條件檢查
- **格式驗證**: 資料格式和結構驗證

## 🔒 封裝原則

### 對外介面
- 統一的 Evaluator 類別介面
- 標準化的評估結果格式
- 清晰的評估報告結構

### 內部實現
- 隱藏複雜的指標計算邏輯
- 封裝第三方評估套件
- 統一的資料預處理

## 🚀 使用範例

```python
# Global 評估
global_evaluator = Evaluator('global', 
                           metrics=['statistical', 'privacy', 'utility'])
global_results = global_evaluator.evaluate(original_data, synthetic_data)

# Columnwise 評估
columnwise_evaluator = Evaluator('columnwise',
                                metrics=['distribution_similarity', 'statistical_tests'],
                                columns=['age', 'income', 'education'])
columnwise_results = columnwise_evaluator.evaluate(original_data, synthetic_data)

# Pairwise 評估
pairwise_evaluator = Evaluator('pairwise',
                              metrics=['correlation', 'mutual_information'],
                              pairs=[('age', 'income'), ('education', 'income')])
pairwise_results = pairwise_evaluator.evaluate(original_data, synthetic_data)

# 自訂評估
custom_evaluator = Evaluator('global',
                           metrics=['custom_metric'],
                           custom_metric_func=my_custom_metric,
                           threshold=0.8)
custom_results = custom_evaluator.evaluate(original_data, synthetic_data)

# 評估摘要
summary = global_evaluator.get_evaluation_summary()
print(f"整體品質分數: {summary['overall_quality_score']}")
print(f"隱私風險等級: {summary['privacy_risk_level']}")
print(f"建議: {summary['recommendations']}")
```

## 📊 評估結果格式

### Global 評估結果
```python
{
    'granularity': 'global',
    'overall_score': 0.85,
    'statistical_metrics': {
        'distribution_similarity': 0.92,
        'correlation_preservation': 0.88,
        'statistical_tests': {...}
    },
    'privacy_metrics': {
        'membership_inference_risk': 0.15,
        'attribute_inference_risk': 0.12,
        'reconstruction_risk': 0.08
    },
    'utility_metrics': {
        'ml_utility': 0.89,
        'query_utility': 0.91,
        'downstream_performance': {...}
    },
    'recommendations': [...]
}
```

### Columnwise 評估結果
```python
{
    'granularity': 'columnwise',
    'column_results': {
        'age': {
            'distribution_similarity': 0.94,
            'statistical_tests': {...},
            'quality_score': 0.91
        },
        'income': {
            'distribution_similarity': 0.87,
            'statistical_tests': {...},
            'quality_score': 0.85
        }
    },
    'overall_columnwise_score': 0.88
}
```

### Pairwise 評估結果
```python
{
    'granularity': 'pairwise',
    'pair_results': {
        ('age', 'income'): {
            'correlation_preservation': 0.92,
            'mutual_information_preservation': 0.89,
            'joint_distribution_similarity': 0.86
        },
        ('education', 'income'): {
            'correlation_preservation': 0.88,
            'mutual_information_preservation': 0.85,
            'joint_distribution_similarity': 0.83
        }
    },
    'overall_pairwise_score': 0.87
}
```

## 🔬 mpUCCs 評估器

### 概述
mpUCCs (Maximal Partial Unique Column Combinations) 評估器是一個先進的指認性風險評估工具，基於最大部分唯一欄位組合理論，提供比傳統方法更準確的隱私風險評估。

### 理論基礎
- **mpUCCs = QIDs**: 最大部分唯一欄位組合等同於準識別符
- **指認性攻擊本質**: 在合成資料中找到唯一的欄位組合，且該組合在原始資料中也對應唯一記錄
- **避免高估風險**: 專注於最大形式組合，避免重複計算非最大形式的欄位組合

### 核心特性
1. **漸進式樹狀搜尋**: 使用基於熵的剪枝策略優化搜尋效率
2. **精度處理**: 支援數值和日期時間欄位的精度處理
3. **雙層進度追蹤**: 提供欄位層級和組合層級的詳細進度顯示
4. **熵增益剪枝**: 基於條件熵增益進行智能剪枝，提高演算法效率

### 配置參數
```python
{
    'eval_method': 'mpuccs',
    'n_cols': None,                    # 目標組合大小 (None/int/list)
    'min_entropy_delta': 0.0,          # 最小熵增益閾值
    'field_decay_factor': 0.5,         # 欄位衰減因子
    'renyi_alpha': 2.0,                # Rényi 熵參數 (碰撞熵)
    'numeric_precision': None,          # 數值精度 (自動偵測或手動設定)
    'datetime_precision': None          # 日期時間精度 (自動偵測或手動設定)
}
```

### 輸出結果
#### Global 結果
- `total_syn_records`: 合成資料總記錄數
- `total_identified`: 被識別的記錄數
- `identification_rate`: 識別率
- `weighted_identification_rate`: 加權識別率
- `total_combinations_checked`: 檢查的組合總數
- `total_combinations_pruned`: 被剪枝的組合數

#### Details 結果
- `combo_size`: 組合大小
- `syn_idx`: 合成資料索引
- `field_combo`: 欄位組合
- `value_combo`: 值組合
- `ori_idx`: 原始資料索引

#### Tree 結果
- `check_order`: 檢查順序
- `combo_size`: 組合大小
- `field_combo`: 欄位組合
- `combo_entropy`: 組合熵
- `entropy_gain`: 熵增益
- `is_pruned`: 是否被剪枝
- `mpuccs_cnt`: mpUCCs 數量
- `mpuccs_collision_cnt`: mpUCCs 碰撞數量
- `weighted_mpuccs_collision_cnt`: 加權 mpUCCs 碰撞數量

### 使用範例
```python
# 基本使用
evaluator = Evaluator('mpuccs')
evaluator.create()
results = evaluator.eval({
    'ori': original_data,
    'syn': synthetic_data
})

# 進階配置
evaluator = Evaluator('mpuccs',
                     n_cols=[1, 2, 3],
                     min_entropy_delta=0.1,
                     numeric_precision=2)
evaluator.create()
results = evaluator.eval({
    'ori': original_data,
    'syn': synthetic_data
})
```

## 🔍 評估流程

### 1. 資料驗證
- **格式檢查**: 確保資料格式一致性
- **結構驗證**: 驗證資料結構匹配
- **型別檢查**: 確保資料型別正確
- **完整性檢查**: 檢查資料完整性

### 2. 指標計算
- **統計指標**: 計算各種統計相似度指標
- **隱私指標**: 評估隱私洩露風險
- **效用指標**: 評估資料實用性
- **自訂指標**: 執行使用者定義的評估指標

### 3. 結果彙總
- **分數計算**: 計算各維度和整體分數
- **風險評估**: 評估隱私和品質風險
- **建議生成**: 基於評估結果生成改善建議
- **報告格式化**: 格式化評估結果供輸出

## 📈 效益

1. **全面評估**: 多維度、多粒度的完整評估體系
2. **標準化**: 統一的評估標準和結果格式
3. **可信度**: 科學嚴謹的評估方法和指標
4. **實用性**: 提供具體的改善建議和指導
5. **可擴展**: 易於添加新的評估指標和方法

這個設計確保 Evaluator 模組提供全面而準確的評估能力，透過清晰的公開介面與其他模組協作，為 PETsARD 系統提供可信的合成資料品質評估服務。