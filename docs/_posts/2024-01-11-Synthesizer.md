The `Synthesizer` module is responsible for synthesizing. You can specify synthetic method in `Synthesizer` class.

`Synthesizer` 模組負責評估合成資料的品質。您可以在 `Synthesizer` 類別中指定評估方式並檢驗合成資料。


```Python
from PETsARD import Synthesizer, Loader

# load = Loader(...)

syn = Synthesizer(
    method='sdv-single_table-gaussiancopula',
)
syn.create(data=transformed_data, metadata=load.metadata.to_csv())
syn.fit_sample()
```


# `Synthesizer`

To initialise an `Synthesizer`, you need to provide the synthetic method and associated parameters for synthesizing the data.

使用 `Synthesizer` 類別的物件，需要提供合成方法及相關的參數。


```python
syn = Synthesizer(
    method,
    epsilon=5.0,
)
```


**Parameters**

`method` (`str`): The synthetic method. The format should be: `{library name}-{function name}`. For example, `'sdv-single_table-gaussiancopula'`. 合成方法。格式須為 `{套件名}-{函式名}`，例如：`'sdv-single_table-gaussiancopula'`

`epsilon` (`float`, default=`5.0`, optional): The epsilon used in differential privacy (DP) algorithm. If the synthetic method does not include DP, the parameter will be ignored. See "[Available Synthesizer Types](https://nics-tw.github.io/PETsARD/Synthesizer.html#Available-Synthesizer-Types)". 用於差分隱私 (DP) 演算法的 epsilon。如果合成方法不包含 DP，此參數會被忽略。詳見 "[Available Synthesizer Types](https://nics-tw.github.io/PETsARD/Synthesizer.html#Available-Synthesizer-Types)"。

`**kwargs` (`dict`): The parameters defined by each synthetic methods. See the following sections. 合成方法的自定義參數。詳見後續章節。


## `create()`


Initiate a synthesizer by loading the original data and the corresponding metadata.

輸入原始資料與元資料以初始化合成器。


**Parameters**


`data` (`pd.DataFrame`): The data to be synthesized 用來合成的資料。

`metadata` (`dict`, default=`None`): The metadata of the data. If `Loader` is used, it is recommended to generate the metadata via `Loader.metadata.to_sdv()` to prevent any unexpected errors caused by `sdv`'s automatic metadata generation process. If `None` is passed, it will be generated automatically. `metadata` is used for `sdv`-related synthesizers and is ignored by other packages. 元資料。如果使用 `Loader`，建議可以透過 `Loader.metadata.to_sdv()` 取得元資料，以避免 `sdv` 自行生成元資料過程中產生的非預期錯誤。如果傳入值為 `None`，系統會自動生成一份。`metadata` 被用於 `sdv` 相關的合成器，且會被其他套件的合成器忽略。

## `fit()`


Learn the synthetic pattern from the original data.

從資料中學習合成模式。


## `sample()`


Generate the synthetic dataset. The synthetic data is stored in the object itself (`self.data_syn`). See "[`self.data_syn`](https://nics-tw.github.io/PETsARD/Synthesizer.html#selfdata_syn)".

生成合成資料。合成資料會存在物件本身 (`self.data_syn`)。詳見 "[`self.data_syn`](https://nics-tw.github.io/PETsARD/Synthesizer.html#selfdata_syn)"。


**Parameters**


`sample_num_rows` (`int`, default=`None`): Number of synthesized data will be sampled. 生成合成資料筆數。

`reset_sampling` (`bool`, default=`False`): Whether the method should reset the randomisation. Only used in `sdv`-related synthesizing method. It will be ignored in other libraries. 是否重置隨機過程。只會用在 `sdv` 相關的合成方法，並會被其他套件忽略。

`output_file_path` (`str`, default=`None`): The location of the output file. 輸出檔案位置。


## `fit_sample()`


Fit and sample from the synthesizer. The combination of the methods `fit()` and `sample()`.

從資料中學習合成模式並生成合成資料。為 `fit()` 和 `sample()` 的整合。


**Parameters**


Same as the `sample()` methods.

與 `sample()` 相同。


## `self.config`


The configuration of `Synthesizer` module:

`Synthesizer` 模組的參數：


- For standard usage, it contains `method`, `epsilon`, `method_code` which come from input. 在標準使用情況下，它包括來自輸入參數的 `method`（合成方法）、`epsilon`（隱私預算）與 `method_code`（合成方法代號）。
- When the `method` is set to `'default'`， `method` will replace to `PETsARD` default synthesizing method: SDV - Gaussian Copula (`sdv-single_table-gaussiancopula'`). 當 `method` 設為 `'default'` 時，`method` 將會被 `PETsARD` 預設的合成方法取代：SDV  - Gaussian Copula (`sdv-single_table-gaussiancopula'`)。
- When the `method` is set to `'custom_data'`, it encompasses `method`, `method_code`, `filepath`, and the configuration of `Loader`. 當 `method` 設為 `'custom_data'` 時，它包含 `method`、`method_code`、`filepath`（檔案路徑）以及其他 `Loader` 的配置。


## `self.data_syn`


Synthetic data is stored in the format of `pd.DataFrame`.

合成資料以 `pd.DataFrame` 的格式儲存。


# Available Synthesizer Types


In this section, we provide a comprehensive list of supported synthesizer types and their `method` name.

在此章節我們列出所有目前支援的合成資料方法及其對應的 `method` 名稱。


<div class="table-wrapper" markdown="block">

| Submodule | Class | Alias (`method` name) | `epsilon` required | `discretizing` needed[^1] |
|---|:---:|:---:|:---:|:---:|
| `sdv` | `CopulaGANSynthesizer` | 'sdv-single_table-copulagan' | | |
| `sdv` | `CTGANSynthesizer` | 'sdv-single_table-ctgan' | | |
| `sdv` | `GaussianCopulaSynthesizer` | 'sdv-single_table-gaussiancopula' | | |
| `sdv` | `TVAESynthesizer` | 'sdv-single_table-tvae' | | |
| `smartnoise` | `SmartNoiseCreator` (AIM) | 'smartnoise-aim' | ✅ | ✅ |
| `smartnoise` | `SmartNoiseCreator` (MST) | 'smartnoise-mst' | ✅ | ✅ |
| `smartnoise` | `SmartNoiseCreator` (PAC-Synth) | 'smartnoise-pacsynth' | ✅ | ✅ |
| `smartnoise` | `SmartNoiseCreator` (DP-CTGAN) | 'smartnoise-dpctgan' | ✅ |  |
| `smartnoise` | `SmartNoiseCreator` (PATE-CTGAN) | 'smartnoise-patectgan' | ✅ |  |

</div>


[^1]: In the `Processor` within `PETsARD`, whether `'discretizing'` should be in the `sequence`. If so, it should be the last elements in the `'sequence'`, and `'encoder'` should not be in the `'sequence'`. 若您使用 `PETsARD` 的 `Processor`，請確認在 `sequence` 中的最後一個元素為 `'discretizing'`，且`'encoder'` 不能在 `sequence` 中。


## SDV


`sdv` provides several methods to synthesize data, including copula-based and neural-network-based synthesizer. For more details, please refer to its official [website](https://sdv.dev/), [document](https://docs.sdv.dev/sdv) and [GitHub](https://github.com/sdv-dev/SDV). Within our package, we intentionally disable the default preprocessing procedure in `sdv` to enhance customization flexibility. Please ensure that your input data is exclusively in numerical format before initiating training. Specifically, in the `Processor` within `PETsARD`, ensure that `'discretizing'` is not in the `sequence`.

`sdv` 提供了數種合成資料的方法，包含基於關聯結構 (copula)及神經網路的合成方法。詳見其官方[網站](https://sdv.dev/)、[說明文件](https://docs.sdv.dev/sdv)及 [GitHub](https://github.com/sdv-dev/SDV)。在本套件中，我們抑制了 `sdv` 原生的資料前處理流程以提升客製化的彈性。在訓練前請確保您的資料皆是數值格式。亦即，若您使用 `PETsARD` 的 `Processor`，請確認在 `sequence` 中沒有 `'discretizing'`。


### `'sdv-single_table-copulagan'`


Use the class `CopulaGANSynthesizer` provided in `sdv`. According to SDV, this is an experimental synthesizer. See [document](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/copulagansynthesizer) for further details.

使用 `sdv` 提供的 `CopulaGANSynthesizer`，根據官方說明，這是實驗性的合成方法。詳見[說明文件](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/copulagansynthesizer)。


**Parameters**


See [document](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/copulagansynthesizer) for further details. 詳見[說明文件](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/copulagansynthesizer)。


### `'sdv-single_table-ctgan'`


Use the class `CTGANSynthesizer` provided in `sdv`. See [document](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/ctgansynthesizer) for further details.

使用 `sdv` 提供的 `CTGANSynthesizer`。詳見[說明文件](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/ctgansynthesizer)。


**Parameters**


See [document](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/ctgansynthesizer) for further details. 詳見[說明文件](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/ctgansynthesizer)。


### `'sdv-single_table-gaussiancopula'`


Use the class `GaussianCopulaSynthesizer` provided in `sdv`. See [document](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/gaussiancopulasynthesizer) for further details.

使用 `sdv` 提供的 `GaussianCopulaSynthesizer`。詳見[說明文件](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/gaussiancopulasynthesizer)。


**Parameters**


See [document](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/gaussiancopulasynthesizer) for further details. 詳見[說明文件](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/gaussiancopulasynthesizer)。


### `'sdv-single_table-tvae'`


Use the class `TVAESynthesizer` provided in `sdv`. See [document](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/tvaesynthesizer) for further details.

使用 `sdv` 提供的 `TVAESynthesizer`。詳見[說明文件](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/tvaesynthesizer)。


**Parameters**


See [document](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/tvaesynthesizer) for further details. 詳見[說明文件](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/tvaesynthesizer)。


## SmartNoise


`smartnoise` is a synthetic data generation package that emphasizes differential privacy (DP), thereby enhancing privacy protection. For more details, please refer to its official [document](https://docs.smartnoise.org/synth/index.html#synthesizers-reference) and [GitHub](https://github.com/opendp/smartnoise-sdk/tree/main/synth). Within our package, we intentionally disable the default preprocessing procedure in `smartnoise` to enhance customization flexibility. It's worth noting that for the methods which `discretizing` is needed, please ensure that your input data is exclusively in categorical format before initiating training. Specifically, in the `Processor` within `PETsARD`, ensure that the last element in the `sequence` is set to `'discretizing'`, and `'encoder'` must not be in the `'sequence'`. Also noted that if you use the method which `discretizing` is not needed, the instance will perform min-max scaling implicitly to make the programme functional.

`smartnoise` 是一個著重在差分隱私 (DP) 的合成資料套件，以提升隱私保護力。詳見其官方[說明文件](https://docs.smartnoise.org/synth/index.html#synthesizers-reference)及 [GitHub](https://github.com/opendp/smartnoise-sdk/tree/main/synth)。在本套件中，我們抑制了 `smartnoise` 原生的資料前處理流程以提升客製化的彈性。請注意，若您使用需要 `discretizing` 的演算法，在訓練前請確保您的資料皆是類別格式。亦即，若您使用 `PETsARD` 的 `Processor`，請確認在 `sequence` 中的最後一個元素為 `'discretizing'`，且`'encoder'` 不能在 `sequence` 中。另外提醒，若使用不需要 `discretizing` 的演算法，該物件會內隱執行 min-max 轉換，以確保程式能正常執行。


### `'smartnoise-aim'`


Use the Adaptive Iterative Mechanism (AIM) algorithm provided in `smartnoise`. See [document](https://docs.smartnoise.org/synth/synthesizers/aim.html) for further details.

使用 `smartnoise` 提供的 Adaptive Iterative Mechanism (AIM) 演算法。詳見[說明文件](https://docs.smartnoise.org/synth/synthesizers/aim.html)。


**Parameters**


See [document](https://docs.smartnoise.org/synth/synthesizers/aim.html) for further details. 詳見[說明文件](https://docs.smartnoise.org/synth/synthesizers/aim.html)。


### `'smartnoise-mst'`


Use the Maximum Spanning Tree (MST) algorithm provided in `smartnoise`. See [document](https://docs.smartnoise.org/synth/synthesizers/mst.html) for further details.

使用 `smartnoise` 提供的 Maximum Spanning Tree (MST) 演算法。詳見[說明文件](https://docs.smartnoise.org/synth/synthesizers/mst.html)。


**Parameters**


See [document](https://docs.smartnoise.org/synth/synthesizers/mst.html) for further details. 詳見[說明文件](https://docs.smartnoise.org/synth/synthesizers/mst.html)。


### `'smartnoise-pacsynth'`


Use the PAC-Synth algorithm provided in `smartnoise`. See [document](https://docs.smartnoise.org/synth/synthesizers/pac_synth.html) for further details.

使用 `smartnoise` 提供的 PAC-Synth 演算法。詳見[說明文件](https://docs.smartnoise.org/synth/synthesizers/pac_synth.html)。


**Parameters**


See [document](https://docs.smartnoise.org/synth/synthesizers/pac_synth.html) for further details. 詳見[說明文件](https://docs.smartnoise.org/synth/synthesizers/pac_synth.html)。


### `'smartnoise-dpctgan'`


Use the DP-CTGAN algorithm provided in `smartnoise`. See [document](https://docs.smartnoise.org/synth/synthesizers/dpctgan.html) for further details.

使用 `smartnoise` 提供的 DP-CTGAN 演算法。詳見[說明文件](https://docs.smartnoise.org/synth/synthesizers/dpctgan.html)。


**Parameters**


See [document](https://docs.smartnoise.org/synth/synthesizers/dpctgan.html) for further details. 詳見[說明文件](https://docs.smartnoise.org/synth/synthesizers/dpctgan.html)。


### `'smartnoise-patectgan'`


Use the PATE-CTGAN algorithm provided in `smartnoise`. See [document](https://docs.smartnoise.org/synth/synthesizers/patectgan.html) for further details.

使用 `smartnoise` 提供的 PATE-CTGAN 演算法。詳見[說明文件](https://docs.smartnoise.org/synth/synthesizers/patectgan.html)。


**Parameters**


See [document](https://docs.smartnoise.org/synth/synthesizers/patectgan.html) for further details. 詳見[說明文件](https://docs.smartnoise.org/synth/synthesizers/patectgan.html)。
