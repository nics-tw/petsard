# PETsARD 架構規則與開發提醒

## 🏗️ 架構規則

### 1. 模組間依賴規則

```
依賴方向 (允許的依賴關係):
Executor → All Modules
Reporter → Evaluator, Metadater
Evaluator → Metadater, Utils
Synthesizer → Metadater, Utils
Processor → Metadater, Utils
Loader → Metadater, Utils
Constrainer → Metadater, Utils
Metadater → (無依賴，作為基礎模組)
Utils → (無依賴，作為工具模組)
```

**禁止的循環依賴**:
- Metadater 不能依賴其他 PETsARD 模組
- Utils 不能依賴其他 PETsARD 模組
- 任何模組都不能形成循環依賴

### 2. 公開 API 設計規則

#### 統一的方法命名規範
```python
# 建立物件
create_*()     # 建立新物件
analyze_*()    # 分析和推斷
validate_*()   # 驗證和檢查

# 資料處理
load()         # 載入資料
process()      # 處理資料
transform()    # 轉換資料
eval()         # 評估資料
```

#### 回傳值規範
```python
# Loader 模組
def load() -> tuple[pd.DataFrame, SchemaMetadata]:
    """統一回傳 (data, metadata) 元組"""

# Evaluator 模組  
def _eval(self, data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """統一回傳 dict[str, pd.DataFrame] 格式"""

# Metadater 模組
def create_schema(data: pd.DataFrame, schema_id: str) -> SchemaMetadata:
    """回傳強型別的 SchemaMetadata 物件"""
```

## 🔔 自動化開發提醒

### 當修改 `petsard/loader/` 時

**必須檢查**:
- [ ] `.ai/functional_design/loader.md` 是否需要更新
- [ ] API 變更是否影響向後相容性
- [ ] 與 Metadater 的整合是否正常
- [ ] `load()` 方法的回傳格式是否一致

**架構檢查**:
```python
# ✅ 正確的 API 設計
class Loader:
    def load(self) -> tuple[pd.DataFrame, SchemaMetadata]:
        # 使用 Metadater 進行詮釋資料處理
        schema = Metadater.create_schema(data, schema_id)
        return data, schema

# ❌ 錯誤的設計 - 不應該直接操作內部結構
class Loader:
    def load(self) -> pd.DataFrame:
        # 直接回傳 DataFrame，缺少詮釋資料
        return data
```

### 當修改 `petsard/metadater/` 時

**必須檢查**:
- [ ] `.ai/functional_design/metadater.md` 是否需要更新
- [ ] 三層架構 (Metadata/Schema/Field) 的完整性
- [ ] 函數式設計原則的遵循
- [ ] 不可變資料結構的使用

**架構檢查**:
```python
# ✅ 正確的不可變設計
@dataclass(frozen=True)
class FieldMetadata:
    def with_stats(self, stats: FieldStats) -> "FieldMetadata":
        return replace(self, stats=stats)

# ❌ 錯誤的設計 - 可變狀態
class FieldMetadata:
    def set_stats(self, stats: FieldStats) -> None:
        self.stats = stats  # 違反不可變原則
```

### 當修改 `petsard/evaluator/` 時

**必須檢查**:
- [ ] `.ai/functional_design/evaluator.md` 是否需要更新
- [ ] 新的評估器是否繼承 `BaseEvaluator`
- [ ] 評估結果格式是否一致
- [ ] 是否正確使用 Metadater 進行資料處理

**架構檢查**:
```python
# ✅ 正確的評估器設計
class CustomEvaluator(BaseEvaluator):
    def _eval(self, data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        # 實現具體的評估邏輯
        return {"global": results_df}

# ❌ 錯誤的設計 - 不繼承基底類別
class CustomEvaluator:
    def evaluate(self, data):  # 缺少型別註解
        return data  # 回傳格式不一致
```

### 當修改 `petsard/synthesizer/` 時

**必須檢查**:
- [ ] 是否正確使用 `SchemaMetadata` 進行詮釋資料管理
- [ ] SDV 轉換邏輯是否與 Metadater 架構整合
- [ ] 合成資料的格式是否與原始資料一致

### 當修改 `petsard/processor/` 時

**必須檢查**:
- [ ] 是否使用 Metadater 的型別推斷功能
- [ ] 處理後的資料是否更新詮釋資料
- [ ] 處理管線是否支援函數式組合

## 🚨 常見架構違規

### 1. 直接內部呼叫
```python
# ❌ 錯誤 - 直接呼叫內部方法
from petsard.metadater.field.field_functions import build_field_metadata

# ✅ 正確 - 使用公開 API
from petsard.metadater import Metadater
field = Metadater.create_field(series, "field_name")
```

### 2. 循環依賴
```python
# ❌ 錯誤 - Metadater 依賴其他模組
from petsard.loader import Loader  # 在 metadater 模組中

# ✅ 正確 - 其他模組依賴 Metadater
from petsard.metadater import Metadater  # 在 loader 模組中
```

### 3. 型別不一致
```python
# ❌ 錯誤 - 回傳型別不一致
def load() -> pd.DataFrame:  # 缺少詮釋資料

# ✅ 正確 - 統一的回傳格式
def load() -> tuple[pd.DataFrame, SchemaMetadata]:
```

## 📋 代碼審查檢查清單

### API 設計檢查
- [ ] 方法命名遵循統一規範
- [ ] 回傳型別符合模組規範
- [ ] 型別註解完整且正確
- [ ] 文檔字串完整

### 架構設計檢查
- [ ] 模組依賴方向正確
- [ ] 沒有循環依賴
- [ ] 使用公開 API 而非內部實現
- [ ] 遵循設計模式

### 品質檢查
- [ ] 單元測試覆蓋
- [ ] 型別檢查通過
- [ ] 向後相容性確認
- [ ] 效能影響評估

## 🎯 最佳實踐

### 1. 使用統一的配置模式
```python
@dataclass
class ModuleConfig(BaseConfig):
    """所有模組配置都繼承 BaseConfig"""
    module_specific_param: str = "default"
    
    def __post_init__(self):
        super().__post_init__()
        # 模組特定的驗證邏輯
```

### 2. 實現清晰的錯誤處理
```python
from petsard.exceptions import PETsARDError

class ModuleSpecificError(PETsARDError):
    """模組特定的異常類型"""
    pass

def method_with_error_handling():
    try:
        # 業務邏輯
        pass
    except SpecificError as e:
        raise ModuleSpecificError(f"具體的錯誤描述: {e}")
```

### 3. 保持函數式設計
```python
# ✅ 純函數設計
def calculate_stats(data: pd.Series, config: StatsConfig) -> FieldStats:
    """純函數：相同輸入總是產生相同輸出"""
    return FieldStats(...)

# ❌ 避免副作用
def calculate_stats_with_side_effect(data: pd.Series):
    global_state.update(data)  # 副作用
    return stats
```

這些架構規則確保 PETsARD 保持清晰、一致的設計，讓所有開發者都能遵循統一的標準。