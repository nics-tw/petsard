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

The `Reporter` module is responsible for producing the outcomes of `PETsARD`, including both the report outputs and the dataset storage. Since Reporter is primarily designed for users to use directly with `Executor`, we strongly recommend using `Executor` directly.

If you still wish to use `Reporter` independently, please be aware that there are specific requirements for the input format of data. Refer to [`create()` section](https://nics-tw.github.io/PETsARD/Reporter.html#create) of this tutorial for configuration.

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

The `Reporter` has two functions: `'save_data'`, which exports a DataFrame to CSV, and `'save_report'`, which exports the results of the `Evaluator` and `Describer` to CSV. These two functions have different requirements for parameters and input data.

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

The function of `Reporter` is to produce a file output given the matched keywords of the input `data`, or to generate a report given the matched keywords.

Within `Executor`, the `data` is organized into specific [full experiment tuples (full_expt_tuple)](https://nics-tw.github.io/PETsARD/Reporter.html#full_expt_tuple) for `Executor`, according to YAML configurations and the experimental flow.

It is assumed that they have already used various `PETsARD` modules to generate the desired evaluation when users want to use `Reporter` independently. Therefore, by following the module you used and naming each step (experiment name, `'expt_name'`), you can compose the full experiment tuple required by `Reporter`.

It is also fine if the user has generated synthetic data or evaluation using other packages. Please refer to the `PETsARD` user guide and consider which `PETsARD` module functions correspond to those of the other packages you used.

**Parameters**

`method` (`str`): The methods for generating reports. Methods are are limited to `'save_data'` and `'save_report'`.

`output` (`str`, default=`'PETsARD'`, optional): The prefix for the default report output filename is `'PETsARD'`. For the specific output filename, please refer to the [`report()` section](https://nics-tw.github.io/PETsARD/Reporter.html#report).

`source` (`str | List[str]`): To specify which module's or experiment name's (`expt_name`) output to use. Required only for `method = 'save_data'`.

`granularity` (`str`): For the evaluating report specified by `eval`, specify the output data precision. Limited to `'global'`, `'columnwise'`, and `'pairwise'`. Required only for `method = 'save_report'`.

`eval` (`str | List[str]`, optional): To specify which `Evaluator` or `Describer`'s evaluating report to output. Accepted only for `method = 'save_report'`.

## `create()`

Create an `Reporter` object with the given data.

**Parameters**

`data` (`dict`): The input `data` for `Reporter` is a dictionary with one to many key-value pairs. The keys are `tuple` in a specific format, which we refer to as the full experimental tuple (`full_expt_tuple`), and the values are all `pandas.DataFrame`.

`data['exist_report']` (`dict`): `exist_report` is a dictionary containing existing evaluation results, where the keys represent the names of each evaluation experiment (`{eval}_[{granularity}]`), and the values are `pandas.DataFrame`. You can pass old evaluations to `Reporter` by including `exist_report` in the `data` for `Reporter.create()`, allowing `Reporter` to output the old and new evaluations together as a report.

When using `Executor` with YAML, you do not need to manually set `exist_report`. The following is for users who use `Reporter` independently, showing how to collect data from different data sources (`Loader`) and perform the same evaluation report method, and finally how to pass the report results to `Reporter` via `exist_report` for cumulative output.

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

`full_expt_tuple` (`tuple[str]`): The full experiment tuple comes in pairs, with an even number of elements, where each pair represents `({module_name}, {expt_name})`.

`module_name` (`str`): Module Name must be one of the following module names that can be set in `PETsARD`'s YAML, with the addition of `Processsor` for convenience. Each module name can appear in the tuple only once. And the search by `Reporter` is targeted at the last pair of elements.

- [Loader](https://nics-tw.github.io/PETsARD/Loader.html)
- [Splitter](https://nics-tw.github.io/PETsARD/Splitter.html)
- [Processor](https://nics-tw.github.io/PETsARD/Processor.html)
- [Preprocessor](https://nics-tw.github.io/PETsARD/Processor.html)
- [Synthesizer](https://nics-tw.github.io/PETsARD/Synthesizer.html)
- [Postprocessor](https://nics-tw.github.io/PETsARD/Processor.html)
- [Evaluator](https://nics-tw.github.io/PETsARD/Evaluator.html)
- [Describer](https://nics-tw.github.io/PETsARD/Describer.html)

`expt_name` (`str`): Experiment Name is the name given to the experiment for this module. Experiment names can be repeated across different modules. For the standards on module and experiment names, please refer to the [Module and Experiment name section in YAML](https://nics-tw.github.io/PETsARD/YAML.html#module-and-experiment-name).

For `source` in `'save_data'`, the last pair's module name or experiment name should matches source.

If you are certain you are backing up a single piece of synthetic data, then the most basic `('Synthesizer', 'my_expt')` would suffice.

However, since `source` can be specified as either a single string or a list of strings, this offers users greater flexibility to use a single `Reporter(method='save_data')` to output all intermediate data they wish to save from the experiment. For example, the following names can all be identified by `source = ['Synthesizer', 'my_expt']`:

```Python
source = ['Synthesizer', 'my_expt']
data = {
    ('Loader', 'my_expt'): pd.Dataframe,
    ('Loader', 'my_expt', 'Synthesizer', 'my_expt'): pd.Dataframe,
    ('Loader', 'default', 'Synthesizer', 'default'): pd.Dataframe,
}
```

`source` does not support `Evaluator` and `Describer`, please use `method='save_report'` for reporting.

In YAML, if the user specifies `source = 'Splitter'`, `PETsARD` will output all data regardless of the number of splits (`num_samples`). `PETsARD` will specifies different `Splitter` operations separated by experiment names, along with their corresponding split data results.

For `'save_report'`, `Reporter` checks if the last pair's module name is either `Evaluator` or `Describer`, and then checks if the experiment name matches the format `{eval}_[{granularity}]`. In the following example, `Reporter` will only match keys that end with `_[global]`, ensuring consistency in the granularity of the report. In the report, `full_expt_name` and fields from each module are used to differentiate between different report sources.

If you are certain that you want to output a single report, then `('Evaluator', 'my_eval_[global]')` is suffice.

```Python
eval = 'my_eval'
granularity = 'global'
data = {
    ('Loader', 'my_data', 'Synthesizer', 'my_expt', 'Evaluator', 'my_eval_[global]'): pd.Dataframe,
    ('Loader', 'default', 'Synthesizer', 'my_expt', 'Evaluator', 'my_eval_[global]'): pd.Dataframe,
}
```

### `full_expt_name`

The full experiment name is created by assembling the full experiment tuple into a single string according to a specific format, serving as an identifier in the report.

The specific format is `{module_name}[expt_name]`, which means each pair of module name and experiment name is connected in the format, and an underscore `_` is used to link between pairs (`{module_name1}[expt_name1]_{module_name2}[expt_name2]` ...).

- ('Loader', 'default') # A
  - `full_expt_name` = 'Loader[my_expt]'
- ('Loader', 'my_expt', 'Synthesizer', 'default') # A-2
  - `full_expt_name` = 'Loader[my_expt]\_Synthesizer[default]'

## `report()`

Save the report results in particular format.

**Outputs**

Reporter will save the report format as CSV.

For the `'save_data'` method, the output filename will be `{output}_{module-expt_name-pairs}.csv`, such as 'PETsARD_Synthesizer[default].csv'.

`output` (`str`): refers to the `output` in the `Reporter` parameters. If not customized by the user, the default is `PETsARD`.

`module-expt_name-pairs` (`str`): refers to the full experiment name (`full_expt_name`) obtained from the data keys specified by `source`.

For the `'save_report'` method, the output filename will be`{output}[Report]_{eval}_[{granularity}].csv`, such as 'PETsARD[Report]\_[global].csv'.

`output` (`str`): refers to the `output` in the `Reporter` parameters. If not customized by the user, the default is `PETsARD`.

`granularity` (`str`): refers to the `granularity` in the `Reporter` parameters, representing the precision of the report data chosen by the user for this evaluation method.

`eval` (`str`, optional): refers to the `eval` in the `Reporter` parameters, representing the name given by the user for this evaluation method. If `eval` is not specified, it will not be displayed. If one or more `eval`s are specified, they will be connected with a hyphen and written before the granularity.

## `self.config`

The configuration of `Reporter` module:

- In all usage, it includes the `method`, `method_code`, and `output` from the input parameters, along with other parameters (`kwargs`).
- When `method` is set to `'save_data'`, it encompasses `source`.
- When `method` is set to `'save_report'`, it encompasses `eval` and `granularity`.

## `self.reporter`

The instantiated reporter itself, instantiated by a factory method.

## `self.result`

`self.result` will be stored in the form of a dictionary, with the format varying based on `method`.

For `'save_data'`, `self.result` consists of one to multiple key-value pairs, with the full experiment name (`full_expt_name`) as the key of the output results. The number of keys depends on how many pieces of data are matched by `source` in `.create(data)`. And each value is a `pandas.DataFrame`.

For `'save_report'`, `self.result` is a dictionary with the key `'Reporter'`. The values contain the following fields:

`'expt_name'` (`str`): The target of the output report. Comes from user input.

`'granularity'` (`str`)：The granularity of the report. Comes from user input.

`'eval_expt_name'` (`str`): The report experiment name, stored in the format of `{eval}_[{granularity}]`, which is the same as the report file name.

`'full_expt_name'` (`str`)：The full experiment name for this report data. It matches the first column `full_expt_name` in the report file.

`'report'` (`pandas.DataFrame`): The content of the report. It matches the content of the report file.
