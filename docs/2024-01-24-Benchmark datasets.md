# Benchmark datasets

**Benchmark datasets** is an extended feature of the `Loader` module in `PETsARD` (`Benchmarker`), providing users with convenient and reliable example data for easier algorithm applicability analysit or Privacy-enhancement evaluating. Therefore, this document will focus on introducing various datasets. For details on how to use `Loader`, please refer to the `Loader` documentation.

Using benchmark datasets is straightforward. You only need to place the corresponding **"Benchmark name"** label for each dataset in the `filepath` parameter of `Loader` in the format `benchmark://{Benchmark name}` (case-insensitive). `PETsARD` will then download the corresponding dataset and load it into `Loader.data`, allowing you to customize the dataset's `metadata` according to other Loader parameters. Here is an example of calling the "adult" dataset:

**基準資料集** (**Benchmark datasets**) 是 `PETsARD` 的 `Loader` 模組的延伸功能 (`Benchmarker`)，提供使用者方便呼叫、且可靠的範例資料，讓後續的演算法適用性分析或隱私強化驗測都更為方便。因此，本文將著重在各資料集的介紹上，關於 `Loader` 的使用方式詳見 `Loader` 文檔。

基準資料集的使用非常簡單，你只要將各資料集對應的 **"Benchmark name"** 標籤，以 `benchmark://{Benchmark name}` 的形式放到 `Loader` 的 `filepath` 參數中（大小寫不限），`PETsARD` 便會將對應的資料集下載好，並遵照 `Loader` 的功能加載在 `Loader.data`，而你仍可以按照 `Loader` 的其他參數去自定義資料集的 `metadata`。以下是呼叫 "adult" 資料集的例子：

```python
loader = PETsARD.Loader(
    filepath='benchmark://adult',
    na_values={k: '?' for k in [
        'workclass',
        'occupation',
        'native-country'
    ]}
)
print(loader.data.head(1))
```

## data lists

- **Name** `benchmark://{Benchmark}`: The labels for benchmark datasets, used as input, are case-insensitive. 基準資料集的標籤，用於輸入，大小寫不限。
- **Filename** ( `./benchmark/{Benchmark filename}`): The actual file will be stored locally and read with the filename. 實際會存到本地、並讀取資料的檔名。
- **Access**: Public or Private. 公開或私有。
- **Columns**: Columns number. 欄位數。
- **Rows**: Rows number. 行數。
- **File size**: File size. 檔案大小。
- **License**: License of datasets. 資料集的授權。
- **Hash**: Top 6 digits of Hash values. 哈希值的前六位。

<!-- This <div> here is special function for sighingnow/jekyll-gitbook -->
<div class="table-wrapper" markdown="block">

|Name              |Filename                         |Access |Columns|Rows       |File size|License        |Hash    |
|:----------------:|:-------------------------------:|:-----:|:-----:|:---------:|:-------:|:-------------:|:------:|
|adult             |adult.csv                        |Public |15     |     48,842|     5 MB|CC BY 4.0      |`1f13ee`|
|alarm             |TODO                             |Public |TODO   |TODO       |TODO     |TODO           |TODO    |
|car_insurance     |TODO                             |Public |TODO   |TODO       |TODO     |TODO           |TODO    |
|census            |TODO                             |Public |TODO   |TODO       |TODO     |CC BY-NC-SA 4.0|TODO    |
|coil2000          |TODO                             |Public |TODO   |TODO       |TODO     |TODO           |TODO    |
|covtype           |TODO                             |Public |TODO   |TODO       |TODO     |CC BY-NC-SA 4.0|TODO    |
|ds_salaries       |ds_salaries.csv                  |Public |11     |        607|TODO     |CC0            |TODO    |
|expedia_hotel_logs|TODO                             |Public |TODO   |TODO       |TODO     |TODO           |TODO    |
|intrusion         |TODO                             |Public |TODO   |TODO       |TODO     |TODO           |TODO    |
|nhanes_diabetes   |B.csv                            |Public |12     |      4,190|    <1 MB|TODO           |TODO    |
|smoking_driking   |smoking_driking_dataset_Ver01.csv|Public |24     |    991,346|   104 MB|CC BY-NC-SA 4.0|TODO    |
|uk_us_pf_household|TODO                             |Public |TODO   |  3,094,494|   167 MB|TODO           |TODO    |
|uk_us_pf_person   |TODO                             |Public |TODO   |  7,688,060|    83 MB|TODO           |TODO    |
|uk_us_pf_prop_net |TODO                             |Public |TODO   |166,971,542| 6,117 MB|TODO           |TODO    |
|us_census_1940    |TODO                             |Private|TODO   |TODO       |TODO     |Restricted     |TODO    |

</div>

### **adult**

- Name: **Adult**
- Alias: **Adult income**, **Census Income**
- Subject Area: **Social Science**
- Precision: 1 Person 1 records
- Columns: 15
  - Continuous: TODO
  - Datetime: 0
  - Discrete: TODO
  - Float: TODO
  - String: TODO
  - Int: TODO
- Missing %: Yes (TODO)
  - Special NA value: "?"
- Hash: `1f13ee2bf9d7c66098429281ab91fa1b51cbabd3b805cc365b3c6b44491ea2c0`

Filtered extraction from 1994 US Census.

來自 1994 年美國人口普查的過濾資料。

```Python
loader = PETsARD.Loader(
    filepath='benchmark://adult',
    na_values={k: '?' for k in [
        'workclass',
        'occupation',
        'native-country'
    ]}
)
print(loader.data.head(1))
```

https://archive.ics.uci.edu/dataset/2/adult
https://archive.ics.uci.edu/dataset/20/census+income
https://www.kaggle.com/datasets/wenruliu/adult-income-dataset

### **alarm**

- Name: **A Logical Alarm Reduction Mechanism (ALARM) monitoring system (synthetic) data set**
- Alias:
- Subject Area: **Health and Medicine**
- Precision: 1 House 1 records
- Columns: TODO
  - Continuous: TODO
  - Datetime: TODO
  - Discrete: TODO
  - Float: TODO
  - String: TODO
  - Int: TODO
- Missing %: Yes (TODO)
  - Special NA value: TODO

https://www.bnlearn.com/documentation/man/alarm.html

### **car_insurance**

- Name: **Insurance evaluation network (synthetic) data set**
- Alias: **insurance**
- Subject Area: **Business**
- Precision: 1 Person 1 records
- Columns: TODO
  - Continuous: TODO
  - Datetime: TODO
  - Discrete: TODO
  - Float: TODO
  - String: TODO
  - Int: TODO
- Missing %: Yes (TODO)
  - Special NA value: TODO

The naming as "car_insurance" is because the name "insurance" may be confused with many datasets provided by insurance companies on Kaggle. This is just a temporary name.

命名為 "car_insurance" 是因為 "insurance" 這個名稱可能會跟許多 Kaggle 上保險公司提供的資料集混淆。這只是暫時的命名。

### **census**

- Name: **Census-Income (KDD)**
- Alias:
- Subject Area: **Social Science**
- Precision: 1 Person 1 records
- Columns: 41
  - Continuous: TODO
  - Datetime: TODO
  - Discrete: TODO
  - Float: TODO
  - String: TODO
  - Int: TODO
- Missing %: Yes (TODO)
  - Special NA value: TODO

The weighted census data extracted from the 1994 and 1995 Current Population Surveys conducted by the U.S. Census Bureau.

從美國人口普查局進行的1994年和1995年的加權人口普查數據。

https://archive.ics.uci.edu/dataset/117/census+income+kdd

### **coil2000**

- Name: **Insurance Company Benchmark (COIL 2000)**
- Alias:
- Subject Area: **Social Science**
- Precision: 1 Person 1 records
- Columns: 86
  - Continuous: TODO
  - Datetime: TODO
  - Discrete: TODO
  - Float: TODO
  - String: TODO
  - Int: TODO
- Missing %: Yes (TODO)
  - Special NA value: TODO

The caravan insurance dataset from the Netherlands, used for the Computational Intelligence and Learning (CoIL) Challenge 2000 in Europe.

荷蘭的房車保險資料集，用於歐洲計算智能和學習（CoIL）挑戰賽 2000。

https://archive.ics.uci.edu/dataset/125/insurance+company+benchmark+coil+2000

### **covtype**

- Name: **Forest cover types datasets**
- Alias:
- Subject Area: **Climate and Enviorment**
- Precision: 1 geospatial 1 records
- Columns: TODO
  - Continuous: TODO
  - Datetime: TODO
  - Discrete: TODO
  - Float: TODO
  - String: TODO
  - Int: TODO
- Missing %: Yes (TODO)
  - Special NA value: TODO

This study area includes four wilderness areas located in the Roosevelt National Forest of northern Colorado, combined data from US Forest Service (USFS) and US Geological Survey (USGS). Predicting forest cover type from cartographic variables only.

這個研究區域包括科羅拉多北部羅斯福國家森林中的四個荒野地區，結合了美國森林服務（USFS）和美國地質調查（USGS）的數據。僅從地圖變數預測森林覆蓋類型。

https://archive.ics.uci.edu/dataset/31/covertype

### **ds_salaries**

- Name: **Data Science Jobs Salaries Dataset**
- Alias:
- Subject Area: **Business**
- Precision: 1 Person 1 records
- Columns: TODO
  - Continuous: TODO
  - Datetime: TODO
  - Discrete: TODO
  - Float: TODO
  - String: TODO
  - Int: TODO
- Missing %: Yes (TODO)
  - Special NA value: TODO

Salary data for Data Scientists from 2020 to 2021 sourced from ai-jobs.net.

來自 ai-jobs.net 的 2020~2021年中的資料科學家薪資資料。

https://www.kaggle.com/datasets/saurabhshahane/data-science-jobs-salaries
https://ai-jobs.net/salaries/form/

### **expedia_hotel_logs**

- Name: **Expedia Hotel Recommendations datasets**
- Alias:
- Subject Area: **Computer Science**
- Precision: 1 Recommendations 1 records
- Columns: TODO
  - Continuous: TODO
  - Datetime: TODO
  - Discrete: TODO
  - Float: TODO
  - String: TODO
  - Int: TODO
- Missing %: Yes (TODO)
  - Special NA value: TODO

From Expedia Hotel Recommendations competitions in Kaggle.

來自 Kaggle 的 Expedia 飯店推薦競賽。

https://www.kaggle.com/competitions/expedia-hotel-recommendations/data

### **intrusion**

- Name: **Intrusion Detector Learning**
- Alias:
- Subject Area: **Computer Science**
- Precision: 1 Connection 1 records
- Columns: TODO
  - Continuous: TODO
  - Datetime: TODO
  - Discrete: TODO
  - Float: TODO
  - String: TODO
  - Int: TODO
- Missing %: Yes (TODO)
  - Special NA value: TODO

This dataset contains network traffic with simulated attacks on a U.S. Air Force LAN and was prepared and managed by MIT Lincoln Labs for the 1998 DARPA Intrusion Detection Evaluation Program, aimed at surveying and evaluating research in intrusion detection. The dataset provides a standardized set of audited data, including a wide variety of intrusions simulated in a military network environment. A version of this dataset was used in the 1999 KDD intrusion detection contest.

這個資料集包含模擬對美國空軍局域網的攻擊的網絡流量，是為了 1998 年 DARPA 入侵檢測評估計劃而由MIT林肯實驗室準備的，旨在調查和評估入侵檢測領域的研究，並使用在 1999 年的 KDD 入侵檢測競賽。

https://kdd.ics.uci.edu/databases/kddcup99/task.html

### **iris**

- Name: **Fisher's Iris data set**
- Alias:
- Subject Area: **Biology**
- Precision: 1 Organism 1 records
- Columns: TODO
  - Continuous: TODO
  - Datetime: TODO
  - Discrete: TODO
  - Float: TODO
  - String: TODO
  - Int: TODO
- Missing %: Yes (TODO)
  - Special NA value: TODO

The Iris dataset, was originally collected by Edgar Anderson to quantify morphological variations in Iris flowers and made famous by Ronald Fisher in 1936. It includes measurements of sepals and petals from three Iris species, usually used to develop a species-distinguishing model in machine learning field.

Iris 資料集，最初是由 Edgar Anderson 收集以量化鳶尾花的形態變異，並在1936年被 Ronald Fisher 使用而知名。它包括三個鳶尾花物種的花萼和花瓣的測量，在機器學習領域上常用於開發區分物種的模型。

來自 Kaggle 的 Expedia 飯店推薦競賽。

https://en.wikipedia.org/wiki/Iris_flower_data_set

### **nhanes_diabetes**

- Name: **National Health and Nutrition Examination Survey (NHANES) 2015-2016 diabetes**
- Alias:
- Subject Area: **Health and Medicine**
- Precision: 1 Person 1 records
- Columns: 12
  - Continuous: TODO
  - Datetime: TODO
  - Discrete: TODO
  - Float: TODO
  - String: TODO
  - Int: TODO
- Missing %: TODO (TODO)
  - Special NA value: TODO

**"nhanes_diabetes"** is integrated from subsets of NHANES data, and is used in PWSCup2021. Composition details can be found in PWSCup2021 GitHub `activ_diabet9_csv.py`. Involves the following subdatasets:

**"nhanes_diabetes"** is named this way because "diabet" is commonly used in the community, especially on Kaggle, to refer to other datasets.

**"nhanes_diabetes"** 是由 NHANES 資料子集整合而成，並在 PWSCup2021 中使用。有關組成詳情可在 PWSCup2021 GitHub 的 `activ_diabet9_csv.py` 中找到。涉及以下子資料集：

- DIQ_I - [Questionnaire Data] Diabetes [問卷資料] 糖尿病
- BMX_I - [Examination Data] Body Measures [檢查資料] 身體測量
- PAQ_I - [Questionnaire Data] Physical Activity [問卷資料] 體育活動
- GHB_I - [Laboratory Data] Glycohemoglobin [實驗室資料] 醣化血色素
- DPQ_I - [Questionnaire Data] Mental Health - Depression Screener [問卷資料] 心理健康 - 憂鬱篩檢
- INQ_I - [Questionnaire Data] Income [問卷資料] 收入

因為 "diabet" 在社群上、尤其是 Kaggle、通常是指其他的資料集，所以本資料集命名為 **"nhanes_diabetes"**。

```Python
loader = PETsARD.Loader(
    filepath='benchmark://nhanes_diabetes',
    header_exist=False,
    header_names=[
      'gen','age','race','edu','mar',
      'bmi','dep','pir','gh','mets',
      'qm','dia'
    ]
)
print(loader.data.head(1))
```
        
https://www.iwsec.org/pws/2021/index.html
https://github.com/kikn88/pwscup2021
https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx?BeginYear=2015
https://hackmd.io/@petworks/rJ-UOh9Rn/https%3A%2F%2Fhackmd.io%2F%40petworks%2Fr15yF3zYT

### **smoking_driking**

- Name: **Smoking and Drinking Dataset with body signal**
- Alias:
- Subject Area: **Health and Medicine**
- Precision: 1 Person 1 records
- Columns: 24
  - Continuous: TODO
  - Datetime: TODO
  - Discrete: TODO
  - Float: TODO
  - String: TODO
  - Int: TODO
- Missing %: Yes (TODO)
  - Special NA value: TODO

Provided by the National Health Insurance Service in Korea, a dataset on smoking, drinking, and body signal (physiological indicators) with sensitive information removed. Dataset labels are named based on the original dataset file names.

由韓國健康保險公團提供，去除機敏資料的抽菸、飲酒、與生理指標資料集。資料集標籤按照原始資料集檔案名稱取名。

https://www.kaggle.com/datasets/sooyoungher/smoking-drinking-dataset/data


### **uk_us_pf_household**

- Name: **UK-US PETs prize challenges - Pandemic Forecasting: Household datasets**
- Alias:
- Subject Area: **Health and Medicine**
- Precision: 1 House 1 records
- Columns: TODO
  - Continuous: TODO
  - Datetime: TODO
  - Discrete: TODO
  - Float: TODO
  - String: TODO
  - Int: TODO
- Missing %: Yes (TODO)
  - Special NA value: TODO

The data is sourced from the Synthetic Epidemiology Challenge within the U.S.-UK Privacy Enhancement Technologies prize challenges. It should be noted that it currently only includes data entity two provided by the University of Virginia from the U.S., and selects only three representative datasets.

資料來源於美國英國隱私強化技術比賽當中的合成流行病學比賽項目。須注意的是目前只包含美國方的維吉尼亞大學提供的資料實體二，且僅挑選三個代表性資料集。

https://petsprizechallenges.com/
https://prepare-vo.org/synthetic-pandemic-outbreaks
https://dataverse.lib.virginia.edu/dataset.xhtml?persistentId=doi:10.18130/V3/ZOG1FF
https://net.science/files/resources/datasets/PET_Prize_PandemicForecasting/

### **uk_us_pf_person**

- Name: **UK-US PETs prize challenges - Pandemic Forecasting: Person datasets**
- Alias:
- Subject Area: **Health and Medicine**
- Precision: 1 Person 1 records
- Columns: TODO
  - Continuous: TODO
  - Datetime: TODO
  - Discrete: TODO
  - Float: TODO
  - String: TODO
  - Int: TODO
- Missing %: Yes (TODO)
  - Special NA value: TODO

See **uk_us_pf_household** for more details.

詳情請見 **uk_us_pf_household**。

### **uk_us_pf_prop_net**

- Name: **UK-US PETs prize challenges - Pandemic Forecasting: Population Network datasets**
- Alias:
- Subject Area: **Health and Medicine**
- Precision: 1 Connection 1 records
- Columns: TODO
  - Continuous: TODO
  - Datetime: TODO
  - Discrete: TODO
  - Float: TODO
  - String: TODO
  - Int: TODO
- Missing %: Yes (TODO)
  - Special NA value: TODO

See **uk_us_pf_household** for more details.

詳情請見 **uk_us_pf_household**。

### **us_census_1940**

- Name: **Version 8.0 Extract of 1940 Census full-count dataset**
- Alias: **US Census**
- Subject Area: **Social Science**
- Precision: 1 Person 1 records
- Columns: 15
  - Continuous: TODO
  - Datetime: TODO
  - Discrete: TODO
  - Float: TODO
  - String: TODO
  - Int: TODO
- Missing %: TODO (TODO)
  - Special NA value: TODO

Any IPUMS USA Full Count data is not redistribute without permission, so we set as "Private"

未經許可，不得重新分發任何 IPUMS USA 全統計資料，故設定為 "Private"。

https://usa.ipums.org/usa/1940CensusDASTestData.shtml

## Data summary

### Subject Area

**Subject Area** refers to the classification of datasets based on the [UC Irvine Machine Learning Repository](https://archive.ics.uci.edu/).

**Subject Area** 是根據[加州大學爾灣分校機器學習資料庫](https://archive.ics.uci.edu/)的資料集分類。

<!-- This <div> here is special function for sighingnow/jekyll-gitbook -->
<div class="table-wrapper" markdown="block">

|Subject Area          |Counts|Public                                                                                  |Private       |
|:--------------------:|:----:|:--------------------------------------------------------------------------------------:|:------------:|
|Biology               |     1|iris                                                                                    |              |
|Business              |     3|car_insurance, ds_salaries, expedia_hotel_logs,                                         |              |
|Climate and Enviorment|     1|covtype                                                                                 |              |
|Computer Science      |     1|intrusion                                                                               |              |
|Engineering           |     0|                                                                                        |              |
|Games                 |     0|                                                                                        |              |
|Health and Medicine   |     5|nhanes_diabetes, smoking_driking, uk_us_pf_household, uk_us_pf_person, uk_us_pf_prop_net|              |
|Law                   |     0|                                                                                        |              |
|Physics and Chemistry |     0|                                                                                        |              |
|Social Science        |     4|adult, census, coil2000                                                                 |us_census_1940|
|Other                 |     0|                                                                                        |              |

</div>

- **car_insurance** be categorized in **Business**, but **coil2000** from UCI ML have been categorized in **Social Science**.

### Precision

<!-- This <div> here is special function for sighingnow/jekyll-gitbook -->
<div class="table-wrapper" markdown="block">

|Precision        |Counts     |Public                      |Private|
|:---------------:|:---------:|:--------------------------:|:-----:|
|By Connection    |          2|intrusion, uk_us_pf_prop_net|       |
|By Geospatial    |          1|covtype                     |       |
|By House         |          1|uk_us_pf_household          |       |
|By Organism      |          1|iris                        |       |
|By Person        |All remains|(skip)                      |(skip) |
|By Recommendation|          1|expedia_hotel_logs          |       |

</div>

### Inclusion Reasons

The inclusion of the Benchmark dataset is based on retaining only the most significant reason.

納入基準資料集原因只保留最重要的一個原因。

<!-- This <div> here is special function for sighingnow/jekyll-gitbook -->
<div class="table-wrapper" markdown="block">

|Reason           |Counts|Public                                                         |Private       |
|:---------------:|:----:|:-------------------------------------------------------------:|:------------:|
|Common PETs      |     2|adult, census                                                  |              |
|Common DS/ML     |     2|coil2000, iris                                                 |              |
|Taiwan guidelines|     1|nhanes_diabetes                                                |              |
|112 ITRI         |     1|ds_salaries, smoking_driking                                   |              |
|Precision        |     3|covtype, expedia_hotel_logs, uk_us_pf_person, uk_us_pf_prop_net|              |
|Replication      |     1|                                                               |us_census_1940|
|Competition      |     1|uk_us_pf_household                                             |              |
|Others           |     1|alarm, car_insurance, intrusion                                |              |

</div>

- Common PETs：Commonly Used in PETs fields 常用於隱私強化技術領域
- Common DS/ML：Commonly Used in Data Science/Machine Learning 常用於資料科學/機器學習領域
  - The value of "iris" in privacy protection research is questionable "iris" 在隱私保護研究的價值是存疑的
- Taiwan guidelines: The Taiwan guideline handbook has been utilized 臺灣指引手冊有使用
  -  PETsWork: included ["nhanes_diabetes"](https://hackmd.io/@petworks/rJ-UOh9Rn/https%3A%2F%2Fhackmd.io%2F%40petworks%2Fr15yF3zYT)
- 112 ITRI: (Industrial Technology Research Institute) 工研院112年計畫成果有使用
  - Some of the data from 112 ITRI are solely test data created by the Academia Sinica, and the dataset size is too small so we excluded. 有些工研院112年使用的只是中研院產生的測試用假資料，且資料大小太小，故不納入。
    - Included **fake_job.csv**, **fake_lat.csv**, **fake_lon.csv**, **revenue_tw_id.csv**, **sports_id.csv**, and **zh_tw_header.csv**.
- Precision: Enrich Precision type 增加多元精度類型
  - The value of **covtype** in privacy protection research is questionable **covtype** 在隱私保護研究的價值是存疑的
- Replication: Replicated research findings 重製研究成果
- Competition: Used in a competition 在隱私強化技術競賽用過
- Others: Others/Uncategorized 其他/未分類
  - some of **SDGym** datasets have be categorized here because not sure are these datasets popular enough. 有些 **SDGym** 的資料集被分在此，是由於不清楚這些資料集是否夠知名。

### Mention in Research

<!-- This <div> here is special function for sighingnow/jekyll-gitbook -->
<div class="table-wrapper" markdown="block">

|Topic     |Paper|Counts|Public                                                                     |Private       |Coverage%|Notes |
|:--------:|:---:|:----:|:-------------------------------------------------------------------------:|:------------:|:-------:|:----:|
|Anonymeter|1.   |     2|adult                                                                      |us_census_1940|    66.7%|a.    |
|SDGym     |2.   |     6|adult, alarm, car_insurance, census, covtype, expedia_hotel_logs, intrusion|              |    66.7%|b.    |
|smartnoise|3.   |     1|iris                                                                       |              |    16.7%|c.d.  |

</div>

1. Giomi, M., Boenisch, F., Wehmeyer, C., & Tasnádi, B. (2023). A Unified Framework for Quantifying Privacy Risk in Synthetic Data. *Proceedings of Privacy Enhancing Technologies Symposium*, 2023(2), 312–328. https://doi.org/10.56553/popets-2023-0055
2. https://docs.sdv.dev/sdgym/customization/datasets/public-sdv-datasets
3. https://github.com/opendp/smartnoise-sdk/tree/main/datasets

a. **texas** requires payment. **texas** 需要付費。
b. **child** and **news** datasets didn't have reference. **child** 和 **news** 資料集缺乏參考資料。
c. 4 **pums** datasets discussion see below. 有關4個 **pums** 資料集的討論請參見下文。
d. **reddit** dataset didn't have reference. **reddit** 資料集缺乏參考資料。

### Used in Competition

<!-- This <div> here is special function for sighingnow/jekyll-gitbook -->
<div class="table-wrapper" markdown="block">

|Topic |Link |Counts|Public                                                |Private|Notes                    |
|:----:|:---:|:----:|:----------------------------------------------------:|:-----:|:-----------------------:|
|PWSCup|1.2. |     2|adult, nhanes_diabetes                                |       |                         |
|UK-US |3.   |     3|uk_us_pf_household, uk_us_pf_person, uk_us_pf_prop_net|       |                         |

</div>

1. PWSCup2021: Use **nhanes_diabetes** https://www.iwsec.org/pws/2021/index.html
2. PWSCup2020: Use Synthetic data from **adult** https://www.iwsec.org/pws/2020/cup20.html
3. UK-US PETs prize challenges 2023: https://petsprizechallenges.com/
  - There's couples of datasets in UK-US, we include only the most representative. Here's remains: TODO

## Appendix for non-included datasets

### **pums**

- Name: **The American Community Survey (ACS) Public Use Microdata Sample (PUMS)**

**OpenDP**'s and **smartnoise**'s demo use 1,000 records of California demographics, only below columns: ["age", "sex", "educ", "race", "income", "married"]. But didn't specific which year they use (2005~2022 is available)

In reference to the NIST CRC 2023 Deidentified Data Archives, it may be possible to define multiple **PUMAs** based on geographical regions, and the classification approach can initially follow their guidelines

**OpenDP** 與 **smartnoise** 的示範使用了 1,000 條加州人口統計數據，僅包含以下欄位：["age", "sex", "educ", "race", "income", "married"]。但並未具體指明使用了哪一年的數據（2005年至2022年的數據均可用）。

參考了 NIST CRC 2023 去識別化資料存檔的介紹，或許可以依照地區定義多個 **PUMAs**，然後分類方法可以先依照他們。

https://www.census.gov/programs-surveys/acs/microdata.html
https://github.com/opendp/smartnoise-sdk/tree/main/datasets
https://pages.nist.gov/privacy_collaborative_research_cycle/pages/archive.html#acceleration-bundle
https://github.com/usnistgov/SDNist/tree/main/nist%20diverse%20communities%20data%20excerpts

### **texas**

- Name: **Texas Hospital Discharge Data Public Use Data**

For data downloads by non-Texas public universities and public health institutions, it is necessary to complete an application form and pay an annual subscription fee.

對於非德州的公立大學和公共衛生機構來說，需要填寫一份申請表格並支付年度訂閱費。

https://www.dshs.texas.gov/texas-health-care-information-collection/general-public-information/hospital-discharge-data-public

## storage

The module of benchmark dataset will first download the requested raw data, and store it in a "benchmark" folder within the working directory (in lowercase). If the folder does not exist, it will be created automatically (`./benchmark/{Benchmark filename}`). Subsequently, it will follow the regular `Loader` process for loading. When using it, please be mindful of your permissions and available hardware space.

If the "benchmark" folder already contains a file with the same filename as the dataset, the program will check if the local data matches the records in `PETsARD`. If they match, the program will skip the download and use the local data directly, making it convenient for users to reuse the data multiple times. It's important to note that if there is a file with the same name but with inconsistent data, `Loader` will issue a warning and stop. In such cases, users should be aware that the benchmark dataset might have been tampered with, potentially contaminating the experimental results.

基準資料集功能會先下載你所請求的原始資料，存到工作目錄下方的 "benchmark" 資料夾裡（小寫），如果不存在會自動開一個 (`./benchmark/{Benchmark filename}`)，之後照一般的 `Loader` 流程加載。使用時請注意你的權限與硬體空間。

如果你的 "benchmark" 資料夾裡面已經有該資料集對應的同名檔案了，則程式會檢驗本地端的資料是否與 `PETsARD` 的紀錄一致，如果一致的話，便會省去下載、直接使用本地端資料，方便使用者多次使用。要注意的是如果同檔名但檢驗不一致的話，`Loader` 會告警並停止，此時使用者應該留意到可能儲存到了非原版的基準資料集，這很有可能對實驗結果造成汙染。

## verification

Classic benchmark datasets are often used in various data analysis or machine learning scenarios. However, when discussing the same dataset, it is common to find inconsistencies in the content in practical experience. Common patterns include:

- Inconsistent variable encoding transformations (e.g., having original categorical variables recorded as strings, `Label Encoding` encoded versions, or generalized categorical versions).
- Inconsistent row counts (e.g., versions before or after removing missing values).
- Inconsistent columns (e.g., column renaming, or versions after feature engineering).

The reasons for these patterns are often not malicious tampering, but rather the release of optimized or preprocessed data, which is then inadvertently propagated by subsequent users. Since the preprocessing methods for privacy-enhancing technologies are crucial, obtaining the same version of the benchmark dataset is the recommended experimental procedure in `PETsARD`.

經典的基準資料集常被用於各種資料分析或機器學習的場合，但實務經驗上，常遇到討論同一個資料集的時候，發現彼此的資料集內容不一致。常見的樣態有：

- 變項編碼轉換不一致（例如分別有原始以字串紀錄的類別變項、`Label Encoding`過的編碼、概化後的分類的版本）
- 筆數不一致（例如剔除遺失值前或後的版本）
- 欄位不一致（例如欄位重命名，或是欄位經過特徵工程的版本）

造成這些樣態原因常常不是惡意竄改，而是某些優化過、或是前處理過的資料被釋出，而後續使用者不經意地加以傳播所導致。由於隱私強化技術的前處理方式至關重要，於是取得相同版本的基準資料集是 `PETsARD` 建議的實驗程序。

### _calculate_sha256()

`PETsARD` ensures the consistency of benchmark datasets' versions by calculating the SHA-256 hash value of files and comparing it to the settings in the `benchmark_datasets.yaml` file. Specifically, `PETsARD` uses `hashlib.sha256()` to calculate the hash of the binary version of a file and records its hexadecimal representation (`.hexdigest()`).

In the functionality related to benchmark datasets, the SHA-256 calculation is entirely background, automated, and in future versions, methods will be provided for users to calculate it manually if desired.

`PETsARD` 藉由計算檔案的 SHA-256 值，與設定檔案 `benchmark_datasets.yaml` 做比較，來確保基準資料集的版本一致。具體來說，`PETsARD` 使用 `hashlib.sha256()` 計算檔案二進位版本的雜湊，並記錄其雜湊值的 16 進位表示 (`.hexdigest()`)。

在基準資料集的功能中，計算 SHA-256 是完全後台的、自動化的，未來版本會再提供方法供使用者自行計算。

## public/private access

The `PETsARD` development team, which belongs to the [National Institute for Cyber Security (NICS)](https://www.nics.nat.gov.tw/), stores the benchmark datasets in their cloud space. These datasets are categorized as **public** or **private access**, and the calling methods for both are identical.

**Public datasets** are securely stored in the cloud space after obtaining proper authorization, and they can be downloaded using `request.get()` On the other hand, **Private datasets**, which may have restrictions based on the dataset's authorization or considerations from the data provider, are intended for internal use by the development team and collaborating parties. Access to private datasets is established through `boto3` connection, and configuring cloud permissions is necessary. For any related inquiries, please contact the development team.

基準資料集儲存在 `PETsARD` 開發團隊所屬的臺灣[國家資通安全研究院 (NICS)](https://www.nics.nat.gov.tw/)雲端空間，分成**公開**與**私有訪問**兩種。兩者的呼叫方式完全一樣。

**公開資料集**皆是確認過其授權後，由團隊保存之雲端備份，使用 `request.get()` 下載。而**私有資料集**，包含了資料集本身授權的限制、或是資料提供方的考量等原因，僅供團隊與合作方內部使用。目前私有資料集使用 `boto3` 連線，需要預先設定雲端權限，相關問題請聯絡開發團隊。