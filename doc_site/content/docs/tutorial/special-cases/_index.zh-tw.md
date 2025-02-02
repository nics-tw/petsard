---
title: 特殊案例
type: docs
weight: 15
prev: docs/tutorial/external-synthesis-default-evaluation
next: docs/tutorial/special-cases/data-description
sidebar:
  open: true
---

在開發隱私保護資料合成流程時，您可能會遇到一些特殊需求。以下場景將幫助您處理這些情況：

1. **資料理解**：[資料描述](docs/tutorial/special-cases/data-description)
   - 在合成之前了解您的資料
   - 從不同的顆粒度分析資料特性
   - 包含全域、欄位與配對統計

2. **合成方法選擇**：[比較合成演算法](docs/tutorial/special-cases/comparing-synthesizers)
   - 比較不同合成演算法的效果
   - 在同一個實驗中使用多種演算法
   - 包含 Gaussian Copula、CTGAN 與 TVAE

3. **資料品質改善**：[資料遺失值處理](docs/tutorial/special-cases/handling-missing-values)
   - 處理資料中的遺失值
   - 針對不同欄位使用不同的處理方法
   - 包含刪除、統計插補與自定義插補

4. **實驗流程驗證**：[基準資料集](docs/tutorial/special-cases/benchmark-datasets)
   - 使用基準資料集測試您的合成流程
   - 確認合成參數設定的合理性
   - 提供可靠的參考標準

5. **客製化評估**：[自定義評測](docs/tutorial/special-cases/custom-evaluation)
   - 建立自己的評測方法
   - 實作不同顆粒度的評估
   - 整合進 PETsARD 的評測流程

每個特殊案例都提供了完整的範例，您可以透過 Colab 連結直接執行與測試。