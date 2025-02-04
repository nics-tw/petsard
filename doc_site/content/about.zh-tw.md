---
title: 關於
type: about
weight: 99
prev: docs
next: index
---

`PETsARD` 的開發專案始於 2023 年，由臺灣數位發展部指導，為隱私強化技術推動計畫的一環，並由國家資通安全研究院執行。

2024 年 12 月，PETsARD v1.0 正式版釋出予數位發展部 (moda)。此套件持續在國家資通安全研究院 (NICS) 下積極開發中，歡迎有興趣的協作者聯繫與貢獻內容。

## 授權

本專案採用 `MIT` 授權，但因相依套件而有額外限制。最主要的限制來自 SDV 的 Business Source License 1.1，禁止將本軟體用於商業性的合成資料服務。詳細的授權資訊請參閱 LICENSE 檔案。

主要相依套件授權：

- SDV: Business Source License 1.1
- Anonymeter: The Clear BSD License
- SDMetrics: MIT License

如需將本軟體用於合成資料的商業服務，請聯絡 DataCebo, Inc.

## 引用

- `Synthesizer` 模組：
  - SDV - [sdv-dev/SDV](https://github.com/sdv-dev/SDV):
    - Patki, N., Wedge, R., & Veeramachaneni, K. (2016). The Synthetic Data Vault. IEEE International Conference on Data Science and Advanced Analytics (DSAA), 399–410. https://doi.org/10.1109/DSAA.2016.49
- `Evaluator` 模組：
  - Anonymeter - [statice/anonymeter](https://github.com/statice/anonymeter):
    - Giomi, M., Boenisch, F., Wehmeyer, C., & Tasnádi, B. (2023). A Unified Framework for Quantifying Privacy Risk in Synthetic Data. Proceedings of Privacy Enhancing Technologies Symposium. https://doi.org/10.56553/popets-2023-0055
  - SDMetrics - [sdv-dev/SDMetrics](https://github.com/sdv-dev/SDMetrics)
