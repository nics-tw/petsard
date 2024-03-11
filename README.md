# PETsARD

PETsARD (Privacy Enhancing Technologies Analysis, Research, and Development) is a Python library for facilitates data generation algorithm and their evaluation processes.

PETsARD（隱私強化技術分析、研究與開發）是一套為了增進資料生成演算法及其評估過程而設計的 Python 程式庫。

The main functionalities include dataset description, various dataset generation algorithms, and the measurements on privacy protection and utility.

其主要功能包括描述資料集、執行各種資料集生成算法，以及對隱私保護和效用進行測量。


# Installation 安裝

This package has encountered dependency conflicts due to third-party packages, therefore we are unable to provide installation methods such as `requirements.txt`. However, the functionality within this package itself operates normally. We kindly request users to follow the `pip install` instructions below to set up their environment:

本套件因為有碰到第三方套件引起的相依性衝突，所以我們沒法提供如 `requirements.txt` 這類的安裝方式。但是，這套件裡面的功能本身是能正常運作的，麻煩使用者跟著下面的 `pip install` 指示來設定環境：

```bash
python -m pip install --upgrade pip
pip install ipykernel
pip install pyyaml==6.0.1
pip install boto3==1.34.58
pip install sdv==1.10.0
pip install smartnoise-synth==1.0.3 # Error can be ignored
pip install anonymeter==1.0.0
pip install git+https://github.com/ryan112358/private-pgm.git
pip install --upgrade torch==2.2.1 # Error can be ignored
pip install requests==2.31.0
```

The known conflicts are as follows. The primary cause is the dependencies of the current version of smartnoise:

已知的衝突如下。主因是 smartnoise 現有版本的相依性：

> > pip install smartnoise-synth # Error can be ignored
> ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
> rdt 1.9.2 requires Faker<20,>=17, but you have faker 15.3.4 which is incompatible.

> > pip install --upgrade torch # Error can be ignored
> ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
> smartnoise-synth 1.0.3 requires torch<2.0.0, but you have torch 2.2.1 which is incompatible.


# Getting Started 入門指南

We recommend that users refer to the [PETsARD-Gitbook manual](https://nics-tw.github.io/PETsARD/) for their experimental planning, write it in [YAML format](https://nics-tw.github.io/PETsARD/YAML.html), and then call the `Executor` of `PETsARD` to read it (also refer to [Executor page](https://nics-tw.github.io/PETsARD/Executor.html)):

我們建議使用者將自己的實驗規劃參考 [PETsARD-Gitbook 手冊](https://nics-tw.github.io/PETsARD/)說明，撰寫成 [YAML 格式](https://nics-tw.github.io/PETsARD/YAML.html)後，呼叫 `PETsARD` 的 `Executor` 讀取即可（同時參見 [Executor 頁面](https://nics-tw.github.io/PETsARD/Executor.html)）：



### `Executor`

Here is the simplest way to get started with `PETsARD`:

以下是最簡單入門的 `PETsARD` 使用方式：

```python
from PETsARD import Executor

filename = 'Exec_Design.yaml'
exec = Executor(config=filename)
exec.run()
```


### YAML


Here, we use the default methods of each module to construct the simplest 'Exec_Design.yaml'. For specific settings of each module, please refer to the [YAML page](https://nics-tw.github.io/PETsARD/YAML.html).

這裡利用各模組的預設方法 (default) 建構最簡單的 'Exec_Design.yaml'，各模組具體設定，請參考 [YAML 頁面](https://nics-tw.github.io/PETsARD/YAML.html)。


```
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
```

# Contributing 貢獻

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. And please make sure to update tests as appropriate.

歡迎提交拉取請求。對於重大變更，請先開啟一個議題來討論您想做的改變。並請確保適當地更新測試。


# License 授權

Undefined 未定


# Citation 引用

Undefined 未定


> The format of version number follows [Semantic Versioning](https://semver.org/).
>
> 版本號格式依照[語意化版本](https://semver.org/lang/zh-TW/)規則設定。