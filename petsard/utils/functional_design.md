# Utils Module Functional Design

## 🎯 模組職責

Utils 模組提供 PETsARD 系統的核心工具函數，特別是外部模組動態載入功能，為其他模組提供通用的工具支援。

## 📁 模組結構

```
petsard/utils.py                # 核心工具函數
```

## 🔧 核心設計原則

1. **通用性**: 提供通用的工具函數，不包含特定領域的邏輯
2. **獨立性**: 不依賴其他 PETsARD 模組，作為基礎工具層
3. **可擴展性**: 支援透過參數自定義行為
4. **錯誤處理**: 提供完善的錯誤捕獲和報告機制

## 📋 公開 API

### 外部模組載入函數
```python
def load_external_module(
    module_path: str,
    class_name: str,
    logger: logging.Logger,
    required_methods: dict[str, list[str]] = None,
    search_paths: list[str] = None,
) -> Tuple[Any, Type]:
    """
    載入外部 Python 模組並返回模組實例和類別

    Args:
        module_path: 模組路徑 (相對或絕對)
        class_name: 要載入的類別名稱
        logger: 日誌記錄器
        required_methods: 必需方法的字典映射
        search_paths: 額外的搜索路徑列表
    
    Returns:
        Tuple[模組實例, 類別]: 包含模組實例和類別的元組
    """
```

### 路徑解析函數
```python
def _resolve_module_path(
    module_path: str, 
    logger: logging.Logger, 
    search_paths: list[str] = None
) -> str:
    """
    解析模組路徑，嘗試多個搜索位置
    
    Args:
        module_path: 要解析的模組路徑
        logger: 日誌記錄器
        search_paths: 額外的搜索路徑
    
    Returns:
        str: 解析後的絕對路徑
    """
```

## 🔄 與其他模組的互動

### 輸出介面 (被其他模組使用)
- **CustomSynthesizer**: 使用 `load_external_module` 載入自定義合成器
- **CustomEvaluator**: 使用 `load_external_module` 載入自定義評估器
- **其他需要動態載入的模組**: 提供通用的模組載入功能

### 輸入依賴
- **標準函式庫**: importlib, os, sys, logging 等
- **無其他 PETsARD 模組依賴**: 作為基礎工具模組

## 🎯 設計模式

### 1. Utility Pattern
- **用途**: 提供靜態工具函數
- **實現**: 獨立的工具函數，無狀態

### 2. Strategy Pattern
- **用途**: 支援不同的路徑搜索策略
- **實現**: 透過 `search_paths` 參數自定義搜索行為

## 📊 功能特性

### 1. 路徑解析
- **絕對路徑支援**: 直接使用已存在的絕對路徑
- **相對路徑解析**: 相對於當前工作目錄解析
- **自定義搜索路徑**: 支援額外的搜索位置
- **智能搜索**: 按順序嘗試多個可能的位置

### 2. 模組載入
- **動態載入**: 運行時動態載入 Python 模組
- **類別驗證**: 確保指定的類別存在於模組中
- **方法驗證**: 驗證類別是否具有必需的方法和參數
- **錯誤處理**: 完善的錯誤捕獲和報告

### 3. 介面驗證
- **方法存在性檢查**: 確保類別具有必需的方法
- **方法可調用性檢查**: 確保方法是可調用的
- **參數簽名驗證**: 檢查方法參數是否符合要求
- **詳細錯誤報告**: 提供具體的錯誤信息

## 🔒 封裝原則

### 對外介面
- 簡潔的函數介面
- 清晰的參數定義
- 統一的錯誤處理

### 內部實現
- 隱藏複雜的路徑解析邏輯
- 封裝模組載入細節
- 統一的日誌記錄

## 🚀 使用範例

```python
import logging
from petsard.utils import load_external_module

# 設置日誌
logger = logging.getLogger(__name__)

# 基本使用 - 載入當前目錄的模組
try:
    module, cls = load_external_module(
        module_path='my_module.py',
        class_name='MyClass',
        logger=logger
    )
    instance = cls(config={'param': 'value'})
except Exception as e:
    logger.error(f"載入失敗: {e}")

# 進階使用 - 自定義搜索路徑
search_paths = [
    '/path/to/custom/modules',
    './external_modules',
    '../shared_modules'
]

try:
    module, cls = load_external_module(
        module_path='advanced_module.py',
        class_name='AdvancedClass',
        logger=logger,
        search_paths=search_paths,
        required_methods={
            '__init__': ['config'],
            'process': ['data'],
            'validate': []
        }
    )
    instance = cls(config={'advanced': True})
except Exception as e:
    logger.error(f"載入失敗: {e}")
```

## 🔍 搜索路徑邏輯

### 預設搜索順序
1. **直接路徑**: 使用提供的 module_path
2. **當前工作目錄**: os.path.join(cwd, module_path)
3. **自定義路徑**: search_paths 參數中的所有路徑

### 路徑解析規則
- 如果是絕對路徑且檔案存在，直接使用
- 按順序嘗試每個搜索路徑
- 找到第一個存在的檔案即停止搜索
- 如果都找不到，拋出 FileNotFoundError

## 📈 架構優勢

### 1. 關注點分離
- **核心功能**: 專注於通用的模組載入邏輯
- **無特定領域邏輯**: 不包含 demo 或其他特定用途的硬編碼

### 2. 可擴展性
- **參數化設計**: 透過參數控制行為
- **搜索路徑自定義**: 支援任意的搜索路徑配置
- **方法驗證可選**: 可選的介面驗證功能

### 3. 錯誤處理
- **詳細錯誤信息**: 提供具體的失敗原因
- **搜索路徑報告**: 列出所有嘗試的路徑
- **分層錯誤處理**: 不同類型的錯誤有不同的處理

### 4. 日誌記錄
- **調試信息**: 詳細的調試日誌
- **錯誤記錄**: 完整的錯誤日誌
- **進度追蹤**: 載入過程的進度記錄

## 📈 與 Demo Utils 的協作

### 分工原則
- **petsard.utils**: 提供通用的核心功能
- **demo.utils**: 提供 demo 特定的搜索路徑和邏輯

### 協作模式
```python
# demo.utils.load_demo_module 的實現
def load_demo_module(module_path, class_name, logger, required_methods=None):
    # 生成 demo 特定的搜索路徑
    demo_search_paths = _get_demo_search_paths(module_path)
    
    # 使用核心功能進行載入
    return load_external_module(
        module_path=module_path,
        class_name=class_name,
        logger=logger,
        required_methods=required_methods,
        search_paths=demo_search_paths
    )
```

## 📈 效益

1. **模組化設計**: 清晰的職責分離，核心功能與特定用途分開
2. **可重用性**: 通用的工具函數可被多個模組使用
3. **可維護性**: 集中的工具函數易於維護和更新
4. **可測試性**: 獨立的函數易於單元測試
5. **可擴展性**: 參數化設計支援多種使用場景

這個設計確保 Utils 模組提供穩定、通用的工具支援，同時保持架構的清潔和模組化原則。