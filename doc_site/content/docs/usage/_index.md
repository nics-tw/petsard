---
title: Usage
type: docs
weight: 10
prev: design-structure
next: docs/usage/01_Executor
sidebar:
  open: true
---

## Installation

To install this package, please follow these steps to set up your environment using the `requirements.txt` file:

1. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

2. Upgrade pip:

```bash
python -m pip install --upgrade pip
```

3. Install the required packages using `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Getting Started

We recommend that users write the experimental planning in [YAML format](https://nics-tw.github.io/ /YAML.html), which details in the [PETsARD - User Guide](https://nics-tw.github.io/petsard/), and use [Executor](https://nics-tw.github.io/petsard/Executor.html) in `PETsARD` to conduct the experiment.

### `Executor`

Here is the simplest way to get started with `PETsARD`:

```Python
from petsard import Executor

filename = "Exec_Design.yaml"
exec = Executor(config=filename)
exec.run()
```

### YAML

Here, we use the default methods of each module to construct the simplest 'Exec_Design.yaml'. For specific settings of each module, please refer to the [YAML page](https://nics-tw.github.io/petsard/YAML.html).

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

### Modules

- `Loader`: The module for data loading, see [Loader page](https://nics-tw.github.io/petsard/Loader.html).
  - Benchmark datasets: The usage of `Loader` to download the benchmark datasets, see [Benchmark datasets page](https://nics-tw.github.io/petsard/Benchmark-datasets.html).
- `Splitter`: The module for splitting a dataset into training and validation datasets, see [Splitter page](https://nics-tw.github.io/petsard/Splitter.html).
- `Processor`: The module for data pre/postprocessing, see [Processor page](https://nics-tw.github.io/petsard/Processor.html).
- `Synthesizer`: The module for data synthesising, see [Synthesizer page](https://nics-tw.github.io/petsard/Synthesizer.html).
- `Evaluator`: The module for synthetic data evaluation, see [Evaluator page](https://nics-tw.github.io/petsard/Evaluator.html).
- `Describer`: The module for data description, see [Describer page](https://nics-tw.github.io/petsard/Describer.html).
- `Reporter`: The module for data saving and report output, see [Reporter page](https://nics-tw.github.io/petsard/Reporter.html).
