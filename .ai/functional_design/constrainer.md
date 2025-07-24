# Constrainer Module Functional Design

## 🎯 模組職責

Constrainer 模組負責定義和執行資料約束條件，確保合成資料符合業務規則、邏輯一致性和現實世界的約束條件，提高合成資料的可用性和可信度。

## 📁 模組結構

```
petsard/constrainer/
├── __init__.py              # 模組匯出介面
├── constrainer.py          # 主要約束器類別
├── base_constraint.py      # 基礎約束抽象類別
├── constraints/            # 約束類型模組
│   ├── __init__.py
│   ├── statistical.py     # 統計約束
│   ├── logical.py          # 邏輯約束
│   ├── business.py         # 業務約束
│   ├── temporal.py         # 時間約束
│   └── relational.py       # 關聯約束
└── utils.py                # 約束工具函數
```

## 🔧 核心設計原則

1. **約束分離**: 將不同類型的約束分離管理
2. **可組合性**: 支援多個約束條件的組合和優先級管理
3. **靈活執行**: 支援軟約束和硬約束的不同執行策略
4. **效能最佳化**: 高效的約束檢查和修正機制

## 📋 公開 API

### Constrainer 類別
```python
class Constrainer:
    def __init__(self, constraints: list, enforcement_strategy: str = 'soft')
    def add_constraint(self, constraint: BaseConstraint) -> None
    def remove_constraint(self, constraint_id: str) -> None
    def apply_constraints(self, data: pd.DataFrame) -> pd.DataFrame
    def validate_constraints(self, data: pd.DataFrame) -> dict
    def get_constraint_violations(self, data: pd.DataFrame) -> list
```

### BaseConstraint 抽象類別
```python
class BaseConstraint(ABC):
    def __init__(self, constraint_id: str, priority: int = 1)
    
    @abstractmethod
    def check(self, data: pd.DataFrame) -> bool
    
    @abstractmethod
    def enforce(self, data: pd.DataFrame) -> pd.DataFrame
    
    def get_violation_details(self, data: pd.DataFrame) -> dict
    def get_constraint_description(self) -> str
```

### 約束類型類別
```python
class StatisticalConstraint(BaseConstraint):
    def __init__(self, column: str, constraint_type: str, **params)
    def check(self, data: pd.DataFrame) -> bool
    def enforce(self, data: pd.DataFrame) -> pd.DataFrame

class LogicalConstraint(BaseConstraint):
    def __init__(self, condition: str, columns: list)
    def check(self, data: pd.DataFrame) -> bool
    def enforce(self, data: pd.DataFrame) -> pd.DataFrame

class BusinessConstraint(BaseConstraint):
    def __init__(self, rule: str, affected_columns: list)
    def check(self, data: pd.DataFrame) -> bool
    def enforce(self, data: pd.DataFrame) -> pd.DataFrame
```

### 工具函數
```python
def create_constraint_from_data(data: pd.DataFrame, constraint_type: str) -> BaseConstraint
def optimize_constraint_order(constraints: list) -> list
def detect_constraint_conflicts(constraints: list) -> list
def generate_constraint_report(violations: list) -> dict
```

## 🔄 與其他模組的互動

### 輸入依賴
- **Synthesizer**: 接收合成資料進行約束檢查和修正
- **Processor**: 接收處理後的資料了解約束需求
- **Loader**: 接收原始資料分析約束模式

### 輸出介面
- **Synthesizer**: 提供約束修正後的資料
- **Evaluator**: 提供約束違反統計供評估
- **Reporter**: 提供約束執行報告

### 內部依賴
- **Metadater**: 使用公開介面進行資料分析
  - 統計計算和資料驗證
  - 型別推斷和結構分析

## 🎯 設計模式

### 1. Strategy Pattern
- **用途**: 支援不同的約束執行策略
- **實現**: 軟約束、硬約束、混合策略

### 2. Chain of Responsibility Pattern
- **用途**: 按優先級順序執行約束檢查
- **實現**: 約束鏈式處理機制

### 3. Command Pattern
- **用途**: 封裝約束操作為可執行命令
- **實現**: 約束執行和撤銷操作

### 4. Composite Pattern
- **用途**: 組合複雜的約束條件
- **實現**: 複合約束類別

## 📊 功能特性

### 1. 約束類型

#### 統計約束
- **範圍約束**: 數值範圍限制
- **分佈約束**: 統計分佈保持
- **唯一性約束**: 唯一值約束
- **完整性約束**: 非空值約束

#### 邏輯約束
- **條件約束**: if-then 邏輯規則
- **互斥約束**: 互斥條件限制
- **依賴約束**: 欄位間依賴關係
- **一致性約束**: 資料一致性規則

#### 業務約束
- **領域規則**: 特定領域的業務規則
- **合規約束**: 法規遵循要求
- **政策約束**: 組織政策限制
- **品質標準**: 資料品質要求

#### 時間約束
- **時序約束**: 時間順序限制
- **週期約束**: 週期性模式保持
- **持續性約束**: 時間持續性規則
- **同步約束**: 時間同步要求

#### 關聯約束
- **外鍵約束**: 參照完整性
- **聚合約束**: 聚合值一致性
- **比例約束**: 比例關係保持
- **平衡約束**: 資料平衡要求

### 2. 執行策略

#### 軟約束 (Soft Constraints)
- **最佳努力**: 盡可能滿足約束條件
- **優先級**: 按重要性順序執行
- **容錯性**: 允許部分違反
- **效能優化**: 平衡約束滿足和效能

#### 硬約束 (Hard Constraints)
- **強制執行**: 必須滿足所有約束
- **拒絕策略**: 拒絕不符合約束的資料
- **修正策略**: 自動修正違反約束的資料
- **回滾機制**: 無法修正時回滾操作

#### 混合策略
- **分層約束**: 不同層級的約束要求
- **動態調整**: 根據情況調整執行策略
- **權衡最佳化**: 在多個約束間找平衡
- **自適應**: 根據資料特性自適應調整

### 3. 約束檢查
- **即時檢查**: 資料生成過程中即時檢查
- **批次檢查**: 批次資料的約束驗證
- **增量檢查**: 僅檢查變更部分
- **並行檢查**: 多約束並行驗證

### 4. 違反處理
- **自動修正**: 自動修正可修正的違反
- **警告報告**: 報告無法修正的違反
- **統計追蹤**: 追蹤違反統計和趨勢
- **建議生成**: 提供改善建議

## 🔒 封裝原則

### 對外介面
- 統一的 Constrainer 類別介面
- 標準化的約束定義格式
- 清晰的違反報告結構

### 內部實現
- 隱藏複雜的約束執行邏輯
- 封裝不同約束類型的實現細節
- 統一的約束檢查機制

## 🚀 使用範例

```python
# 基本約束定義
constrainer = Constrainer([
    StatisticalConstraint('age', 'range', min_val=0, max_val=120),
    StatisticalConstraint('income', 'positive'),
    LogicalConstraint('age >= 18 OR student == False', ['age', 'student']),
    BusinessConstraint('manager_salary > employee_salary', ['manager_salary', 'employee_salary'])
], enforcement_strategy='soft')

# 應用約束
constrained_data = constrainer.apply_constraints(synthetic_data)

# 檢查約束違反
violations = constrainer.get_constraint_violations(synthetic_data)
print(f"發現 {len(violations)} 個約束違反")

# 複雜約束組合
complex_constrainer = Constrainer([
    # 統計約束
    StatisticalConstraint('salary', 'distribution', target_dist='lognormal'),
    StatisticalConstraint('id', 'unique'),
    
    # 邏輯約束
    LogicalConstraint('start_date <= end_date', ['start_date', 'end_date']),
    LogicalConstraint('age >= 16 IF employed == True', ['age', 'employed']),
    
    # 業務約束
    BusinessConstraint('total_amount == sum(item_amounts)', ['total_amount', 'item_amounts']),
    BusinessConstraint('credit_score BETWEEN 300 AND 850', ['credit_score']),
    
    # 時間約束
    TemporalConstraint('transaction_time', 'business_hours'),
    TemporalConstraint('events', 'chronological_order'),
    
    # 關聯約束
    RelationalConstraint('department_budget >= sum(employee_salaries)', 
                        ['department_budget', 'employee_salaries'])
], enforcement_strategy='mixed')

# 約束驗證報告
validation_report = constrainer.validate_constraints(data)
print(f"約束滿足率: {validation_report['satisfaction_rate']}")
print(f"關鍵違反: {validation_report['critical_violations']}")
```

## 🔧 約束定義語法

### 1. 統計約束
```python
# 範圍約束
StatisticalConstraint('age', 'range', min_val=0, max_val=120)
StatisticalConstraint('score', 'range', min_val=0, max_val=100)

# 分佈約束
StatisticalConstraint('income', 'distribution', target_dist='lognormal')
StatisticalConstraint('height', 'distribution', target_dist='normal', mean=170, std=10)

# 唯一性約束
StatisticalConstraint('id', 'unique')
StatisticalConstraint('email', 'unique')
```

### 2. 邏輯約束
```python
# 條件約束
LogicalConstraint('age >= 18 IF has_license == True', ['age', 'has_license'])
LogicalConstraint('salary > 0 IF employed == True', ['salary', 'employed'])

# 互斥約束
LogicalConstraint('NOT (student == True AND retired == True)', ['student', 'retired'])

# 依賴約束
LogicalConstraint('end_date > start_date', ['start_date', 'end_date'])
```

### 3. 業務約束
```python
# 計算約束
BusinessConstraint('total == price * quantity', ['total', 'price', 'quantity'])
BusinessConstraint('bmi == weight / (height^2)', ['bmi', 'weight', 'height'])

# 合規約束
BusinessConstraint('age >= 21 IF alcohol_purchase == True', ['age', 'alcohol_purchase'])
BusinessConstraint('gdpr_consent == True IF eu_resident == True', ['gdpr_consent', 'eu_resident'])
```

## 📊 約束執行報告

### 違反統計
```python
{
    'total_constraints': 15,
    'satisfied_constraints': 12,
    'violated_constraints': 3,
    'satisfaction_rate': 0.8,
    'critical_violations': 1,
    'warning_violations': 2,
    'violation_details': [
        {
            'constraint_id': 'age_range',
            'violation_type': 'range_exceeded',
            'affected_rows': [123, 456, 789],
            'severity': 'critical',
            'auto_corrected': False
        }
    ]
}
```

### 執行效能
```python
{
    'total_execution_time': 2.5,
    'constraint_execution_times': {
        'statistical_constraints': 0.8,
        'logical_constraints': 1.2,
        'business_constraints': 0.5
    },
    'rows_processed': 10000,
    'processing_rate': 4000  # rows/second
}
```

## 📈 最佳化策略

### 1. 約束順序最佳化
- **依賴分析**: 分析約束間的依賴關係
- **成本評估**: 評估約束檢查的計算成本
- **並行化**: 識別可並行執行的約束
- **快速失敗**: 優先執行容易失敗的約束

### 2. 記憶體最佳化
- **增量處理**: 僅處理變更的資料部分
- **分塊處理**: 大型資料集分塊處理
- **快取機制**: 快取約束檢查結果
- **懶載入**: 按需載入約束定義

### 3. 執行最佳化
- **向量化**: 使用向量化操作加速檢查
- **索引優化**: 建立適當的資料索引
- **預編譯**: 預編譯複雜的約束表達式
- **並行執行**: 多執行緒並行約束檢查

## 📈 效益

1. **資料品質**: 確保合成資料符合現實約束
2. **業務相關性**: 保持業務邏輯的一致性
3. **合規性**: 滿足法規和政策要求
4. **可信度**: 提高合成資料的可信度和可用性
5. **靈活性**: 支援多樣化的約束需求

這個設計確保 Constrainer 模組提供強大而靈活的約束管理能力，透過清晰的公開介面與其他模組協作，為 PETsARD 系統提供全面的資料約束和品質保證服務。