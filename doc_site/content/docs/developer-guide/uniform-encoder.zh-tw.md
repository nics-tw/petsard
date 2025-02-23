---
title: 均勻編碼
type: docs
weight: 83
prev: docs/developer-guide/benchmark-datasets
next: docs/developer-guide/anonymeter
---

將類別變數轉換為連續值時，均勻編碼 (Uniform Encoder) 能提供更好的生成模型效果。此方法由 [datacebo](https://datacebo.com/) 提出，核心概念是將各類別對應到均勻分布中的特定區間，區間大小由該類別在資料中的比例決定。

## 原理說明

**基本概念**

- 將離散的類別映射到 [0,1] 區間
- 依照類別出現頻率決定映射區間大小
- 在區間內隨機取值作為編碼結果

**優勢**

1. 將離散分布轉換為連續分布，有利於建模
2. 固定的值域範圍 [0,1]，便於還原類別
3. 保留原始分布資訊，常見類別有較大的取樣機率

## 實作範例

假設有個類別變數包含三個類別 'a'、'b'、'c'，出現比例為 1:3:1：

```python
mapping = {
    'a': [0.0, 0.2),  # 20% 的區間
    'b': [0.2, 0.8),  # 60% 的區間
    'c': [0.8, 1.0]   # 20% 的區間
}
```

**編碼過程**

- 類別 'a' → 隨機取值於 [0.0, 0.2)
- 類別 'b' → 隨機取值於 [0.2, 0.8)
- 類別 'c' → 隨機取值於 [0.8, 1.0]

**還原過程**

- 檢查數值落在哪個區間
- 對應回該區間的類別

## 使用建議

- 適用於類別數量較少的特徵
- 對不平衡的類別分布特別有效
- 可與其他前處理方法（如尺度轉換）組合使用

## 參考資料

- [Improving Synthetic Data Quality with the Uniform Encoder](https://datacebo.com/blog/improvement-uniform-encoder/)