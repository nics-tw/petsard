---
title: 入門指南
type: docs
weight: 2
prev: docs
next: docs/tutorial
---

## 安裝

PETsARD 已發布至 PyPI，可根據您的需求選擇不同的依賴群組進行安裝。您也可以使用 `pyproject.toml` 或 `requirements.txt` 從原始碼安裝。

### PyPI 安裝（推薦）

```bash
# 基本安裝（僅配置解析功能）
pip install petsard

# 資料科學功能（推薦給大多數使用者）
pip install petsard[ds]

# 完整安裝，包含開發工具
pip install petsard[all]

# 僅開發工具
pip install petsard[dev]
```

### 安裝選項

| 群組 | 指令 | 包含功能 |
|------|------|----------|
| **預設** | `pip install petsard` | 配置、讀檔、合成、評測的基本功能（pyyaml、pandas、anonymeter、sdmetrics、sdv、torch 等） |
| **資料科學** | `pip install petsard[ds]` | 基本功能 + Jupyter Notebook 支援（ipykernel、jupyterlab、notebook 等） |
| **完整** | `pip install petsard[all]` | 資料科學功能 + 延伸支援（基準資料集下載、Excel 檔案支援） |
| **開發** | `pip install petsard[dev]` | 測試與開發工具（pytest、ruff、coverage 等） |

### 原始碼安裝

用於開發或自訂建置：

```bash
# 複製儲存庫
git clone https://github.com/nics-tw/petsard.git
cd petsard

# 使用 pyproject.toml 安裝
pip install -e ".[all]"

# 或使用 requirements.txt 安裝（基於預設安裝）
pip install -r requirements.txt
```

**開發推薦工具：**
* `pyenv` - Python 版本管理
* `poetry` / `uv` - 套件管理

### 離線環境準備

對於無法連接網路的環境，我們提供了輪子下載工具來預先準備所有依賴套件：

```bash
# 僅下載核心依賴套件
python demo/petsard_wheel_downloader.py --branch main --python-version 3.11 --os linux

# 下載額外的依賴群組
python demo/petsard_wheel_downloader.py --branch main --python-version 3.11 --os linux --groups ds
```

**參數說明：**
- `--branch`：Git 分支名稱（如：main, dev）
- `--python-version`：Python 版本（如：3.10, 3.11, 3.11.5）
- `--os`：目標作業系統，支援：
  - `linux`：Linux 64位元
  - `windows`：Windows 64位元
  - `macos`：macOS Intel
  - `macos-arm`：macOS Apple Silicon
- `--groups`：可選的依賴群組（可用空格分隔指定多個群組）

## 快速開始

PETsARD 是一個隱私強化資料合成與評估框架。要開始使用 PETsARD：

1. 建立最簡單的 YAML 設定檔：
   ```yaml
   # config.yaml
   Loader:
       demo:
           method: 'default'  # 使用 Adult Income 資料集
   Synthesizer:
       demo:
           method: 'default'  # 使用 SDV Gaussian Copula
   Reporter:
       output:
           method: 'save_data'
           output: 'result'
           source: 'Synthesizer'
   ```

2. 使用兩行程式碼執行：
   ```python
   from petsard import Executor


   exec = Executor(config='config.yaml')
   exec.run()
   ```

## 基本設定

這是一個使用預設設定的完整範例。此設定會：

1. 載入 Adult Income 示範資料集
2. 自動判斷資料型別並套用適當的前處理
3. 使用 SDV 的 Gaussian Copula 方法生成合成資料
4. 使用 SDMetrics 評估基本品質指標與隱私度量
5. 儲存合成資料與評估報告

```yaml
Loader:
    demo:
        method: 'default'
Preprocessor:
    demo:
        method: 'default'
Synthesizer:
    demo:
        method: 'default'
Postprocessor:
    demo:
        method: 'default'
Evaluator:
    demo:
        method: 'default'
Reporter:
    save_data:
        method: 'save_data'
        output: 'demo_result'
        source: 'Postprocessor'
    save_report:
        method: 'save_report'
        output: 'demo_report'
        eval: 'demo'
        granularity: 'global'
```

## 下一步

* 查看教學區段以獲取詳細範例
* 查看 API 文件以取得完整模組參考
* 探索基準資料集進行測試
* 在 GitHub 儲存庫中檢視範例設定