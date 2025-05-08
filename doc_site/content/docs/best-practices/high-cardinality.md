---
title: High-Cardinality variables - Constraints
type: docs
weight: 44
prev: docs/best-practices/categorical
next: docs/best-practices/high-cardinality-multi-table
---

## Case Background

A public university seeks to share student academic and enrollment records with campus researchers. These records contain sensitive personal data (socioeconomic status, ethnicity, disability status), previously accessible only to designated teams in controlled environments.

Recent efforts using aggregated data with differential privacy improved access but reduced analytical precision. The Academic Affairs Office is now partnering with the Information Science Department to develop synthetic data solutions that maintain individual-level granularity and analytical accuracy while protecting privacy, aiming to enhance research capabilities and enable future cross-institutional collaboration.

### Data Characteristics and Challenges

- **High-Cardinality Categorical variables**: The diversity of student identity categories, academic departments, and admission programs results in many data fields containing numerous unique values.

## High Cardinality

Cardinality refers to the number of non-zero elements in a vector, and in the data field, it indicates the quantity of different values in a data set or variable. Specifically, for a categorical variable, its cardinality is the number of unique values.

High Cardinality (or Large Cardinality) refers to situations where a categorical variable contains an especially large number of unique values. There is no clear threshold in academia or practice defining exactly how many values constitute "high" cardinality, but literature has mentioned the following definitions:

1. Nominal variables with more than 100 unique values: Based on modeling results from previous literature [^1]
2. Categorical variables that increase with sample size [^2]
3. In databases, when the number of unique values greatly exceeds local cache memory capacity (L1/L2) [^3]

### Constraint Processing for High Cardinality Categories

As explained in the previous article on [categorical variables](./categorical), data preprocessing techniques recommend encoding nominal or ordinal scale categorical variables, but these methods often face serious challenges when dealing with high cardinality scenarios. Applying these encoding methods to high cardinality categorical variables can easily lead to feature space dimension explosion, sparsity issues, statistical learning inefficiency, and decreased model generalization ability.

In addition to recommending uniform encoding for any categorical variable, the CAPE team suggests incorporating constraint conditions in the recursive synthesis process for post-generation validation when dealing with high cardinality situations. This approach is easier to implement and provides better control over domain knowledge through professional expertise.

Since synthetic data is based on probabilistic models, although it can learn the implicit relationship structures within the data, extreme cases that violate business logic may still occur during extensive sampling. Constraint design ensures synthetic data complies with business regulations. Cutting-edge synthetic data research has begun utilizing knowledge graphs to generate constraints [^5], integrating constraints into conditional probabilities [^6] or penalty terms [^7] of synthetic models, and even producing synthetic data solely based on constraints [^8]. Additionally, constraints help eliminate discrimination and enhance fairness [^8].

## Constraint Condition Inventory Demonstration

This demonstration dataset contains various business logic rules. The CAPE team will demonstrate how to govern these fields using several mainstream constraint logics with our team-developed constraint processor. These governance methods serve as references, and users can achieve similar objectives using different approaches. Determining which conditions are necessary and which can be written differently is what we recommend data owners to inventory and decide on their own in this best practice article.

- Birthday and Zodiac Sign: Field Constraints (`field_constraints`)

    - Since year, month, and day are synthesized separately, situations that violate large/small months and leap years occur, such as February having 30 or 31 days
    - Additionally, zodiac signs are synthesized separately, so birthdays and zodiac signs do not correspond

- University, College, and Department: Field Combination Constraints (`field_combinations`)

  - This simulation used National Taiwan University and National Chengchi University with three colleges: College of Liberal Arts, College of Science, and College of Electrical Engineering & Computer Science
  - Different schools have variations in department design: NTU calls it "College of Electrical Engineering & Computer Science" while NCCU calls it "College of Information Science"; NTU's College of Liberal Arts also includes Anthropology, Library & Information Science, Japanese, Drama, and its College of Science includes Physics, Chemistry, Geology, etc. The synthesis may produce mismatches between college names and school names
  - Even with the same department name, different department codes between the two schools may produce codes that don't correspond to the appropriate school

- Nationality and Nationality Code: Missing Value Group Constraints (`nan_group`)

    - The Ministry of Education's enrollment statistics assign nationality codes for foreign students, so for the majority of domestic students, the nationality code field is empty

### Birthday and Zodiac Sign: Field Constraints

There are 145 records (1.5%) with incorrectly formatted dates and 9,145 records (91.5%) with zodiac signs that don't match the dates.

|  | index | reason | year | month | day |
|------|------|------|------|------|------|
| 0 | 55 | Day 31 does not exist in 2 of that year | 2005 | 2 | 31 |
| 1 | 116 | Day 31 does not exist in 4 of that year | 2002 | 4 | 31 |
| 2 | 260 | Day 30 does not exist in 2 of that year | 2001 | 2 | 30 |

| index | reason | month | day | zodiac | expected_zodiac |
|-------|--------|-------|-----|--------|----------------|
| 0 | Zodiac mismatch | 6 | 10 | Scorpio | Gemini |
| 1 | Zodiac mismatch | 12 | 7 | Scorpio | Sagittarius |
| 2 | Zodiac mismatch | 2 | 23 | Virgo | Pisces |

### University, College, and Department: Field Combination Constraints

#### University

There are 1,340 records (13.4%) where the synthesized school does not match the school code.

| index | university_code | university |
|-------|----------------|------------|
| 1 | 001 | National Chengchi University | University code and name mismatch: National Taiwan University |
| 28 | 001 | National Chengchi University | University code and name mismatch: National Taiwan University |
| 31 | 001 | National Chengchi University | University code and name mismatch: National Taiwan University |

#### College

There are 6,415 records (64.2%) where the synthesized college does not match the college code, and 5,285 records (52.9%) where the synthesized college code doesn't match the university code.

| index | college_code | college | reason |
|-------|-------------|----------|--------|
| 0 | 100 | College of Information Science | College code and name mismatch: College of Liberal Arts |
| 1 | 1000 | College of Electrical Engineering & Computer Science | College code and name mismatch: College of Liberal Arts |
| 2 | 9000 | College of Information Science | College code and name mismatch: College of Electrical Engineering & Computer Science |

| index | university_code | college_code | reason |
|-------|----------------|--------------|--------|
| 0 | 001 | 100 | College 100 does not belong to University 001 |
| 1 | 002 | 2000 | College 2000 does not belong to University 002 |
| 2 | 002 | 1000 | College 1000 does not belong to University 002 |

#### Department

There are 9,540 records (95.4%) where the synthesized department does not match the department code, and 9,425 records (94.3%) where the synthesized department code doesn't match the college code.

| index | college_code | department_code | reason |
|-------|-------------|----------------|--------|
| 0 | 9000 | 101 | Department 101 does not belong to this college |
| 1 | 100 | 117 | Department with unknown code does not belong to this college |
| 2 | 2000 | 101 | Department 101 does not belong to this college |

| index | department_code | department_name | reason |
|-------|----------------|-----------------|--------|
| 0 | 101 | Department of Electrical Engineering | Department code and name mismatch: Department of Chinese Literature |
| 1 | 117 | Department of Chinese Literature | Department code and name mismatch: Unknown Department |
| 2 | 101 | Department of Atmospheric Sciences | Department code and name mismatch: Department of Chinese Literature |

### Nationality and Nationality Code: Missing Value Group Constraints

There are 1,353 records (13.5%) where the synthesized nationality and nationality code have incorrect missing value correspondence.

| index | nationality_code | nationality | reason |
|-------|-----------------|-------------|--------|
| 0 | 113 | Republic of China | ROC nationality should not have nationality code |
| 1 | 113 | Republic of China | ROC nationality should not have nationality code |
| 2 | 113 | Republic of China | ROC nationality should not have nationality code |

## Constraint Settings

In the synthetic data generation process, the CAPE team's PETsARD framework includes three key constraint types: missing value group constraints, field constraints, and field combination constraints. Together, these ensure that the generated data not only reflects the statistical characteristics of the original data but also complies with specific domain logic and business regulations. Here are the key considerations when using PETsARD constraint conditions:

1. These constraint mechanisms operate with an "all conditions must be satisfied" logic, meaning that synthetic data must simultaneously meet all defined constraint conditions to be retained. Any record violating a single rule will be filtered out, thus guaranteeing the complete compliance of the final results.

2. Since the constraint types in PETsARD are designed as fixed and independent functional modules, users should declare constraints separately according to their type when dealing with data scenarios that span multiple constraint requirements. For example, if the same set of fields requires both missing value logic checks and field combination relationship validation, constraints should be declared separately under their corresponding constraint types rather than attempting to process all rules within a single constraint type.

3. Missing value group constraints (`nan_groups`): Allow three different missing value handling methods: deleting records with missing values, setting related fields to missing values, or copying values from one field to other fields. When using these, ensure the operation type meets the actual data requirements.

4. Field constraints (`field_constraints`): Support comparison operations (>, >=, ==, !=, <, <=), logical operations (&, |), and special checks (IS, IS NOT), and can use the DATE() function to process date values. When using these, properly utilize parentheses to clearly define the logical order of complex expressions and ensure unambiguous condition parsing.

5. Field combination constraints (`field_combinations`): Provide single-field mapping and multi-field mapping functions, defining valid value combination relationships between fields in a positive enumeration manner. These are particularly suitable for establishing correspondence rules between categorical variables.

This article primarily focuses on best practices, showcasing only validated and effective constraint condition setting combinations. However, human natural language and logical expressions are complex and variable, and the same set of data and constraint condition inventory may lead to multiple potential declaration methods. Users should refer to the official PETsARD data constraint tutorial documents as their main reference. For special requirements, we recommend contacting the PETsARD team directly for customized development support.

### Birth Dates and Zodiac Signs: Field Constraints

- For birth dates, we established the following constraints:

    - Birth year should be between 1990 and 2020
    - Birth day must be greater than 1
    - For monthly day limits, we used a single condition that restricts:
        - Days in months with 31 days must be less than or equal to 31
        - Days in months with 30 days (excluding February) must be less than or equal to 30
        - February follows leap year rules:
            - In leap years (explicitly listed), days can be up to 29
            - In regular years, days must be less than or equal to 28

```yaml
Constrainer:
  demo:
    field_constraints:
      # 出生年限制 Birth year restriction
      - (birth_year >= 1990) & (birth_year <= 2020)
      # 出生日限制 Birth day minimum restriction
      - birth_day >= 1
      # 出生月日限制：包含 1990-2020 的閏年列表
      # Birth month and day restrictions, including list of leap years between 1990-2020
      - |
        (((birth_month == 1) | (birth_month ==  3) | (birth_month ==  5) | (birth_month == 7) |
          (birth_month == 8) | (birth_month == 10) | (birth_month == 12)
         ) & (birth_day <= 31)
        ) |
        (((birth_month == 4) | (birth_month == 6) | (birth_month == 9) | (birth_month == 11)
         ) & (birth_day <= 30)
        ) |
        ((birth_month == 2) & (
          (((birth_year == 1992) | (birth_year == 1996) | (birth_year == 2000) |
            (birth_year == 2004) | (birth_year == 2008) | (birth_year == 2012) |
            (birth_year == 2016) | (birth_year == 2020)
           ) & (birth_day <= 29) |
          (birth_day <= 28)
          )
         )
        )
```

- For zodiac signs, we used a single condition:

    - Each zodiac sign corresponds to dates spanning two months, with specific day ranges for each month

```yaml
Constrainer:
  demo:
    field_constraints:
      # 星座與出生日期的對應關係 Zodiac Sign and Birth Date Correspondence
      - |
        ((zodiac == '摩羯座') &
        (((birth_month == 12) & (birth_day >= 22)) |
        ((birth_month == 1) & (birth_day <= 19)))) |

        ((zodiac == '水瓶座') &
        (((birth_month == 1) & (birth_day >= 20)) |
        ((birth_month == 2) & (birth_day <= 18)))) |

        ((zodiac == '雙魚座') &
        (((birth_month == 2) & (birth_day >= 19)) |
        ((birth_month == 3) & (birth_day <= 20)))) |

        ((zodiac == '牡羊座') &
        (((birth_month == 3) & (birth_day >= 21)) |
        ((birth_month == 4) & (birth_day <= 19)))) |

        ((zodiac == '金牛座') &
        (((birth_month == 4) & (birth_day >= 20)) |
        ((birth_month == 5) & (birth_day <= 20)))) |

        ((zodiac == '雙子座') &
        (((birth_month == 5) & (birth_day >= 21)) |
        ((birth_month == 6) & (birth_day <= 21)))) |

        ((zodiac == '巨蟹座') &
        (((birth_month == 6) & (birth_day >= 22)) |
        ((birth_month == 7) & (birth_day <= 22)))) |

        ((zodiac == '獅子座') &
        (((birth_month == 7) & (birth_day >= 23)) |
        ((birth_month == 8) & (birth_day <= 22)))) |

        ((zodiac == '處女座') &
        (((birth_month == 8) & (birth_day >= 23)) |
        ((birth_month == 9) & (birth_day <= 22)))) |

        ((zodiac == '天秤座') &
        (((birth_month == 9) & (birth_day >= 23)) |
        ((birth_month == 10) & (birth_day <= 23)))) |

        ((zodiac == '天蠍座') &
        (((birth_month == 10) & (birth_day >= 24)) |
        ((birth_month == 11) & (birth_day <= 22)))) |

        ((zodiac == '射手座') &
        (((birth_month == 11) & (birth_day >= 23)) |
        ((birth_month == 12) & (birth_day <= 21))))
```

### University, College, and Department: Field Combination Constraints

- For universities, colleges, and departments, we designed multi-level mapping relationships:

  - University code to university name mapping (e.g., "001" corresponds to "National Taiwan University")
  - University code to its contained college code groups (e.g., NTU contains college codes "1000", "2000", and "9000")
  - College code to college name mapping (e.g., "1000" corresponds to "College of Liberal Arts")
  - Department code to department name mapping (e.g., "1010" corresponds to "Department of Chinese Literature")
  - Mapping of nationality codes to invalid values: When the nationality is "Republic of China", the nationality code is set to invalid (NaN)

```yaml
    field_combinations:
      # 大學代碼與大學名稱的對應關係 University code and university name mapping
      -
        - {'university_code': 'university'}
        - {
            '001': ['國立臺灣大學'],
            '002': ['國立政治大學'],
          }
      # 學院代碼與學院名稱的對應關係 College code and college name mapping
      -
        - {'college_code': 'college'}
        - {
            # 臺大 NTU
            '1000': ['文學院'],
            '2000': ['理學院'],
            '9000': ['電機資訊學院'],
            # 政大 NCCU
            '100': ['文學院'],
            '700': ['理學院'],
            'ZA0': ['資訊學院']
          }
      # 大學代碼與學院代碼的對應關係 University code and college code mapping
      -
        - {'university_code': 'college_code'}
        - {
            '001': ['1000', '2000', '9000'],
            '002': ['100', '700', 'ZA0']
          }
      # 系所代碼與系所名稱的對應關係 Department code and department name mapping
      -
        - {'department_code': 'department_name'}
        - {
            # 臺大 NTU
            '1010': ['中國文學系'],
            '1020': ['外國語文學系'],
            '1030': ['歷史學系'],
            '1040': ['哲學系'],
            '1050': ['人類學系'],
            '1060': ['圖書資訊學系'],
            '1070': ['日本語文學系'],
            '1090': ['戲劇學系'],
            '2010': ['數學系'],
            '2020': ['物理學系'],
            '2030': ['化學系'],
            '2040': ['地質科學系'],
            '2070': ['心理學系'],
            '2080': ['地理環境資源學系'],
            '2090': ['大氣科學系'],
            '9010': ['電機工程學系'],
            '9020': ['資訊工程學系'],
            # 政大 NCCU
            '101': ['中國文學系'],
            '102': ['教育學系'],
            '103': ['歷史學系'],
            '104': ['哲學系'],
            '701': ['應用數學系'],
            '702': ['心理學系'],
            '703': ['資訊科學系']
          }
      # 學院代碼與系所代碼的對應關係 College code and department code mapping
      -
        - {'college_code': 'department_code'}
        - {
            # 臺大 NTU
            '1000': ['1010', '1020', '1030', '1040', '1050', '1060', '1070', '1090'],
            '2000': ['2010', '2020', '2030', '2040', '2070', '2080', '2090'],
            '9000': ['9010', '9020'],
            # 政大 NCCU
            '100': ['101', '102', '103', '104'],
            '700': ['701', '702'],
            'ZA0': ['703']
          }
```

### Nationality and Nationality Code: Missing Value Group Constraints

- For nationality codes, we have designed the following mapping relationships:

    - Mapping of nationality codes to invalid values: When the nationality is "Republic of China", the nationality code is set to invalid (NaN)

```yaml
Constrainer:
  demo:
    nan_groups:
      nationality_code:
        nan_if_condition:
          nationality:
            - '中華民國' # ROC (Taiwan)
```

### Why Are the Constrained Data Still Incorrect?

This is because the maximum number of trials (`max_trials`) of 500 set in our demonstration is not sufficient to successfully constrain the college and department combination condition.

```yaml
Constrainer:
  demo:
    max_trials: 500
```

In PETsARD, to prevent users from providing invalid constraint conditions, we set a maximum number of trials, defaulting to 300. When the synthesis cannot generate and constrain a result with the same number of rows as the original data after 300 resampling attempts, the current synthesis result is thrown. You can see that other conditions have passed, with only 704 records not meeting the college and department pairing combination.

From a data structure perspective, this is due to the already large combination of colleges and departments (23 departments). From the synthesizer's viewpoint, Gaussian coupling cannot effectively learn their underlying constraint conditions, so it can only resample on the normal distribution and then be rejected by the constrainer.

There are several ways to handle this situation:

1. **Increase the maximum number of trials**: Observations show that about 10 constrained synthetic data points are generated per 10 constraint resampling attempts. Raising `max_trials` to 1,000 - which is double the current synthesis time, or even a more conservative 1,500 - would be a reasonable parameter adjustment.

2. **Discard the constraint condition**: If the college and department combination is not critical. For example, if the user's downstream task is to calculate average grades for each college and department separately, then considering the Gaussian coupling modeling logic, the average of such one-to-one fields can be well-preserved. This entirely depends on the data owner's professional knowledge.

3. **Replace with a synthesizer better at learning latent patterns**: Deep learning-inspired synthesizers such as GANs or VAEs can theoretically better learn conditional probabilities between categorical variables. Conditions difficult to achieve in Gaussian coupling can be confidently implemented in advanced synthesizers.

4. **Synthesize only the most important few columns for attributes that can be inferred from each other**: Taking university departments as an example, since departments are the highest granularity and colleges and schools can be derived, even departments with the same name can be additionally sampled and allocated. Thus, you can first synthesize departments using the synthesizer, and then programmatically add other derivable fields.

Similarly, we have not yet governed the reasonableness of admission methods, and the synthesized results have many aspects that do not conform to real-world data. This demonstrates how we weigh and balance such considerations.

## Full Demonstration

Click the button below to run the example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/best-practice/high-cardinality.ipynb)

```yaml
Constrainer:
  demo:
    max_trials: 500
    field_constraints:
      # 出生年限制 Birth year restriction
      - (birth_year >= 1990) & (birth_year <= 2020)
      # 出生日限制 Birth day minimum restriction
      - birth_day >= 1
      # 出生月日限制：包含 1990-2020 的閏年列表
      # Birth month and day restrictions, including list of leap years between 1990-2020
      - |
        (((birth_month == 1) | (birth_month ==  3) | (birth_month ==  5) | (birth_month == 7) |
          (birth_month == 8) | (birth_month == 10) | (birth_month == 12)
         ) & (birth_day <= 31)
        ) |
        (((birth_month == 4) | (birth_month == 6) | (birth_month == 9) | (birth_month == 11)
         ) & (birth_day <= 30)
        ) |
        ((birth_month == 2) & (
          (((birth_year == 1992) | (birth_year == 1996) | (birth_year == 2000) |
            (birth_year == 2004) | (birth_year == 2008) | (birth_year == 2012) |
            (birth_year == 2016) | (birth_year == 2020)
           ) & (birth_day <= 29) |
          (birth_day <= 28)
          )
         )
        )
      # 星座與出生日期的對應關係 Zodiac Sign and Birth Date Correspondence
      - |
        ((zodiac == '摩羯座') &
        (((birth_month == 12) & (birth_day >= 22)) |
        ((birth_month == 1) & (birth_day <= 19)))) |

        ((zodiac == '水瓶座') &
        (((birth_month == 1) & (birth_day >= 20)) |
        ((birth_month == 2) & (birth_day <= 18)))) |

        ((zodiac == '雙魚座') &
        (((birth_month == 2) & (birth_day >= 19)) |
        ((birth_month == 3) & (birth_day <= 20)))) |

        ((zodiac == '牡羊座') &
        (((birth_month == 3) & (birth_day >= 21)) |
        ((birth_month == 4) & (birth_day <= 19)))) |

        ((zodiac == '金牛座') &
        (((birth_month == 4) & (birth_day >= 20)) |
        ((birth_month == 5) & (birth_day <= 20)))) |

        ((zodiac == '雙子座') &
        (((birth_month == 5) & (birth_day >= 21)) |
        ((birth_month == 6) & (birth_day <= 21)))) |

        ((zodiac == '巨蟹座') &
        (((birth_month == 6) & (birth_day >= 22)) |
        ((birth_month == 7) & (birth_day <= 22)))) |

        ((zodiac == '獅子座') &
        (((birth_month == 7) & (birth_day >= 23)) |
        ((birth_month == 8) & (birth_day <= 22)))) |

        ((zodiac == '處女座') &
        (((birth_month == 8) & (birth_day >= 23)) |
        ((birth_month == 9) & (birth_day <= 22)))) |

        ((zodiac == '天秤座') &
        (((birth_month == 9) & (birth_day >= 23)) |
        ((birth_month == 10) & (birth_day <= 23)))) |

        ((zodiac == '天蠍座') &
        (((birth_month == 10) & (birth_day >= 24)) |
        ((birth_month == 11) & (birth_day <= 22)))) |

        ((zodiac == '射手座') &
        (((birth_month == 11) & (birth_day >= 23)) |
        ((birth_month == 12) & (birth_day <= 21))))
    field_combinations:
      # 大學代碼與大學名稱的對應關係 University code and university name mapping
      -
        - {'university_code': 'university'}
        - {
            '001': ['國立臺灣大學'],
            '002': ['國立政治大學'],
          }
      # 學院代碼與學院名稱的對應關係 College code and college name mapping
      -
        - {'college_code': 'college'}
        - {
            # 臺大 NTU
            '1000': ['文學院'],
            '2000': ['理學院'],
            '9000': ['電機資訊學院'],
            # 政大 NCCU
            '100': ['文學院'],
            '700': ['理學院'],
            'ZA0': ['資訊學院']
          }
      # 大學代碼與學院代碼的對應關係 University code and college code mapping
      -
        - {'university_code': 'college_code'}
        - {
            '001': ['1000', '2000', '9000'],
            '002': ['100', '700', 'ZA0']
          }
      # 系所代碼與系所名稱的對應關係 Department code and department name mapping
      -
        - {'department_code': 'department_name'}
        - {
            # 臺大 NTU
            '1010': ['中國文學系'],
            '1020': ['外國語文學系'],
            '1030': ['歷史學系'],
            '1040': ['哲學系'],
            '1050': ['人類學系'],
            '1060': ['圖書資訊學系'],
            '1070': ['日本語文學系'],
            '1090': ['戲劇學系'],
            '2010': ['數學系'],
            '2020': ['物理學系'],
            '2030': ['化學系'],
            '2040': ['地質科學系'],
            '2070': ['心理學系'],
            '2080': ['地理環境資源學系'],
            '2090': ['大氣科學系'],
            '9010': ['電機工程學系'],
            '9020': ['資訊工程學系'],
            # 政大 NCCU
            '101': ['中國文學系'],
            '102': ['教育學系'],
            '103': ['歷史學系'],
            '104': ['哲學系'],
            '701': ['應用數學系'],
            '702': ['心理學系'],
            '703': ['資訊科學系']
          }
      # 學院代碼與系所代碼的對應關係 College code and department code mapping
      -
        - {'college_code': 'department_code'}
        - {
            # 臺大 NTU
            '1000': ['1010', '1020', '1030', '1040', '1050', '1060', '1070', '1090'],
            '2000': ['2010', '2020', '2030', '2040', '2070', '2080', '2090'],
            '9000': ['9010', '9020'],
            # 政大 NCCU
            '100': ['101', '102', '103', '104'],
            '700': ['701', '702'],
            'ZA0': ['703']
          }
    nan_groups:
      nationality_code:
        nan_if_condition:
          nationality:
            - '中華民國' # ROC (Taiwan)
```

### Practical Experience Insights

The constraint system for synthetic data is a key element in ensuring data quality and business compliance, covering missing value handling logic, temporal rules, reasonable value range limitations, and business regulations. Based on our practical application experience, effective constraint design must balance rigor with practicality. Here are the key practical experience summaries:

- **Integration of Business Knowledge**

  - Combine domain expert knowledge to design constraints, center on actual business scenarios, and validate constraint effects through real-world situation testing

- **Gradual Constraint Strategy**

  - Start with basic logical rules, incorporate complex constraints after stabilization, and repeatedly and continuously evaluate the impact of each constraint on data quality

- **Balance Between Constraint Strength and Performance**

  - Too many or overly strict constraints may lead to extremely low sampling efficiency or failure to converge; identify and retain truly necessary constraints
  - Adopt a phased implementation strategy, handling high-priority constraints first, observing results before adding secondary constraints, and pre-assessing potential conflicts between constraints

- **High Cardinality Field Processing Outside the Synthesis Flow**

  - Consider strategically classifying or aggregating high cardinality fields before synthesis to effectively reduce the number of unique values
  - Whether decomposing for synthesis or setting constraints, utilize hierarchical structures to handle complex categorical variables, adopting a layered approach of "first synthesize subcategories, then derive the main category"
  - For data with clear correspondence, consider temporarily removing corresponding fields and reintroducing them through matching mechanisms after synthesis is complete
  - For ultra-high cardinality quasi-identifier fields (such as identity codes, detailed addresses, etc.), timely adopt pattern-based logic generation mechanisms as an alternative to direct synthesis

### Why Does PETsARD Need Its Own Constraint Module?

Taking the SDV synthetic data tool ecosystem used by the CAPE team as an example, some synthesis modules do provide constraint functionality, but most restrict advanced constraint features to commercial versions. PETsARD develops its own constraint module mainly based on the following considerations:

- Functional completeness: Ensuring basic constraint functions are not limited by commercial versions, such as chained inequalities, all-empty combinations, and mixed range constraints
- Localization requirements: Providing customized constraint support for Taiwan's special data scenarios (such as Chinese language processing, specific industry regulations)
- Performance optimization: Designing more efficient constraint satisfaction algorithms specifically for high cardinality categorical variables, reducing the efficiency issues of pure rejection sampling
- Research autonomy: Maintaining research and development autonomy of the constraint system to more flexibly respond to different data synthesis requirements

### Can Better Synthesizers Replace Constraints?

As mentioned in previous papers, novel research indeed indicates that methods like deep learning can continuously enhance synthesizers' ability to learn relationship structures. Although our team's demonstrations are primarily based on the basic Gaussian Copula model, adopting more advanced synthesizers can indeed reduce constraint violations. However, even advanced synthesizers still have a certain probability of not fully learning or possibly incorrectly generating data that does not meet conditions, and more complex models often require longer training times and larger datasets.

Therefore, the CAPE team recommends viewing constraints as "gatekeepers" in the data synthesis process, adopting an integrated strategy of "quality synthesizers with necessary constraints." This approach can effectively reduce synthesizer training and parameter tuning requirements through constraints while avoiding synthesis time delays due to repeated sampling failures caused by overly complex constraints through high-quality synthesizers. This complementary strategy achieves a better balance between data quality and computational efficiency.

### Conclusion

The constraint system serves as the gatekeeper for synthetic data quality. By applying constraints through these practice-oriented strategies, one can ensure business compliance of synthetic data while maintaining reasonable computational efficiency and statistical quality of the synthetic data.

## References

[^1]: Moeyersoms, J., & Martens, D. (2015). Including high-cardinality attributes in predictive models: A case study in churn prediction in the energy sector. Decision Support Systems, 72, 72-81.

[^2]: Cerda, P., & Varoquaux, G. (2022). Encoding high-cardinality string categorical variables. IEEE Transactions on Knowledge and Data Engineering, 34(3), 1164-1176. https://doi.org/10.1109/TKDE.2020.2992529

[^3]: Siddiqui, T., Narasayya, V., Dumitru, M., & Chaudhuri, S. (2023). Cache-efficient top-k aggregation over high cardinality large datasets. Proceedings of the VLDB Endowment, 17(4), 644-656. https://doi.org/10.14778/3636218.3636222

[^4]: Kotal, A., & Joshi, A. (2024). KIPPS: Knowledge infusion in Privacy Preserving Synthetic Data Generation. arXiv. https://arxiv.org/abs/2409.17315

[^5]: Ge, C., Mohapatra, S., He, X., & Ilyas, I. F. (2021). Kamino: Constraint-aware differentially private data synthesis. Proceedings of the VLDB Endowment, 14(10), 1886-1899. https://doi.org/10.14778/3467861.3467876

[^6]: Li, W. (2020). Supporting database constraints in synthetic data generation based on generative adversarial networks. In Proceedings of the 2020 ACM SIGMOD International Conference on Management of Data (pp. 2875-2877). ACM. https://doi.org/10.1145/3318464.3384414

[^7]: Arasu, A., Kaushik, R., & Li, J. (2011). Data Generation using Declarative Constraints. Proceedings of the 2011 ACM SIGMOD International Conference on Management of Data, 685-696. https://doi.org/10.1145/1989323.1989395

[^8]: Abroshan, M., Elliott, A., & Khalili, M. M. (2024). Imposing fairness constraints in synthetic data generation. Proceedings of The 27th International Conference on Artificial Intelligence and Statistics, 238, 2269-2277.
