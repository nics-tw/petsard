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

## 框架結構

PETsARD 依照以下流程運作：

1. `Loader`：從檔案或基準資料集載入資料
2. `Splitter`：將資料分割成訓練/驗證集（選用）
3. `Preprocessor`：準備資料進行合成（如：類別值編碼）
4. `Synthesizer`：創建隱私強化的合成資料
5. `Postprocessor`：將合成資料格式化回原始結構
6. `Evaluator`：測量合成品質與隱私指標
7. `Describer`：產生資料集統計與分析
8. `Reporter`：儲存結果並產生報告

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