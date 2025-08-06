# Adapter 模組功能設計文件

## 🎯 模組職責

Adapter 模組提供統一的適配器介面，將各個功能模組（Loader、Processor、Synthesizer 等）封裝為可執行的適配器，負責模組間的資料流轉、狀態管理和執行協調。

## 📋 核心功能

### 1. 統一適配器介面
- **BaseAdapter**: 定義所有適配器的基礎介面
- **執行協調**: 統一的執行流程和錯誤處理
- **輸入設定**: 標準化的輸入資料設定機制
- **結果管理**: 統一的結果取得和元資料管理

### 2. 模組封裝
- **LoaderAdapter**: 資料載入適配器
- **SplitterAdapter**: 資料分割適配器
- **PreprocessorAdapter**: 資料前處理適配器
- **SynthesizerAdapter**: 資料合成適配器
- **PostprocessorAdapter**: 資料後處理適配器
- **ConstrainerAdapter**: 約束條件適配器
- **EvaluatorAdapter**: 資料評估適配器
- **DescriberAdapter**: 資料描述適配器
- **ReporterAdapter**: 結果報告適配器

### 3. 資料流管理
- **依賴解析**: 自動解析模組間的資料依賴關係
- **資料傳遞**: 安全的資料在模組間傳遞
- **狀態同步**: 保持執行狀態的一致性
- **元資料追蹤**: 追蹤資料變換過程中的元資料變化

### 4. 統一計時系統
- **自動計時**: 透過 logging 機制自動記錄執行時間
- **時間追蹤**: 記錄每個適配器的開始、結束和持續時間
- **錯誤計時**: 支援錯誤情況下的計時記錄
- **解耦設計**: 適配器保持獨立，不依賴外部狀態管理

## 🏗️ 架構設計

### 設計模式
- **Template Method Pattern**: BaseAdapter 定義執行模板
- **Strategy Pattern**: 不同適配器實作不同策略
- **Adapter Pattern**: 將功能模組適配為適配器介面
- **Decorator Pattern**: 為適配器添加日誌和錯誤處理

### 核心類別架構

#### BaseAdapter 抽象基類
```python
class BaseAdapter:
    """適配器基礎介面"""
    
    def __init__(self, config: dict)
    def run(self, input: dict)                    # 模板方法（包含自動計時）
    def _run(self, input: dict)                   # 具體實作
    def set_input(self, status) -> dict           # 輸入設定
    def get_result(self)                          # 結果取得
    def get_metadata(self) -> SchemaMetadata      # 元資料取得
```

#### 統一計時機制
```python
def run(self, input: dict):
    """執行適配器並自動記錄時間"""
    start_time = time.time()
    
    # 記錄開始時間
    self._logger.info(f"TIMING_START|{self.module_name}|run|{start_time}")
    self._logger.info(f"Starting {self.module_name} execution")
    
    try:
        # 執行具體邏輯
        self._run(input)
        
        # 記錄成功結束
        end_time = time.time()
        duration = end_time - start_time
        self._logger.info(f"TIMING_END|{self.module_name}|run|{end_time}|{duration}")
        self._logger.info(f"Completed {self.module_name} execution (elapsed: {timedelta(seconds=round(duration))})")
        
    except Exception as e:
        # 記錄錯誤結束
        end_time = time.time()
        duration = end_time - start_time
        self._logger.info(f"TIMING_ERROR|{self.module_name}|run|{end_time}|{duration}|{str(e)}")
        raise
```

#### 具體適配器類別
```python
class LoaderAdapter(BaseAdapter):
    """資料載入適配器"""
    def __init__(self, config: dict)
    def _run(self, input: dict)
    def set_input(self, status) -> dict
    def get_result(self) -> pd.DataFrame
    def get_metadata(self) -> SchemaMetadata

class SynthesizerAdapter(BaseAdapter):
    """資料合成適配器"""
    def __init__(self, config: dict)
    def _run(self, input: dict)
    def set_input(self, status) -> dict
    def get_result(self) -> pd.DataFrame
```

## 🔄 與 Metadater 整合

### 元資料類型統一
- **舊版**: `petsard.loader.Metadata`
- **新版**: `petsard.metadater.SchemaMetadata`

### 整合優勢
- **型別安全**: 使用 SchemaMetadata 提供強型別檢查
- **功能增強**: 利用 Metadater 的豐富功能
- **統一介面**: 所有適配器使用相同的元資料格式
- **向後相容**: 保持現有 API 的相容性

### 具體改動
```python
# 舊版
from petsard.loader import Metadata
def get_metadata(self) -> Metadata: ...

# 新版
from petsard.metadater import SchemaMetadata
def get_metadata(self) -> SchemaMetadata: ...
```

## 📊 公開 API

### BaseAdapter API
```python
# 基礎適配器介面
adapter = SomeAdapter(config_dict)
adapter.run(input_dict)                    # 執行適配器
result = adapter.get_result()              # 取得執行結果
metadata = adapter.get_metadata()          # 取得元資料
input_dict = adapter.set_input(status)     # 設定輸入資料
```

### 適配器生命週期
```python
# 1. 建立適配器
adapter = LoaderAdapter({'method': 'csv', 'path': 'data.csv'})

# 2. 設定輸入
input_data = adapter.set_input(status)

# 3. 執行適配器
adapter.run(input_data)

# 4. 取得結果
data = adapter.get_result()
metadata = adapter.get_metadata()

# 5. 更新狀態
status.put(module_name, expt_name, adapter)
```

## 🔧 使用範例

### 基本適配器使用
```python
from petsard.adapter import LoaderAdapter, SynthesizerAdapter
from petsard.config import Status, Config

# 建立配置和狀態
config = Config(yaml_config)
status = Status(config)

# 使用 LoaderAdapter
loader_adapter = LoaderAdapter({'method': 'csv', 'path': 'data.csv'})
loader_input = loader_adapter.set_input(status)
loader_adapter.run(loader_input)

# 更新狀態
status.put('Loader', 'load_data', loader_adapter)

# 使用 SynthesizerAdapter
synth_adapter = SynthesizerAdapter({'method': 'sdv', 'model': 'GaussianCopula'})
synth_input = synth_adapter.set_input(status)  # 自動從 status 取得前一步的資料
synth_adapter.run(synth_input)

# 取得結果
synthetic_data = synth_adapter.get_result()
```

### 自定義適配器
```python
class CustomAdapter(BaseAdapter):
    """自定義適配器範例"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.custom_processor = CustomProcessor(**config)
    
    def _run(self, input: dict):
        """實作具體執行邏輯"""
        self._logger.debug("開始自定義處理")
        self.result = self.custom_processor.process(input['data'])
        self._logger.debug("自定義處理完成")
    
    def set_input(self, status) -> dict:
        """設定輸入資料"""
        pre_module = status.get_pre_module("Custom")
        return {'data': status.get_result(pre_module)}
    
    def get_result(self):
        """取得處理結果"""
        return self.result
    
    def get_metadata(self) -> SchemaMetadata:
        """取得元資料"""
        return self.custom_processor.get_metadata()
```

### 錯誤處理和日誌
```python
class RobustAdapter(BaseAdapter):
    """具備完善錯誤處理的適配器"""
    
    @BaseAdapter.log_and_raise_config_error
    def set_input(self, status) -> dict:
        """使用裝飾器處理配置錯誤"""
        if 'required_param' not in self.config:
            raise ValueError("缺少必要參數")
        return {'data': status.get_result('PreviousModule')}
    
    def _run(self, input: dict):
        """執行時記錄詳細日誌"""
        self._logger.info("開始處理資料")
        try:
            # 處理邏輯
            self.result = self._process_data(input['data'])
            self._logger.info("資料處理成功")
        except Exception as e:
            self._logger.error(f"處理失敗: {str(e)}")
            raise
```

## 🧪 測試策略

### 單元測試
- 各適配器的獨立功能測試
- 輸入設定邏輯測試
- 結果和元資料取得測試
- 錯誤處理機制測試

### 整合測試
- 適配器間資料流轉測試
- 狀態管理整合測試
- 完整工作流程測試
- 元資料一致性測試

### 測試範例
```python
import pytest
from petsard.adapter import LoaderAdapter
from petsard.config import Status, Config

def test_loader_adapter():
    """測試 LoaderAdapter 基本功能"""
    config = {'method': 'csv', 'path': 'test_data.csv'}
    adapter = LoaderAdapter(config)
    
    # 測試初始化
    assert adapter.config == config
    assert adapter.module_name == "LoaderAdapter"
    
    # 測試執行
    status = create_test_status()
    input_data = adapter.set_input(status)
    adapter.run(input_data)
    
    # 驗證結果
    result = adapter.get_result()
    metadata = adapter.get_metadata()
    
    assert isinstance(result, pd.DataFrame)
    assert isinstance(metadata, SchemaMetadata)
```

## 🔮 未來發展

### 功能增強
- **非同步執行**: 支援非同步適配器執行
- **批次處理**: 支援批次資料處理
- **快取機制**: 實作智慧快取減少重複計算
- **動態配置**: 支援執行時配置調整

### 效能最佳化
- **記憶體管理**: 最佳化大型資料集的記憶體使用
- **並行處理**: 支援適配器並行執行
- **資料流最佳化**: 最佳化模組間資料傳遞
- **懶載入**: 實作資料的懶載入機制

### 擴展性改善
- **插件系統**: 支援第三方適配器插件
- **配置範本**: 提供常用適配器配置範本
- **監控介面**: 提供適配器執行監控
- **除錯工具**: 提供適配器除錯和分析工具

## 📝 注意事項

### 設計原則
1. **統一介面**: 所有適配器遵循相同的介面規範
2. **單一職責**: 每個適配器專注於特定功能
3. **依賴注入**: 透過 Status 物件注入依賴
4. **錯誤處理**: 完善的錯誤捕獲和處理機制

### 最佳實踐
1. **日誌記錄**: 記錄詳細的執行過程和狀態變化
2. **資源管理**: 適當管理記憶體和系統資源
3. **型別檢查**: 使用型別提示和檢查
4. **文檔完整**: 為每個適配器提供完整文檔

### 常見問題
1. **依賴順序**: 確保適配器執行順序正確
2. **資料格式**: 確保模組間資料格式一致
3. **元資料同步**: 保持元資料在模組間的一致性
4. **記憶體洩漏**: 注意大型資料的記憶體管理

### 遷移指南
從舊版 Metadata 遷移到 SchemaMetadata：
```python
# 舊版
from petsard.loader import Metadata
metadata: Metadata = adapter.get_metadata()

# 新版
from petsard.metadater import SchemaMetadata
metadata: SchemaMetadata = adapter.get_metadata()

# API 使用基本保持不變，但內部實作使用 Metadater