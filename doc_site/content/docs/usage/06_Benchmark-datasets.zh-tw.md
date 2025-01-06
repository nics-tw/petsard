---
title: "Benchmark datasets"
draft: false
weight: 17
toc: true
---

基準資料集 (Benchmark datasets) 是 `PETsARD` 的 `loader` 模組的延伸功能，提供使用者方便呼叫、且可靠的範例資料，讓後續的演算法適用性分析或隱私強化驗測都更為方便。因此，本文將著重在各資料集的介紹上，關於 `Loader` 的使用方式詳見 `Loader` 文檔。

基準資料集的使用非常簡單，你只要將各資料集對應的 "Benchmark dataset name" 標籤，以 `benchmark://{Benchmark dataset name}` 的形式放到 `Loader` 的 `filepath` 參數中（大小寫不限），`PETsARD` 便會將對應的資料集下載好，並遵照 `Loader` 的功能加載在 `Loader.data`，而你仍可以按照 `Loader` 的其他參數去自定義資料集的 `metadata`。以下是呼叫 "adult" 資料集的例子：

```Python
from petsard import Loader

load = Loader(
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

## 動機

經典的基準資料集常被用於各種資料分析或機器學習的場合，但實務經驗上，常遇到討論同一個資料集的時候，發現彼此的資料集內容不一致。常見的樣態有：

- 變項編碼轉換不一致（例如分別有原始以字串紀錄的類別變項、`Label Encoding` 過的編碼、概化後的分類的版本）
- 筆數不一致（例如剔除遺失值前或後的版本）
- 欄位不一致（例如欄位重命名，或是欄位經過特徵工程的版本）

造成這些樣態原因常常不是惡意竄改，而是某些優化過、或是前處理過的資料被釋出，而後續使用者不經意地加以傳播所導致。由於隱私強化技術的前處理方式至關重要，於是取得相同版本的基準資料集是 `PETsARD` 建議的實驗程序。

## 儲存

基準資料集功能會先下載你所請求的原始資料，存到工作目錄下方的 "benchmark" 資料夾裡（小寫），如果不存在會自動開一個 (`./benchmark/{Benchmark filename}`)，之後照一般的 `Loader` 流程加載。使用時請注意你的權限與硬體空間。

如果你的 "benchmark" 資料夾裡面已經有該資料集對應的同名檔案了，則程式會檢驗本地端的資料是否與 `PETsARD` 的紀錄一致，如果一致的話，便會省去下載、直接使用本地端資料，方便使用者多次使用。要注意的是如果同檔名但檢驗不一致的話，`Loader` 會告警並停止，此時使用者應該留意到可能儲存到了非原版的基準資料集，這很有可能對實驗結果造成汙染。

### 校驗 SHA256（可選）

`PETsARD` 套件中計算檔案 SHA256 的函式如下：

```Python
from petsard.loader.util import DigestSha256


sha256 = DigestSha256(filepath='benchmark/adult-income.csv')
print(sha256)
```

```plain_text
1f13ee2bf9d7c66098429281ab91fa1b51cbabd3b805cc365b3c6b44491ea2c0
```

## 可用的基準資料集

- **名稱**: 資料集名稱。
- **檔名**: 在 `PETsARD` 中的資料集名稱。
- **權縣**: 公開/私有訪問。
  - 私有資料集包含了資料集本身授權的限制、或是資料提供方的考量等原因，僅供團隊與合作方內部使用。相關問題請聯絡開發團隊。
- **欄位數**: 欄位數。
- **筆數**: 資料筆數。
- **檔案大小**: 檔案大小。
  - 小於 1 MB 的檔案會被標註為 "< 1 MB"。
- **授權**: 資料集的原始授權。
- **小樣本**: 資料集少於 5000 筆資料。
- **類別為主**: 超過 75% 的欄位為類別欄位。
- **數值為主**: 超過 75% 的欄位為數值欄位。
- **均衡型態**: 類別欄位與數值欄位皆未超過 75%。
- **極端值**: 任一欄位 $\text{abs}(\text{skewness})\geq 3$，符合條件的欄位數會標注在表格中。
- **高基數**: 任一類別資料欄位類別數 $\geq 10$，符合條件的欄位數會標注在表格中。
- **哈希值**: 在基準資料集中的哈希值。
  - 僅記錄前七碼。

### 人口學 (Demographic)

<div class="table-wrapper" markdown="block">

|       基準名        |                                 名稱                                  |       檔名       |  權限  | 欄位數 |   筆數    | 檔案大小 |   授權    | 小樣本 | 類別為主 | 數值為主 | 均衡型態 | 極端值 | 高基數 |  哈希值   |
| :-----------------: | :-------------------------------------------------------------------: | :--------------: | :----: | :----: | :-------: | :------: | :-------: | :----: | :------: | :------: | :------: | :----: | :----: | :-------: |
|        adult        |                              Adult [^1]                               |  adult_uci.csv   | Public |   15   |  32,561   |  3.6 MB  | CC BY 4.0 |        |          |          |    ✅    |  ✅2   |  ✅3   | `b1ee591` |
|    adult-income     |                       Adult income dataset [^2]                       | adult-income.csv | Public |   15   |  48,842   |  5.1 MB  |  Unknown  |        |          |          |    ✅    |  ✅2   |  ✅3   | `1f13ee2` |
|    census-income    |                       Census-Income (KDD) [^3]                        |  census_kdd.csv  | Public |   45   |  199,523  | 97.4 MB  | CC BY 4.0 |        |          |          |    ✅    |  ✅4   |  ✅11  | `edda240` |
|     nist-ma2018     | The NIST Diverse Communities Data Excerpts: Massachusetts (2018) [^4] |    ma2018.csv    | Public |   24   |   7244    |  < 1 MB  |  Unknown  |        |          |    ✅    |          |  ✅8   |        | `067b99e` |
|     nist-ma2019     | The NIST Diverse Communities Data Excerpts: Massachusetts (2019) [^4] |    ma2019.csv    | Public |   24   |   7634    |  < 1 MB  |  Unknown  |        |          |    ✅    |          |  ✅8   |        | `5489f7d` |
|  nist-national2018  |   The NIST Diverse Communities Data Excerpts: National (2018) [^4]    | national2018.csv | Public |   24   |   27111   |  1.9 MB  |  Unknown  |        |          |    ✅    |          |  ✅7   |  ✅1   | `d3f9b74` |
|  nist-national2019  |   The NIST Diverse Communities Data Excerpts: National (2019) [^4]    | national2019.csv | Public |   24   |   27253   |  1.9 MB  |  Unknown  |        |          |    ✅    |          |  ✅9   |  ✅1   | `9e039c8` |
|     nist-tx2018     |     The NIST Diverse Communities Data Excerpts: Texas (2018) [^4]     |    tx2018.csv    | Public |   24   |   8,775   |  < 1 MB  |  Unknown  |        |          |    ✅    |          |  ✅8   |        | `f6a6d7b` |
|     nist-tx2019     |     The NIST Diverse Communities Data Excerpts: Texas (2019) [^4]     |    tx2019.csv    | Public |   24   |   9,276   |  < 1 MB  |  Unknown  |        |          |    ✅    |          |  ✅8   |        | `0dab7a8` |
|     acs-person      |           American Community Survey: Person-level [^5] [^6]           |  ss15pusab.csv   | Public |  284   | 3,147,005 |  2.2 GB  |    CC0    |        |          |    ✅    |          |  ✅95  |  ✅2   | `82d9174` |
|    acs-household    |         American Community Survey: Household-level [^5] [^6]          |  ss15husab.csv   | Public |  235   | 1,496,678 |  1.1 GB  |    CC0    |        |          |    ✅    |          |  ✅75  |        | `69381ce` |
|  voter2022-family   |             CPS Youth Voter Data: Family-level [^7] [^8]              |   ffpub23.csv    | Public |   85   |  65,767   | 14.0 MB  |  Unknown  |        |          |    ✅    |          |  ✅53  |        | `0c105bb` |
| voter2022-household |            CPS Youth Voter Data: Household-level [^7] [^8]            |   hhpub23.csv    | Public |  140   |  88,978   | 28.9 MB  |  Unknown  |        |          |    ✅    |          |  ✅58  |  ✅1   | `c88192c` |
|  voter2022-person   |             CPS Youth Voter Data: Person-level [^7] [^8]              |   pppub23.csv    | Public |  829   |  146,133  | 268.0 MB |  Unknown  |        |          |    ✅    |          | ✅513  |  ✅1   | `19b5653` |

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

### 商業 (Business)

<div class="table-wrapper" markdown="block">

|        基準         |                        名稱                        |           檔名           |  權限   | 欄位數 |    筆樹     | 檔案大小 |         授權         | 小樣本 | 類別為主 | 數值為主 | 均衡型態 | 極端值 | 高基數 |  哈希值   |
| :-----------------: | :------------------------------------------------: | :----------------------: | :-----: | :----: | :---------: | :------: | :------------------: | :----: | :------: | :------: | :------: | :----: | :----: | :-------: |
| insurance_synthetic |           insurance_synthetic_data [^9]            | insurance_synthetic.csv  | Public  |   10   |     700     |  < 1 MB  |       Unknown        |   ✅   |          |          |    ✅    |        |  ✅4   | `462bc38` |
|      coil2000       |   Insurance Company Benchmark (COIL 2000) [^10]    |       ticdata.csv        | Public  |   86   |    9,822    |  1.6 MB  |      CC BY 4.0       |        |          |    ✅    |          |  ✅39  |        | `1b5669a` |
|  bank-marketing-1   |             Bank Marketing (01) [^11]              |      bank_full.csv       | Public  |   17   |   45,211    |  3.5 MB  |      CC BY 4.0       |        |          |          |    ✅    |  ✅4   |  ✅2   | `b44507c` |
|  bank-marketing-2   |             Bank Marketing (02) [^11]              | bank_additional_full.csv | Public  |   21   |   41,188    |  4.7 MB  |      CC BY 4.0       |        |          |          |    ✅    |  ✅4   |  ✅2   | `5797716` |
|    credit_score     |         Credit score classification [^12]          |     credit_score.csv     | Public  |   28   |   100,000   | 29.7 MB  |         CC0          |        |          |          |    ✅    |  ✅5   |  ✅15  | `76761c6` |
|  creditcard-fraud   |         Credict Card Fraud Detection [^13]         |      creditcard.csv      | Public  |   31   |   284,807   | 143.8 MB |      DbCL v1.0       |        |          |    ✅    |          |  ✅9   |        | `76274b6` |
|      bank_loan      |             Bank_Loan_modelling [^14]              |      bank_loan.csv       | Public  |   13   |    5,000    |  < 1 MB  |         CC0          |        |          |    ✅    |          |  ✅2   |        | `740e87b` |
|    netflix_prize    |              Netflix Prize data [^15]              |    netflix_prize.csv     | Private |   4    | 100,480,507 |  2.6 GB  |      Restricted      |        |    ✅    |          |          |        |  ✅3   | `d7ff1d6` |
|     bike-sales      |             Bike Sales in Europe [^16]             |        sales.csv         | Public  |   18   |   113,036   | 14.4 MB  |       Unknown        |        |          |          |    ✅    |  ✅3   |  ✅5   | `1b04713` |
|        olist        | Brazilian E-Commerce Public Dataset by Olist [^17] |        olist.csv         | Public  |   22   |   117,601   | 39.2 MB  | CC BY-NC-SA 4.0 DEED |        |          |          |    ✅    |  ✅5   |  ✅13  | `832cffa` |
|     telco-churn     |             Telco_Customer_Churn [^18]             |        telco.csv         | Public  |   21   |    7,043    |  < 1 MB  |       Unknown        |        |    ✅    |          |          |        |  ✅2   | `a0ea74c` |

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

### 生物 (Biology)

<div class="table-wrapper" markdown="block">

|    基準名     |                        名稱                        |       檔名        |  權限  | 欄位數 |  筆數   | 檔案大小 |   授權    | 小樣本 | 類別為主 | 數值為主 | 均衡型態 | 極端值 | 高基數 |  哈希值   |
| :-----------: | :------------------------------------------------: | :---------------: | :----: | :----: | :-----: | :------: | :-------: | :----: | :------: | :------: | :------: | :----: | :----: | :-------: |
|   covertype   |                  Covertype [^19]                   |   covertype.csv   | Public |   55   | 581,012 | 71.7 MB  | CC BY 4.0 |        |          |    ✅    |          |  ✅39  |        | `ea35ca6` |
| penguins_size | Palmer Archipelago (Antarctica) penguin data [^20] | penguins_size.csv | Public |   7    |   344   |  < 1 MB  |    CC0    |   ✅   |          |          |    ✅    |        |        | `aa72859` |
|     iris      |                 Iris dataset [^21]                 |     iris.csv      | Public |   5    |   150   |  < 1 MB  |    CC0    |   ✅   |          |    ✅    |          |        |        | `c52742e` |

</div>

[^19]: https://archive.ics.uci.edu/dataset/31/covertype

[^20]: https://www.kaggle.com/datasets/parulpandey/palmer-archipelago-antarctica-penguin-data

[^21]: https://www.kaggle.com/datasets/himanshunakrani/iris-dataset

### 環境 (Environment)

<div class="table-wrapper" markdown="block">

|       基準名        |           名稱            |          檔名           |  權限  | 欄位數 |  筆數  | 檔案大小 |  授權   | 小樣本 | 類別為主 | 數值為主 | 均衡型態 | 極端值 | 高基數 |  哈希值   |
| :-----------------: | :-----------------------: | :---------------------: | :----: | :----: | :----: | :------: | :-----: | :----: | :------: | :------: | :------: | :----: | :----: | :-------: |
| energydata_complete | energydata_complete [^22] | energydata_complete.csv | Public |   29   | 19,735 | 11.4 MB  | Unknown |        |          |    ✅    |          |  ✅1   |  ✅1   | `2820bf7` |
|     airquality      |   AirQuality_UCI [^23]    |     airquality.csv      | Public |   15   | 9,357  |  < 1 MB  | Unknown |        |          |          |    ✅    |  ✅1   |  ✅7   | `b602b78` |

</div>

[^22]: https://www.kaggle.com/datasets/oladimejiwilliams/energydata-complete

[^23]: https://www.kaggle.com/datasets/parimalbhoyar25/airquality-uci

### 人文科學 (Human Resource)

<div class="table-wrapper" markdown="block">

|     基準名      |                          名稱                           |      檔名      |  權限  | 欄位數 | 筆數  | 檔案大小 |   授權    | 小樣本 | 類別為主 | 數值為主 | 均衡型態 | 極端值 | 高基數 |  哈希值   |
| :-------------: | :-----------------------------------------------------: | :------------: | :----: | :----: | :---: | :------: | :-------: | :----: | :------: | :------: | :------: | :----: | :----: | :-------: |
|    ds_salary    |        Data Science Jobs Salaries Dataset [^24]         | ds_salary.csv  | Public |   11   |  245  |  < 1 MB  |    CC0    |   ✅   |          |          |    ✅    |  ✅1   |  ✅4   | `01e439a` |
| candidates_list |                  Candidates_list [^25]                  | candidates.csv | Public |   24   |  392  |  < 1 MB  |  Unknown  |   ✅   |          |          |    ✅    |  ✅3   |  ✅9   | `d08b595` |
|  ibm-attrition  | IBM HR Analytics Employee Attrition & Performance [^26] | attrition.csv  | Public |   35   | 1,470 |  < 1 MB  | DbCL v1.0 |   ✅   |          |          |    ✅    |        |        | `d11789e` |

</div>

[^24]: https://www.kaggle.com/datasets/saurabhshahane/data-science-jobs-salaries

[^25]: https://www.kaggle.com/datasets/saikrishna20/candidates-list

[^26]: https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset

### 醫療 (Medical)

<div class="table-wrapper" markdown="block">

|      基準名      |                        名稱                         |        檔名         |  權限  | 欄位數 |  筆數   | 檔案大小 |         授權         | 小樣本 | 類別為主 | 數值為主 | 均衡型態 | 極端值 | 高基數 |  哈希值   |
| :--------------: | :-------------------------------------------------: | :-----------------: | :----: | :----: | :-----: | :------: | :------------------: | :----: | :------: | :------: | :------: | :----: | :----: | :-------: |
| nhanes_diabetes  |             NHANES diabetes [^27] [^28]             | nhanes_diabetes.csv | Public |   12   |  4,189  |  < 1 MB  |       Unknown        |   ✅   |          |          |    ✅    |        |        | `aa46d7a` |
| smokingdrinking  | Smoking and Drinking Dataset with body signal [^29] | smokingdrinking.csv | Public |   24   | 991,346 | 103.5 MB | CC BY-NC-SA 4.0 DEED |        |          |    ✅    |          |  ✅14  |        | `d07c6e7` |
| cervical_cancer  |                Cervical Cancer [^30]                | cervical_cancer.csv | Public |   36   |   835   |  < 1 MB  |      Apache 2.0      |   ✅   |          |    ✅    |          |  ✅23  |        | `2e53eb6` |
| heart_cleveland  |          Heart Disease Cleveland UCI [^31]          | heart_cleveland.csv | Public |   14   |   297   |  < 1 MB  |       Unknown        |   ✅   |          |    ✅    |          |        |        | `386015b` |
| breast_cancer-01 |    Breast Cancer Wisconsin (Original) (01) [^32]    |  breast_cancer.csv  | Public |   11   |   699   |  < 1 MB  |      CC BY 4.0       |   ✅   |          |    ✅    |          |  ✅2   |  ✅1   | `870d17a` |
| breast_cancer-02 |    Breast Cancer Wisconsin (Original) (02) [^32]    |      wdbc.csv       | Public |   32   |   569   |  < 1 MB  |      CC BY 4.0       |   ✅   |          |    ✅    |          |  ✅6   |        | `0f5803c` |
| breast_cancer-03 |    Breast Cancer Wisconsin (Original) (03) [^32]    |      wpbc.csv       | Public |   35   |   198   |  < 1 MB  |      CC BY 4.0       |   ✅   |          |    ✅    |          |  ✅1   |  ✅1   | `0bbca0c` |
|     mimic3c      |            MIMIC3c aggregated data [^33]            |     mimic3c.csv     | Public |   28   | 58,976  | 11.3 MB  |       Unknown        |        |          |          |    ✅    |  ✅15  |  ✅4   | `0f1013c` |

</div>

[^27]: https://github.com/kikn88/pwscup2021

[^28]: https://www.kaggle.com/datasets/cdc/national-health-and-nutrition-examination-survey

[^29]: https://www.kaggle.com/datasets/sooyoungher/smoking-drinking-dataset/data

[^30]: https://www.kaggle.com/datasets/ranzeet013/cervical-cancer-dataset

[^31]: https://www.kaggle.com/datasets/cherngs/heart-disease-cleveland-uci

[^32]: https://archive.ics.uci.edu/dataset/15/breast+cancer+wisconsin+origina

[^33]: https://www.kaggle.com/datasets/drscarlat/mimic3c/data

### 電腦科學 (Computer Science)

<div class="table-wrapper" markdown="block">

|   基準名   |           名稱           |     檔名     |  權限  | 欄位數 |   筆數    | 檔案大小 |         授權         | 小樣本 | 類別為主 | 數值為主 | 均衡型態 | 極端值 | 高基數 | 哈希值    |
| :--------: | :----------------------: | :----------: | :----: | :----: | :-------: | :------: | :------------------: | :----: | :------: | :------: | :------: | :----: | :----: | --------- |
|   isolet   |       ISOLET [^34]       |  isolet.csv  | Public |  618   |   7,797   | 31.2 MB  |      CC BY 4.0       |        |          |    ✅    |          |  ✅50  |        | `03b5454` |
| kddcup1999 | KDD Cup 1999 [^35] [^36] |  kddcup.csv  | Public |   42   | 4,898,431 | 644.2 MB |       Unknown        |        |          |    ✅    |          |  ✅25  |  ✅3   | `deffe97` |
|   nslkdd   |   NSL-KDD [^37] [^38]    |  nslkdd.csv  | Public |   43   |  148,517  | 19.8 MB  |     Conditional      |        |          |    ✅    |          |  ✅21  |  ✅3   | `ca3156f` |
|  unswnb15  |  UNSW-NB15 [^39] [^40]   | unswnb15.csv | Public |   36   |  257,673  | 39.2 MB  | CC BY-NC-SA 4.0 DEED |        |          |    ✅    |          |  ✅24  |  ✅4   | `010605e` |
| rt_iot2022 |     RT-IoT2022 [^41]     |  rt_iot.csv  | Public |   84   |  123,117  | 50.0 MB  |      CC BY 4.0       |        |          |    ✅    |          |  ✅65  |  ✅2   | `416a637` |

</div>

[^34]: https://archive.ics.uci.edu/dataset/54/isolet

[^35]: https://kdd.ics.uci.edu/databases/kddcup99/kddcup99.html

[^36]: https://www.kaggle.com/datasets/galaxyh/kdd-cup-1999-data?select=kddcup.data.gz

[^37]: https://www.unb.ca/cic/datasets/nsl.html

[^38]: https://www.kaggle.com/datasets/hassan06/nslkdd

[^39]: https://research.unsw.edu.au/projects/unsw-nb15-dataset

[^40]: https://www.kaggle.com/datasets/dhoogla/unswnb15

[^41]: https://archive.ics.uci.edu/dataset/942/rt-iot2022

### 社會科學 (Social Science)

<div class="table-wrapper" markdown="block">

|         基準名         |                           名稱                           |     檔名     |  權限  | 欄位數 |  筆數  | 檔案大小 |   授權    | 小樣本 | 類別為主 | 數值為主 | 均衡型態 | 極端值 | 高基數 |  哈希值   |
| :--------------------: | :------------------------------------------------------: | :----------: | :----: | :----: | :----: | :------: | :-------: | :----: | :------: | :------: | :------: | :----: | :----: | :-------: |
|        dowjones        |                  Dow Jones Index [^42]                   | dowjones.csv | Public |   16   |  750   |  < 1 MB  | CC BY 4.0 |   ✅   |          |          |    ✅    |  ✅3   |  ✅8   | `5e9d6d2` |
| election-portugal-2019 | Real Time Election Results: Portugal 2019 Data Set [^43] | election.csv | Public |   28   | 21,643 |  3.0 MB  | ODbL v1.0 |        |          |    ✅    |          |  ✅16  |  ✅3   | `2662ee9` |

</div>

[^42]: https://archive.ics.uci.edu/dataset/312/dow+jones+index

[^43]: https://www.kaggle.com/datasets/ishandutta/real-time-election-results-portugal-2019-data-set

### 交通 (Transportation)

<div class="table-wrapper" markdown="block">

|    基準名     |    名稱     |  檔名  |  權限   | 欄位數 |   筆數   | 檔案大小  | 授權 | 小樣本 | 類別為主 | 數值為主 | 均衡型態 | 極端值 |  高基數   | 哈希值 |
| :-----------: | :---------: | :----: | :-----: | :----: | :------: | :-------: | :--: | :----: | :------: | :------: | :------: | :----: | :-------: | :----: |
| PEMS-SF [^44] | pems_sf.csv | Public | 137,710 |  440   | 401.3 MB | CC BY 4.0 |  ✅  |        |    ✅    |          |          |        | `1d4c800` |

</div>

[^44]: https://archive.ics.uci.edu/dataset/204/pems+sf

### 其他 (Others)

<div class="table-wrapper" markdown="block">

|      基準名       |          名稱           |         檔名          |  權限  | 欄位數 |   筆數    | 檔案大小 |   授權    | 小樣本 | 類別為主 | 數值為主 | 均衡型態 | 極端值 | 高基數 |  哈希值   |
| :---------------: | :---------------------: | :-------------------: | :----: | :----: | :-------: | :------: | :-------: | :----: | :------: | :------: | :------: | :----: | :----: | :-------: |
|  winequality_red  |  wine (red wine) [^45]  |  winequality_red.csv  | Public |   12   |   1,599   |  < 1 MB  | CC BY 4.0 |   ✅   |          |    ✅    |          |  ✅2   |        | `7d246d4` |
| winequality_white | wine (white wine) [^45] | winequality_white.csv | Public |   12   |   4898    |  < 1 MB  | CC BY 4.0 |   ✅   |          |    ✅    |          |  ✅1   |        | `91e7afe` |
|        car        |  Car Evaluation [^46]   |        car.csv        | Public |   7    |   1,728   |  < 1 MB  | CC BY 4.0 |   ✅   |    ✅    |          |          |        |        | `0023b86` |
|    poker_hand     |    Poker Hand [^47]     |    poker_hand.csv     | Public |   11   | 1,025,010 | 23.0 MB  | CC BY 4.0 |        |    ✅    |          |          |        |  ✅6   | `f458aba` |

</div>

[^45]: https://archive.ics.uci.edu/dataset/186/wine+quality

[^46]: https://archive.ics.uci.edu/dataset/19/car+evaluation

[^47]: https://archive.ics.uci.edu/dataset/158/poker+hand
