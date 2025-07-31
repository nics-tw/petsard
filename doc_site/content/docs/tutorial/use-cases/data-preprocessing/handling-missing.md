---
title: Handling Missing Values
type: docs
weight: 21
prev: docs/tutorial/use-cases/data-preprocessing
next: docs/tutorial/use-cases/data-preprocessing/encoding-category
---

Most synthetic data algorithms are probabilistic models, and CAPE team research has shown that the majority cannot directly support missing values (`None`, `np.nan`, `pd.NA`). Even for algorithms that claim to handle missing values, it's challenging to verify the appropriateness of their implementation methods. Therefore, `PETsARD` recommends proactively handling any columns containing missing values:

* Numeric columns: Default to mean imputation (`missing_mean`)
* Categorical/text/date columns: Default to row deletion (`missing_drop`)

 `PETsARD` offers several methods for handling missing values.

Click the below button to run this example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/use-cases/preproc/handling-missing-values.ipynb)

```yaml
---
Loader:
  data:
    filepath: 'benchmark/adult-income.csv'
    na_values: '?' # every '?' in the dataset will be considered as missing value
Preprocessor:
  missing-only:
    # only execute the missing values handler and encoding by their default,
    #   the rest of the preprocessing steps will be skipped
    # keep encoding due to we have categorical features
    sequence:
      - 'missing'
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

## Customized setting

This configuration is used to customize missing value handling. Setting `method: 'default'` indicates that all fields not specifically configured will use default processing methods.

In the `missing` section, three fields are customized: missing values in the `workclass` field will be dropped, missing values in the `occupation` field will be imputed with the mode value, and missing values in the `native-country` field will be filled with the specified value 'Galactic Empire'.

```yaml
Preprocessor:
  missing-custom:
    missing:
      workclass: 'missing_drop'
      occupation: 'missing_mode'
      native-country:
        method: 'missing-simple'
        value: 'Galactic Empire'
```

## Missing Value Handling Methods

1. Drop Missing Values (`missing_drop`)

  - Removes rows containing missing values
  - Suitable when missing values are rare
  - Note: May lose important information

2. Statistical Imputation

  - Mean imputation (`missing_mean`): Fill with column mean
  - Median imputation (`missing_median`): Fill with column median
  - Mode imputation (`missing_mode`): Fill with most frequent value
  - Suitable for different data types:
    - Use mean or median for numerical data
    - Use mode for categorical data

3. Custom Imputation (`missing_simple`)

  - Fill missing values with a specified value
  - Requires setting the `value` parameter
  - Suitable when specific business logic applies

You can use different methods for different columns by specifying the appropriate configuration in your settings file.