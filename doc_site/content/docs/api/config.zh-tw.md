---
title: Config
type: docs
weight: 62
prev: docs/api/operator
next: docs/api/status
---

```python
Config(config)
```

Config 類別管理實驗配置並為 PETsARD 管線建立操作器執行流程。它解析配置字典、驗證設定，並生成操作器佇列進行順序執行。

## 設計概覽

Config 系統將宣告式配置轉換為可執行的管線流程。它處理模組排序、實驗命名和操作器實例化，同時提供驗證和錯誤檢查。

### 核心原則

1. **宣告式配置**：透過結構化字典定義實驗
2. **自動流程生成**：將配置轉換為可執行的操作器序列
3. **驗證**：全面的配置驗證和錯誤報告
4. **靈活性**：支援複雜實驗配置和自訂命名

## 參數

- `config` (dict)：定義實驗管線的配置字典

## 配置結構

配置遵循階層結構：

```python
{
    "ModuleName": {
        "experiment_name": {
            "parameter1": "value1",
            "parameter2": "value2"
        }
    }
}
```

### 配置範例

```python
config_dict = {
    "Loader": {
        "load_data": {
            "filepath": "data.csv"
        }
    },
    "Splitter": {
        "split_data": {
            "train_split_ratio": 0.8,
            "num_samples": 3
        }
    },
    "Synthesizer": {
        "generate": {
            "method": "sdv",
            "model": "GaussianCopula"
        }
    },
    "Evaluator": {
        "evaluate": {
            "method": "sdmetrics"
        }
    },
    "Reporter": {
        "report": {
            "method": "save_report",
            "granularity": "global"
        }
    }
}
```

## 屬性

### 核心屬性

- `config` (queue.Queue)：準備執行的實例化操作器佇列
- `module_flow` (queue.Queue)：對應每個操作器的模組名稱佇列
- `expt_flow` (queue.Queue)：對應每個操作器的實驗名稱佇列
- `sequence` (list)：執行順序的模組名稱列表
- `yaml` (dict)：處理後的配置字典

## 方法

### 配置處理

Config 類別在初始化期間自動處理配置：

1. **驗證**：檢查無效的實驗命名模式
2. **Splitter 展開**：處理多樣本分割配置
3. **操作器建立**：為每個實驗實例化操作器
4. **流程生成**：使用深度優先搜尋建立執行佇列

## 特殊處理

### Splitter 配置

Config 類別為具有多個樣本的 Splitter 配置提供特殊處理：

```python
# 原始配置
"Splitter": {
    "split_data": {
        "train_split_ratio": 0.8,
        "num_samples": 3
    }
}

# 自動展開為：
"Splitter": {
    "split_data_[3-1]": {"train_split_ratio": 0.8, "num_samples": 1},
    "split_data_[3-2]": {"train_split_ratio": 0.8, "num_samples": 1},
    "split_data_[3-3]": {"train_split_ratio": 0.8, "num_samples": 1}
}
```

### 實驗命名規則

- 實驗名稱不能以 `_[xxx]` 模式結尾（保留供內部使用）
- 每個實驗名稱在其模組內必須唯一
- 名稱用於結果追蹤和報告

## 使用範例

### 基本配置

```python
from petsard.config import Config

# 簡單管線配置
config_dict = {
    "Loader": {
        "load_data": {"filepath": "benchmark://adult-income"}
    },
    "Synthesizer": {
        "generate": {"method": "sdv", "model": "GaussianCopula"}
    }
}

config = Config(config_dict)

# 存取配置屬性
print(f"模組序列: {config.sequence}")
print(f"操作器數量: {config.config.qsize()}")
```

### 複雜多模組配置

```python
from petsard.config import Config

config_dict = {
    "Loader": {
        "load_benchmark": {"method": "default"},
        "load_custom": {"filepath": "custom_data.csv"}
    },
    "Preprocessor": {
        "preprocess": {"method": "default"}
    },
    "Splitter": {
        "split_train_test": {
            "train_split_ratio": 0.8,
            "num_samples": 5
        }
    },
    "Synthesizer": {
        "sdv_gaussian": {"method": "sdv", "model": "GaussianCopula"},
        "sdv_ctgan": {"method": "sdv", "model": "CTGAN"}
    },
    "Evaluator": {
        "evaluate_all": {"method": "sdmetrics"}
    },
    "Reporter": {
        "save_results": {
            "method": "save_data",
            "source": "Synthesizer"
        },
        "generate_report": {
            "method": "save_report",
            "granularity": "global"
        }
    }
}

config = Config(config_dict)
```

### 與 Executor 整合

```python
from petsard.config import Config
from petsard.executor import Executor

# Config 通常與 Executor 一起使用
config = Config(config_dict)
executor = Executor(config)
executor.run()
```

## 驗證和錯誤處理

### 配置驗證

Config 類別執行多項驗證檢查：

- **命名驗證**：確保實驗名稱不使用保留模式
- **結構驗證**：驗證適當的配置階層
- **參數驗證**：委託給個別操作器進行參數檢查

### 錯誤類型

- `ConfigError`：無效配置結構或命名違規時引發
- 模組特定錯誤：從個別操作器初始化傳播

## 架構優勢

### 1. 關注點分離
- **配置解析**：處理結構和驗證
- **操作器管理**：建立和組織執行單元
- **流程控制**：管理執行序列和相依性

### 2. 靈活性
- **多個實驗**：支援每個模組的多個實驗
- **複雜管線**：處理任意模組組合
- **自訂配置**：可擴展的參數系統

### 3. 驗證
- **早期錯誤檢測**：在執行前捕獲配置問題
- **清晰錯誤訊息**：詳細的除錯回饋
- **一致驗證**：跨所有模組的標準化驗證

### 4. 整合
- **Executor 相容性**：與執行系統的無縫整合
- **Status 管理**：與 Status 追蹤系統相容
- **操作器抽象**：對底層操作器的清潔介面

Config 系統為 PETsARD 靈活且強健的實驗配置提供基礎，透過簡單的宣告式規格實現複雜的資料處理管線。