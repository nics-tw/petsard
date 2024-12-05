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

The `Synthesizer` module is responsible for synthesizing. You can specify synthetic method in `Synthesizer` class.

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

To initialise an `Synthesizer`, you need to provide the synthetic method and associated parameters for synthesizing the data.

```Python
syn = Synthesizer(
    method,
    epsilon=5.0,
)
```

**Parameters**

`method` (`str`): The synthetic method. The format should be: `{library name}-{function name}`. For example, `'sdv-single_table-gaussiancopula'`.

`epsilon` (`float`, default=`5.0`, optional): The epsilon used in differential privacy (DP) algorithm. If the synthetic method does not include DP, the parameter will be ignored. See "[Available Synthesizer Types](https://nics-tw.github.io/PETsARD/Synthesizer.html#Available-Synthesizer-Types)".

`**kwargs` (`dict`): The parameters defined by each synthetic methods. See the following sections.

## `create()`

Initiate a synthesizer by loading the original data and the corresponding metadata.

**Parameters**

`data` (`pd.DataFrame`): The data to be synthesized.

`metadata` (`Metadata`, default=`None`): The metadata of the data. If `Loader`/`Splitter`/`Processor` is used, it is recommended to generate the metadata via last use module `Loader.metadata`/`Splitter.metadata`/`Processor._metadata` to prevent any unexpected errors caused by `sdv`'s automatic metadata generation process. If `None` is passed, it will be generated automatically. `metadata` is used for `sdv`-related synthesizers and is ignored by other packages. Note that the requirement is for the `Metadata` type itself, not `Metadata.metadata` as a dictionary. See the [Metadata page](https://nics-tw.github.io/PETsARD/Metadata.html) for more information.

## `fit()`

Learn the synthetic pattern from the original data.

## `sample()`

Generate the synthetic dataset. The synthetic data is stored in the object itself (`self.data_syn`). See "[`self.data_syn`](https://nics-tw.github.io/PETsARD/Synthesizer.html#selfdata_syn)".

**Parameters**

`sample_num_rows` (`int`, default=`None`): Number of synthesized data will be sampled.

`reset_sampling` (`bool`, default=`False`): Whether the method should reset the randomisation. Only used in `sdv`-related synthesizing method. It will be ignored in other libraries.

`output_file_path` (`str`, default=`None`): The location of the output file.

## `fit_sample()`

Fit and sample from the synthesizer. The combination of the methods `fit()` and `sample()`.

**Parameters**

Same as the `sample()` methods.

## `self.config`

The configuration of `Synthesizer` module:

- For standard usage, it contains `method`, `epsilon`, `method_code` which come from input.
- When the `method` is set to `'default'`， `method` will replace to `PETsARD` default synthesizing method: SDV - Gaussian Copula (`sdv-single_table-gaussiancopula'`).
- When the `method` is set to `'custom_data'`, it encompasses `method`, `method_code`, `filepath`, and the configuration of `Loader`.

## `self.data_syn`

Synthetic data is stored in the format of `pd.DataFrame`.

# Available Synthesizer Types

In this section, we provide a comprehensive list of supported synthesizer types and their `method` name.

<div class="table-wrapper" markdown="block">

| Submodule    |              Class               |       Alias (`method` name)       | `epsilon` required | `discretizing` required[^1] [^2] |
| ------------ | :------------------------------: | :-------------------------------: | :----------------: | :------------------------------: |
| `sdv`        |      `CopulaGANSynthesizer`      |   'sdv-single_table-copulagan'    |                    |                                  |
| `sdv`        |        `CTGANSynthesizer`        |     'sdv-single_table-ctgan'      |                    |                                  |
| `sdv`        |   `GaussianCopulaSynthesizer`    | 'sdv-single_table-gaussiancopula' |                    |                                  |
| `sdv`        |        `TVAESynthesizer`         |      'sdv-single_table-tvae'      |                    |                                  |
| `smartnoise` |    `SmartNoiseCreator` (AIM)     |         'smartnoise-aim'          |         ✅         |                ✅                |
| `smartnoise` |    `SmartNoiseCreator` (MST)     |         'smartnoise-mst'          |         ✅         |                ✅                |
| `smartnoise` | `SmartNoiseCreator` (PAC-Synth)  |       'smartnoise-pacsynth'       |         ✅         |                ✅                |
| `smartnoise` |  `SmartNoiseCreator` (DP-CTGAN)  |       'smartnoise-dpctgan'        |         ✅         |                ❌                |
| `smartnoise` | `SmartNoiseCreator` (PATE-CTGAN) |      'smartnoise-patectgan'       |         ✅         |                ❌                |

</div>

[^1]: In the `Processor` within `PETsARD`, whether `'discretizing'` should be in the `sequence`. If so, it should be the last elements in the `'sequence'`, and `'encoder'` should not be in the `'sequence'`.

[^2]: ❌ indicates that it is not applicable for the method.

## SDV

`sdv` provides several methods to synthesize data, including copula-based and neural-network-based synthesizer. For more details, please refer to its official [website](https://sdv.dev/), [document](https://docs.sdv.dev/sdv) and [GitHub](https://github.com/sdv-dev/SDV). Within our package, we intentionally disable the default preprocessing procedure in `sdv` to enhance customization flexibility. Please ensure that your input data is exclusively in numerical format before initiating training. Specifically, in the `Processor` within `PETsARD`, ensure that `'discretizing'` is not in the `sequence`.

### `'sdv-single_table-copulagan'`

Use the class `CopulaGANSynthesizer` provided in `sdv`. According to SDV, this is an experimental synthesizer. See [document](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/copulagansynthesizer) for further details.

**Parameters**

See [document](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/copulagansynthesizer) for further details.

### `'sdv-single_table-ctgan'`

Use the class `CTGANSynthesizer` provided in `sdv`. See [document](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/ctgansynthesizer) for further details.

**Parameters**

See [document](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/ctgansynthesizer) for further details.

### `'sdv-single_table-gaussiancopula'`

Use the class `GaussianCopulaSynthesizer` provided in `sdv`. See [document](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/gaussiancopulasynthesizer) for further details.

**Parameters**

See [document](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/gaussiancopulasynthesizer) for further details.

### `'sdv-single_table-tvae'`

Use the class `TVAESynthesizer` provided in `sdv`. See [document](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/tvaesynthesizer) for further details.

**Parameters**

See [document](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/tvaesynthesizer) for further details.

## SmartNoise

`smartnoise` is a synthetic data generation package that emphasizes differential privacy (DP), thereby enhancing privacy protection. For more details, please refer to its official [document](https://docs.smartnoise.org/synth/index.html#synthesizers-reference) and [GitHub](https://github.com/opendp/smartnoise-sdk/tree/main/synth). Within our package, we intentionally disable the default preprocessing procedure in `smartnoise` to enhance customization flexibility. It's worth noting that for the methods which `discretizing` is needed, please ensure that your input data is exclusively in categorical format before initiating training. Specifically, in the `Processor` within `PETsARD`, ensure that the last element in the `sequence` is set to `'discretizing'`, and `'encoder'` must not be in the `'sequence'`. Also noted that if you use the method which `discretizing` is not needed, the instance will perform min-max scaling implicitly to make the programme functional.

### `'smartnoise-aim'`

Use the Adaptive Iterative Mechanism (AIM) algorithm provided in `smartnoise`. See [document](https://docs.smartnoise.org/synth/synthesizers/aim.html) for further details.

**Parameters**

See [document](https://docs.smartnoise.org/synth/synthesizers/aim.html) for further details.

### `'smartnoise-mst'`

Use the Maximum Spanning Tree (MST) algorithm provided in `smartnoise`. See [document](https://docs.smartnoise.org/synth/synthesizers/mst.html) for further details.

**Parameters**

See [document](https://docs.smartnoise.org/synth/synthesizers/mst.html) for further details.

### `'smartnoise-pacsynth'`

Use the PAC-Synth algorithm provided in `smartnoise`. See [document](https://docs.smartnoise.org/synth/synthesizers/pac_synth.html) for further details.

**Parameters**

See [document](https://docs.smartnoise.org/synth/synthesizers/pac_synth.html) for further details.

### `'smartnoise-dpctgan'`

Use the DP-CTGAN algorithm provided in `smartnoise`. See [document](https://docs.smartnoise.org/synth/synthesizers/dpctgan.html) for further details.

**Parameters**

See [document](https://docs.smartnoise.org/synth/synthesizers/dpctgan.html) for further details.

### `'smartnoise-patectgan'`

Use the PATE-CTGAN algorithm provided in `smartnoise`. See [document](https://docs.smartnoise.org/synth/synthesizers/patectgan.html) for further details.

**Parameters**

See [document](https://docs.smartnoise.org/synth/synthesizers/patectgan.html) for further details.
