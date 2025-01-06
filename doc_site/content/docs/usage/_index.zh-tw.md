---
title: Usage
type: docs
weight: 10
prev: design-structure
next: docs/usage/01_Executor
sidebar:
  open: true
---

## 安裝

要安裝本套件，請依照以下步驟使用 `requirements.txt` 檔案來設定您的環境：

1. 建立虛擬環境並啟動：

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or 或是
venv\Scripts\activate     # Windows
```

2. 升級 pip：

```bash
python -m pip install --upgrade pip
```

3. 使用 `requirements.txt` 安裝所需套件：

```bash
pip install -r requirements.txt
```

## 入門指南

我們建議使用者將自己的實驗規劃撰寫成 [YAML 格式](https://nics-tw.github.io/petsard/YAML.html)，呼叫 `PETsARD` 的 [Executor](https://nics-tw.github.io/petsard/Executor.html) 讀取執行實驗，以上的細節可參見 [PETsARD - User Guide](https://nics-tw.github.io/petsard/)。

### `Executor`

以下是最簡單入門的 `PETsARD` 使用方式：

```Python
from petsard import Executor

filename = "Exec_Design.yaml"
exec = Executor(config=filename)
exec.run()
```

### YAML

這裡利用各模組的預設方法 (default) 建構最簡單的 'Exec_Design.yaml'，各模組具體設定，請參考 [YAML 頁面](https://nics-tw.github.io/petsard/YAML.html)。

```YAML
---
Loader:
  demo:
    # default of Loader is Adult Income dataset
    method: 'default'
Preprocessor:
  demo:
    # default of Preprocessor automatically determines the data type
    #   and uses the corresponding method.
    method: 'default'
Synthesizer:
  demo:
    # default of Synthesizer is SDV Gaussian Copula
    method: 'default'
Postprocessor:
  # make sure the expt_name of Postprocessor is same as the Preprocessor
  demo:
    method: 'default'
Evaluator:
  demo:
    # defalut of Evaluator is SDMetrics QualityReport
    method: 'default'
Reporter:
  save_data:
    method: 'save_data'
    output: 'YAML Demo'
    # source of Reporter means which result of module/expt_name should Reporter use
    #   accept string (for only one) and list of string (for multiple result)
    source: 'Postprocessor'
  save_report_global:
    method: 'save_report'
    output: 'YAML Demo'
    # eval in Reporter means which
    #   expt_name of Evaluator/Describer should Reporter use
    eval: 'demo'
    # granularity = 'global' indicates that
    #   the scoring covers the entire dataset with a comprehensive level of detail.
    granularity: 'global'
...
```

### 模組

- `Loader`：讀取資料的模組，見 [Loader 頁面](https://nics-tw.github.io/petsard/Loader.html)。
  - Benchmark datasets：如何利用 `Loader` 獲取預先載入的基準資料集，見 [Benchmark datasets 頁面](https://nics-tw.github.io/petsard/Benchmark-datasets.html)。
- `Splitter`：把資料切分成實驗組與控制組的模組，見 [Splitter 頁面](https://nics-tw.github.io/petsard/Splitter.html)。
- `Processor`：對資料進行前處理跟後處理的模組，見 [Processor 頁面](https://nics-tw.github.io/petsard/Processor.html)。
- `Synthesizer`：對資料做合成資料等隱私強化處理的模組，見 [Synthesizer 頁面](https://nics-tw.github.io/petsard/Synthesizer.html)。
- `Evaluator`：對合成資料結果做評估的模組，見 [Evaluator 頁面](https://nics-tw.github.io/petsard/Evaluator.html)。
- `Describer`：對資料本身做描述的模組，見 [Describer 頁面](https://nics-tw.github.io/petsard/Describer.html)。
- `Reporter`：對資料進行存檔、以及資料評估與描述輸出報告的模組，見 [Reporter 頁面](https://nics-tw.github.io/petsard/Reporter.html)。
