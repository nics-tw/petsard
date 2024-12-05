---
title: "User Story"
draft: false
weight: 14
toc: true
---

User Story demo is designed to assist users in setting their own configuration file. Enjoy : )

It is recommended to refer to the `demo/User Story...ipynb` user story scenarios in the [demo/REAMD.ME](https://github.com/nics-tw/PETsARD/tree/main/demo) and [yaml/README.md](https://github.com/nics-tw/PETsARD/tree/main/yaml), which helps clarify the implementation of your requirements.

## Environment

In `PETsARD`, the only thing you need to do is to prepare a YAML file following the example and execute the `Executor`.

Assuming your YAML file is `config.yaml`, your Python code would be:

```Python
exec = Executor(config='config.yaml')
exec.run()
```

# User Story A

**Privacy Enhancing Data Generation**

This demo illustrates how to generate privacy-enhanced data using `PETsARD`.

In this demonstration, you, as the user, already possess a data file locally, and `PETsARD` will assist you in loading that file and then generating a privacy-enhanced version of it.

Besides, privacy-enhancing algorithms often have restrictions on specific formats and/or specific data processing procedures. `PETsARD` takes care of these as well. `PETsARD` offers both default and customizable preprocessing and postprocessing workflows to help users get started quickly.

## User Story A-1

**Default Synthesizing Procedure**

Given an original dataset without specifying any algorithm, the pipeline will generate a list of privacy-enhanced datasets using the default algorithms.

## User Story A-2

**Customized Synthesizing Procedure**

Given an original dataset, specified privacy enhancing data generation algorithms and parameters, the pipeline will generate a privacy-enhanced dataset.

# User Story B

**Privacy Enhancing Data Generation and Evaluation**

This demo will show how to generate and evaluate privacy-enhanced data using `PETsARD`.

In this demonstration, you, as the user, already possess a data file locally, and `PETsARD` will assist you in loading that file and then generating a privacy-enhanced version of it.

## User Story B-1

**Default Evaluating Procedure**

Following User Story A, if users enable the 'evaluate' step, the evaluation module will create a report covering default privacy risk and utility metrics.

## User Story B-2

**Customized Evaluating Procedure**

Following User Story B-1, if specific types of metrics are set or a customized evaluation script is provided, the module will create a customized evaluation report.

# User Story C

**Privacy Enhancing Data Evaluation**

This demo will show how to evaluate privacy-enhanced data using `PETsARD`.

In this demonstration, you, as the user, already have a data file on your local machine, as well as its corresponding synthetic data results, which are likely from your existing privacy protection service. `PETsARD` will assist you in reading these files and evaluating the results, helping you compare your current solution with other technologies.

## User Story C-1

**Describing Procedure**

Given a dataset as an input, the pipeline can go through the 'describe' module to get a summary of the dataset.

## User Story C-2

**Evaluating based on given data**

Given an original dataset and a privacy-enhanced dataset to the evaluation module, the pipeline will create a report covering default/general metrics of privacy risk and utility.

The 'custom data' here indicates the situation that users already have synthesizing data, and you require `PETsARD` for the evaluation only. Therefore, please refer to C-1 and C-2 for the usage of `'custom_data'` on different module given certain `Evaluator`.

### User Story C-2a

C-2a demonstrates the evaluation approach of the `Evaluator` that comparing 'original data' with 'synthetic data', for instance, using`method = 'default'` or tools starting with `'sdmetrics-'` from SDMetrics.

The 'original data' can be directly loaded using the `Loader`. At this point, the 'synthetic data' needs to be placed in the `Synthesizer`, using `method = 'custom_data'` to specify custom data.

After using `method = 'custom_data'`, similar to the `Loader`, the file location is specified using `filepath`.

### User Story C-2b

C-2b demonstrates the evaluation approach of the Evaluator that comparing 'original data used in synthesis' (abbreviated as ori), 'original data not used in synthesis' (abbreviated as control), and 'synthesized data' (abbreviated as syn) at the same time, for example, using tools starting with `method = 'anonymeter-'` from Anonymeter.

'Used in synthesis' and 'Not used in synthesis' are achieved by using the `Splitter` module. Therefore, please apply `method = 'custom_data'` to the `Splitter`, where `filepath` requires two inputs: `'ori'` corresponds to 'original data used in synthesis', and `'control'` corresponds to 'original data not used in synthesis'. The setting method for 'synthesized data' in the `Synthesizer` remains the same as C-2a.

Here, we also demonstrate the evaluation with `method = 'default'`. For scenarios directly comparing 'original data' and 'synthesized data', C-2b automatically considers the `'ori'` in the `Splitter` as 'original data' for comparison, obtaining results from both SDMetrics and Anonymeter. User should take care of their own data partition method to ensure the representativeness of the original data.

# User Story D

**Research on Benchmark datasets**

This demo will show how to use `PETsARD`'s benchmark datasets to evaluate synthetic algorithms.

In this demonstration, as an advanced user with a basic understanding of different differential privacy/synthetic data technologies and their corresponding evaluation metrics, you aim to assess the differences between technologies and other academic and practical issues.

PETsARD provides a complete platform that, which helps you to obtain comprehensive data support at ease on academic work or development. This enables you to easily obtain comprehensive data support, focusing on your academic or development work.

## User Story D-1

**Synthesizing on default data**

With a specified data generation algorithm, a default benchmark dataset collection will serve as inputs, and the pipeline will generate the corresponding privacy-enhanced datasets as output, using the selected algorithm.

## User Story D-2

**Synthesizing on multiple data**

Following User Story D-1, the user can specify a list of datasets instead.

## User Story D-3

**Synthesizing and Evaluating on default data**

Following User Story D-1, if users enable the evaluation step, the evaluation module will create a report covering default privacy risk and utility metrics for all datasets.
