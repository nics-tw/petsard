---
title: Constrainer
type: docs
weight: 57
prev: docs/api/synthesizer
next: docs/api/evaluator
---


```python
Constrainer(config)
```

合成資料的約束條件處理器。支援空值處理、欄位約束及欄位組合規則。

## 參數

- `config` (dict)：約束條件設定字典，包含以下鍵值：

  - `nan_groups` (dict)：空值處理規則
    - 鍵：包含空值的欄位名稱
    - 值對於 'delete' 動作：字串 'delete'
    - 值對於 'erase' 和 'copy' 動作：包含動作和目標欄位的字典
      - 'erase'：`{'erase': target_field}`，其中 target_field 可以是字串或字串列表
      - 'copy'：`{'copy': target_field}`，其中 target_field 是字串
    - 值對於 'nan_if_condition' 動作：`{'nan_if_condition': condition_dict}`
      - condition_dict 是一個字典，其中：
        - 鍵：要檢查條件的目標欄位名稱
        - 值：該欄位中符合條件的值（可以是單一值或值列表）
      - 當目標欄位的值符合指定條件時，主欄位的值將被設為 pd.NA

  - `field_constraints` (List[str])：以字串表示的欄位約束條件
    - 支援運算子：>、>=、==、!=、<、<=、IS、IS NOT
    - 支援邏輯運算子：&、|
    - 支援括號運算式
    - 特殊值：pd.NA 用於空值檢查
    - DATE() 函數用於日期比較

  - `field_combinations` (List[tuple])：欄位組合規則
    - 每個元組包含 (欄位映射, 允許值)
      - 欄位映射：包含一個來源對目標欄位的映射字典
      - 允許值：來源值對應允許目標值的字典

  - `field_proportions` (List[dict])：欄位比例維護規則列表
    - 每個規則是一個字典，包含：
      - `fields` (str 或 List[str])：要維護比例的欄位名稱，可以是單一欄位或欄位列表
      - `mode` (str)：'all'（維護所有值分布）或 'missing'（僅維護缺失值比例）
      - `tolerance` (float, 可選)：允許與原始比例的偏差範圍（0.0-1.0），預設為 0.1（10%）

> 註：
> 1. 所有約束條件都是以 AND 邏輯組合。一筆資料必須滿足所有約束條件才會被保留。
> 2. 欄位組合規則採用正面表列方式，只影響指定的值。例如，若規定教育程度為 PhD 時績效需要是 [4,5]，這個規則只會過濾教育程度是 PhD 的資料，其他教育程度或空值都不受此規則影響。
> 3. 欄位比例規則透過迭代移除過量資料同時保護代表性不足的群體，來維護原始資料分布。
> 4. 當在 YAML 或 Python 設定中處理空值時，請一律使用字串 "pd.NA"（大小寫敏感）來表示，而非使用 None、np.nan 或 pd.NA 物件，以避免意外情況。

## 範例

```python
from petsard import Constrainer


# 設定約束條件
config = {
    # 空值處理規則 - 指定當某欄位為空值時，如何處理相關欄位
    'nan_groups': {
        'name': 'delete',  # name 是空值時，刪除整列
        'job': {
            'erase': ['salary', 'bonus']  # job 是空值時，把 salary 和 bonus 設為空值
        },
        'salary': {
            'copy': 'bonus'  # salary 有值但 bonus 是空值時，複製 salary 的值到 bonus
        }
    },

    # 欄位條件 - 指定單一欄位的值域範圍
    # 支援運算子：>, >=, ==, !=, <, <=, IS, IS NOT
    # 支援邏輯運算子：&, |
    # 支援括號運算式和 DATE() 函數
    'field_constraints': [
        "age >= 20 & age <= 60",  # 年齡必須在 20-60 歲之間
        "performance >= 4"  # 績效必須大於等於 4 分
    ],

    # 欄位組合規則 - 指定不同欄位間的值域配對關係
    # 格式：(欄位映射, 允許值配對)
    # 注意：這是正面表列，未列出的值不會被過濾，例如：
    # - 若教育程度不是 PhD/Master/Bachelor，不會被過濾
    # - 若教育程度是 PhD 但績效不是 4 或 5，才會被過濾
    'field_combinations': [
        (
            {'education': 'performance'},  # 教育程度和績效的對應
            {
                'PhD': [4, 5],  # 博士只允許 4 或 5 分
                'Master': [4, 5],  # 碩士只允許 4 或 5 分
                'Bachelor': [3, 4, 5]  # 學士允許 3, 4, 5 分
            }
        ),
        # 可以設定多個欄位的組合
        (
            {('education', 'performance'): 'salary'},  # 教育程度+績效對應薪資
            {
                ('PhD', 5): [90000, 100000],  # 博士且績效 5 分的薪資範圍
                ('Master', 4): [70000, 80000]  # 碩士且績效 4 分的薪資範圍
            }
        )
    ],

    # 欄位比例規則 - 維護原始資料分布比例
    'field_proportions': [
        # 維護類別分布，使用預設容忍度 10%
        {'fields': 'category', 'mode': 'all'},

        # 維護收入欄位的缺失值比例，自定義容忍度 5%
        {'fields': 'income', 'mode': 'missing', 'tolerance': 0.05},

        # 維護欄位組合比例，使用預設容忍度 10%
        {'fields': ['gender', 'age_group'], 'mode': 'all'}
    ]
}

cnst: Constrainer = Constrainer(config)
result: pd.DataFrame = cnst.apply(df)
```

### 欄位比例範例

```python
# 範例 1：基本欄位比例（使用預設 tolerance 0.1）
config = {
    'field_proportions': [
        {'fields': 'category', 'mode': 'all'}  # 維護類別分布，預設 10% 容忍度
    ]
}

# 範例 2：缺失值比例（自定義 tolerance）
config = {
    'field_proportions': [
        {'fields': 'income', 'mode': 'missing', 'tolerance': 0.05}  # 維護缺失比例，5% 容忍度
    ]
}

# 範例 3：多欄位組合
config = {
    'field_proportions': [
        {'fields': 'category', 'mode': 'all'},  # 預設 10% 容忍度
        {'fields': 'income', 'mode': 'missing', 'tolerance': 0.05},  # 自定義 5% 容忍度
        {'fields': ['gender', 'age_group'], 'mode': 'all', 'tolerance': 0.15}  # 自定義 15% 容忍度
    ]
}
```

## 方法

### `apply()`

```python
cnst.apply(df)
```

套用已設定的約束條件到輸入的資料框。

**參數**

- `df` (pd.DataFrame)：要套用約束的輸入資料框

**回傳值**

- pd.DataFrame：套用所有約束後的資料框

### `resample_until_satisfy()`

```python
cnst.resample_until_satisfy(
    data=df,
    target_rows=1000,
    synthesizer=synthesizer,
    postprocessor=None,
    max_trials=300,
    sampling_ratio=10.0,
    verbose_step=10
)
```

重複採樣直到滿足約束條件且達到目標列數。

**參數**

- `data` (pd.DataFrame)：要套用約束的輸入資料框
- `target_rows` (int)：目標列數
- `synthesizer`：用於生成合成資料的合成器實例
- `postprocessor` (optional)：資料轉換的後處理器（選用）
- `max_trials` (int, default=300)：最大嘗試次數
- `sampling_ratio` (float, default=10.0)：每次生成的資料量是目標列數的倍數
- `verbose_step` (int, default=10)：每隔幾次嘗試顯示進度

**回傳值**

- pd.DataFrame：滿足所有約束條件且具有目標列數的資料框

### register()

註冊新的約束條件類型。

**參數**

- `name` (str)：約束條件類型名稱
- `constraint_class` (type)：實現約束條件的類別

**回傳值**

無

## 屬性

- `resample_trails`：重新抽樣的次數，僅在執行 `resample_until_satisfy()` 後產生 (int)