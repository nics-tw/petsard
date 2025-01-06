---
title: "Benchmark datasets"
draft: false
weight: 17
toc: true
---

Benchmark datasets is an extended feature of the `loader` module in `PETsARD`, providing users with convenient and reliable example data for algorithm feasibility analysis and PETs evaluation. Therefore, this document focuses on the introduction to various datasets. For details on how to use `Loader`, please refer to the `Loader` documentation.

The usage of benchmark datasets is straightforward. All you need to do is to place the corresponding "Benchmark dataset name" in the `filepath` parameter of `Loader`: `benchmark://{Benchmark dataset name}` (case-insensitive). `PETsARD` will download the corresponding dataset and load it into `Loader.data`. You are able to customize the dataset's `metadata` according to other `Loader` parameters. Here is an example of calling the "adult" dataset:

```Python
from petsard import Loader

load = Loader(
    filepath='benchmark://adult-income',
    na_values={k: '?' for k in [
        'workclass',
        'occupation',
        'native-country'
    ]}
)
load.load()
print(loader.data.head(1))
```

## Motivation

Classic benchmark datasets are often used in various data analysis or machine learning scenarios. However, in practical experience, it is common to find inconsistencies for two datasets with the same name. Common patterns include:

- Inconsistent variable encoding transformations (e.g., Original categorical variables recorded as strings, `Label Encoding` encoded versions, or generalized categorical versions).
- Inconsistent row counts (e.g., versions before or after removing missing values).
- Inconsistent columns (e.g., column renaming, or versions after feature engineering).

Usually, The reasons for these patterns are not malicious tampering, but rather for optimization or preprocessing, which is then inadvertently released by subsequent users. Since the preprocessing methods for privacy-enhancing technologies are crucial, obtaining the same version of the benchmark dataset is the recommended experimental procedure in `PETsARD`.

## Storage

The module first downloads the requested raw data, and store it in a "benchmark" folder within the working directory (in lowercase). If the folder does not exist, it will be created automatically (`./benchmark/{Benchmark filename}`). Subsequently, it will follow the regular `Loader` process for loading. When using it, please make sure that you have appropriate permissions and available hardware space.

If the "benchmark" folder already contains a file with the same filename, the program will check if the local data matches the records in `PETsARD`. If they are matched, the program will skip the download and use the local data directly, making it convenient for users to reuse the data. It's important to note that if there is a file with the same name but with different content, `Loader` will issue a warning and stop. In such cases, users should be aware that the benchmark dataset might have been tampered with and contaminating the experimental results potentially.

### Verify SHA256 (optional)

The function for calculating the SHA256 of a file in the `PETsARD` package is as follows:

```Python
from petsard.loader.util import DigestSha256


sha256 = DigestSha256(filepath='benchmark/adult-income.csv')
print(sha256)
```

```plain_text
1f13ee2bf9d7c66098429281ab91fa1b51cbabd3b805cc365b3c6b44491ea2c0
```

## Available Benchmark Datasets

- **Name**: Dataset name.
- **Filename**: Name used in `PETsARD`.
- **Access**: Whether the dataset is public or private.
  - For private datasets, which may have restrictions based on the dataset's authorization or considerations from the data provider, are intended for internal use by the development team and collaborating parties. For any related inquiries, please contact the development team.
- **Columns**: Number of columns.
- **Rows**: Number of rows.
- **File Size**: File size.
  - If it is less than 1 MB, it will be denoted as "< 1 MB".
- **License**: License of the dataset.
- **Too Few Samples**: Less than 5,000 rows.
- **Categorical-dominant**: Over 75% columns are categorical.
- **Numerical-dominant**: Over 75% columns are numerical.
- **Non-dominant**: Neither categorical nor numerical columns are over 75%.
- **Extreme Values**: $\text{abs}(\text{skewness})\geq 3$ for any column. The number of columns meeting the requirement is shown in the table.
- **High Cardinality**: Categories $\geq 10$ for any categorical column. The number of columns meeting the requirement is shown in the table.
- **Hash**: Hash value in Benchmark Datasets.
  - Only the first seven characters are recorded.

### Demographic

<div class="table-wrapper" markdown="block">

|      Benchmark      |                                 Name                                  |     Filename     | Access | Columns |   Rows    | File Size |  License  | Too Few Samples | Categorical-dominant | Numerical-dominant | Non-dominant | Extreme Values | High Cardinality |   Hash    |
| :-----------------: | :-------------------------------------------------------------------: | :--------------: | :----: | :-----: | :-------: | :-------: | :-------: | :-------------: | :------------------: | :----------------: | :----------: | :------------: | :--------------: | :-------: |
|    adult-income     |                       Adult income dataset [^2]                       | adult-income.csv | Public |   15    |  48,842   |  5.1 MB   |  Unknown  |                 |                      |                    |      ✅      |      ✅2       |       ✅3        | `1f13ee2` |

</div>

[^1]: https://www.kaggle.com/datasets/wenruliu/adult-income-dataset
