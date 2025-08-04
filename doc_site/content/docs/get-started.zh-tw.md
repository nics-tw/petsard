---
title: 入門指南
type: docs
weight: 2
prev: docs
next: docs/tutorial
---

## 安裝

*以下我們展示 Python 原生環境的設定方式。不過，為了更好的依賴套件管理，我們推薦使用：*

**推薦工具：**
* `pyenv` - Python 版本管理
* `poetry` / `uv` - 套件管理

### Python 原生環境設定

1. 建立並啟動虛擬環境：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或是
   venv\Scripts\activate     # Windows
   ```

2. 升級 pip：
   ```bash
   python -m pip install --upgrade pip
   ```

3. 安裝必要套件：
   ```bash
   pip install -r requirements.txt
   ```

### 離線環境準備

對於無法連接網路的環境，我們提供了輪子下載工具來預先準備所有依賴套件：

```bash
# 僅下載核心依賴套件
python demo/petsard_wheel_downloader.py --branch main --python-version 3.11 --os linux

# 下載額外的依賴群組
python demo/petsard_wheel_downloader.py --branch main --python-version 3.11 --os linux --groups pytorch jupyter
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
  - `pytorch`：PyTorch 和 CUDA 相關套件，用於深度學習
  - `jupyter`：Jupyter Notebook 和 IPython 套件，用於互動式開發
  - `dev`：開發工具如 pytest、ruff 等實用工具

**依賴群組範例：**

```bash
# 僅下載核心依賴套件
python demo/petsard_wheel_downloader.py --branch main --python-version 3.11 --os linux

# 下載 PyTorch 支援
python demo/petsard_wheel_downloader.py --branch main --python-version 3.11 --os linux --groups pytorch

# 下載 Jupyter 支援
python demo/petsard_wheel_downloader.py --branch main --python-version 3.11 --os linux --groups jupyter

# 下載多個群組
python demo/petsard_wheel_downloader.py --branch main --python-version 3.11 --os linux --groups pytorch jupyter

# 下載所有可用群組
python demo/petsard_wheel_downloader.py --branch main --python-version 3.11 --os linux --groups pytorch jupyter dev
```

此工具會下載 PETsARD 及其所有依賴項的輪子檔案，並產生詳細的安裝日誌。

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