# YAML

The basic format of YAML is as follows:

YAML 的基礎格式如下：

```
{module name}:
    {experiment name}:
        {config of module}: ...
```

- module name：A module that performs specific tasks. The modules required for this user story include:
  - `Loader`: Data loading
  - `Preprocessor`: Data pre-processing
  - `Synthesizer`: Data synthesizing
  - `Postprocessor`: Data post-processing
  - `Evaluator`: Data Evaluating
  - `Describer`: Data Describing
  - `Reporter`: Data/Report output
- experiment name: A custom name for a single experimental parameter for that module. Mandatory.
- config of module：For complete parameters, please refer to the descriptions of each module in the manual.

- 模組名稱：執行特定工作的模組。本用戶故事所需的模組包含：
  - `Loader`: 資料讀取
  - `Preprocessor`: 資料前處理
  - `Synthesizer`: 資料合成
  - `Postprocessor`: 資料後處理
  - `Evaluator`: 資料評估
  - `Describer`: 資料描述
  - `Reporter`: 資料/報表輸出
- 實驗名稱：對於該模組，單一個實驗參數的自訂名稱。必填。
- 模組的設定：完整參數請參考各模組於手冊上的說明。


## Loader (default)

The `method` parameter of the Loader is only used when `method = 'default'`.

`method = 'default'` is equivalent to `filepath = 'benchmark://adult-income'`, which by default uses the Adult Income dataset.

Loader 的 `method` 參數僅在 `method = 'default'` 時使用。

`method = 'default'` 等價於 `filepath = 'benchmark://adult-income'`，預設使用的是 Adult Income 資料集。


## Loader (filpath = 'benchmark:\\\\-')

The `filpath` parameter specifies the location of the file to be read. It is mandatory.

However, when used in the form of `filpath = 'benchmark:\\{benchmark name}'`, the string `benchmark name` directs the Loader to retrieve the corresponding benchmark dataset from the cloud. See the manual for details.

`filpath` 參數指定欲讀取檔案的位置。必填。

但當以 `filpath = 'benchmark:\\{benchmark name}'` 的形式使用時，`benchmark name` 這個字串就會帶領 Loader 去雲端獲得字串所對應的基準資料集。詳情見手冊。


## Loader, Splitter, Synthesizer (custom_data)

`method = 'custom_data'` requires you to decide the placement of your pre-prepared dataset in the analysis process based on the Evaluator you are using.

This part of the explanation is provided together with User Stories C-2a and C-2b for a clearer understanding, especially when paired with the configuration file.

`method = 'custom_data'` 必須依照你所使用的 Evaluator，來決定你要把預先準備的資料集放在分析流程的哪個位置。

這部份的說明放在用戶故事 C-2a 跟 C-2b，搭配設定檔一併解釋會更清楚。


## Synthesizer (default)

`method` specifies the desired synthesis method (see the manual for complete options). Mandatory.

`method = 'default'` will use the default method for synthesis (currently SDV's Gaussian Copula).

`method` 指定所希望使用的合成方法（完整選項見手冊）。必填。

`method = 'default'` 將使用預設的方式做合成（目前是 SDV 的 Gaussian Copula）。


## Evaluator (default)

`method` specifies the desired evaluate method (see the manual for complete options). Mandatory.

`method = 'default'` will use the default method for evaluate (currently SDMetrics' QualityReport).

`method` 指定所希望使用的評估方法（完整選項見手冊）。必填。

`method = 'default'` 將使用預設的方式做評估（目前是 SDMetrics 的 QualityReport）。


## Evaluator (custom_method)

`method = 'custom_method'` performed according to the user-provided Python code path (`filepath`) and class (`method` specifies the class name) to evaluating

`method = 'custom_method'` 則依照使用者給定的 Python 程式碼路徑 (`filepath`) 與類別 (`method` 指定類別名稱) 做計分。

## Evaluator (custom_method) - Python

Custom evaluations require users to define a Python class that conforms to a specific format. 

This class should include an __init__ method that accepts settings (`config`), a `.create()` method that takes a dictionary named `data` for input of evaluation data, and `.get_global()`, `.get_columnwise()`, `.get_pairwiser()` methods to output results at different levels of granularity for the entire dataset, individual fields, and between fields, respectively.

We recommend directly inheriting the `BaseEvaluator` class to meet the requirements. Its location is

自訂評測需要使用者自訂一個符合格式的 Python 類別。

該類別應該在 `__init__` 時接受設定 (`config`)，提供 `.create()` 方法接受名為 `data` 的字典做評測資料的輸入，以及 `.get_global()`, `.get_columnwise()`, `.get_pairwiser()` 方法以分別輸出全資料集、個別欄位、與欄位與欄位間不同報告粒度的結果。

我們建議直接繼承 `BaseEvaluator` 類別來滿足要求。它的位置在

```Python
from PETsARD.evaluator.evaluator_base import BaseEvaluator
```


## Describer (default)

`method` specifies the desired describing method (see the manual for complete options). Mandatory.

`method = 'default'` will use the default method for describe.

`method` 指定所希望使用的描述方法（完整選項見手冊）。必填。

`method = 'default'` 將使用預設的方式做描述。


## Reporter (save_data)

`method` specifies the desired reporting method. When `method = 'save_data'`, it will capture and output the result data of the module.

`source` is a parameter unique to `method = 'save_data'`, specifying which module(s) results to output. Specifying `'Postprocessor'` means wishing to obtain the results of the Postprocessor, that is, data that has undergone preprocessing, synthesis, and postprocessing, which retains the data's privacy-enhanced characteristics and ensures the data format matches the original.

`method` 指定所希望使用的報告方法，當 `method = 'save_data'`，則會擷取模組的結果資料做輸出。

`source` 是 `method = 'save_data'` 特有的參數，指定哪個/哪些模組的結果做輸出。這邊指定為 `'Postprocessor'` 代表希望拿 Postprocessor 的結果，即經過前處理、合成、後處理的資料，其保有隱私強化的資料特性、且資料樣態將符合原始資料。

## Reporter (save_report)

`method` specifies the desired reporting method. When `method = 'save_report'`, it will capture and output the result data from the `Evaluator`/`Describer` module.

`eval` is a parameter unique to `method = 'save_report'`, specifying which experiment results to output by their experiment name. Specifying `'demo'` means wishing to obtain the results from the Evaluator named `'demo'`.

`method` 指定所希望使用的報告方法，當 `method = 'save_report'`，則會擷取 `Evaluator`/`Describer` 模組評測的結果資料做輸出。

`eval` 是 `method = 'save_data'` 特有的參數，藉由實驗名稱指定哪個實驗的結果做輸出。這邊指定為 `'demo'` 代表希望拿名為 `'demo'` 的 Evaluator 的結果。


`granularity` is a parameter unique to `method = 'save_report'`,  specifying the level of detail, or granularity, of the result data. Specifying 'global' means that the granularity of the score obtained covers the entire dataset as a whole.

Depending on the evaluation methods of different `Evaluator`/`Describer`, scoring might be based on calculating a comprehensive score for the entire dataset, or it might involve calculating scores for each field individually, or even calculating scores between fields.

However, regardless of the evaluation method used, for users, it is usually most practical to understand the "overall score of the entire dataset". Therefore, we have conducted preliminary academic research on different Evaluators/Describers and have appropriately averaged or weighted different scores to provide a `'global' level of scoring granularity that covers the entire dataset.

`granularity` 是 `method = 'save_report'` 特有的參數，指定結果資料的細節程度、我們稱為粒度。這邊指定為 `'global'` 代表取得的是整個資料集一個總體評分的粒度。

根據不同 `Evaluator`/`Describer` 的評測方式，其評分可能是基於整個資料集計算出一個總體分數，或者可能是針對每個欄位單獨計算分數，甚至是欄位與欄位間計算分數。

但無論使用哪種評測，對使用者而言，通常最實用的是了解「整個資料集的總體評分」。因此，我們預先針對不同的 `Evaluator`/`Describer` 進行了學術研究，並對不同評分做適當的平均或加權處理，以便能夠提供以全資料集為單位、`'global'` 的評分粒度。
