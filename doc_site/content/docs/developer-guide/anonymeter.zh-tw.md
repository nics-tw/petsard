---
title: Anonymeter 隱私風險評測
type: docs
weight: 84
prev: docs/developer-guide/benchmark-datasets
next: docs/developer-guide/mpuccs
math: true
---

Anonymeter 是一套由 [Statice](https://www.statice.ai/) 開發的 Python 函式庫，專門用於評估合成表格資料的隱私風險。此工具實作了歐盟個人資料保護指令第29條工作小組 (WP29) 於 2014 年提出的匿名化技術評估標準，並於 2023 年獲得法國國家資訊自由委員會 (CNIL) 的認可。

## 評測架構

Anonymeter 從三個面向評估隱私風險：

### 指認性風險 (Singling Out Risk)

評估從資料中識別出特定個體的可能性。例如：「能找出唯一具有特徵 X、Y、Z 的個體」。

### 連結性風險 (Linkability Risk)

評估連結不同資料集中相同個體紀錄的可能性。例如：「能判斷紀錄 A 和 B 屬於同一人」。

為處理混合資料類型，此評測使用高爾距離 (Gower's Distance)：
- 數值變數：歸一化後的絕對差值
- 類別變數：不相等時距離為 1

### 推斷性風險 (Inference Risk)

評估從已知特徵推斷其他屬性的可能性。例如：「具有特徵 X 和 Y 的人，其特徵 Z 為何」。

## 風險計算

### 隱私風險分數

隱私風險分數採用以下公式計算：

$$
Privacy Risk = \frac{Attack Rate_{Main} - Attack Rate_{Control}}{1 - Attack Rate_{Control}}
$$

此公式衡量：
- 分子：合成資料帶來的額外風險（相對於控制組）
- 分母：理想攻擊的最大效果（相對於控制組）

分數範圍為 0-1，越高代表隱私風險越大。

### 攻擊成功率

攻擊成功率使用威爾遜分數計算：

$$
Attack Rate = \frac{N_{Success} + \frac{Z^2}{2}}{N_{Total} + Z^2}
$$

其中：
- N_Success：成功攻擊次數
- N_Total：總攻擊次數
- Z：95% 信心水準的 Z 分數

### 三種攻擊率

1. **主要攻擊率** (Main Attack Rate)：使用合成資料推斷原始資料的成功率

2. **基線攻擊率** (Baseline Attack Rate)：隨機猜測的成功率
   - 如果主要攻擊率低於基線，表示評測結果無意義
   - 可能原因：攻擊次數不足、輔助資訊太少、資料本身問題

3. **控制攻擊率** (Control Attack Rate)：使用合成資料推斷控制組資料的成功率

## 參考資料

- [WP29 Guidelines](https://ec.europa.eu/justice/article-29/documentation/opinion-recommendation/files/2014/wp216_en.pdf)
- [Anonymeter GitHub](https://github.com/statice/anonymeter)
- [CNIL Opinion](https://www.cnil.fr/en/home)
