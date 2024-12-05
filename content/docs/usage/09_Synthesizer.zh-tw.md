---
title: "Synthesizer"
# description: "Guides lead a user through a specific task they want to accomplish, often with a sequence of steps."
# summary: ""
date: 2023-09-07T16:04:48+02:00
lastmod: 2023-09-07T16:04:48+02:00
draft: false
weight: 20
toc: true
---

`Synthesizer` 模組負責評估合成資料的品質。您可以在 `Synthesizer` 類別中指定評估方式並檢驗合成資料。

```Python
from PETsARD import Synthesizer, Loader


# load = Loader(...)

syn = Synthesizer(method='sdv-single_table-gaussiancopula')
syn.create(
    data=transformed_data,
    metadata=proc._metadata,
)
syn.fit_sample()
```

# `Synthesizer`

使用 `Synthesizer` 類別的物件，需要提供合成方法及相關的參數。

```Python
syn = Synthesizer(
    method,
    epsilon=5.0,
)
```

**參數**

`method` (`str`): 合成方法。格式須為 `{套件名}-{函式名}`，例如：`'sdv-single_table-gaussiancopula'`

`epsilon` (`float`, default=`5.0`, optional): 用於差分隱私 (DP) 演算法的 epsilon。如果合成方法不包含 DP，此參數會被忽略。詳見 "[Available Synthesizer Types](https://nics-tw.github.io/PETsARD/Synthesizer.html#Available-Synthesizer-Types)"。

`**kwargs` (`dict`): 合成方法的自定義參數。詳見後續章節。

## `create()`

輸入原始資料與元資料以初始化合成器。

**參數**

`data` (`pd.DataFrame`): 用來合成的資料。

`metadata` (`Metadata`, default=`None`): 元資料。如果使用 `Loader`/`Splitter`/`Processor`，建議可以透過最後使用模組的 `Loader.metadata`/`Splitter.metadata`/`Processor._metadata` 取得元資料，以避免 `sdv` 自行生成元資料過程中產生的非預期錯誤。如果傳入值為 `None`，系統會自動生成一份。`metadata` 被用於 `sdv` 相關的合成器，且會被其他套件的合成器忽略。需注意的是這裡所需要的是 `Metadata` 類型本身，而非字典形式的 `Metadata.metadata`。可參閱 [Metadata 頁面](https://nics-tw.github.io/PETsARD/Metadata.html)

## `fit()`

從資料中學習合成模式。

## `sample()`

生成合成資料。合成資料會存在物件本身 (`self.data_syn`)。詳見 "[`self.data_syn`](https://nics-tw.github.io/PETsARD/Synthesizer.html#selfdata_syn)"。

**參數**

`sample_num_rows` (`int`, default=`None`): 生成合成資料筆數。

`reset_sampling` (`bool`, default=`False`): 是否重置隨機過程。只會用在 `sdv` 相關的合成方法，並會被其他套件忽略。

`output_file_path` (`str`, default=`None`): 輸出檔案位置。

## `fit_sample()`

從資料中學習合成模式並生成合成資料。為 `fit()` 和 `sample()` 的整合。

**參數**

與 `sample()` 相同。

## `self.config`

`Synthesizer` 模組的參數：

- 在標準使用情況下，它包括來自輸入參數的 `method`（合成方法）、`epsilon`（隱私預算）與 `method_code`（合成方法代號）。
- 當 `method` 設為 `'default'` 時，`method` 將會被 `PETsARD` 預設的合成方法取代：SDV - Gaussian Copula (`sdv-single_table-gaussiancopula'`)。
- 當 `method` 設為 `'custom_data'` 時，它包含 `method`、`method_code`、`filepath`（檔案路徑）以及其他 `Loader` 的配置。

## `self.data_syn`

合成資料以 `pd.DataFrame` 的格式儲存。

# 可用的 Synthesizer 類型

在此章節我們列出所有目前支援的合成資料方法及其對應的 `method` 名稱。

<div class="table-wrapper" markdown="block">

| 子模組       |                類                |        別名 (`method` 名)         | 需要 `epsilon` | 需要 `discretizing`[^1] [^2] |
| ------------ | :------------------------------: | :-------------------------------: | :------------: | :--------------------------: |
| `sdv`        |      `CopulaGANSynthesizer`      |   'sdv-single_table-copulagan'    |                |                              |
| `sdv`        |        `CTGANSynthesizer`        |     'sdv-single_table-ctgan'      |                |                              |
| `sdv`        |   `GaussianCopulaSynthesizer`    | 'sdv-single_table-gaussiancopula' |                |                              |
| `sdv`        |        `TVAESynthesizer`         |      'sdv-single_table-tvae'      |                |                              |
| `smartnoise` |    `SmartNoiseCreator` (AIM)     |         'smartnoise-aim'          |       ✅       |              ✅              |
| `smartnoise` |    `SmartNoiseCreator` (MST)     |         'smartnoise-mst'          |       ✅       |              ✅              |
| `smartnoise` | `SmartNoiseCreator` (PAC-Synth)  |       'smartnoise-pacsynth'       |       ✅       |              ✅              |
| `smartnoise` |  `SmartNoiseCreator` (DP-CTGAN)  |       'smartnoise-dpctgan'        |       ✅       |              ❌              |
| `smartnoise` | `SmartNoiseCreator` (PATE-CTGAN) |      'smartnoise-patectgan'       |       ✅       |              ❌              |

</div>

[^1]: 若您使用 `PETsARD` 的 `Processor`，請確認在 `sequence` 中的最後一個元素為 `'discretizing'`，且`'encoder'` 不能在 `sequence` 中。

[^2]: ❌ 代表此操作不適用於此合成方法。

## SDV

`sdv` 提供了數種合成資料的方法，包含基於關聯結構 (copula)及神經網路的合成方法。詳見其官方[網站](https://sdv.dev/)、[說明文件](https://docs.sdv.dev/sdv)及 [GitHub](https://github.com/sdv-dev/SDV)。在本套件中，我們抑制了 `sdv` 原生的資料前處理流程以提升客製化的彈性。在訓練前請確保您的資料皆是數值格式。亦即，若您使用 `PETsARD` 的 `Processor`，請確認在 `sequence` 中沒有 `'discretizing'`。

### `'sdv-single_table-copulagan'`

使用 `sdv` 提供的 `CopulaGANSynthesizer`，根據官方說明，這是實驗性的合成方法。詳見[說明文件](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/copulagansynthesizer)。

**參數**

詳見[說明文件](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/copulagansynthesizer)。

### `'sdv-single_table-ctgan'`

使用 `sdv` 提供的 `CTGANSynthesizer`。詳見[說明文件](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/ctgansynthesizer)。

**參數**

詳見[說明文件](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/ctgansynthesizer)。

### `'sdv-single_table-gaussiancopula'`

使用 `sdv` 提供的 `GaussianCopulaSynthesizer`。詳見[說明文件](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/gaussiancopulasynthesizer)。

**參數**

詳見[說明文件](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/gaussiancopulasynthesizer)。

### `'sdv-single_table-tvae'`

使用 `sdv` 提供的 `TVAESynthesizer`。詳見[說明文件](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/tvaesynthesizer)。

**參數**

詳見[說明文件](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/tvaesynthesizer)。

## SmartNoise

`smartnoise` 是一個著重在差分隱私 (DP) 的合成資料套件，以提升隱私保護力。詳見其官方[說明文件](https://docs.smartnoise.org/synth/index.html#synthesizers-reference)及 [GitHub](https://github.com/opendp/smartnoise-sdk/tree/main/synth)。在本套件中，我們抑制了 `smartnoise` 原生的資料前處理流程以提升客製化的彈性。請注意，若您使用需要 `discretizing` 的演算法，在訓練前請確保您的資料皆是類別格式。亦即，若您使用 `PETsARD` 的 `Processor`，請確認在 `sequence` 中的最後一個元素為 `'discretizing'`，且`'encoder'` 不能在 `sequence` 中。另外提醒，若使用不需要 `discretizing` 的演算法，該物件會內隱執行 min-max 轉換，以確保程式能正常執行。

### `'smartnoise-aim'`

使用 `smartnoise` 提供的 Adaptive Iterative Mechanism (AIM) 演算法。詳見[說明文件](https://docs.smartnoise.org/synth/synthesizers/aim.html)。

**參數**

詳見[說明文件](https://docs.smartnoise.org/synth/synthesizers/aim.html)。

### `'smartnoise-mst'`

使用 `smartnoise` 提供的 Maximum Spanning Tree (MST) 演算法。詳見[說明文件](https://docs.smartnoise.org/synth/synthesizers/mst.html)。

**參數**

詳見[說明文件](https://docs.smartnoise.org/synth/synthesizers/mst.html)。

### `'smartnoise-pacsynth'`

使用 `smartnoise` 提供的 PAC-Synth 演算法。詳見[說明文件](https://docs.smartnoise.org/synth/synthesizers/pac_synth.html)。

**參數**

詳見[說明文件](https://docs.smartnoise.org/synth/synthesizers/pac_synth.html)。

### `'smartnoise-dpctgan'`

使用 `smartnoise` 提供的 DP-CTGAN 演算法。詳見[說明文件](https://docs.smartnoise.org/synth/synthesizers/dpctgan.html)。

**參數**

詳見[說明文件](https://docs.smartnoise.org/synth/synthesizers/dpctgan.html)。

### `'smartnoise-patectgan'`

使用 `smartnoise` 提供的 PATE-CTGAN 演算法。詳見[說明文件](https://docs.smartnoise.org/synth/synthesizers/patectgan.html)。

**參數**

詳見[說明文件](https://docs.smartnoise.org/synth/synthesizers/patectgan.html)。
