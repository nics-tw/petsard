---
title: "YAML"
draft: false
weight: 13
toc: true
---

YAML（YAML Ain't Markup Language）是一個可讀性高，用來表達資料序列化的格式，它旨在易於人類閱讀和編輯，同時也能被電腦輕鬆解析。`PETsARD` 的 `Executor` 讓使用者以 YAML 格式配置 `PETsARD` 的程式設定，藉由本文的介紹，期待讓使用者能以最快時間上手，無痛設定並執行自己的實驗，並利用 YAML 方便管理自己的實驗設定（同時參見 [Executor 頁面](PETsARD/zh-tw/docs/usage/01_executor/)）。

本文僅說明基本的 YAML 設定，建議搭配程式碼庫中 [demo/README.md](https://github.com/nics-tw/PETsARD/tree/main/demo) 的 `demo/User Story*.ipynb` 用戶故事情境範例、與 [yaml/README.md](https://github.com/nics-tw/PETsARD/tree/main/yaml)，幫助釐清您的需求如何實現（亦參考 [User Story 頁面](PETsARD/zh-tw/docs/usage/03_user-story/)）。

## 教學

以下是 YAML 範例以及對應的執行圖解。

```
Loader:
    adult-income:
        filepath: 'benchmark://adult-income'
        na_values:
            workclass: '?'
            occupation: '?'
            native-country: '?'
        column_types:
            category:
                - income
    bank-marketing-1:
        filepath: 'benchmark://bank-marketing-1'
    bank-marketing-2:
        filepath: 'benchmark://bank-marketing-2'
    nist-ma2019:
        filepath: 'benchmark://nist-ma2019'
        na_values: 'N'
Splitter:
    p80:
        num_samples: 5
        train_split_ratio: 0.8
Preprocessor:
    default-smartnoise:
        sequence:
            - 'missing'
            - 'outlier'
            - 'encoder'
            - 'scaler'
Synthesizer:
    smartnoise-dpctgan10:
        method: 'smartnoise-dpctgan'
        epsilon: 10.0
        epochs: 1000
        sigma: 1
        batch_size: 64
    smartnoise-dpctgan3:
        method: 'smartnoise-dpctgan'
        epsilon: 3.0
        epochs: 1000
        sigma: 1
        batch_size: 64
Postprocessor:
    default-smartnoise:
        method: 'default'
Evaluator:
    anonymeter-singlingout_5:
        method: 'anonymeter-singlingout'
        n_cols: 5
        max_attempts: 100000
    anonymeter-singlingout_10:
        method: 'anonymeter-singlingout'
        n_cols: 10
        max_attempts: 100000
    sdmetrics-diag:
        method: 'sdmetrics-diagnosticreport'
    sdmetrics-qual:
        method: 'sdmetrics-qualityreport'
    mlutility-cluster:
        method: 'mlutility-cluster'
        n_splits: 5
Reporter:
    save_data:
        method: 'save_data'
        output: 'exp_data'
        source:
            - 'Splitter'
            - 'Postprocessor'
    save_report_global:
        method: 'save_report'
        output: 'exp_global_report'
        granularity: 'global'
    save_report_columnwise:
        method: 'save_report'
        output: 'exp_col_report'
        granularity: 'columnwise'

```

<p align="center"><img src="/PETsARD/images/YAML_final.png" height="1080"></p>

值得注意的是，每個模組（圓角虛線範圍內）會被執行/創建多次，次數取決於上游任務/物件的數目，詳見 [Config 設定](PETsARD/zh-tw/docs/usage/02_yaml/) 章節。

## YAML

YAML 的基礎格式如下：

```YAML
---
{module name}:
    {experiment name}:
        {config of module}: ...
...
```

YAML 文件以 `---` 開始、以 `...` 結束。本教學使用這些標記，主要是為了正式展現格式。實際上，這兩項設定都是可選的，且 `pyyaml` 能夠在不設定這兩項的情況下進行編譯。需要特別留意的是，`---` 也常被用於在單一文件中分隔多個 YAML 設定檔，但 `PETsARD` 只支援一個檔案一個設定檔的形式。

- `module name`：執行特定工作的模組。`PETsARD` 的模組包含：
  - `Loader`: 資料讀取。見 [Loader 頁面](PETsARD/zh-tw/docs/usage/04_loader/).
  - `Preprocessor`: 資料前處理。見 [Processor 頁面](PETsARD/zh-tw/docs/usage/08_processor/).
  - `Synthesizer`: 資料合成。見 [Synthesizer 頁面](PETsARD/zh-tw/docs/usage/09_synthesizer/).
  - `Postprocessor`: 資料後處理。見 [Processor 頁面](PETsARD/zh-tw/docs/usage/08_processor/).
  - `Evaluator`: 資料評估。見 [Evaluator 頁面](PETsARD/zh-tw/docs/usage/10_evaluator/).
  - `Describer`: 資料描述。見 [Describer 頁面](PETsARD/zh-tw/docs/usage/11_describer/).
  - `Reporter`: 資料/報表輸出。見 [Reporter 頁面](PETsARD/zh-tw/docs/usage/12_reporter/).
- `experiment name`：對於該模組，單一個實驗參數的自訂名稱。必填。
- `config of module`：完整參數請參考各模組於手冊上的說明。

一般來說，使用者可以透過 YAML 格式將模組所需參數傳入，詳見 [Config Setup 頁面](PETsARD/zh-tw/docs/usage/02_yaml/)。然而，`Executor` 可以接受其他在 YAML 檔案上的特殊參數與指令，請參閱後續章節。

## `Executor` 的特定參數

### `Loader`

#### `method`

`Loader` 區段中的 `method` 參數只能用於設定 `method = 'default'` 與 `method = 'custom_data'`。前者相當於 `filepath = 'benchmark://adult-income'` 的設置，後者則是用於自定義資料集與深度客製化評估過程，因此使用者必須自行決定預先準備資料集的在分析流程中的放置位置。詳見用戶故事 C-2a 跟 C-2b。

### `Splitter`

#### `method`

`Splitter` 區段中的 `method` 參數只能用於設定 `method = 'custom_data'`，其用於自定義資料集與深度客製化評估過程，因此使用者必須自行決定預先準備資料集的在分析流程中的放置位置。詳見用戶故事 C-2a 跟 C-2b。

### `Preprocessor`

`Preprocessor` 是一部分的 `Processor` 類別。根據 [Processor 頁面](PETsARD/zh-tw/docs/usage/08_processor/)，`metadata` 是必須參數。然而若您使用 YAML 進行實驗，此參數會被忽略，且 `Executor` 會處理這個部分。另外，若要傳入 `Processor` 中的 `config`，您可以直接提供 `config` 的巢狀結構（以 YAML 的形式）。`Processor.fit()` 中的 `sequence` 也可以在此使用。

### `Synthesizer`

#### `method`

`method` 指定所希望使用的合成方法（完整選項見手冊）。必填。`method = 'default'` 將使用預設的方式做合成（目前是 `sdv` 的 Gaussian Copula）。此外，`method = 'custom_data'` 用於自定義資料集與深度客製化評估過程，因此使用者必須自行決定預先準備資料集的在分析流程中的放置位置。詳見用戶故事 C-2a 跟 C-2b。

### `Postprocessor`

`Postprocessor` 是一部分的 `Processor` 類別。它必須與 `Preprocessor` 一致，因此建議使用與 `Preprocessor` 相同的實驗名稱，另外 `method` 需設為 `'default'`。

### `Evaluator`

#### `method`

`method` 指定所希望使用的評估方法（完整選項見手冊）。必填。`method = 'default'` 將使用預設的方式做評估（目前是 `sdmetrics` 的 QualityReport）。`method = 'custom_method'` 則依照使用者給定的 Python 程式碼路徑 (`filepath`) 與類別 (`method` 指定類別名稱) 做評估。自訂評測需要使用者自訂一個符合格式的 Python 類別。該類別應該在 `__init__` 時接受設定 (`config`)，提供 `.create()` 方法接受名為 `data` 的字典做評測資料的輸入，以及 `.get_global()`, `.get_columnwise()`, `.get_pairwiser()` 方法以分別輸出全資料集、個別欄位、與欄位與欄位間不同報告顆粒度的結果。我們建議直接繼承 `EvaluatorBase` 類別來滿足要求。可利用下方程式碼導入：

```Python
from PETsARD.evaluator.evaluator_base import EvaluatorBase
```

### `Describer`

#### `method`

`method` 指定所希望使用的描述方法（完整選項見手冊）。必填。`method = 'default'` 將使用預設的方式做描述。

### `Reporter`

#### `method`

`method` 指定所希望使用的報告產出方法。可接受的值為以下兩者之一：`'save_data'`、`'save_report'`。

##### `'save_data'`

當 `method = 'save_data'`，模組會擷取模組的結果資料做輸出。`source` 是 `method = 'save_data'` 特有的參數，指定哪個/哪些模組的結果做輸出。這邊指定為 `'Postprocessor'` 代表希望拿 Postprocessor 的結果，即經過前處理、合成、後處理的資料，其保有隱私強化的資料特性、且資料樣態將符合原始資料。

##### `'save_report'`

當 `method = 'save_report'`，則會擷取 `Evaluator`/`Describer` 模組評測的結果資料做輸出。`eval` 是 `method = 'save_data'` 特有的參數，藉由實驗名稱指定哪個實驗的結果做輸出。這邊指定為 `'demo'` 代表希望拿名為 `'demo'` 的 Evaluator 的結果。

`granularity` 是 `method = 'save_report'` 特有的參數，指定結果資料的細節程度、我們稱為粒度。這邊指定為 `'global'` 代表取得的是整個資料集一個總體評分的粒度。根據不同 `Evaluator`/`Describer` 的評測方式，其評分可能是基於整個資料集計算出一個總體分數，或者可能是針對每個欄位單獨計算分數，甚至是欄位與欄位間計算分數。

## 模組與實驗名稱

YAML 的模組名稱是唯一的，其編排的順序即是 YAML 執行各模組的順序 (`sequence`)。如果使用者希望同時做多種不同的實驗設定，例如您想用同樣的資料集做不同的合成資料方式，這屬於實驗名稱層級，您可以在同一個模組名稱中設定多個實驗名稱。以這個例子來說，也就是在 `Synthesizer` 下設定兩個實驗名稱，假設叫 `A` 跟 `B`：

```YAML
Loader:
    my_load:
        {config of my_load}: ...
Preprocessor:
    my_preproc:
        {config of my_preproc}: ...
Synthesizer:
    A:
        {config of A}: ...
    B:
        {config of B}: ...
Postprocessor:
    my_preproc:
        {config of my_preproc}: ...
Report:
    my_save_data:
        {config of my_save_data}: ...
```

這個 YAML 的模組順序 (`sequence`) 即為：

```
Loader -> Preprocessor -> Synthesizer -> Postprocessor -> Reporter
```

而設定 (`Config.config`) 則會依照模組順序 (`sequence`) ，擴展為：

```
Loader: my_load -> Preprocessor: my_preproc -> Synthesizer: A -> Postprocessor: my_preproc -> Reporter: my_save_data
->  Synthesizer: B ->Postprocessor: my_preproc` -> Reporter: my_save_data
```

我們在下一章 Config Generation 會更具體的說明多個實驗名稱如何擴展。

總結而言，實驗名稱是可自訂的，但在同一個模組內不能重複。特別說明，以下這種特定的實驗名稱字串型態，因為涉及 `PETsARD` 的內部操作，是無法使用的，`Executor` 會回傳錯誤並停止：`*_[*]`（以半形底線接左中括號、接任意字串、然後接右中括號做實驗名稱的結尾）。 `PETsARD` 會用這樣的形態串連您的實驗名稱以供後續使用。

## Config 產生

針對使用者提供 YAML 設定檔時，`Executor` 會呼叫內部的 `Config` 類別來組織設定。

`Config` 採用深度優先搜尋策略，依照模組名稱的順序 (`sequence`)，將設定檔視作一個遍歷樹，它在達到每個分支的末端後、會回溯至前一個分岔路口，繼續探索其他的實驗名稱設定。這個方法允許 `Executor` 在一個 YAML 設定檔中，實施多種實驗的組合，並高效重用相同的實驗設置進行多次實驗。我們來看例子：

```YAML
---
Loader:
    data_a:
        {config of data_a}: ...
    data_b:
        {config of data_b}: ...
Preprocessor:
    preproc:
        {config of preproc}: ...
Synthesizer:
    syn_a:
        {config of syn_a}: ...
    syn_b:
        {config of syn_b}: ...
Postprocessor:
    preproc:
        {config of preproc}: ...
Evaluator:
    eval_a:
        {config of eval_a}: ...
    eval_b:
        {config of eval_b}: ...
Report:
    save_data:
        {config of save_data}: ...
    save_report:
        {config of save_report}: ...
...
```

這個 YAML 的模組順序 (`sequence`) 即為：

```
Loader -> Preprocessor -> Synthesizer -> Postprocessor -> Evaluator -> Reporter
```

我們來搭配每個分岔點，具體說明 `Config.config` 是怎麼遍歷實驗的：

```
- 分岔點 1 - Loader: `data_a` 或 `data_b`
- Preprocessor: `preproc`
- 分岔點 2 - Synthesizer: `syn_a` 或 `syn_b`
- Postprocessor: `preproc`
- 分岔點 3 - Evaluator: `eval_a` 或 `eval_b`
- 分岔點 4 - Reporter: `save_data` 或 `save_report`
```

四個分岔點，每個分岔各兩條路，我們應該有 `2*2*2*2 = 16` 個實驗組合。我們僅列出第一條路的完整版，後面的十五條路，僅概略說明：

```
1. Loader: data_a -> Preprocessor: preproc -> Synthesizer: syn_a -> Postprocessor: preproc -> Evaluator: eval_a -> Reporter: save_data

回到 Evaluator

2. -> Reporter: save_report

回到 Postprocessor

3. -> Evaluator: eval_b -> Reporter: save_data

回到 Evaluator

4. -> Reporter: save_report

回到 Synthesizer

5. -> Synthesizer: syn_b -> Postprocessor: preproc -> Evaluator: eval_a -> Reporter: save_data

6.~8. 只是在 Synthesizer: syn_b 下重複 2.~3.

回到 Loader

9. Loader: data_b -> Preprocessor: preproc -> Synthesizer: syn_a -> Postprocessor: preproc -> Evaluator: eval_a -> Reporter: save_data

10.~16. 只是在 Loader: data_b 下重複 2.~8.
```

以上我們將得到 16 個實驗結果。值得注意的是，`Reporter` 的 `method: 'save_data'` 跟 `method: 'save_report'` 做的是不同事情。`'save_data'` 會把該實驗組合當中指定的模組結果輸出，而 `'save_report'` 則會把指定的 `Evaluator`/`Describer` 結果按設定輸出。所以實際上我們是得到 8 個資料集結果、加上 8 個評估報告共 16 個實驗結果。詳情請參考[Reporter頁面](PETsARD/zh-tw/docs/usage/12_reporter/)。

## Config 設定

對於 YAML 的第三層，每個模組各自的參數，使用者應該將參數視作一個字典來傳入，此時字典的鍵值便是模組的參數。請看下面的例子：

```Python
from PETsARD import Loader


## experiment name: my-adult-income
load = Loader(
    filepath='benchmark/adult-income.csv',
    column_types={
        'category': [
            'workclass',
            'education',
            'marital-status',
            'occupation',
            'relationship',
            'race',
            'gender',
            'native-country',
            'income',
        ],
    },
    na_values={
        'workclass': '?',
        'occupation': '?',
        'native-country': '?',
    }
)
load.load()
print(load.data.head(1))
```

此時轉成 YAML 便會寫成：

```YAML
---
Loader:
    my-adult-income:
        filepath: 'benchmark/adult-income.csv'
        column_types:
            category:
                - workclass
                - education
                - marital-status
                - occupation
                - relationship
                - race
                - gender
                - native-country
                - income
        na_values:
            workclass: '?'
            occupation: '?'
            native-country: '?'
...
```

YAML 的第三層有三個鍵 `filepath`、`column_types`、`na_values`，對應 [Loader 模組](PETsARD/zh-tw/docs/usage/04_loader/)的參數。各參數的值均參考模組頁面進行設定。以本例 `Loader` 來說：

- `filepath` 為字串。當字串內容沒有特殊字元時，不需要使用單雙引號。
- `na_values` 為鍵值對均為字串的字典。YAML 的字典以 `key: value` 方式表示，半形冒號後面需要有一個半形空格。問號為特殊字元，故使用單引號。
- `column_types` 亦為字典，而鍵 `'category'` 的值為列表。列表中的值以 `- value` 方式表示，半形連字號後面需要有一個半形空格。

其他 YAML 格式，可參閱 [wiki - YAML](https://zh.wikipedia.org/zh-tw/YAML) 等資源。
