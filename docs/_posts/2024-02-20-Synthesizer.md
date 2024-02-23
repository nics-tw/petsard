The `synthesizer` module is responsible for synthesizing. You can specify synthetic method in `Synthesizer` class.

`synthesizer` 模組負責評估合成資料的品質。您可以在 `Synthesizer` 類別中指定評估方式並檢驗合成資料。

```python
from PETsARD.synthesizer.synthesizer import Synthesizer

synthesizer = Synthesizer(data,
                          synthesizing_method='smartnoise-mwem',
                          epsilon=5.0)

synthesizer.fit_sample()
```

# `Synthesizer`

To initialise an `Synthesizer`, you need to provide the synthetic method and associated parameters for synthesizing the data.

使用 `Synthesizer` 類別的物件，需要提供合成方法及相關的參數。


```python
synthesizer = Synthesizer(
    data, 
    synthesizing_method,
    epsilon=5.0,
    **kwargs
)
```

**Parameters**

`data` (`pd.DataFrame`): The data to be synthesized 用來合成的資料。

`synthesizing_method` (`str`): The synthetic method. The format should be: `{library name}-{function name}`. For example, `'sdv-singletable-gaussiancopula'`. 合成方法。格式須為 `{套件名}-{函式名}`，例如：`'sdv-singletable-gaussiancopula'`

`epsilon` (`float`, default=`5.0`, optional): The epsilon used in differential privacy (DP) algorithm. If the synthetic method does not include DP, the parameter will be ignored. See "Available Synthesizer Types". 用於差分隱私 (DP) 演算法的 epsilon。如果合成方法不包含 DP，此參數會被忽略。詳見 "Available Synthesizer Types"。

`**kwargs` (`dict`): The parameters defined by each synthetic methods. See the following sections. 合成方法的自定義參數。詳見後續章節。

## `fit()`

Learn the synthetic pattern from the original data.

從資料中學習合成模式。

## `sample()`

Generate the synthetic dataset. The synthetic data is stored in the object itself (`self.data_syn`). See "`self.data_syn`".

生成合成資料。合成資料會存在物件本身 (`self.data_syn`)。詳見 "`self.data_syn`"。

**Parameters**

`sample_num_rows` (`int`, default=`None`): Number of synthesized data will be sampled. 生成合成資料筆數。

`reset_sampling` (`bool`, default=`False`): Whether the method should reset the randomisation. Only used in `sdv`-related synthesizing method. It will be ignored in other libraries. 是否重置隨機過程。只會用在 `sdv` 相關的合成方法，並會被其他套件忽略。

`output_file_path` (`str`, default=`None`): The location of the output file. 輸出檔案位置。

## `fit_sample()`

Fit and sample from the synthesizer. The combination of the methods `fit()` and `sample()`.

從資料中學習合成模式並生成合成資料。為 `fit()` 和 `sample()` 的整合。

**Parameters**

`sample_num_rows` (`int`, default=`None`): Number of synthesized data will be sampled. 生成合成資料筆數。

`reset_sampling` (`bool`, default=`False`): Whether the method should reset the randomisation. Only used in `sdv`-related synthesizing method. It will be ignored in other libraries. 是否重置隨機過程。只會用在 `sdv` 相關的合成方法，並會被其他套件忽略。

`output_file_path` (`str`, default=`None`): The location of the output file. 輸出檔案位置。

## `self.data_syn`

Synthetic data is stored in the format of `pd.DataFrame`. 

合成資料以 `pd.DataFrame` 的格式儲存。

# Available Synthesizer Types

In this section, we provide a comprehensive list of supported synthesizer types and their `synthesizing_method` name.

在此章節我們列出所有目前支援的合成資料方法及其對應的 `synthesizing_method` 名稱。

| Submodule | Class | Alias (`synthesizing_method` name) | `epsilon` required |
|---|:---:|:---:|:---:|
| `sdv` | `CopulaGANSynthesizer` | 'sdv-singletable-copulagan' | |
| `sdv` | `CTGANSynthesizer` | 'sdv-singletable-ctgan' | |
| `sdv` | `GaussianCopulaSynthesizer` | 'sdv-singletable-gaussiancopula' | |
| `sdv` | `TVAESynthesizer` | 'sdv-singletable-tvae' | |
| `smartnoise` | `SmartNoiseCreator` (AIM) | 'smartnoise-aim' | ✅ |
| `smartnoise` | `SmartNoiseCreator` (MWEM) | 'smartnoise-mwem' | ✅ |
| `smartnoise` | `SmartNoiseCreator` (MST) | 'smartnoise-mst' | ✅ |
| `smartnoise` | `SmartNoiseCreator` (PAC-Synth) | 'smartnoise-pacsynth' | ✅ |

## SDV

`sdv` provides several methods to synthesize data, including copula-based and neural-network-based synthesizer. For more details, please refer to its official [website](https://sdv.dev/), [document](https://docs.sdv.dev/sdv) and [GitHub](https://github.com/sdv-dev/SDV). Within our package, we intentionally disable the default preprocessing procedure in `sdv` to enhance customization flexibility. Please ensure that your input data is exclusively in numerical format before initiating training.

`sdv` 提供了數種合成資料的方法，包含基於關聯結構 (copula)及神經網路的合成方法。詳見其官方[網站](https://sdv.dev/)、[說明文件](https://docs.sdv.dev/sdv)及 [GitHub](https://github.com/sdv-dev/SDV)。在本套件中，我們抑制了 `sdv` 原生的資料前處理流程以提升客製化的彈性。在訓練前請確保您的資料皆是數值格式。

### `'sdv-singletable-copulagan'`

Use the class `CopulaGANSynthesizer` provided in `sdv`. According to SDV, this is an experimental synthesizer. See [document](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/copulagansynthesizer) for further details.

使用 `sdv` 提供的 `CopulaGANSynthesizer`，根據官方說明，這是實驗性的合成方法。詳見[說明文件](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/copulagansynthesizer)。

**Parameters**

See [document](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/copulagansynthesizer) for further details. 詳見[說明文件](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/copulagansynthesizer)。

### `'sdv-singletable-ctgan'`

Use the class `CTGANSynthesizer` provided in `sdv`. See [document](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/ctgansynthesizer) for further details.

使用 `sdv` 提供的 `CTGANSynthesizer`。詳見[說明文件](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/ctgansynthesizer)。

**Parameters**

See [document](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/ctgansynthesizer) for further details. 詳見[說明文件](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/ctgansynthesizer)。

### `'sdv-singletable-gaussiancopula'`

Use the class `GaussianCopulaSynthesizer` provided in `sdv`. See [document](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/gaussiancopulasynthesizer) for further details.

使用 `sdv` 提供的 `GaussianCopulaSynthesizer`。詳見[說明文件](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/gaussiancopulasynthesizer)。

**Parameters**

See [document](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/gaussiancopulasynthesizer) for further details. 詳見[說明文件](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/gaussiancopulasynthesizer)。

### `'sdv-singletable-tvae'`

Use the class `TVAESynthesizer` provided in `sdv`. See [document](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/tvaesynthesizer) for further details.

使用 `sdv` 提供的 `TVAESynthesizer`。詳見[說明文件](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/tvaesynthesizer)。

**Parameters**

See [document](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/tvaesynthesizer) for further details. 詳見[說明文件](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/tvaesynthesizer)。

## SmartNoise

`smartnoise` is a synthetic data generation package that emphasizes differential privacy (DP), thereby enhancing privacy protection. For more details, please refer to its official [document](https://docs.smartnoise.org/synth/index.html#synthesizers-reference) and [GitHub](https://github.com/opendp/smartnoise-sdk/tree/main/synth). Within our package, we intentionally disable the default preprocessing procedure in `smartnoise` to enhance customization flexibility. it's worth noting that we only support the utilization of cube-style (histogram-based) synthesizers, as listed above. Please ensure that your input data is exclusively in categorical format before initiating training.

`smartnoise` 是一個著重在差分隱私 (DP) 的合成資料套件，以提升隱私保護力。詳見其官方[說明文件](https://docs.smartnoise.org/synth/index.html#synthesizers-reference)及 [GitHub](https://github.com/opendp/smartnoise-sdk/tree/main/synth)。在本套件中，我們抑制了 `smartnoise` 原生的資料前處理流程以提升客製化的彈性。同時我們也只支援 cube-style (基於長條圖的) 合成資料演算法，如上表所附。在訓練前請確保您的資料皆是類別格式。

### `'smartnoise-aim'`

Use the Adaptive Iterative Mechanism (AIM) algorithm provided in `smartnoise`. See [document](https://docs.smartnoise.org/synth/synthesizers/aim.html) for further details.

使用 `smartnoise` 提供的 Adaptive Iterative Mechanism (AIM) 演算法。詳見[說明文件](https://docs.smartnoise.org/synth/synthesizers/aim.html)。

**Parameters**

See [document](https://docs.smartnoise.org/synth/synthesizers/aim.html) for further details. 詳見[說明文件](https://docs.smartnoise.org/synth/synthesizers/aim.html)。

### `'smartnoise-mwem'`

Use the Multiplicative Weights Exponential Mechanism (MWEM) algorithm provided in `smartnoise`. See [document](https://docs.smartnoise.org/synth/synthesizers/mwem.html) for further details.

使用 `smartnoise` 提供的 Multiplicative Weights Exponential Mechanism (MWEM) 演算法。詳見[說明文件](https://docs.smartnoise.org/synth/synthesizers/mwem.html)。

**Parameters**

See [document](https://docs.smartnoise.org/synth/synthesizers/mwem.html) for further details. 詳見[說明文件](https://docs.smartnoise.org/synth/synthesizers/mwem.html)。

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


