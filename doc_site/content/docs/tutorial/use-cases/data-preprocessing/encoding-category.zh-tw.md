---
title: 類別編碼
type: docs
weight: 22
prev: docs/tutorial/use-cases/data-preprocessing/handling-missing
next: docs/tutorial/use-cases/data-preprocessing
---

多數合成演算法僅支援數值型欄位的合成，即使直接支援類別欄位合成，也通常涉及合成器本身內建的前處理與後處理還原轉換。而 CAPE 團隊正是希望控制這些第三方套件不可預期的行為而設計了 `PETsARD`，建議對於任何包含類別變項的欄位，都應主動進行編碼處理：

* 類別變項：預設使用均勻編碼（Uniform Encoding），技術細節見開發者手冊中的[均勻編碼](docs/developer-guide/uniform-encoder/)

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/use-cases/preproc/encoding-category.ipynb)

```yaml
---
Loader:
  data:
    filepath: 'benchmark/adult-income.csv'
Preprocessor:
  encoding-only:
    # only execute the encoding by their default,
    sequence:
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

下面配置用於客製化類別編碼的處理方式。設定 `method: 'default'` 表示除了特別指定的欄位外，其他欄位都採用預設的處理方式。

在 `encoder` 區塊中，我們針對三個欄位採用不同的編碼策略：`workclass` 欄位採用均勻編碼來處理遺失值，`occupation` 欄位使用標籤編碼、並假設職業類別的字母排序反映了其階層性質，而 `native-country` 欄位則採用獨熱編碼、將其轉換為 k 維二元變數，以保留每個國家類別的獨特性質且避免引入虛假的順序關係。

```yaml
Preprocessor:
  encoding-custom:
    sequence:
      - 'encoder'
    encoder:
      workclass: 'encoding_uniform'
      occupation: 'encoding_label'
      native-country: 'encoding_onehot'
```

## 編碼處理方法

1. 均勻差補編碼（`encoding_uniform`）
  - 將類別值轉換為均勻分布的數值
  - 適用於一般類別變項
  - 預設的編碼方式

2. 標籤編碼（`encoding_label`）
  - 將類別值轉換為連續整數
  - 適用於有序類別變項
  - 保留類別之間的順序關係

3. 獨熱編碼（`encoding_onehot`）
  - 將每個類別轉換為獨立的特徵欄位，每個欄位代表一個類別的存在與否
  - 類別資料在合成過程中以獨立特徵的形式處理，合成後再重新組合還原
  - 適用於類別數量較少的變項，因為每增加一個類別就會增加一個特徵維度

4. 日期編碼（`encoder_date`）
   - 將日期時間值轉換為數值格式以進行合成
   - 支援多種輸出格式：
       - 純日期：基本日期資訊
       - 日期時間：完整的日期和時間資訊
       - 含時區的日期時間：包含時區的完整時間資訊
   - 提供特殊功能：
       - 支援自訂曆法（如民國年）
       - 彈性的日期解析
       - 多種無效日期處理策略
       - 時區處理支援

您可以針對不同欄位使用不同的編碼方法，只要在設定檔中指定相應的設定即可。