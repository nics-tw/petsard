# PETsARD 專案上下文配置

## 🎯 專案概述

PETsARD (Privacy Enhancing Technologies Synthetic and Real Data) 是一個隱私增強技術的合成資料生成與評估框架。

## 🏗️ 核心架構原則

### 1. 模組化設計
- **職責分離**: 每個模組都有明確的職責邊界
- **統一介面**: 模組間透過公開 API 進行互動
- **可組合性**: 模組可以靈活組合使用

### 2. 函數式程式設計
- **純函數**: 核心業務邏輯使用純函數實現
- **不可變資料**: 使用 `@dataclass(frozen=True)` 確保資料不可變
- **函數組合**: 支援管線式的資料處理流程

### 3. 型別安全
- **強型別檢查**: 所有公開介面都有完整的型別註解
- **編譯時檢查**: 利用 mypy 等工具進行靜態型別檢查
- **清晰介面**: 明確的輸入輸出型別定義

### 4. 向後相容性
- **API 穩定性**: 公開 API 保持向後相容
- **適配器模式**: 使用適配器處理版本差異
- **漸進式升級**: 支援逐步遷移到新版本

## 📁 模組架構

### Loader 模組 (資料載入)
```python
# 職責：統一的資料載入介面
from petsard.loader import Loader, Splitter
loader = Loader(filepath="data.csv")
data, metadata = loader.load()  # 回傳 (data, metadata) 元組
```

### Metadater 模組 (詮釋資料管理核心)
```python
# 職責：三層架構的詮釋資料管理
from petsard.metadater import Metadater
schema = Metadater.create_schema(data, "schema_id")  # Schema 層
field = Metadater.create_field(series, "field_name")  # Field 層
metadata = Metadater.create_metadata("dataset_id")   # Metadata 層
```

### Evaluator 模組 (品質評估)
```python
# 職責：多維度的合成資料品質評估
from petsard.evaluator import Evaluator
evaluator = Evaluator(method="anonymeter")
evaluator.create()
results = evaluator.eval({"ori": original_data, "syn": synthetic_data})
```

### 其他核心模組
- **Processor**: 資料前處理和轉換
- **Synthesizer**: 合成資料生成
- **Reporter**: 結果報告和匯出
- **Constrainer**: 約束條件管理

## 🔧 開發規範

### 1. 代碼結構規範
```python
# 標準模組結構
@dataclass
class ModuleConfig(BaseConfig):
    """模組配置類別，繼承 BaseConfig"""
    pass

class Module:
    """主要模組類別"""
    def __init__(self, config: ModuleConfig):
        self.config = config
    
    def main_method(self) -> ReturnType:
        """主要功能方法，明確的回傳型別"""
        pass
```

### 2. API 設計規範
- **統一命名**: create/analyze/validate 等動詞前綴
- **型別註解**: 所有公開方法都要有完整型別註解
- **文檔字串**: 使用 Google 風格的 docstring
- **錯誤處理**: 明確的異常類型和錯誤訊息

### 3. 測試規範
- **單元測試**: 每個公開方法都要有對應測試
- **整合測試**: 模組間互動的測試
- **型別測試**: 使用 mypy 進行型別檢查

## 📋 開發檢查清單

### 修改現有模組時
- [ ] 檢查對應的 `.ai/functional_design/` 文檔
- [ ] 確認 API 變更不會破壞向後相容性
- [ ] 更新相關的型別註解
- [ ] 執行相關的單元測試
- [ ] 更新文檔和使用範例

### 新增功能時
- [ ] 遵循現有的架構設計原則
- [ ] 實現對應的配置類別
- [ ] 添加完整的型別註解
- [ ] 撰寫單元測試
- [ ] 更新功能設計文檔

### 發佈前檢查
- [ ] 所有測試通過
- [ ] 型別檢查通過
- [ ] 文檔更新完成
- [ ] 向後相容性確認
- [ ] 效能影響評估

## 🎯 品質標準

### 代碼品質
- **可讀性**: 清晰的命名和結構
- **可維護性**: 模組化和低耦合
- **可測試性**: 純函數和依賴注入
- **效能**: 合理的時間和空間複雜度

### 文檔品質
- **完整性**: 所有公開 API 都有文檔
- **準確性**: 文檔與實際實現一致
- **實用性**: 包含具體的使用範例
- **時效性**: 隨代碼變更及時更新

這個專案上下文將幫助所有開發者理解 PETsARD 的架構設計和開發規範，確保團隊協作的一致性。