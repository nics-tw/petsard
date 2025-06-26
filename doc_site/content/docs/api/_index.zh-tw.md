---
title: API 文件
type: docs
weight: 50
prev: docs/best-practices
next: docs/developer-guide
sidebar:
  open: false
---


## API 參考概覽

| 模組 | 物件名稱 | 建立方法 | 主要方法 |
|------|----------|----------|----------|
| [Executor](./executor) | `Executor` | `Executor(config)` | `run()`, `get_result()`, `get_timing()` |
| [Loader](./loader) | `Loader` | `Loader(filepath, **kwargs)` | `load()` |
| [Metadater](./metadater) | `Metadater` | `Metadater.create_schema()` | `create_schema()`, `validate_schema()` |
| [Splitter](./splitter) | `Splitter` | `Splitter(**kwargs)` | `split()` |
| [Processor](./processor) | `Processor` | `Processor(metadata, config)` | `fit()`, `transform()`, `inverse_transform()` |
| [Synthesizer](./synthesizer) | `Synthesizer` | `Synthesizer(**kwargs)` | `create()`, `fit_sample()` |
| [Constrainer](./constrainer) | `Constrainer` | `Constrainer(config)` | `apply()`, `resample_until_satisfy()` |
| [Evaluator](./evaluator) | `Evaluator` | `Evaluator(**kwargs)` | `create()`, `eval()` |
| [Describer](./describer) | `Describer` | `Describer(**kwargs)` | `create()`, `eval()` |
| [Reporter](./reporter) | `Reporter` | `Reporter(method, **kwargs)` | `create()`, `report()` |
| [Operator](./operator) | `*Operator` | `*Operator(config)` | `run()`, `set_input()`, `get_result()` |
| [Config](./config) | `Config` | `Config(config_dict)` | 初始化時自動處理 |
| [Status](./status) | `Status` | `Status(config)` | `put()`, `get_result()`, `create_snapshot()` |
| [Utils](./utils) | 函式 | 直接匯入 | `load_external_module()` |

## 配置與執行
- [Executor](./executor) - 實驗管線的主要介面

## 資料管理
- [Metadater](./metadater) - 資料集架構和詮釋資料管理

## 管線組件
- [Loader](./loader) - 資料載入和處理
- [Splitter](./splitter) - 實驗資料分割
- [Processor](./processor) - 資料前處理和後處理
- [Synthesizer](./synthesizer) - 合成資料生成
- [Constrainer](./constrainer) - 合成資料的資料約束處理器
- [Evaluator](./evaluator) - 隱私、保真度和效用評估
- [Describer](./describer) - 描述性資料摘要
- [Reporter](./reporter) - 結果匯出和報告

## 系統組件
- [Operator](./operator) - 所有模組的標準化執行包裝器
- [Config](./config) - 實驗配置管理
- [Status](./status) - 管線狀態和進度追蹤
- [Utils](./utils) - 核心工具函式和外部模組載入