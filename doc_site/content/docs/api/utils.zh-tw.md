---
title: Utils
type: docs
weight: 65
prev: docs/api/status
next: docs/api
---

```python
petsard.utils
```

PETsARD 系統的核心工具函數，提供外部模組載入和其他常用操作的基本工具。

## 設計概述

Utils 模組提供 PETsARD 系統中使用的通用工具函數。它遵循關注點分離的原則，提供核心功能而不包含特定領域的邏輯。

### 核心原則

1. **通用性**: 提供通用的工具函數，不包含特定領域的邏輯
2. **獨立性**: 不依賴其他 PETsARD 模組，作為基礎工具層
3. **可擴展性**: 支援透過參數自定義行為
4. **錯誤處理**: 提供完善的錯誤捕獲和報告機制

## 函數

### `load_external_module()`

```python
load_external_module(module_path, class_name, logger, required_methods=None, search_paths=None)
```

載入外部 Python 模組並返回模組實例和類別。

**參數**

- `module_path` (str): 外部模組的路徑 (相對或絕對)
- `class_name` (str): 要從模組載入的類別名稱
- `logger` (logging.Logger): 用於記錄訊息的日誌記錄器
- `required_methods` (dict[str, list[str]], 可選): 方法名稱對應必需參數名稱的字典
- `search_paths` (list[str], 可選): 解析模組路徑時嘗試的額外搜索路徑

**回傳值**

- `Tuple[Any, Type]`: 包含模組實例和類別的元組

**例外**

- `FileNotFoundError`: 如果模組檔案不存在
- `ConfigError`: 如果無法載入模組或模組不包含指定的類別

## 使用範例

### 基本使用

```python
import logging
from petsard.utils import load_external_module

# 設置日誌記錄器
logger = logging.getLogger(__name__)

# 從當前目錄載入模組
try:
    module, cls = load_external_module(
        module_path='my_module.py',
        class_name='MyClass',
        logger=logger
    )
    instance = cls(config={'param': 'value'})
except Exception as e:
    logger.error(f"載入失敗: {e}")
```

### 使用自定義搜索路徑的進階用法

```python
import logging
from petsard.utils import load_external_module

logger = logging.getLogger(__name__)

# 自定義搜索路徑
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

## 路徑解析邏輯

### 預設搜索順序

1. **直接路徑**: 直接使用提供的 module_path
2. **當前工作目錄**: os.path.join(cwd, module_path)
3. **自定義路徑**: search_paths 參數中的所有路徑

### 解析規則

- 如果是絕對路徑且檔案存在，直接使用
- 按順序嘗試每個搜索路徑
- 找到第一個存在的檔案即停止
- 如果都找不到，拋出 FileNotFoundError

## 架構優勢

### 1. 關注點分離
- **核心功能**: 專注於通用的模組載入邏輯
- **無特定領域邏輯**: 不包含 demo 或其他特定用途的硬編碼

### 2. 可擴展性
- **參數化設計**: 透過參數控制行為
- **自定義搜索路徑**: 支援任意的搜索路徑配置
- **可選方法驗證**: 可選的介面驗證功能

### 3. 錯誤處理
- **詳細錯誤信息**: 提供具體的失敗原因
- **搜索路徑報告**: 列出所有嘗試的路徑
- **分層錯誤處理**: 不同類型的錯誤有不同的處理

### 4. 日誌記錄
- **調試信息**: 詳細的調試日誌
- **錯誤記錄**: 完整的錯誤日誌
- **進度追蹤**: 載入過程的進度記錄

## 與 Demo Utils 的協作

### 職責分工
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

## 效益

1. **模組化設計**: 清晰的職責分離，核心功能與特定用途分開
2. **可重用性**: 通用的工具函數可被多個模組使用
3. **可維護性**: 集中的工具函數易於維護和更新
4. **可測試性**: 獨立的函數易於單元測試
5. **可擴展性**: 參數化設計支援多種使用場景

這個設計確保 Utils 模組提供穩定、通用的工具支援，同時保持架構的清潔和模組化原則。