---
title: 高基數變項 - 約束條件
type: docs
weight: 44
prev: docs/best-practices/categorical
next: docs/best-practices/high-cardinality-multi-table
---

## 個案背景

某公立大學教務處擁有豐富的學生入學資訊與學業表現紀錄，希望能更廣泛地提供這些資料給校內教育政策與社會經濟研究學者使用。然而，這些資料包含社經背景、族裔、身心障礙等高度敏感個資，過去僅能透過指定研究案方式，由受限研究團隊在封閉環境下使用，容易引發學術資源公平近用的疑慮。

近兩年，該校採取將資料匯總並導入差分隱私技術的作法，讓校內教研團隊可公開申請使用，但此方法一定程度限制了資料分析的精確度，讓團隊難以評估研究成果的泛化能力。基於對現有資料準確性的評估需求，以及未來跨校系合作的長遠展望，該教務處與資訊系所合作，正尋求能兼顧資料準確性與個資保護的解決方案，期望透過合成資料技術，以一筆學生一筆資料的顆粒度開放原始精度的學術使用，同時協助評估隱私保護與資料可用性間的最佳平衡點。

### 資料特性與挑戰

- **高基數類別變數**：因學生身份類別多樣、系所與入學方案也眾多，許多欄位都具有大量獨特值。

## 高基數

基數 (Cardinality) 指的是一個向量中非零元素的數量，在資料領域中指的是某個資料集合或變數中不同值的數量。具體來說，對於一個類別變數，其基數即為該變數唯一值 (unique value) 的數量。

而高基數（High Cardinality / Large Cardinality）則是指當一個類別變數的唯一值數量特別多的情況。一般學術跟實務上都沒有對基數要「多高」才叫高基數訂下明確的界限，但文獻中提過以下定義：

1. 超過 100 個唯一值的名義屬性：依據過去文獻的建模結果 [^1]
2. 隨著樣本數增加而增加的類別屬性 [^2]
3. 在資料庫中唯一值數量遠大於本地快取記憶體容量 (L1/L2) [^3]

### 高基數類別的約束處理

而前一篇[類別變項](./categorical)解釋過，資料前處理技術會建議以編碼 (encoding) 處理名目或順序尺度的類別變項，但這些方法在面對高基數情境時常會遇到嚴重挑戰，在高基數類別變量上應用這些編碼很容易導致特徵空間維度爆炸、稀疏性問題、統計學習效率低下及模型泛化能力下降。

本 CAPE 團隊除了建議使用均勻編碼處理任何類別變項之外，在高基數情況，建議搭配約束條件在遞迴的合成流程中做合成器的事後檢驗，會更為容易操作、也更具有專業知識的控制領域知識。

由於主流的合成資料是基於機率模型，雖然能學習到資料內隱含的關係結構，但在大量抽樣過程中仍可能產生違反商業邏輯的極端狀況。約束條件的設計正是為了確保合成資料符合業務規範，而最前沿的合成資料研究也開始利用知識圖產生約束條件 [^4]，在合成模型的條件機率 [^5] 或懲罰項 [^6] 當中整合約束條件，甚至純粹只用約束條件產生合成資料 [^7]，並且約束條件亦有助於消除歧視、提升公平性 [^8]。

## 約束條件盤點示範

本示範資料集有許多種商業邏輯，CAPE 團隊將示範用我們團隊開發的約束條件處理器、所設定的幾種主流的約束邏輯，來治理這些欄位。治理方式作為參考，使用者可以用不同方法達成類似的目的，而權衡哪些條件是必要的、哪些條件可以換個方法寫，便是我們在這篇最佳實踐裡推薦資料擁有者自行盤點決策的部分。

- 生日與星座：欄位約束 (`field_constraints`)

  - 由於年月日是分開合成的，因此產生了 2 月有 30、31 日，這種違反大小月以及閏年的情況
  - 此外星座也是分開合成的，因此生日跟星座並不對應

- 大學、學院、與系所：欄位組合約束 (`field_combinations`)

  - 本模擬使用了臺灣大學跟政治大學三個院系：文學院、理學院、和電資學院
  - 但不同學校有系所設計的差異：臺大的叫電機資訊學院、政大的叫資訊學院，臺大的文學院還多了人類學、圖資、日文、戲劇，理學院還多了物理、化學、地質、等等，合成出來可能會出現院系名稱跟校名不對應的情況
  - 即使是同樣系名，由於兩校的系所編號不同，也可能合成出編號不對應該學校

- 國籍與國籍代碼：遺失值群組約束 (`nan_group`)

  - 教育部入學統計的國籍是針對外籍學生而編號的，因此占最大多數的本國同學，在國籍代碼對照會是空的

由於合成資料具有隨機性，以下示範的檢查錯誤，不一定會與使用者操作復現所看到的一致，請自行對照：

### 生日與星座：欄位約束

共有 145 筆 (1.5%) 合成的日期不合格式，9,145 筆 (91.5%) 合成資料的星座不符合日期。

|  | index | reason | year | month | day |
|------|------|------|------|------|------|
| 0 | 55 | 該年2月沒有31日 | 2005 | 2 | 31 |
| 1 | 116 | 該年4月沒有31日 | 2002 | 4 | 31 |
| 2 | 260 | 該年2月沒有30日 | 2001 | 2 | 30 |

| index | reason | month | day | zodiac | expected_zodiac |
|-------|--------|-------|-----|--------|----------------|
| 0 | 星座與出生日期不匹配 | 6 | 10 | 天蠍座 | 雙子座 |
| 1 | 星座與出生日期不匹配 | 12 | 7 | 天蠍座 | 射手座 |
| 2 | 星座與出生日期不匹配 | 2 | 23 | 處女座 | 雙魚座 |

### 大學、學院、與系所：欄位組合約束

#### 大學

共有 1,340 筆 (13.4%) 合成的學校不符合學校代碼。

| index | university_code | university | reason |
|-------|----------------|------------|------------|
| 1 | 001 | 國立政治大學 | 大學代碼與名稱不符，大學代碼應對應 國立臺灣大學 |
| 28 | 001 | 國立政治大學 | 大學代碼與名稱不符，大學代碼應對應 國立臺灣大學 |
| 31 | 001 | 國立政治大學 | 大學代碼與名稱不符，大學代碼應對應 國立臺灣大學 |

#### 學院

有 6,415 筆 (64.2%) 合成的學院不符合學院代碼，5,285 筆 (52.9%) 合成的學院代碼跟學校代碼不符合。

| index | college_code | college | reason |
|-------|-------------|----------|--------|
| 0 | 100 | 資訊學院 | 學院代碼與名稱不符，學院代碼應對應 文學院 |
| 1 | 1000 | 電機資訊學院 | 學院代碼與名稱不符，學院代碼應對應 文學院 |
| 2 | 9000 | 資訊學院 | 學院代碼與名稱不符，學院代碼應對應 電機資訊學院 |

| index | university_code | college_code | reason |
|-------|----------------|--------------|--------|
| 0 | 001 | 100 | 學院 100 不屬於大學 001 |
| 1 | 002 | 2000 | 學院 2000 不屬於大學 002 |
| 2 | 002 | 1000 | 學院 1000 不屬於大學 002 |

#### 系所

有 9,540 筆 (95.4%) 合成的系所不符合系所代碼， 9,425 筆 (94.3%) 合成的系所代碼跟學院代碼不符合。

| index | college_code | department_code | reason |
|-------|-------------|----------------|--------|
| 0 | 9000 | 101 | 系所 101 不屬於該學院 |
| 1 | 100 | 117 | 系所 未知編號 不屬於該學院 |
| 2 | 2000 | 101 | 系所 101 不屬於該學院 |

| index | department_code | department_name | reason |
|-------|----------------|-----------------|--------|
| 0 | 101 | 電機工程學系 | 系所代碼與名稱不符，系所代碼應對應 中國文學系 |
| 1 | 117 | 中國文學系 | 系所代碼與名稱不符，系所代碼應對應 未知系所 |
| 2 | 101 | 大氣科學系 | 系所代碼與名稱不符，系所代碼應對應 中國文學系 |

### 國籍與國籍代碼：遺失值群組約束

有 1,353 筆 (13.5%) 合成的國籍與國籍代碼的遺失值對應有誤。

| index | nationality_code | nationality | reason |
|-------|-----------------|-------------|--------|
| 0 | 113 | 中華民國 | 中華民國國籍不應有國籍代碼 |
| 1 | 113 | 中華民國 | 中華民國國籍不應有國籍代碼 |
| 2 | 113 | 中華民國 | 中華民國國籍不應有國籍代碼 |

## 約束條件設定

在合成資料生成過程中，CAPE 團隊提供的 PETsARD 框架包含三種關鍵約束類型：遺失值群組約束、欄位約束和欄位組合約束，它們共同確保生成的資料不僅在統計特性上反映原始資料，還能符合特定領域邏輯和業務規範。以下是使用 PETsARD 約束條件時需注意的關鍵事項：

1. 這些約束機制以「全部滿足」的邏輯運作，意味著合成資料必須同時符合所有定義的約束條件才會被保留，任何違反單一規則的記錄都將被篩除，從而保證最終結果的完整合規性。
2. 由於 PETsARD 中的約束類型被設計為固定且獨立的功能模組，使用者在處理橫跨多種約束需求的資料情境時，應當根據約束類型分別宣告。例如，同一組欄位可能既需要檢查遺失值邏輯，又需要驗證欄位間的組合關係，在這種情況下，應將約束條件依照其邏輯分類分別宣告於對應的約束類型下，而非嘗試在單一約束類型中處理全部規則。
3. 遺失值群組約束 (`nan_groups`)：允許三種不同的遺失值處理方式：刪除含遺失值的記錄、將相關欄位設為遺失值、或從一個欄位複製值到其他欄位，使用時需確保操作類型符合資料的實際需求。
4. 欄位約束 (`field_constraints`)：複支援比較運算（>、>=、==、!=、<、<=）、邏輯運算（&、|）及特殊檢查（IS、IS NOT），並可使用 DATE() 函數處理日期值，使用時應善用括號明確定義複雜表達式的邏輯順序，確保條件解析無歧義。
5. 欄位組合約束 (`field_combinations`)：提供單一欄位映射與多欄位映射功能，以正面表列方式定義欄位間的有效值組合關係，特別適用於建立類別變數間的對應規則。

本文主要聚焦於最佳實踐，僅展示經驗證有效的約束條件設定組合。然而，人類自然語言與邏輯表述複雜多變，同一組資料與約束條件盤點，可能衍生多種潛在的宣告方式。使用者請以 PETsARD 官方資料[約束教學](../../tutorial/use-cases/data-constraining/)文件為主要參考依據，若有特殊需求，建議直接聯絡 PETsARD 團隊尋求客製化開發支援。

### 生日與星座：欄位約束

- 對於生日，我們限定了

  - 出生年應該在 1990 ~ 2020 年間
  - 出生日必須大於 1
  - 對月份天數用同一個條件限制：
    - 大月的月份日期小於 31
    - 小月（除了二月）的月份日期小於 30
    - 二月依照平閏年
      - 閏年正面表列，可以小於 29
      - 其他的視為平年，必須小於 28

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

- 對於星座，我們用同一個條件：

  - 每個星座對應兩個月份，而各自有對應的日期大小限制

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

### 大學、學院、與系所：欄位組合約束

- 對於大學、學院與系所，我們設計了多層次的對應關係：

  - 大學編碼與大學名稱的對映（如「001」對應「國立臺灣大學」）
  - 大學編碼與其包含的學院編碼群組（如臺大包含「1000」、「2000」和「9000」學院編碼）
  - 學院編碼與學院名稱的對映（如「1000」對應「文學院」）
  - 系所編碼與系所名稱的對映（如「1010」對應「中國文學系」）
  - 國籍代碼與無效值的對映：當國籍為「中華民國」時，將國籍代碼設為無效（NaN）

```yaml
Constrainer:
  demo:
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

### 國籍與國籍代碼：遺失值群組約束

- 對於國籍代碼，我們設計了下列對應關係：

  - 國籍代碼與無效值的對映：當國籍為「中華民國」時，將國籍代碼設為無效（NaN）

```yaml
Constrainer:
  demo:
    nan_groups:
      nationality_code:
        nan_if_condition:
          nationality:
            - '中華民國' # ROC (Taiwan)
```

### 為什麼產生出來的資料仍然有錯？

這是因為我們示範當中所設定的最大嘗試次數 (`max_trials`) 500 次，尚不足以成功約束學院與系所配對組合這個條件。

```yaml
Constrainer:
  demo:
    max_trials: 500
```

在 PETsARD 中，為了避免使用者提供無效的約束條件，我們設定有最大嘗試次數，預設 300 次，當重新合成 300 次後、仍然沒辦法合成並約束出跟原始資料一樣多筆數的結果，便會拋出當前的合成結果。你可以看到其他條件都通過了，僅剩下 704 筆不符合學院與系所配對組合的紀錄。

從資料結構來看，這是由於學院跟系所的組合數已經很大（23 個系），而從合成器來看，高斯耦合沒辦法很好的學習到他們潛在的約束條件，所以只能重新在常態分配上抽樣、然後再被約束器拒絕。

這個情況有幾種處理方式：

1. **提高最大嘗試次數**：經觀察，每 10 次約束重抽，大約可以產生 10 筆左右的合成約束資料，那將 max_trails 提升到 1,000、也就是花目前兩倍的合成時間，甚至更保險的 1,500 就是合理的調參方式。
2. **捨棄該約束條件**：如果學院跟系所的組合並非重要，舉例來說，使用者的下游任務是分別計算各學院跟各系所的平均成績，那考量高斯耦合的建模邏輯，這種一對一欄位的平均數是可以很好的保真的，那就或許不需要這個約束條件。這完全取決於資料擁有者對於資料的專業知識做判斷。
3. **更換更能學習潛在模式的合成器**：諸如 GAN 或 VAE 等深度學習為啟發的合成器，理論上均可以更好的學習到類別變項之間的條件機率，因此可以咸認在高斯耦合上很難達到的條件，可以放心的放在進階的合成器中執行
4. **對於可彼此推理的屬性，只合成最重要的少數欄位**：以學校系所為例，由於系所是最高顆粒度，而學院、學校都可以靠推衍得來，即使是同名的系所，也可以額外抽樣分配，故可以先用合成器合成系所就好，合成完再另外用程式邏輯補上可被推衍的其他欄位。

同樣的，事實上我們對於入學方式的合理性也尚未治理，合成出來的結果有很多不符合現實資料的地方，這也是示範我們如何加以權衡的部分。

## 完整示範

請點擊下方按鈕在 Colab 中執行範例：

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

### 實踐經驗心得

合成資料的約束條件系統是確保資料品質與業務合規性的關鍵要素，涵蓋遺失值處理邏輯、時序性規則、合理值域限制及業務規範等多面向。基於我們的實際應用經驗，有效的約束條件設計需兼顧嚴謹性與實用性，以下是關鍵的實務經驗總結：

- **業務知識的融入**

  - 結合領域專家知識設計約束條件，以實際業務場景為中心，並透過真實情境測試驗證約束效果

- **循序漸進的約束策略**

  - 從基本邏輯規則開始，穩定後再納入複雜約束，並反覆與持續的評估每個約束對資料品質的影響。

- **約束強度與效能平衡**

  - 過多或過於嚴格的約束可能導致抽樣效率極低或無法收斂，建議識別並保留真正必要的約束
  - 採用分批實施策略，先處理高優先級約束，觀察結果後再加入次要約束，並預先評估約束間的潛在衝突。

- **合成流程外的高基數欄位處理**

  - 考慮在合成前，對高基數欄位進行策略性分類或聚合，有效降低唯一值數量。
  - 無論是拆開來合成、或設定約束條件，都可以善用階層式結構處理複雜類別變數，採取「先合成子類別，再推衍主類別」的分層方法。
  - 對於具明確對應關係的資料，考慮暫時移除對應欄位、完成合成後再透過配對機制重新導入。
  - 針對超高基數的準識別欄位（如身份識別碼、詳細地址等），適時採用模式化邏輯生成機制，作為直接合成的替代方案。

### 為何 PETsARD 要有自己的約束條件模組？

以 CAPE 團隊使用的 SDV 合成資料工具生態系為例，的確有部分合成模組有提供約束功能，但多數將高級約束功能設為商用版限制。PETsARD 開發自有的約束條件模組，主要基於以下考量：

- 功能完整性：確保基本約束功能不受商業版本限制，如鍊式不等式、全空組合和混合範圍約束等
- 本地化需求：針對臺灣特殊資料場景（如中文處理、特定產業規範）提供客製化約束支援
- 效能優化：專為高基數類別變數設計更高效的約束滿足算法，減少純拒絕抽樣的效率問題
- 研究自主性：保持約束系統的研究與開發自主權，能更靈活應對不同資料合成需求

### 更好的合成器可以取代約束條件嗎？

如前面的論文所述，新穎研究確實指出運用深度學習等方法能不斷強化合成器對關係結構的學習能力。儘管本團隊示範主要基於基礎的高斯耦合（Gaussian Copula）模型，採用更先進的合成器的確能減少約束條件的違反情形。然而，即便是先進合成器仍有一定機率無法完全學習到或可能錯誤生成不符合條件的資料，且更複雜的模型往往需要更長的訓練時間和更大的資料量。

因此，CAPE 團隊建議將約束條件視為資料合成流程中的「守門人」，採取「優質合成器搭配必要約束條件」的整合策略。這種方法既能透過約束條件有效降低合成器訓練與參數調校的需求，同時藉由高品質合成器避免因約束條件過於複雜而導致反覆抽樣無果，進而引起的合成時間延宕問題。這種互補策略能在資料品質與計算效率間取得更佳平衡。

### 總結

約束條件系統是合成資料品質的守門員，透過這些實務導向的策略來運用約束條件，能在確保合成資料業務合規性的同時，維持合理的計算效率與合成資料的統計品質。

## 參考資料

[^1]: Moeyersoms, J., & Martens, D. (2015). Including high-cardinality attributes in predictive models: A case study in churn prediction in the energy sector. Decision Support Systems, 72, 72-81.

[^2]: Cerda, P., & Varoquaux, G. (2022). Encoding high-cardinality string categorical variables. IEEE Transactions on Knowledge and Data Engineering, 34(3), 1164-1176. https://doi.org/10.1109/TKDE.2020.2992529

[^3]: Siddiqui, T., Narasayya, V., Dumitru, M., & Chaudhuri, S. (2023). Cache-efficient top-k aggregation over high cardinality large datasets. Proceedings of the VLDB Endowment, 17(4), 644-656. https://doi.org/10.14778/3636218.3636222

[^4]: Kotal, A., & Joshi, A. (2024). KIPPS: Knowledge infusion in Privacy Preserving Synthetic Data Generation. arXiv. https://arxiv.org/abs/2409.17315

[^5]: Ge, C., Mohapatra, S., He, X., & Ilyas, I. F. (2021). Kamino: Constraint-aware differentially private data synthesis. Proceedings of the VLDB Endowment, 14(10), 1886-1899. https://doi.org/10.14778/3467861.3467876

[^6]: Li, W. (2020). Supporting database constraints in synthetic data generation based on generative adversarial networks. In Proceedings of the 2020 ACM SIGMOD International Conference on Management of Data (pp. 2875-2877). ACM. https://doi.org/10.1145/3318464.3384414

[^7]: Arasu, A., Kaushik, R., & Li, J. (2011). Data Generation using Declarative Constraints. Proceedings of the 2011 ACM SIGMOD International Conference on Management of Data, 685-696. https://doi.org/10.1145/1989323.1989395

[^8]: Abroshan, M., Elliott, A., & Khalili, M. M. (2024). Imposing fairness constraints in synthetic data generation. Proceedings of The 27th International Conference on Artificial Intelligence and Statistics, 238, 2269-2277.
