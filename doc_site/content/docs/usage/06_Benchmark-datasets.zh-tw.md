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
|    adult-income     |                       Adult income dataset [^2]                       | adult-income.csv | Public |   15   |  48,842   |  5.1 MB  |  Unknown  |        |          |          |    ✅    |  ✅2   |  ✅3   | `1f13ee2` |

</div>

[^1]: https://www.kaggle.com/datasets/wenruliu/adult-income-dataset
