---
title: PETsARD (/pəˈtɑrd/)
toc: false
---

<p style="text-align:center">
  隱私強化技術分析、研究與開發
</p>

<p align="center"><img src="/PETsARD/images/PETsARD-logo.png"></p>

`PETsARD`（隱私強化技術分析、研究與開發, /pəˈtɑrd/）是一套為了促進資料生成演算法及其評估過程而設計的 Python 程式庫。

其主要功能包括描述資料集、執行各種資料集生成算法，以及對隱私保護和效用進行測量。

- [Release Note](https://github.com/nics-tw/PETsARD/releases)
  - Release Note提供 `PETsARD` 每個版本的變更內容。
- [CHANGELOG.md](https://github.com/nics-tw/PETsARD/blob/main/CHANGELOG.md)
  - Changelog 提供 `PETsARD` 隨時間演進的所有變更。

## 探索

{{< cards >}}
{{< card link="docs/design-structure/" title="文件" icon="book-open" >}}
{{< card link="about" title="關於" icon="user" >}}
{{< /cards >}}

## 開源

歡迎提交拉取請求。對於重大變更，請先開啟一個議題來討論您想做的改變。並請確保適當地更新測試。

## 授權

本專案採用 `MIT` 授權，但因相依套件而有額外限制。最主要的限制來自 SDV 的 Business Source License 1.1，禁止將本軟體用於商業性的合成資料服務。詳細的授權資訊請參閱 LICENSE 檔案。

主要相依套件授權：

- SDV: Business Source License 1.1
- Anonymeter: The Clear BSD License
- SDMetrics: MIT License
- Smartnoise: MIT License

如需將本軟體用於合成資料的商業服務，請聯絡 DataCebo, Inc.

## 引用

- `Synthesizer` module:
  - SDV - [sdv-dev/SDV](https://github.com/sdv-dev/SDV):
    - Patki, N., Wedge, R., & Veeramachaneni, K. (2016). The Synthetic Data Vault. IEEE International Conference on Data Science and Advanced Analytics (DSAA), 399–410. https://doi.org/10.1109/DSAA.2016.49
  - smartnoise - [opendp/smartnoise-sdk](https://github.com/opendp/smartnoise-sdk):
- `Evaluator` module:
  - Anonymeter - [statice/anonymeter](https://github.com/statice/anonymeter):
    - Giomi, M., Boenisch, F., Wehmeyer, C., & Tasnádi, B. (2023). A Unified Framework for Quantifying Privacy Risk in Synthetic Data. Proceedings of Privacy Enhancing Technologies Symposium. https://doi.org/10.56553/popets-2023-0055
  - SDMetrics - [sdv-dev/SDMetrics](https://github.com/sdv-dev/SDMetrics)
