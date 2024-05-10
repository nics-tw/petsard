<p align="center"><img width=75% src="docs/assets/images/PETsARD-logo.png"></p>


![Python 3.10](https://img.shields.io/badge/python-v3.10-blue.svg)
![Contributions welcome](https://img.shields.io/badge/contributions-welcome-orange.svg)
<!-- GitHub Issues number, build, dependency
TODO Git
-->


`PETsARD` (Privacy Enhancing Technologies Analysis, Research, and Development, /pəˈtɑrd/) is a Python library for facilitating data generation algorithm and their evaluation processes.

The main functionalities include dataset description, various dataset generation algorithms, and the measurements on privacy protection and utility.


`PETsARD`（隱私強化技術分析、研究與開發）是一套為了促進資料生成演算法及其評估過程而設計的 Python 程式庫。

其主要功能包括描述資料集、執行各種資料集生成算法，以及對隱私保護和效用進行測量。


- [Milestone](https://github.com/nics-tw/PETsARD/releases/latest)
    - The Milestone document provide detailed information about the latest version of `PETsARD`.
    - 里程碑文件包含了 `PETsARD` 最新版本的詳細資訊。
- [CHANGELOG.md](https://github.com/nics-tw/PETsARD/blob/main/CHANGELOG.md)
    - The Changelog document provide the changelog for understand the evolution of the `PETsARD` over time.
    - 歷史文件提供了提供了變更日誌，以便了解 `PETsARD` 隨時間演進的情況。
- [PETsARD - User Guide](https://nics-tw.github.io/PETsARD/)
    - The User Guide aims to assist developers in rapidly acquiring the necessary skills for utlisiing `PETsARD` in data synthesis, evaluating synthesized data, and enhancing the research efficiency in Privacy Enhancing Technologies-related fields.
    - 使用者指南旨在幫助開發者迅速獲得必要的技能，以使用 `PETsARD` 進行數據合成、合成數據的評估，以及提升開發者隱私增強相關領域的研究效率。


# Installation 安裝

This package has encountered dependency conflicts due to third-party packages, therefore we are unable to provide installation methods such as `requirements.txt`. However, the functionality within this package itself operates normally. We kindly request users to follow the `pip install` instructions below to set up their environment:

本套件因為有碰到第三方套件引起的相依性衝突，所以我們沒法提供如 `requirements.txt` 這類的安裝方式。但是，這套件裡面的功能本身是能正常運作的，麻煩使用者跟著下面的 `pip install` 指示來設定環境：

```bash
python -m pip install --upgrade pip
pip install smartnoise-synth==1.0.3
pip install ipykernel pyyaml==6.0.1 requests boto3 sdv==1.12.1 sdmetrics==0.14.0 anonymeter==1.0.0 git+https://github.com/ryan112358/private-pgm.git
```

The known conflicts are as follows. The primary cause is the dependencies of the current version of smartnoise:

已知的衝突如下。主因是 smartnoise 現有版本的相依性：

> \> pip install smartnoise-synth # Error can be ignored
>
> ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
> rdt 1.9.2 requires Faker<20,>=17, but you have faker 15.3.4 which is incompatible.

> \> pip install --upgrade torch # Error can be ignored
>
> ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
> smartnoise-synth 1.0.3 requires torch<2.0.0, but you have torch 2.2.1 which is incompatible.


# Getting Started 入門指南

We recommend that users write the experimental planning in [YAML format](https://nics-tw.github.io/PETsARD/YAML.html), which details in the [PETsARD - User Guide](https://nics-tw.github.io/PETsARD/), and use [Executor](https://nics-tw.github.io/PETsARD/Executor.html) in `PETsARD` to conduct the experiment.

我們建議使用者將自己的實驗規劃撰寫成 [YAML 格式](https://nics-tw.github.io/PETsARD/YAML.html)，呼叫 `PETsARD` 的 [Executor](https://nics-tw.github.io/PETsARD/Executor.html) 讀取執行實驗，以上的細節可參見 [PETsARD - User Guide](https://nics-tw.github.io/PETsARD/)。



## `Executor`

Here is the simplest way to get started with `PETsARD`:

以下是最簡單入門的 `PETsARD` 使用方式：

```Python
from PETsARD import Executor

filename = "Exec_Design.yaml"
exec = Executor(config=filename)
exec.run()
```


## YAML


Here, we use the default methods of each module to construct the simplest 'Exec_Design.yaml'. For specific settings of each module, please refer to the [YAML page](https://nics-tw.github.io/PETsARD/YAML.html).

這裡利用各模組的預設方法 (default) 建構最簡單的 'Exec_Design.yaml'，各模組具體設定，請參考 [YAML 頁面](https://nics-tw.github.io/PETsARD/YAML.html)。


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


## Modules 各模組

- `Loader`: The module for data loading, see [Loader page](https://nics-tw.github.io/PETsARD/Loader.html).
    - Benchmark datasets: The usage of `Loader` to download the benchmark datasets, see [Benchmark datasets page](https://nics-tw.github.io/PETsARD/Benchmark-datasets.html).
- `Splitter`: The module for splitting a dataset into training and validation datasets, see [Splitter page](https://nics-tw.github.io/PETsARD/Splitter.html).
- `Processor`: The module for data pre/postprocessing, see [Processor page](https://nics-tw.github.io/PETsARD/Processor.html).
- `Synthesizer`: The module for data synthesising, see [Synthesizer page](https://nics-tw.github.io/PETsARD/Synthesizer.html).
- `Evaluator`: The module for synthetic data evaluation, see [Evaluator page](https://nics-tw.github.io/PETsARD/Evaluator.html).
- `Describer`: The module for data description, see [Describer page](https://nics-tw.github.io/PETsARD/Describer.html).
- `Reporter`: The module for data saving and report output, see [Reporter page](https://nics-tw.github.io/PETsARD/Reporter.html).

<br>

- `Loader`：讀取資料的模組，見 [Loader 頁面](https://nics-tw.github.io/PETsARD/Loader.html)。
    - Benchmark datasets：如何利用 `Loader` 獲取預先載入的基準資料集，見 [Benchmark datasets 頁面](https://nics-tw.github.io/PETsARD/Benchmark-datasets.html)。
- `Splitter`：把資料切分成實驗組與控制組的模組，見 [Splitter 頁面](https://nics-tw.github.io/PETsARD/Splitter.html)。
- `Processor`：對資料進行前處理跟後處理的模組，見 [Processor 頁面](https://nics-tw.github.io/PETsARD/Processor.html)。
- `Synthesizer`：對資料做合成資料等隱私強化處理的模組，見 [Synthesizer 頁面](https://nics-tw.github.io/PETsARD/Synthesizer.html)。
- `Evaluator`：對合成資料結果做評估的模組，見 [Evaluator 頁面](https://nics-tw.github.io/PETsARD/Evaluator.html)。
- `Describer`：對資料本身做描述的模組，見 [Describer 頁面](https://nics-tw.github.io/PETsARD/Describer.html)。
- `Reporter`：對資料進行存檔、以及資料評估與描述輸出報告的模組，見 [Reporter 頁面](https://nics-tw.github.io/PETsARD/Reporter.html)。



# Contributing 貢獻

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. And please make sure to update tests as appropriate.

歡迎提交拉取請求。對於重大變更，請先開啟一個議題來討論您想做的改變。並請確保適當地更新測試。


# License 授權

Undefined 未定
<!--
TODO Defined License
-->


# Citation 引用

- `Synthesizer` module:
  - SDV - [sdv-dev/SDV](https://github.com/sdv-dev/SDV):
      - Patki, N., Wedge, R., & Veeramachaneni, K. (2016). The Synthetic Data Vault. IEEE International Conference on Data Science and Advanced Analytics (DSAA), 399–410. https://doi.org/10.1109/DSAA.2016.49
  - smartnoise - [opendp/smartnoise-sdk](https://github.com/opendp/smartnoise-sdk):
- `Evaluator` module:
  - Anonymeter - [statice/anonymeter](https://github.com/statice/anonymeter):
      - Giomi, M., Boenisch, F., Wehmeyer, C., & Tasnádi, B. (2023). A Unified Framework for Quantifying Privacy Risk in Synthetic Data. Proceedings of Privacy Enhancing Technologies Symposium. https://doi.org/10.56553/popets-2023-0055
  - SDMetrics - [sdv-dev/SDMetrics](https://github.com/sdv-dev/SDMetrics)

