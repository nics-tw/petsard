---
title: 資料約束
type: docs
weight: 32
prev: docs/tutorial/use-cases/custom-synthesis
next: docs/tutorial/use-cases/ml-utility
---

透過欄位值規則、欄位組合和空值處理策略來約束合成資料。
目前的實作支援三種約束：欄位約束、欄位組合和空值群組。

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/use-cases/data-constraining.ipynb)

```yaml
---
Loader:
  data:
    filepath: 'benchmark/adult-income.csv'
Preprocessor:
  demo:
    method: 'default'
Synthesizer:
  demo:
    method: 'default'
Postprocessor:
  demo:
    method: 'default'
Constrainer:
  demo:
    nan_groups:
      # 當 workclass 是空值時刪除整列
      workclass: 'delete'
      # 當 occupation 是空值時，把 income 設為空值
      occupation:
        'erase':
          - 'income'
      # 當 age 有值但 educational-num 是空值時，複製 age 的值到 educational-num
      age:
        'copy':
          'educational-num'
    field_constraints:
      - "age >= 18 & age <= 65" # 年齡限制在 18-65 歲
      - "hours-per-week >= 20 & hours-per-week <= 60" # 每週工時限制在 20-60 小時
    field_combinations:
      -
        - {'education': 'income'} # 教育程度和收入的對應關係
        - {'Doctorate': ['>50K'], 'Masters': ['>50K', '<=50K']} # 博士只能高收入，碩士可以高低收入
Reporter:
  output:
    method: 'save_data'
    source: 'Constrainer'
...
```

## 資料約束方法

資料約束是一種精細控制合成資料品質和一致性的機制，允許使用者透過多層次的規則定義資料的可接受範圍。`PETsARD` 提供三種主要的約束類型：遺失值群組約束、欄位約束和欄位組合約束。這些約束共同確保生成的合成資料不僅在統計特性上忠實於原始資料，更能符合特定的領域邏輯和業務規範。

> 備註：
> 1. 所有約束條件都以嚴格的「全部滿足」邏輯進行組合，這意味著一筆資料必須同時滿足所有已定義的約束條件，才會被最終保留。換言之，只有完全符合每一個約束規則的資料紀錄，才能通過篩選
> 2. 欄位組合規則使用正面表列方式，僅影響指定的值，對於欄位中未被提及的值是不受影響的
> 3. 在 YAML 使用 NA 值時，請始終使用字串 `"pd.NA"`
> 4. 強烈建議使用者在定義約束條件前，先對原始資料進行徹底的邏輯檢查，確保所設計的約束規則準確反映資料的本質特性。

### 遺失值（NaN）群組約束 (`nan_groups`)

- 遺失值群組約束允許您以客製化的方式處理缺失資料
  - `delete`：當特定欄位為 NA 時，刪除整列
  - `erase`：當主要欄位為 NA 時，將其他欄位設為 NA
  - `copy`：當主要欄位有值時，將值複製到其他欄位
- 資料約束與資料前處理的遺失值處理（`missing`）並不衝突，因為約束機制是在資料合成與資料還原後、進行篩選與驗證。這兩個步驟扮演互補角色：前處理階段處理資料的基礎缺失值問題以幫助合成，而約束機制則進一步確保合成資料符合特定的領域邏輯和統計規範。

  ```yaml
  Constrainer:
    demo:
      nan_groups:
        # 當 workclass 是 NA 時刪除整列
        workclass: 'delete'

        # 當 occupation 是 NA 時，將 income 設為 NA
        occupation:
          'erase':
            - 'income'

        # 當 age 是 NA 且 educational-num 有值時，複製 educational-num 的值到 age
        age:
          'copy':
            'educational-num'
  ```

### 欄位約束 (`field_constraints`)

- 欄位約束允許您對單一欄位設定特定的值域規則。
- 支援的運算子：
  - 比較運算子：`>`, `>=`, `==`, `!=`, `<`, `<=`
  - 邏輯運算子：`&`（且）, `|`（或）
  - 特殊檢查：`IS`, `IS NOT`
  - 日期函數：`DATE()` 函數允許在約束中宣告特定日期，並與其他欄位和邏輯運算子靈活組合

- 目前 `PETsARD` 的欄位約束實作採用自定義的語法解析器，支援複雜的邏輯運算與欄位比較，能夠處理多層巢狀的布林表達式，但仍存在一些功能限制。若遇到無法滿足的特定約束需求或複雜篩選邏輯，建議從原始資料剔除極端情況，或是直接聯絡 CAPE 團隊，以獲得更客製化的解決方案。

  ```yaml
  Constrainer:
    demo:
      field_constraints:
        - "age >= 18 & age <= 65"  # 年齡限制在 18-65 歲
        - "hours-per-week >= 20 & hours-per-week <= 60"  # 每週工時限制在 20-60 小時
        - "income == '<=50K' | (age > 50 & hours-per-week < 40)"  # 低收入或年長且工時少
        - "native-country IS NOT 'United-States'"  # 非美國籍
        - "occupation IS pd.NA"  # 職業資訊遺失
        - "education == 'Doctorate' & income == '>50K'"  # 博士學位必須高收入
        - "(race != 'White') == (income == '>50K')"  # 非白人種與高收入的互斥檢查
        - "(marital-status == 'Married-civ-spouse' & hours-per-week > 40) | (marital-status == 'Never-married' & age < 30)" # 複雜的邏輯組合

  ```

### 欄位組合約束 (`field_combinations`)

- 欄位組合約束允許您定義不同欄位之間的值域關係。
- 支援的組合類型：
  - 單一欄位映射：基於單一欄位的值進行約束
  - 多欄位映射：同時考慮多個欄位的值進行更複雜的約束
- 對於下面的範例：
  - 對於 income：只有博士和碩士的收入受到約束，學士的收入不受影響
  - 對於 salary：只有美國、加拿大和英國的博士有特定的薪資範圍限制
  - 非這三個國家的博士，或不是博士的這三個國家的人，都不會被過濾或影響
- 在當前的實作中，欄位組合約束採用正面表列方式，僅支援明確列出的值組合。數值欄位可以進行有效值的枚舉，但尚未支援像欄位約束中使用比較運算子進行數值的邏輯判斷。

  ```yaml
  Constrainer:
    demo:
      field_combinations:
        -
          - {'education': 'income'}
          - {
              'Doctorate': ['>50K'],           # 博士只允許高收入
              'Masters': ['>50K', '<=50K']      # 碩士允許高低收入
            }
        -
          - {('education', 'native-country'): 'salary'}
          - {
              ('Doctorate', 'United-States'): [90000, 100000],    # 美國的博士，薪資範圍
              ('Doctorate', 'Canada'): [85000, 95000],             # 加拿大的博士，薪資範圍
              ('Doctorate', 'United-Kingdom'): [80000, 90000]      # 英國的博士，薪資範圍
            }
  ```