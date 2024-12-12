---
title: "Benchmark datasets"
draft: false
weight: 17
toc: true
---

Benchmark datasets is an extended feature of the `loader` module in `PETsARD`, providing users with convenient and reliable example data for algorithm feasibility analysis and PETs evaluation. Therefore, this document focuses on the introduction to various datasets. For details on how to use `Loader`, please refer to the `Loader` documentation.

The usage of benchmark datasets is straightforward. All you need to do is to place the corresponding "Benchmark dataset name" in the `filepath` parameter of `Loader`: `benchmark://{Benchmark dataset name}` (case-insensitive). `PETsARD` will download the corresponding dataset and load it into `Loader.data`. You are able to customize the dataset's `metadata` according to other `Loader` parameters. Here is an example of calling the "adult" dataset:

```Python
from PETsARD import Loader

load = PETsARD.Loader(
    filepath='benchmark://adult',
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
from PETsARD.loader.util import DigestSha256


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
|        adult        |                              Adult [^1]                               |  adult_uci.csv   | Public |   15    |  32,561   |  3.6 MB   | CC BY 4.0 |                 |                      |                    |      ✅      |      ✅2       |       ✅3        | `b1ee591` |
|    adult-income     |                       Adult income dataset [^2]                       | adult-income.csv | Public |   15    |  48,842   |  5.1 MB   |  Unknown  |                 |                      |                    |      ✅      |      ✅2       |       ✅3        | `1f13ee2` |
|    census-income    |                       Census-Income (KDD) [^3]                        |  census_kdd.csv  | Public |   45    |  199,523  |  97.4 MB  | CC BY 4.0 |                 |                      |                    |      ✅      |      ✅4       |       ✅11       | `edda240` |
|     nist-ma2018     | The NIST Diverse Communities Data Excerpts: Massachusetts (2018) [^4] |    ma2018.csv    | Public |   24    |   7244    |  < 1 MB   |  Unknown  |                 |                      |         ✅         |              |      ✅8       |                  | `067b99e` |
|     nist-ma2019     | The NIST Diverse Communities Data Excerpts: Massachusetts (2019) [^4] |    ma2019.csv    | Public |   24    |   7634    |  < 1 MB   |  Unknown  |                 |                      |         ✅         |              |      ✅8       |                  | `5489f7d` |
|  nist-national2018  |   The NIST Diverse Communities Data Excerpts: National (2018) [^4]    | national2018.csv | Public |   24    |   27111   |  1.9 MB   |  Unknown  |                 |                      |         ✅         |              |      ✅7       |       ✅1        | `d3f9b74` |
|  nist-national2019  |   The NIST Diverse Communities Data Excerpts: National (2019) [^4]    | national2019.csv | Public |   24    |   27253   |  1.9 MB   |  Unknown  |                 |                      |         ✅         |              |      ✅9       |       ✅1        | `9e039c8` |
|     nist-tx2018     |     The NIST Diverse Communities Data Excerpts: Texas (2018) [^4]     |    tx2018.csv    | Public |   24    |   8,775   |  < 1 MB   |  Unknown  |                 |                      |         ✅         |              |      ✅8       |                  | `f6a6d7b` |
|     nist-tx2019     |     The NIST Diverse Communities Data Excerpts: Texas (2019) [^4]     |    tx2019.csv    | Public |   24    |   9,276   |  < 1 MB   |  Unknown  |                 |                      |         ✅         |              |      ✅8       |                  | `0dab7a8` |
|     acs-person      |           American Community Survey: Person-level [^5] [^6]           |  ss15pusab.csv   | Public |   284   | 3,147,005 |  2.2 GB   |    CC0    |                 |                      |         ✅         |              |      ✅95      |       ✅2        | `82d9174` |
|    acs-household    |         American Community Survey: Household-level [^5] [^6]          |  ss15husab.csv   | Public |   235   | 1,496,678 |  1.1 GB   |    CC0    |                 |                      |         ✅         |              |      ✅75      |                  | `69381ce` |
|  voter2022-family   |             CPS Youth Voter Data: Family-level [^7] [^8]              |   ffpub23.csv    | Public |   85    |  65,767   |  14.0 MB  |  Unknown  |                 |                      |         ✅         |              |      ✅53      |                  | `0c105bb` |
| voter2022-household |            CPS Youth Voter Data: Household-level [^7] [^8]            |   hhpub23.csv    | Public |   140   |  88,978   |  28.9 MB  |  Unknown  |                 |                      |         ✅         |              |      ✅58      |       ✅1        | `c88192c` |
|  voter2022-person   |             CPS Youth Voter Data: Person-level [^7] [^8]              |   pppub23.csv    | Public |   829   |  146,133  | 268.0 MB  |  Unknown  |                 |                      |         ✅         |              |     ✅513      |       ✅1        | `19b5653` |

</div>

[^1]: https://archive.ics.uci.edu/dataset/2/adult

[^2]: https://www.kaggle.com/datasets/wenruliu/adult-income-dataset

[^3]: https://archive.ics.uci.edu/dataset/117/census+income+kdd

[^4]: https://github.com/usnistgov/SDNist/tree/main/nist%20diverse%20communities%20data%20excerpts

[^5]:
    https://data.census.gov/
    https://www.census.gov/programs-surveys/acs/data.html

[^6]: https://www.kaggle.com/datasets/census/2015-american-community-survey?select=ss15husa.csv

[^7]: https://www.census.gov/data/tables/time-series/demo/voting-and-registration/p20-586.html

[^8]: https://www.census.gov/programs-surveys/cps/data/datasets.html

### Business

<div class="table-wrapper" markdown="block">

|      Benchmark      |                        Name                        |         Filename         | Access  | Columns |    Rows     | File Size |       License        | Too Few Samples | Categorical-dominant | Numerical-dominant | Non-dominant | Extreme Values | High Cardinality |   Hash    |
| :-----------------: | :------------------------------------------------: | :----------------------: | :-----: | :-----: | :---------: | :-------: | :------------------: | :-------------: | :------------------: | :----------------: | :----------: | :------------: | :--------------: | :-------: |
| insurance_synthetic |           insurance_synthetic_data [^9]            | insurance_synthetic.csv  | Public  |   10    |     700     |  < 1 MB   |       Unknown        |       ✅        |                      |                    |      ✅      |                |       ✅4        | `462bc38` |
|      coil2000       |   Insurance Company Benchmark (COIL 2000) [^10]    |       ticdata.csv        | Public  |   86    |    9,822    |  1.6 MB   |      CC BY 4.0       |                 |                      |         ✅         |              |      ✅39      |                  | `1b5669a` |
|  bank-marketing-1   |             Bank Marketing (01) [^11]              |      bank_full.csv       | Public  |   17    |   45,211    |  3.5 MB   |      CC BY 4.0       |                 |                      |                    |      ✅      |      ✅4       |       ✅2        | `b44507c` |
|  bank-marketing-2   |             Bank Marketing (02) [^11]              | bank_additional_full.csv | Public  |   21    |   41,188    |  4.7 MB   |      CC BY 4.0       |                 |                      |                    |      ✅      |      ✅4       |       ✅2        | `5797716` |
|    credit_score     |         Credit score classification [^12]          |     credit_score.csv     | Public  |   28    |   100,000   |  29.7 MB  |         CC0          |                 |                      |                    |      ✅      |      ✅5       |       ✅15       | `76761c6` |
|  creditcard-fraud   |         Credict Card Fraud Detection [^13]         |      creditcard.csv      | Public  |   31    |   284,807   | 143.8 MB  |      DbCL v1.0       |                 |                      |         ✅         |              |      ✅9       |                  | `76274b6` |
|      bank_loan      |             Bank_Loan_modelling [^14]              |      bank_loan.csv       | Public  |   13    |    5,000    |  < 1 MB   |         CC0          |                 |                      |         ✅         |              |      ✅2       |                  | `740e87b` |
|    netflix_prize    |              Netflix Prize data [^15]              |    netflix_prize.csv     | Private |    4    | 100,480,507 |  2.6 GB   |      Restricted      |                 |          ✅          |                    |              |                |       ✅3        | `d7ff1d6` |
|     bike-sales      |             Bike Sales in Europe [^16]             |        sales.csv         | Public  |   18    |   113,036   |  14.4 MB  |       Unknown        |                 |                      |                    |      ✅      |      ✅3       |       ✅5        | `1b04713` |
|        olist        | Brazilian E-Commerce Public Dataset by Olist [^17] |        olist.csv         | Public  |   22    |   117,601   |  39.2 MB  | CC BY-NC-SA 4.0 DEED |                 |                      |                    |      ✅      |      ✅5       |       ✅13       | `832cffa` |
|     telco-churn     |             Telco_Customer_Churn [^18]             |        telco.csv         | Public  |   21    |    7,043    |  < 1 MB   |       Unknown        |                 |          ✅          |                    |              |                |       ✅2        | `a0ea74c` |

</div>

[^9]: https://www.kaggle.com/datasets/jayrdixit/insurance-synthetic-data

[^10]: https://archive.ics.uci.edu/dataset/125/insurance+company+benchmark+coil+2000

[^11]: https://archive.ics.uci.edu/dataset/222/bank+marketing

[^12]: https://www.kaggle.com/datasets/parisrohan/credit-score-classification?select=train.csv

[^13]: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud

[^14]: https://www.kaggle.com/datasets/itsmesunil/bank-loan-modelling

[^15]: https://www.kaggle.com/datasets/netflix-inc/netflix-prize-data

[^16]: https://www.kaggle.com/datasets/sadiqshah/bike-sales-in-europe

[^17]: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

[^18]: https://www.kaggle.com/datasets/serapgr/telco-customer-churn

### Biology

<div class="table-wrapper" markdown="block">

|   Benchmark   |                        Name                        |     Filename      | Access | Columns |  Rows   | File Size |  License  | Too Few Samples | Categorical-dominant | Numerical-dominant | Non-dominant | Extreme Values | High Cardinality |   Hash    |
| :-----------: | :------------------------------------------------: | :---------------: | :----: | :-----: | :-----: | :-------: | :-------: | :-------------: | :------------------: | :----------------: | :----------: | :------------: | :--------------: | :-------: |
|   covertype   |                  Covertype [^19]                   |   covertype.csv   | Public |   55    | 581,012 |  71.7 MB  | CC BY 4.0 |                 |                      |         ✅         |              |      ✅39      |                  | `ea35ca6` |
| penguins_size | Palmer Archipelago (Antarctica) penguin data [^20] | penguins_size.csv | Public |    7    |   344   |  < 1 MB   |    CC0    |       ✅        |                      |                    |      ✅      |                |                  | `aa72859` |
|     iris      |                 Iris dataset [^21]                 |     iris.csv      | Public |    5    |   150   |  < 1 MB   |    CC0    |       ✅        |                      |         ✅         |              |                |                  | `c52742e` |

</div>

[^19]: https://archive.ics.uci.edu/dataset/31/covertype

[^20]: https://www.kaggle.com/datasets/parulpandey/palmer-archipelago-antarctica-penguin-data

[^21]: https://www.kaggle.com/datasets/himanshunakrani/iris-dataset

### Environment

<div class="table-wrapper" markdown="block">

|      Benchmark      |           Name            |        Filename         | Access | Columns |  Rows  | File Size | License | Too Few Samples | Categorical-dominant | Numerical-dominant | Non-dominant | Extreme Values | High Cardinality |   Hash    |
| :-----------------: | :-----------------------: | :---------------------: | :----: | :-----: | :----: | :-------: | :-----: | :-------------: | :------------------: | :----------------: | :----------: | :------------: | :--------------: | :-------: |
| energydata_complete | energydata_complete [^22] | energydata_complete.csv | Public |   29    | 19,735 |  11.4 MB  | Unknown |                 |                      |         ✅         |              |      ✅1       |       ✅1        | `2820bf7` |
|     airquality      |   AirQuality_UCI [^23]    |     airquality.csv      | Public |   15    | 9,357  |  < 1 MB   | Unknown |                 |                      |                    |      ✅      |      ✅1       |       ✅7        | `b602b78` |

</div>

[^22]: https://www.kaggle.com/datasets/oladimejiwilliams/energydata-complete

[^23]: https://www.kaggle.com/datasets/parimalbhoyar25/airquality-uci

### Human Resource

<div class="table-wrapper" markdown="block">

|    Benchmark    |                          Name                           |    Filename    | Access | Columns | Rows  | File Size |  License  | Too Few Samples | Categorical-dominant | Numerical-dominant | Non-dominant | Extreme Values | High Cardinality |   Hash    |
| :-------------: | :-----------------------------------------------------: | :------------: | :----: | :-----: | :---: | :-------: | :-------: | :-------------: | :------------------: | :----------------: | :----------: | :------------: | :--------------: | :-------: |
|    ds_salary    |        Data Science Jobs Salaries Dataset [^24]         | ds_salary.csv  | Public |   11    |  245  |  < 1 MB   |    CC0    |       ✅        |                      |                    |      ✅      |      ✅1       |       ✅4        | `01e439a` |
| candidates_list |                  Candidates_list [^25]                  | candidates.csv | Public |   24    |  392  |  < 1 MB   |  Unknown  |       ✅        |                      |                    |      ✅      |      ✅3       |       ✅9        | `d08b595` |
|  ibm-attrition  | IBM HR Analytics Employee Attrition & Performance [^26] | attrition.csv  | Public |   35    | 1,470 |  < 1 MB   | DbCL v1.0 |       ✅        |                      |                    |      ✅      |                |                  | `d11789e` |

</div>

[^24]: https://www.kaggle.com/datasets/saurabhshahane/data-science-jobs-salaries

[^25]: https://www.kaggle.com/datasets/saikrishna20/candidates-list

[^26]: https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset

### Medical

<div class="table-wrapper" markdown="block">

|    Benchmark     |                        Name                         |      Filename       | Access | Columns |  Rows   | File Size |       License        | Too Few Samples | Categorical-dominant | Numerical-dominant | Non-dominant | Extreme Values | High Cardinality |   Hash    |
| :--------------: | :-------------------------------------------------: | :-----------------: | :----: | :-----: | :-----: | :-------: | :------------------: | :-------------: | :------------------: | :----------------: | :----------: | :------------: | :--------------: | :-------: |
| nhanes_diabetes  |             NHANES diabetes [^27] [^28]             | nhanes_diabetes.csv | Public |   12    |  4,189  |  < 1 MB   |       Unknown        |       ✅        |                      |                    |      ✅      |                |                  | `aa46d7a` |
| smokingdrinking  | Smoking and Drinking Dataset with body signal [^29] | smokingdrinking.csv | Public |   24    | 991,346 | 103.5 MB  | CC BY-NC-SA 4.0 DEED |                 |                      |         ✅         |              |      ✅14      |                  | `d07c6e7` |
| cervical_cancer  |                Cervical Cancer [^30]                | cervical_cancer.csv | Public |   36    |   835   |  < 1 MB   |      Apache 2.0      |       ✅        |                      |         ✅         |              |      ✅23      |                  | `2e53eb6` |
| heart_cleveland  |          Heart Disease Cleveland UCI [^31]          | heart_cleveland.csv | Public |   14    |   297   |  < 1 MB   |       Unknown        |       ✅        |                      |         ✅         |              |                |                  | `386015b` |
| breast_cancer-01 |    Breast Cancer Wisconsin (Original) (01) [^32]    |  breast_cancer.csv  | Public |   11    |   699   |  < 1 MB   |      CC BY 4.0       |       ✅        |                      |         ✅         |              |      ✅2       |       ✅1        | `870d17a` |
| breast_cancer-02 |    Breast Cancer Wisconsin (Original) (02) [^32]    |      wdbc.csv       | Public |   32    |   569   |  < 1 MB   |      CC BY 4.0       |       ✅        |                      |         ✅         |              |      ✅6       |                  | `0f5803c` |
| breast_cancer-03 |    Breast Cancer Wisconsin (Original) (03) [^32]    |      wpbc.csv       | Public |   35    |   198   |  < 1 MB   |      CC BY 4.0       |       ✅        |                      |         ✅         |              |      ✅1       |       ✅1        | `0bbca0c` |
|     mimic3c      |            MIMIC3c aggregated data [^33]            |     mimic3c.csv     | Public |   28    | 58,976  |  11.3 MB  |       Unknown        |                 |                      |                    |      ✅      |      ✅15      |       ✅4        | `0f1013c` |

</div>

[^27]: https://github.com/kikn88/pwscup2021

[^28]: https://www.kaggle.com/datasets/cdc/national-health-and-nutrition-examination-survey

[^29]: https://www.kaggle.com/datasets/sooyoungher/smoking-drinking-dataset/data

[^30]: https://www.kaggle.com/datasets/ranzeet013/cervical-cancer-dataset

[^31]: https://www.kaggle.com/datasets/cherngs/heart-disease-cleveland-uci

[^32]: https://archive.ics.uci.edu/dataset/15/breast+cancer+wisconsin+origina

[^33]: https://www.kaggle.com/datasets/drscarlat/mimic3c/data

### Computer Science

<div class="table-wrapper" markdown="block">

| Benchmark  |           Name           |   Filename   | Access | Columns |   Rows    | File Size |       License        | Too Few Samples | Categorical-dominant | Numerical-dominant | Non-dominant | Extreme Values | High Cardinality | Hash      |
| :--------: | :----------------------: | :----------: | :----: | :-----: | :-------: | :-------: | :------------------: | :-------------: | :------------------: | :----------------: | :----------: | :------------: | :--------------: | --------- |
|   isolet   |       ISOLET [^34]       |  isolet.csv  | Public |   618   |   7,797   |  31.2 MB  |      CC BY 4.0       |                 |                      |         ✅         |              |      ✅50      |                  | `03b5454` |
| kddcup1999 | KDD Cup 1999 [^35] [^36] |  kddcup.csv  | Public |   42    | 4,898,431 | 644.2 MB  |       Unknown        |                 |                      |         ✅         |              |      ✅25      |       ✅3        | `deffe97` |
|   nslkdd   |   NSL-KDD [^37] [^38]    |  nslkdd.csv  | Public |   43    |  148,517  |  19.8 MB  |     Conditional      |                 |                      |         ✅         |              |      ✅21      |       ✅3        | `ca3156f` |
|  unswnb15  |  UNSW-NB15 [^39] [^40]   | unswnb15.csv | Public |   36    |  257,673  |  39.2 MB  | CC BY-NC-SA 4.0 DEED |                 |                      |         ✅         |              |      ✅24      |       ✅4        | `010605e` |
| rt_iot2022 |     RT-IoT2022 [^41]     |  rt_iot.csv  | Public |   84    |  123,117  |  50.0 MB  |      CC BY 4.0       |                 |                      |         ✅         |              |      ✅65      |       ✅2        | `416a637` |

</div>

[^34]: https://archive.ics.uci.edu/dataset/54/isolet

[^35]: https://kdd.ics.uci.edu/databases/kddcup99/kddcup99.html

[^36]: https://www.kaggle.com/datasets/galaxyh/kdd-cup-1999-data?select=kddcup.data.gz

[^37]: https://www.unb.ca/cic/datasets/nsl.html

[^38]: https://www.kaggle.com/datasets/hassan06/nslkdd

[^39]: https://research.unsw.edu.au/projects/unsw-nb15-dataset

[^40]: https://www.kaggle.com/datasets/dhoogla/unswnb15

[^41]: https://archive.ics.uci.edu/dataset/942/rt-iot2022

### Social Science

<div class="table-wrapper" markdown="block">

|       Benchmark        |                           Name                           |   Filename   | Access | Columns |  Rows  | File Size |  License  | Too Few Samples | Categorical-dominant | Numerical-dominant | Non-dominant | Extreme Values | High Cardinality |   Hash    |
| :--------------------: | :------------------------------------------------------: | :----------: | :----: | :-----: | :----: | :-------: | :-------: | :-------------: | :------------------: | :----------------: | :----------: | :------------: | :--------------: | :-------: |
|        dowjones        |                  Dow Jones Index [^42]                   | dowjones.csv | Public |   16    |  750   |  < 1 MB   | CC BY 4.0 |       ✅        |                      |                    |      ✅      |      ✅3       |       ✅8        | `5e9d6d2` |
| election-portugal-2019 | Real Time Election Results: Portugal 2019 Data Set [^43] | election.csv | Public |   28    | 21,643 |  3.0 MB   | ODbL v1.0 |                 |                      |         ✅         |              |      ✅16      |       ✅3        | `2662ee9` |

</div>

[^42]: https://archive.ics.uci.edu/dataset/312/dow+jones+index

[^43]: https://www.kaggle.com/datasets/ishandutta/real-time-election-results-portugal-2019-data-set

### Transportation

<div class="table-wrapper" markdown="block">

|   Benchmark   |    Name     | Filename | Access  | Columns |   Rows   | File Size | License | Too Few Samples | Categorical-dominant | Numerical-dominant | Non-dominant | Extreme Values | High Cardinality | Hash |
| :-----------: | :---------: | :------: | :-----: | :-----: | :------: | :-------: | :-----: | :-------------: | :------------------: | :----------------: | :----------: | :------------: | :--------------: | :--: |
| PEMS-SF [^44] | pems_sf.csv |  Public  | 137,710 |   440   | 401.3 MB | CC BY 4.0 |   ✅    |                 |          ✅          |                    |              |                |    `1d4c800`     |

</div>

[^44]: https://archive.ics.uci.edu/dataset/204/pems+sf

### Others

<div class="table-wrapper" markdown="block">

|     Benchmark     |          Name           |       Filename        | Access | Columns |   Rows    | File Size |  License  | Too Few Samples | Categorical-dominant | Numerical-dominant | Non-dominant | Extreme Values | High Cardinality |   Hash    |
| :---------------: | :---------------------: | :-------------------: | :----: | :-----: | :-------: | :-------: | :-------: | :-------------: | :------------------: | :----------------: | :----------: | :------------: | :--------------: | :-------: |
|  winequality_red  |  wine (red wine) [^45]  |  winequality_red.csv  | Public |   12    |   1,599   |  < 1 MB   | CC BY 4.0 |       ✅        |                      |         ✅         |              |      ✅2       |                  | `7d246d4` |
| winequality_white | wine (white wine) [^45] | winequality_white.csv | Public |   12    |   4898    |  < 1 MB   | CC BY 4.0 |       ✅        |                      |         ✅         |              |      ✅1       |                  | `91e7afe` |
|        car        |  Car Evaluation [^46]   |        car.csv        | Public |    7    |   1,728   |  < 1 MB   | CC BY 4.0 |       ✅        |          ✅          |                    |              |                |                  | `0023b86` |
|    poker_hand     |    Poker Hand [^47]     |    poker_hand.csv     | Public |   11    | 1,025,010 |  23.0 MB  | CC BY 4.0 |                 |          ✅          |                    |              |                |       ✅6        | `f458aba` |

</div>

[^45]: https://archive.ics.uci.edu/dataset/186/wine+quality

[^46]: https://archive.ics.uci.edu/dataset/19/car+evaluation

[^47]: https://archive.ics.uci.edu/dataset/158/poker+hand
