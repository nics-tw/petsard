---
title: "Reporter"
# description: "Guides lead a user through a specific task they want to accomplish, often with a sequence of steps."
# summary: ""
date: 2023-09-07T16:04:48+02:00
lastmod: 2023-09-07T16:04:48+02:00
draft: false
weight: 23
toc: true
---

`Reporter` 模組負責產製 `PETsARD` 的成果，其中包括報告輸出、以及資料集儲存。由於 `Reporter` 主要是為了使用者藉由 `Executor` 產製報告而設計，我們強烈建議使用者直接使用 `Executor`。

如果您仍希望單獨使用 `Reporter`，請注意資料的輸入格式有特別的要求，請參考本教學的 [`create()` 章節](https://nics-tw.github.io/PETsARD/Reporter.html#create)做設定。

**`method = 'save_data'`**

```Python
from PETsARD import Reporter


syn_expt_name: str = 'default'
syn_idx: tuple = ('Synthesizer', syn_expt_name)

# syn = Synthesizer(...)
# syn.create(data=...)
# syn.fit_sample()

rpt_data = Reporter(
    method = 'save_data',
    source = 'Synthesizer',
)
rpt_data.create(data={
    syn_idx: syn.data_syn
})
rpt_data.report()
```

```Python
Now is PETsARD_Synthesizer[default] save to csv...
```

```plain_text
output: PETsARD_Synthesizer[default].csv
```

**`method = 'save_report'`**

```Python
from PETsARD import Reporter


granularity: str = 'global'
eval_idx: tuple = ('Evaluator', f"{eval_name}_[{granularity}]")

# eval = Evaluator(...)
# eval.create(data={...})
# eval.eval()

rpt_report = Reporter(
    method = 'save_report',
    granularity = granularity,
)
rpt_report.create(data={
    eval_idx: eval.get_global() # granularity = global
})
rpt_report.report()
```

```Python
Now is PETsARD[Report]_default_[global] save to csv...
```

```plain_text
output: PETsARD[Report]_default_[global].csv
```

# `Reporter`

`Reporter` 具備兩種功能：將 DataFrame 輸出為 CSV 的 `'save_data'`，以及將 `Evaluator` 跟 `Describer` 報告結果輸出為 CSV 的 `'save_report'`，這兩者對參數與輸入資料的要求不同。

```Python
rpt = Reporter(
    method='save_data',
    output='MyData',
    source=['Synthesizer','Postprocessor'],
)
```

```Python
rpt = Reporter(
    method='save_report',
    output='MyReport',
    granularity='global',
    eval='MyEval',
)
```

`Reporter` 的功能是根據輸入 `data` 中吻合的關鍵字來產生檔案輸出，或是吻合的關鍵字產生報告輸出。

在 `Executor` 中，這個 `data` 會按照 YAML 的設定與實驗流程，整理成特定的[完整實驗元組 (full_expt_tuple)](https://nics-tw.github.io/PETsARD/Reporter.html#full_expt_tuple) 供 `Reporter` 檢索。

而當使用者想單獨使用 `Reporter` 的時候，相信使用者是已經使用 `PETsARD` 各模組產生出自己想要的評測了，於是照著你所使用的模組、並對每個步驟加以命名（實驗名稱, `'expt_name'`），便可以組合成 `Reporter` 所需要的完整實驗元組。

如果使用者是使用其他套件產生的合成資料或評測也沒問題，請對照 `PETsARD` 手冊，思考您使用的其他套件所對應的 `PETsARD` 模組功能是什麼即可。

**參數**

`method` (`str`): 產出報告的方法。限於 `'save_data'` 與 `'save_report'` 兩種。

`output` (`str`, default=`'PETsARD'`, optional): 報告輸出檔名的前綴，預設為 `'PETsARD'`。具體輸出的檔名請參考 [`report()` 章節](https://nics-tw.github.io/PETsARD/Reporter.html#report)。

`source` (`str | List[str]`): 用以指定輸出目標是哪個模組或是哪個實驗名稱 (`expt_name`) 的結果。僅必要於 `method = 'save_data'`。

`granularity` (`str`): 對於 `eval` 所指定的評估報告，指定輸出的資料顆粒度。限於 `'global'`、`'columnwise'`、`'pairwise'` 三種。僅必要於 `method = 'save_report'`。

`eval` (`str | List[str]`, optional): 用以指定輸出目標是哪個 `Evaluator` 或 `Describer` 的評估報告。僅適用於 `method = 'save_report'`。

## `create()`

利用給定的資料創建 `Reporter`。

**參數**

`data` (`dict`): `Reporter` 輸入的 `data` 為一個一至多個鍵值對的字典。其鍵為特定格式的元組 (`tuple`)，我們稱其為完整實驗元組 (`full_expt_tuple`)，而值都是 `pandas.DataFrame`。

`data['exist_report']` (`dict`): `exist_report` 是一個包含現有評測結果的字典，字典的鍵代表著各個評估的實驗名稱 (`{eval}_[{granularity}]`)，而值則是 `pandas.DataFrame`。你可以藉由在 `Reporter.create()` 的 `data` 中加上 `exist_report` 把舊的評測送給 `Reporter`，讓 `Reporter` 跟新的評測一起輸出報告。

當你使用 `Executor` 搭配 YAML 的時候，你無需自行設定 `exist_report`。下面則為單獨使用 `Reporter` 的使用者，展示了如何從不同的資料源 (`Loader`) 收集資料並執行相同的評估報告方法，最後如何透過 `exist_report` 將報告結果傳遞給 `Reporter` 以累積輸出。

```Python
import pandas as pd

from PETsARD import Loader, ... Reporter


eval_name: str = 'exist_report-demo'
granularity: str = 'global'
eval_expt_name: str = f"{eval_name}_[{granularity}]"

report_input: dict = {}
eval_name_tuple: tuple = None
exist_report: pd.DataFrame = None
for benchmark in ['adult-income', 'bank-marketing-2']:
    # load
    load = Loader(filepath=f"benchmark://{benchmark}")
    load.load()
    # syn = Synthesizer(...) ...
    # eval = Evaluator(...) ...

    # collect input
    eval_name_tuple = ('Loader', benchmark, 'Evaluator', eval_expt_name)
    report_input[eval_name_tuple] = eval.get_global() # global granularity
    # collect exist_report if exist
    if exist_report is not None:
        report_input['exist_report'] = {}
        report_input['exist_report'][eval_expt_name] = exist_report

    # report
    rpt_report = Reporter(
        method = 'save_report',
        granularity = granularity,
    )
    rpt_report.create(data=report_input)
    rpt_report.report()

    # collect exist_report from result
    exist_report = rpt_report.result['Reporter']['report'].copy()

print(rpt_report.result)
```

```Python
{'Reporter': {'eval_expt_name': 'default-by-module_[global]',
              'granularity': 'global',
              'report':                                            full_expt_name            Loader  \
result  Loader[adult-income]_Evaluator[global] ...      adult-income
result  Loader[bank-marketing-2]_Evaluator[glo ...  bank-marketing-2

                         Evaluator     Score  Column Shapes  \
result  [global]  0.674120       0.722361
result  [global]  0.681132       0.752968

        Column Pair Trends
result            0.625879
result            0.609297  }}
```

### `full_expt_tuple`

`full_expt_tuple` (`tuple[str]`): 完整實驗元組為兩兩一組，必定是偶數個元素，其每組配對都代表著 `({模組名稱}, {實驗名稱})`。

`module_name` (`str`): 模組名稱必須是以下 `PETsARD` 在 YAML 裡可以設定的模組名稱之一，每個模組名稱在同一個元組裡只能出現一次。而 `Reporter` 的搜尋是針對最後一組元素組。

- [Loader](https://nics-tw.github.io/PETsARD/Loader.html)
- [Splitter](https://nics-tw.github.io/PETsARD/Splitter.html)
- [Processor](https://nics-tw.github.io/PETsARD/Processor.html)
- [Preprocessor](https://nics-tw.github.io/PETsARD/Processor.html)
- [Synthesizer](https://nics-tw.github.io/PETsARD/Synthesizer.html)
- [Postprocessor](https://nics-tw.github.io/PETsARD/Processor.html)
- [Evaluator](https://nics-tw.github.io/PETsARD/Evaluator.html)
- [Describer](https://nics-tw.github.io/PETsARD/Describer.html)

`expt_name` (`str`): 實驗名稱為本模組的實驗所取的名稱。不同模組間的實驗名稱可以重複。模組與實驗名稱的規範一併請參考 [YAML 的 Module and Experiment name 章節](https://nics-tw.github.io/PETsARD/YAML.html#module-and-experiment-name)。

對於 `'save_data'` 的 `source`，最後一組的模組名稱或實驗名稱應該與 `source` 匹配。

如果您很清楚您就是單一個合成資料要做備份，那用最基本的 `('Synthesizer', 'my_expt')` 即可。

但由於 `source` 可以指定為單一個字串，也可以指定為一個字串組成的列表，這提供使用者更好的彈性去用單一個 `Reporter(method='save_data')` 輸出實驗中所有想保存的中繼資料。舉例來說，下面的名稱都可以被 `source = ['Synthesizer', 'my_expt']` 識別到：

```Python
source = ['Synthesizer', 'my_expt']
data = {
    ('Loader', 'my_expt'): pd.Dataframe,
    ('Loader', 'my_expt', 'Synthesizer', 'my_expt'): pd.Dataframe,
    ('Loader', 'default', 'Synthesizer', 'default'): pd.Dataframe,
}
```

`source` 不支援 `Evaluator` 跟 `Describer`，對於報告請使用 `method='save_report'`。

在 YAML 中，如果使用者指定 `source = 'Splitter'`，無論幾個切分 (`num_samples`) `PETsARD` 都會同時輸出所有資料。`PETsARD` 會以實驗名稱分別指定了不同切分分開的 `Splitter` 操作，以及其對應的切分資料結果。

對於 `'save_report'`，`Reporter` 會檢查最後一組的模組名稱是否為 `Evaluator` 或 `Describer`，然後再檢查實驗名稱是否與 `{eval}_[{granularity}]` 這個格式匹配。以下面的例子來說，`Reporter` 只會與 `_[global]` 結尾的鍵匹配，確保報告結果顆粒度的一致性。而在報告當中，會再利用 `full_expt_name` 與各模組的欄位區別不同的報告來源。

如果您很清楚您就是單一個報告要輸出，那用 `('Evaluator', 'my_eval_[global]')` 即可。

```Python
eval = 'my_eval'
granularity = 'global'
data = {
    ('Loader', 'my_data', 'Synthesizer', 'my_expt', 'Evaluator', 'my_eval_[global]'): pd.Dataframe,
    ('Loader', 'default', 'Synthesizer', 'my_expt', 'Evaluator', 'my_eval_[global]'): pd.Dataframe,
}
```

### `full_expt_name`

完整實驗名稱是將完整實驗元組按照特定格式組合成一個單獨的字串，用作報告中的標識。

具體的格式為 `{module_name}[expt_name]`，也就是每組模組名稱跟實驗名稱以格式兩兩連接，而對於組跟組之間使用半形底線 `_` 連結 (`{module_name1}[expt_name1]_{module_name2}[expt_name2]` ...)。

- ('Loader', 'default') # A
  - `full_expt_name` = 'Loader[my_expt]'
- ('Loader', 'my_expt', 'Synthesizer', 'default') # A-2
  - `full_expt_name` = 'Loader[my_expt]\_Synthesizer[default]'

## `report()`

以特定格式儲存報告結果。

**輸出**

`Reporter` 將會將報告格式儲存為 CSV。

對於 `'save_data'` 方法，輸出的檔名會是 `{output}_{module-expt_name-pairs}.csv`，如 'PETsARD_Synthesizer[default].csv'。

`output` (`str`): 即 `Reporter` 參數中的 `output`，如果使用者沒有自訂，預設為 `PETsARD`。

`module-expt_name-pairs` (`str`): 針對 `source` 所指定的 data 鍵值所取得的實驗全名 (`full_expt_name`)

對於 `'save_report'` 方法，輸出的檔名會是 `{output}[Report]_{eval}_[{granularity}].csv`，如 'PETsARD[Report]\_[global].csv'。

`output` (`str`): 即 `Reporter` 參數中的 `output`，如果使用者沒有自訂，預設為 `PETsARD`。

`granularity` (`str`): 即 `Reporter` 參數中的 `granularity`，代表著使用者對這個評估方式所取的報告資料經度。

`eval` (`str`, optional): 即 `Reporter` 參數中的 `eval`，代表著使用者為這個評估方式所取的名字。如果未指定 `eval`，則不顯示，而如果指定了一個或多個 `eval`，他們將以半形連接號連接，並寫在顆粒度前面。

## `self.config`

`Reporter` 模組的參數：

- 在每個使用情況下，它包括來自輸入參數的 `method`（報告方法）、`method_code`（報告方法代號）、和 `output`（輸出檔名前綴），以及其他參數 (`kwargs`)。
- 當 `method` 設為 `'save_data'` 時，它包含了 `source`（輸出資料目標）。
- 當 `method` 設為 `'save_report'` 時，它包含了 `eval`（輸出報告目標）和 `granularity`（報告顆粒度）。

## `self.reporter`

被實例化的報告器本身。

## `self.result`

`self.result` 會以字典的方式儲存，格式則基於 `method` 而有所不同。

對於 `'save_data'`，`self.result` 會是一至多個鍵值對，每個鍵都是輸出結果所組成的實驗全名 (`full_expt_name`)，數量則看 `source` 在 `.create(data)` 裡對應到幾個資料，而值則都是 `pandas.DataFrame`。

對於 `'save_report'`，`self.result` 則是一個鍵為 `'Reporter'` 的字典。其值具有以下欄位：

`'expt_name'` (`str`): 輸出報告目標。來自使用者輸入。

`'granularity'` (`str`)：報告顆粒度。來自使用者輸入‧

`'eval_expt_name'` (`str`): 報告實驗名稱，以 `{eval}_[{granularity}]` 的格式儲存，與報告存檔檔名相同。

`'full_expt_name'` (`str`)：本次報告資料的完整實驗名稱。與報告存檔內容的第一欄 `'full_expt_name'` 相同。

`'report'` (`pandas.DataFrame`): 報告內容。與報告存檔內容相同。
