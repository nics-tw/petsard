---
title: "YAML"
draft: false
weight: 13
toc: true
---

YAML (YAML Ain't Markup Language) is a highly readable format used to express data serialization, designed for easily reading and editing, while also being easily parsed by computers. `Executor` in `PETsARD` allows users to configure the settings of PETsARD in YAML format. Through the introduction of this document, we hope that users can quickly get started, effortlessly set up and run their experiments effortlessly, and manage their experimental settings with YAML conveniently (See [Executor page](PETsARD/docs/usage/01_executor/) also).

This document explains the basic YAML settings only. It is recommended to refer to the `demo/User Story*.ipynb` user story scenarios in the [demo/REAMD.ME](https://github.com/nics-tw/PETsARD/tree/main/demo), and [yaml/README.md](https://github.com/nics-tw/PETsARD/tree/main/yaml), which can help clarify how your requirements can be implemented (See [User Story page](PETsARD/docs/usage/03_user-story/) also).

# Tutorial

Below is a demo YAML file and the illustration of how it works.

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

<p align="center"><img src="https://nics-tw.github.io/PETsARD/assets/images/YAML_final.png" height="1080"></p>

Noted that in each module (enclosed by the dash line), it will be executed/created several times, depending on the number of upstream tasks/instances. See [Config generation](https://nics-tw.github.io/PETsARD/YAML.html#config-generation) for details.

# YAML

The basic format of YAML is as follows:

```YAML
---
{module name}:
    {experiment name}:
        {config of module}: ...
...
```

A YAML document starts and ends with `---` and `...`, respectively. The markers used in this tutorial are primarily to display the format formally. In reality, both of these settings are optional, and `pyyaml` can compile without setting either. It is important to note that `---` is also often used to separate multiple YAML configuration files within a single document, but `PETsARD` only supports the format of one configuration file per document.

- `module name`: A module that performs specific tasks. The modules required for `PETsARD` include:
  - `Loader`: Data loading. See [Loader page](https://nics-tw.github.io/PETsARD/Loader.html).
  - `Preprocessor`: Data pre-processing. See [Processor page](https://nics-tw.github.io/PETsARD/Processor.html).
  - `Synthesizer`: Data synthesizing. See [Synthesizer page](https://nics-tw.github.io/PETsARD/Synthesizer.html).
  - `Postprocessor`: Data post-processing. See [Processor page](https://nics-tw.github.io/PETsARD/Synthesizer.html).
  - `Evaluator`: Data Evaluating. See [Evaluator page](https://nics-tw.github.io/PETsARD/Evaluator.html).
  - `Describer`: Data Describing. See [Describer page](https://nics-tw.github.io/PETsARD/Describer.html).
  - `Reporter`: Data/Report output. See [Reporter page](https://nics-tw.github.io/PETsARD/Reporter.html).
- `experiment name`: A custom name for a single experimental parameter for that module. Mandatory.
- `config of module`: For detailed configuration, please refer to the descriptions of each module in the manual.

Ideally, you can pass the parameters accepted by the module in YAML format. See [Config Setup page](https://nics-tw.github.io/PETsARD/YAML.html#config-setup) for details. However, there are several parameters and commands in YAML accepted by `Executor`, please refer to the following section.

# Parameters Specific to `Executor`

## `Loader`

### `method`

The parameter `method` in the `Loader` section is only used for `method = 'default'` and `method = 'custom_data'`. The former is equivalent to `filepath = 'benchmark://adult-income'`, and the latter is used for custom datasets and in-depth evaluation process customisation and requires users to decide the placement of the dataset in the analysis process. Please refer to User Stories C-2a and C-2b for more details.

## `Splitter`

### `method`

The parameter `method` in the `Splitter` section is only used for `method = 'custom_data'`. It is used for custom datasets and in-depth evaluation process customisation and requires users to decide the placement of the dataset in the analysis process. Please refer to User Stories C-2a and C-2b for more details.

## `Preprocessor`

`Preprocessor` is part of the `Processor` class. According to [Processor page](https://nics-tw.github.io/PETsARD/Processor.html), `metadata` is required. However, it is ignored, and `Executor` will take care of this, when using YAML. To pass the `config` from `Processor`, you can provide the nested structure `config` (in YAML format) directly. The parameter `sequence` in `Processor.fit()` is acceptable in this section as well.

## `Synthesizer`

### `method`

`method` specifies the desired synthesis method (see the manual for complete options). Mandatory. `method = 'default'` will use the default method for synthesis (currently Gaussian Copula from `sdv`). Besides, `method = 'custom_data'` is used for custom datasets and in-depth evaluation process customisation and requires users to decide the placement of the dataset in the analysis process. Please refer to User Stories C-2a and C-2b for more details.

## `Postprocessor`

`Postprocessor` is part of the `Processor` class. It should be identical to `Preprocessor`. Hence, it is recommended to using the same experiment name as `Preprocessor`. Besides, the `method` should be `'default'`.

## `Evaluator`

### `method`

`method` specifies the desired evaluate method (see the manual for detailed options). Mandatory. `method = 'default'` will use the default method for evaluate (currently QualityReport from `sdmetrics`). Besides, `method = 'custom_method'` performed evaluation according to the user-provided Python code path (`filepath`) and class (`method` specifies the class name). The user-defined class should include an `__init__` method that accepts settings (`config`), a `.create()` method that takes a dictionary named `data` for input of evaluation data, and `.get_global()`, `.get_columnwise()`, `.get_pairwiser()` methods to output results at different levels of granularity for the entire dataset, individual fields, and between fields, respectively. We recommend inheriting the `EvaluatorBase` class directly to meet the requirements. You can import the module using the following code.

```Python
from PETsARD.evaluator.evaluator_base import EvaluatorBase
```

## `Describer`

### `method`

`method` specifies the desired describing method (see the manual for detailed options). Mandatory. `method = 'default'` will use the default method for describe.

## `Reporter`

### `method`

`method` specifies the desired reporting method. Either of two values is accepted: `'save_data'` and `'save_report'`.

#### `'save_data'`

When `method = 'save_data'`, it will capture and output the result data of the module. `source` is a parameter unique to `method = 'save_data'`, specifying which module(s) results to output. Specifying `'Postprocessor'` means wishing to obtain the results of the Postprocessor, that is, data that has undergone preprocessing, synthesis, and postprocessing, which retains the data's privacy-enhanced characteristics and ensures the data format matches the original.

#### `'save_report'`

When `method = 'save_report'`, it will capture and output the result data from the `Evaluator`/`Describer` module. `eval` is a parameter unique to `method = 'save_report'`, specifying which experiment results to output by their experiment name. Specifying `'demo'` means wishing to obtain the results from the Evaluator named `'demo'`.

`granularity` is another parameter unique to `method = 'save_report'`, specifying the level of detail, or granularity, of the result data. Specifying `'global'` means that the granularity of the score obtained covers the entire dataset as a whole. Depending on the evaluation methods of different `Evaluator`/`Describer`, scoring might be based on calculating a comprehensive score for the entire dataset, or it might involve calculating scores for each field individually, or even calculating scores between fields.

# Module and Experiment Name

The module names in YAML are unique, and its arrangement dictates the execution order of the modules within YAML. If users wish to conduct multiple different experimental setups simultaneously, such as using the same dataset for different synthetic data generation methods, this falls under the experiment name level. You can set up multiple experiment names under the same module name. For example, you could set up two experiment names under `Synthesizer`, let's assume they are called `A` and `B`:

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

The `sequence` of modules in this YAML would be:

```
Loader -> Preprocessor -> Synthesizer -> Postprocessor -> Reporter
```

And the `Config.config` would be expanded according to the module `sequence` as:

```
Loader: my_load -> Preprocessor: my_preproc -> Synthesizer: A -> Postprocessor: my_preproc -> Reporter: my_save_data
->  Synthesizer: B ->Postprocessor: my_preproc` -> Reporter: my_save_data
```

In the next chapter, "Config Generation," we will provide more specific explanations on how multiple experiment names are expanded.

In summary, experiment name are customisable, but they cannot be duplicated within the same module. It is important to note that the following specific experiment name string formats are not usable due to `PETsARD`'s internal operations. The `Executor` will return an error and stop if they are used: `*_[*]`, which ends an experiment name with an underscore followed by an open bracket, any string, and then a close bracket. `PETsARD` uses this format to append to the experiment names to describe specific experimental process results.

# Config Generation

When the user provides a YAML config file, the `Executor` invokes the internal `Config` class to organise the configuration.

The `Config` class employs a Depth-First Search strategy, treating the configuration file as a traversal tree based on the module name order (`sequence`). It backtracks to the previous junction after reaching the end of each branch, continuing to explore settings for other experiment names. This approach allows the `Executor` to implement a combination of multiple experiments within a single YAML configuration file, efficiently reusing the same experiment setup for numerous experiments. Let's look at an example:

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

The `sequence` of modules in this YAML would be:

```
Loader -> Preprocessor -> Synthesizer -> Postprocessor -> Evaluator -> Reporter
```

Let's explain in detail how the `Config.config` traverse the experiments, considering each junction point:

```
- Juction 1 - Loader: `data_a` or `data_b`
- Preprocessor: `preproc`
- Juction 2 - Synthesizer: `syn_a` or `syn_b`
- Postprocessor: `preproc`
- Juction 3 - `Evaluator`: `eval_a` or `eval_b`
- Juction 4 - `Reporter`: `save_data` or `save_report`
```

With four junction points, each having two paths, we should have `2*2*2*2 = 16` experiment combinations. We will only list the complete version for the first path, and for the remaining fifteen paths, we will provide a brief explanation:

```
1. Loader: data_a -> Preprocessor: preproc -> Synthesizer: syn_a -> Postprocessor: preproc -> Evaluator: eval_a -> Reporter: save_data

Back to Evaluator

2. -> Reporter: save_report

Back to Postprocessor

3. -> Evaluator: eval_b -> Reporter: save_data

Back to Evaluator

4. -> Reporter: save_report

Back to Synthesizer

5. -> Synthesizer: syn_b -> Postprocessor: preproc -> Evaluator: eval_a -> Reporter: save_data

6.~8. just repeat 2.~3. under Synthesizer: syn_b

Back to Loader

9. Loader: data_b -> Preprocessor: preproc -> Synthesizer: syn_a -> Postprocessor: preproc -> Evaluator: eval_a -> Reporter: save_data

10.~16. just repeat 2.~8. under Loader: data_b
```

From the above, we will obtain 16 experiment results. It's worth noting that `Reporter`'s `method: 'save_data'` and `method: 'save_report'` perform different tasks. `'save_data'` exports the results of the specified module within the experiment combination, while `'save_report'` exports the results of the specified `Evaluator`/`Describer` according to config. Therefore, in reality, we obtain 8 datasets results, plus 8 evaluation reports, totaling 16 experiment results. For more details, please refer to the [Reporter page](https://nics-tw.github.io/PETsARD/Reporter.html).

# Config Setup

For the third layer in YAML, the parameters for each module should be considered as a dictionary to pass in. In this case, the keys of the dictionary are the parameters of the module. Please see the example below:

```Python
from PETsARD import Loader


# experiment name: my-adult-income
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

At this point, it would be written in YAML as:

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

The third layer of YAML contains three keys: `filepath`, `column_types`, and `na_values`, corresponding to the parameters of `Loader` module. The values for each parameter are set according to the module page. Taking `Loader` as an example:

- `filepath` is a string. If the string content does not contain any special characters, single or double quotes are not necessary.
- `na_values` is a dictionary where both keys and values are strings. Dictionaries in YAML are represented as `key: value`, with a space following the colon. The question mark is a special character, hence it is enclosed in single quotes.
- `column_types` is also a dictionary, which the value of the key `'category'` is a list. Values in the list are represented as `- value`, with a space following the hyphen.

For other YAML formats, please refer to resources [wiki - YAML](https://en.wikipedia.org/wiki/YAML).
