# Synthesizer Module Functional Design

## 🎯 模組職責

Synthesizer 模組負責合成資料的生成，支援多種合成演算法和自訂合成器，為隱私保護資料分析提供高品質的合成資料集。

## 📁 模組結構

```
petsard/synthesizer/
├── __init__.py              # 模組匯出介面
├── synthesizer.py          # 主要合成器類別
├── custom_synthesizer.py   # 自訂合成器支援
├── base_synthesizer.py     # 基礎合成器抽象類別
└── utils.py                # 合成工具函數
```

## 🔧 核心設計原則

1. **演算法無關**: 支援多種合成演算法的統一介面
2. **可擴展性**: 易於整合新的合成方法和第三方套件
3. **品質保證**: 內建合成品質檢查和驗證機制
4. **隱私保護**: 確保合成過程的隱私保護特性

## 📋 公開 API

### Synthesizer 類別
```python
class Synthesizer:
    def __init__(self, method: str, **kwargs)
    def fit(self, data: pd.DataFrame) -> None
    def sample(self, n_samples: int) -> pd.DataFrame
    def get_metadata(self) -> dict
```

### CustomSynthesizer 類別
```python
class CustomSynthesizer(BaseSynthesizer):
    def __init__(self, module_path: str, class_name: str, **kwargs)
    def fit(self, data: pd.DataFrame) -> None
    def sample(self, n_samples: int) -> pd.DataFrame
    def validate_synthesizer(self) -> bool
```

### BaseSynthesizer 抽象類別
```python
class BaseSynthesizer(ABC):
    @abstractmethod
    def fit(self, data: pd.DataFrame) -> None
    @abstractmethod
    def sample(self, n_samples: int) -> pd.DataFrame
    def get_privacy_budget(self) -> float
    def get_synthesis_params(self) -> dict
```

### 工具函數
```python
def validate_synthesis_quality(original: pd.DataFrame, synthetic: pd.DataFrame) -> dict
def calculate_privacy_metrics(synthesizer: BaseSynthesizer) -> dict
def optimize_synthesis_params(data: pd.DataFrame, method: str) -> dict
```

## 🔄 與其他模組的互動

### 輸入依賴
- **Processor**: 接收預處理後的訓練資料
- **Loader**: 接收原始資料和元資料
- **使用者配置**: 合成參數和演算法選擇

### 輸出介面
- **Evaluator**: 提供合成資料供評估
- **Reporter**: 提供合成統計和元資料
- **檔案系統**: 儲存合成模型和資料

### 內部依賴
- **Utils**: 使用核心工具函數進行外部模組載入
  - `petsard.utils.load_external_module` 提供通用的外部模組載入功能
- **Demo Utils**: 使用 demo 特定的模組載入功能 (優先選擇)
  - `demo.utils.load_demo_module` 提供 demo 目錄的智能搜索
- **Metadater**: 使用公開介面進行資料處理和元資料管理

## 🎯 設計模式

### 1. Strategy Pattern
- **用途**: 支援不同的合成演算法
- **實現**: 可插拔的合成器實現

### 2. Factory Pattern
- **用途**: 根據方法名稱建立對應的合成器
- **實現**: SynthesizerFactory 類別

### 3. Template Method Pattern
- **用途**: 定義合成流程的通用步驟
- **實現**: BaseSynthesizer 定義抽象流程

### 4. Adapter Pattern
- **用途**: 整合第三方合成套件
- **實現**: CustomSynthesizer 作為適配器

## 📊 功能特性

### 1. 內建合成器
- **統計方法**: 基於統計分佈的合成
- **機器學習**: 基於 ML 模型的合成
- **深度學習**: GAN、VAE 等深度學習方法
- **差分隱私**: 支援差分隱私的合成方法

### 2. 自訂合成器支援
- **動態載入**: 支援外部合成器模組載入
- **介面驗證**: 確保自訂合成器符合介面規範
- **參數傳遞**: 靈活的參數配置機制
- **錯誤處理**: 完善的錯誤捕獲和報告

### 3. 品質控制
- **合成驗證**: 自動檢查合成資料品質
- **統計一致性**: 確保統計特性保持
- **隱私評估**: 評估隱私保護程度
- **效能監控**: 監控合成過程效能

### 4. 參數最佳化
- **自動調參**: 基於資料特性自動調整參數
- **網格搜尋**: 支援參數空間搜尋
- **交叉驗證**: 使用交叉驗證選擇最佳參數
- **早停機制**: 防止過度訓練

## 🔒 封裝原則

### 對外介面
- 統一的 Synthesizer 類別介面
- 標準化的配置參數格式
- 一致的錯誤訊息和日誌

### 內部實現
- 隱藏複雜的演算法實現細節
- 封裝第三方套件的差異性
- 統一的資料格式處理

## 🚀 使用範例

```python
# 使用內建合成器
synthesizer = Synthesizer('gaussian_copula', 
                         enforce_min_max_values=True,
                         enforce_rounding=True)
synthesizer.fit(training_data)
synthetic_data = synthesizer.sample(1000)

# 使用自訂合成器
custom_synthesizer = Synthesizer('custom',
                                module_path='my_synthesizers.advanced_gan',
                                class_name='AdvancedGAN',
                                epochs=100,
                                batch_size=32)
custom_synthesizer.fit(training_data)
synthetic_data = custom_synthesizer.sample(5000)

# 差分隱私合成
dp_synthesizer = Synthesizer('dp_gaussian',
                            epsilon=1.0,
                            delta=1e-5,
                            sensitivity=1.0)
dp_synthesizer.fit(sensitive_data)
private_synthetic_data = dp_synthesizer.sample(2000)

# 品質評估
quality_metrics = validate_synthesis_quality(original_data, synthetic_data)
print(f"統計相似度: {quality_metrics['statistical_similarity']}")
print(f"隱私風險: {quality_metrics['privacy_risk']}")
```

## 🔧 合成演算法支援

### 1. 統計方法
- **Gaussian Copula**: 基於高斯連結函數的合成
- **Bayesian Networks**: 貝氏網路結構學習
- **Marginal Distributions**: 邊際分佈保持合成
- **Correlation Preservation**: 相關性保持合成

### 2. 機器學習方法
- **Decision Trees**: 決策樹基礎合成
- **Random Forest**: 隨機森林合成
- **Clustering**: 聚類基礎合成
- **Ensemble Methods**: 集成方法合成

### 3. 深度學習方法
- **Generative Adversarial Networks (GANs)**: 對抗生成網路
- **Variational Autoencoders (VAEs)**: 變分自編碼器
- **Transformer Models**: 基於 Transformer 的合成
- **Diffusion Models**: 擴散模型合成

### 4. 隱私保護方法
- **Differential Privacy**: 差分隱私機制
- **k-Anonymity**: k-匿名化合成
- **l-Diversity**: l-多樣性保證
- **t-Closeness**: t-接近性維持

## 🔍 品質評估指標

### 1. 統計指標
- **分佈相似度**: KS 檢定、Wasserstein 距離
- **相關性保持**: 皮爾森、斯皮爾曼相關係數
- **邊際分佈**: 各欄位分佈比較
- **聯合分佈**: 多變數分佈一致性

### 2. 機器學習指標
- **預測效能**: 使用合成資料訓練模型的效能
- **特徵重要性**: 特徵重要性排序一致性
- **模型泛化**: 跨資料集泛化能力
- **分類效能**: 分類任務效能比較

### 3. 隱私指標
- **成員推斷攻擊**: 抵抗成員推斷的能力
- **屬性推斷攻擊**: 抵抗屬性推斷的能力
- **重建攻擊**: 抵抗資料重建的能力
- **差分隱私預算**: 隱私預算消耗追蹤

## 📈 架構特點

### 外部模組載入架構
- **核心功能**: `petsard.utils.load_external_module` 提供通用的外部模組載入
- **Demo 特定功能**: `demo.utils.load_demo_module` 提供 demo 目錄智能搜索
- **智能回退**: CustomSynthesizer 優先使用 demo 功能，失敗時回退至核心功能
- **關注點分離**: 核心 utils 不包含 demo 特定的硬編碼路徑

### 設計特點
- **模組化設計**: 核心功能與 demo 特定功能完全分離
- **智能路徑解析**: demo.utils 提供多層目錄搜索支援
- **自訂合成器驗證**: 完善的驗證邏輯
- **參數傳遞機制**: 靈活的參數配置
- **記憶體效率**: 優化的記憶體使用
- **品質監控**: 完善的合成品質監控

### 架構優勢
- **可維護性**: demo 路徑邏輯集中在 demo/utils.py 中
- **可擴展性**: 新的 demo 目錄可以輕鬆添加到 demo/utils.py
- **向後相容**: 核心 API 保持不變
- **優雅降級**: 即使沒有 demo utils，核心功能仍然可用

## 📈 模組效益

1. **演算法多樣性**: 支援多種合成方法滿足不同需求
2. **可擴展性**: 易於整合新的合成演算法
3. **品質保證**: 內建品質評估確保合成效果
4. **隱私保護**: 提供多層次的隱私保護機制
5. **使用便利**: 統一介面降低使用複雜度

這個設計確保 Synthesizer 模組提供強大而靈活的合成能力，透過清晰的公開介面與其他模組協作，為 PETsARD 系統提供高品質的合成資料生成服務。