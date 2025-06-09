---
title: Encoding Categorical Variables
type: docs
weight: 22
prev: docs/tutorial/use-cases/data-preprocessing/handling-missing
next: docs/tutorial/use-cases/data-preprocessing
---

Most synthetic data algorithms only support numerical field synthesis. Even when they directly support categorical field synthesis, it usually involves the synthesizer's built-in preprocessing and post-processing restoration transformations. The CAPE team designed `PETsARD` specifically to control these unpredictable behaviors from third-party packages, recommending active encoding for any fields containing categorical variables:

* Categorical variables: Default to Uniform Encoding, see technical details in the developer manual [Uniform Encoding](docs/developer-guide/uniform-encoder/)

Click the below button to run this example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/use-cases/preproc/encoding-category.ipynb)

```yaml
---
Loader:
  data:
    filepath: 'benchmark/adult-income.csv'
Preprocessor:
  encoding-only:
    # only execute the encoding by their default,
    sequence:
      - 'encoder'
Synthesizer:
  demo:
    method: 'default'
Postprocessor:
  demo:
    method: 'default'
Evaluator:
  demo-quality:
    method: 'sdmetrics-qualityreport'
Reporter:
  output:
    method: 'save_data'
    source: 'Synthesizer'
  save_report_global:
    method: 'save_report'
    granularity: 'global'
...
```

## Custom Configuration

The following configuration is used to customize categorical encoding processing. Setting `method: 'default'` indicates that all fields not specifically configured will use the default processing method.

In the `encoder` block, we apply different encoding strategies for three fields: `workclass` uses uniform encoding for handling categorical values, `occupation` employs label encoding assuming the alphabetical order of occupation categories reflects their hierarchical nature, and `native-country` utilizes one-hot encoding to transform into k-dimensional binary variables, preserving the unique characteristics of each country category while avoiding artificial ordering relationships.

```yaml
Preprocessor:
  encoding-custom:
    sequence:
      - 'encoder'
    encoder:
      workclass: 'encoding_uniform'
      occupation: 'encoding_label'
      native-country: 'encoding_onehot'
```

## Encoding Methods

1. Uniform Encoding (`encoding_uniform`)
  - Converts categorical values to uniformly distributed numbers
  - Suitable for general categorical variables
  - Default encoding method

2. Label Encoding (`encoding_label`)
  - Converts categorical values to consecutive integers
  - Suitable for ordinal categorical variables
  - Preserves order relationships between categories

3. One-Hot Encoding (`encoding_onehot`)
  - Transforms each category into an independent feature column, where each column represents the presence or absence of a category
  - Categorical data is processed as independent features during synthesis and recombined afterward
  - Suitable for variables with fewer categories, as each additional category increases feature dimensionality

4. Date Encoding (`encoder_date`)
   - Converts datetime values into numerical format for synthesis
   - Supports multiple output formats:
       - Date only: Basic date information
       - Datetime: Full date and time information
       - Datetime with timezone: Complete temporal information
   - Provides special features:
       - Custom calendar support (e.g., Minguo calendar)
       - Flexible date parsing with or without format strings
       - Invalid date handling strategies
       - Timezone awareness

You can use different encoding methods for different columns by specifying the appropriate configuration in your settings file.