---
title: 資料前處理
type: docs
weight: 20
prev: docs/tutorial/use-cases/data-description
next: docs/tutorial/use-cases/comparing-synthesizers
sidebar:
  open: false
---


在進行資料合成之前，確保原始資料的品質是相當重要的。高品質的輸入資料不僅能提升合成結果的品質，也能降低合成過程中可能遇到的技術問題。`PETsARD` 提供了完整的資料前處理工具，協助您進行資料品質改善：

> **重要提醒**：CAPE 預設先進行遺失值處理（missing）與極端值處理（outlier）後再進行編碼 (encoder) 與縮放 (scaler)。建議使用者僅在實驗性質並熟知自己的流程技術細節與目的下執行此行為，`PETsARD` 不保證改動預設順序的資料前處理的有效性。

## 資訊調整

### [遺失值處理](./handling-missing)

- 處理資料中的遺失值缺漏值
- 透過刪除、統計插補與自定義插補等方式確保資料完整性
- 針對不同的資料欄位與型態提供客製化選項

<!-- [極端值處理](./handling-outliers) -->
### 極端值處理（撰寫中）

- 識別並處理異常或極端的數值
- 避免極端值影響合成模型的學習
- 提供多種極端值判定和處理策略

## 表示形式轉換

### [類別編碼](./encoding-category)

- 將類別型資料轉換為數值型態
- 支援多種編碼方式以保留資料特性
- 確保合成演算法能有效處理所有資料型態

<!-- [連續值離散化](./discretizing-continuous) -->
### 連續值離散化（撰寫中）

- 將連續數值轉換為離散區間
- 降低資料的複雜度
- 提供多種分組策略選擇

<!-- [數值尺度轉換](./scaling-numeric) -->
### 數值尺度轉換（撰寫中）

- 統一不同欄位的數值範圍
- 改善合成模型的收斂性能
- 支援多種標準化與正規化方法

## 附錄：支援處理方式

依照 CAPE 團隊制定的前處理分類法，`PETsARD` 將資料前處理操作區分為兩大類別，並分別提供支援：


- **資訊調整** (Information Modification) 針對資料品質進行增強。包括：
  - **遺失值處理** (Missing handling)：對資料缺失處進行補齊
  - **極端值處理** (Outlier handling)：對資料雜訊進行弭平

- **表示形式轉換** (Representation Transformation) 則指在保留原始資訊的前提下，改變資料的呈現形式。包括：
  - **編碼** (Encoding)：將類別資料轉換為數值表示
  - **離散化** (Discretizing)：連續值轉換為類別資料表示
  - **尺度轉換** (Scaling)：數值範圍的重新映射

下表列出 `PETsARD` 支援的所有前處理方法。您可以透過閱讀各方法的教學範例來了解使用方式，或是前往 [Processor](../../../api/processor/) 查看詳細的技術實現。

| 處理類型 | 處理方式 | 參數 |
| :---: | :---: | :---: |
| 遺失值 | `MissingMean`   | 'missing_mean'   |
| 遺失值 | `MissingMedian` | 'missing_median' |
| 遺失值 | `MissingMode`   | 'missing_mode'   |
| 遺失值 | `MissingSimple` | 'missing_simple' |
| 遺失值 | `MissingDrop`   | 'missing_drop'   |
| 極端值 | `OutlierZScore`          | 'outlier_zscore'          |
| 極端值 | `OutlierIQR`             | 'outlier_iqr'             |
| 極端值 | `OutlierIsolationForest` | 'outlier_isolationforest' |
| 極端值 | `OutlierLOF`             | 'outlier_lof'             |
| 編碼 | `EncoderUniform` | 'encoder_uniform' |
| 編碼 | `EncoderLabel`   | 'encoder_label'   |
| 編碼 | `EncoderOneHot`  | 'encoder_onehot'  |
| 離散化 | `DiscretizingKBins` | 'discretizing_kbins' |
| 尺度 | `ScalerStandard`   | 'scaler_standard'   |
| 尺度 | `ScalerZeroCenter` | 'scaler_zerocenter' |
| 尺度 | `ScalerMinMax`     | 'scaler_minmax'     |
| 尺度 | `ScalerLog`        | 'scaler_log'        |
| 尺度 | `ScalerTimeAnchor` | 'scaler_timeanchor' |