---
title: 遺失值處理
type: docs
weight: 21
prev: docs/tutorial/use-cases/data-preprocessing
next: docs/tutorial/use-cases/data-preprocessing/encoding-category
---


由於大部分合成演算法是基於機率模型，經 CAPE 團隊研究發現，多數演算法無法直接支援遺失值（`None`、`np.nan`、`pd.NA`）。即使部分演算法宣稱可以處理遺失值，也很難確認各自的實現方法是否恰當。因此，`PETsARD` 建議對於任何包含遺失值的欄位，都應主動進行處理：

* 數值型欄位：預設使用平均值插補
* 類別型/文字型/日期型欄位：預設採用直接刪除策略

`PETsARD` 亦提供多種遺失值處理方法供您選擇。

請點擊下方按鈕在 Colab 中執行範例：

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

## 自訂設定

下面配置用於客製化遺失值的處理方式。設定 `method: 'default'` 表示除了特別指定的欄位外，其他欄位都採用預設的處理方式。

在 `missing` 區塊中，針對三個欄位進行客製化處理：`workclass` 欄位的遺失值會被直接刪除、`occupation` 欄位的遺失值會用眾數填補，而 `native-country` 欄位的遺失值則會用指定的值 'Galactic Empire' 進行填補。

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

## 遺失值處理方法

1. 直接刪除 (`missing_drop`)

  - 刪除含有遺失值的資料列
  - 適用於遺失值較少的情況
  - 需注意可能損失重要資訊

2. 統計插補

  - 平均值插補 (`missing_mean`)：用該欄位的平均值填入
  - 中位數插補 (`missing_median`)：
  - 眾數插補 (`missing_mode`)：
  - 適用於不同資料型態：
    - 數值型資料可使用平均值或中位數
    - 類別型資料建議使用眾數

3. 自定義插補 (`missing_simple`)

  - 用指定的數值填補遺失值
  - 需要設定 `value` 參數
  - 適用於有特定業務邏輯的情況

您可以針對不同欄位使用不同的處理方法，只要在設定檔中指定相應的設定即可。