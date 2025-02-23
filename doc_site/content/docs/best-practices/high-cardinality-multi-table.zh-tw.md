---
title: 高基數與多表格資料的合成
type: docs
weight: 41
prev: docs/best-practices
next: docs/best-practices
---


## 緣起

某政策性金融機構擁有豐富的企業融資相關數據，包含企業基本資訊、融資申請、財務變化等多面向歷史紀錄。機構希望透過合成資料技術來推動與金融科技業者的創新合作，讓第三方能在確保資料隱私的前提下，利用這些資料開發風險預測模型，協助機構提升風險管理效能。

## 資料特性與挑戰

- **複雜的表格結構**：原始資料分散在多個業務系統的資料表中，涉及企業基本資料、申請紀錄、財務追蹤等不同面向
- **高基數類別變數**：因產業類別多樣、融資方案眾多，許多欄位都具有大量獨特值
- **時序性資料**：包含多個關鍵時間點（如申請日期、核准日期、追蹤時間等），且這些時間點之間具有邏輯順序關係
- **資料品質議題**：存在遺失值、異常值，以及需要跨表整合的複雜度

## 模擬資料示範

考量資料隱私，以下使用模擬資料展示資料結構與商業邏輯。這些資料雖然是模擬的，但保留了原始資料的關鍵特性與業務限制：

### 企業基本資料

```python
# 企業基本資料表範例 (Example of company basic information)
company_info = pd.DataFrame({
   'company_id': ['C000001', 'C000002', 'C000003'],
   'industry': ['製造業', '服務業', '批發零售'],
   'sub_industry': ['電子零組件', '物流', '電子商務'],
   'city': ['新北市', '臺北市', '桃園市'],
   'district': ['板橋區', '內湖區', '中壢區'],
   'established_date': ['2015-03-15', '2018-06-20', '2016-09-10'],
   'capital': [15000000, 8000000, 12000000]  # 單位：元 (Unit: NTD)
})
```

### 融資申請紀錄

```python
# 融資申請表範例 (Example of financing applications)
applications = pd.DataFrame({
    'application_id': ['A00000001', 'A00000002', 'A00000003', 'A00000004'],
    'company_id': ['C000001', 'C000001', 'C000002', 'C000003'],
    'loan_type': ['營運週轉金', '購置機器設備', '營運週轉金', '數位轉型'],
    'apply_date': ['2023-03-15', '2023-09-20', '2023-05-10', '2023-07-01'],
    'approval_date': ['2023-04-10', '2023-10-15', None, '2023-07-25'],
    'status': ['approved', 'approved', 'rejected', 'approved'],
    'amount_requested': [5000000, 8000000, 3000000, 4000000],  # 單位：元 (Unit: NTD)
    'amount_approved': [4000000, 7000000, None, 3500000]       # 單位：元 (Unit: NTD)
})
```

### 財務追蹤紀錄

```python
# 財務追蹤表範例 (Example of financial tracking)
tracking = pd.DataFrame({
    'track_id': ['T00000001', 'T00000002', 'T00000003', 'T00000004'],
    'application_id': ['A00000001', 'A00000001', 'A00000004', 'A00000004'],
    'company_id': ['C000001', 'C000001', 'C000003', 'C000003'],
    'tracking_date': ['2023-07-10', '2023-10-10', '2023-10-25', '2024-01-25'],
    'revenue': [12000000, 13500000, 8000000, 7500000],   # 單位：元 (Unit: NTD)
    'profit': [600000, 810000, 240000, -150000],         # 單位：元 (Unit: NTD)
    'profit_ratio': [0.05, 0.06, 0.03, -0.02],           # 單位：% (Unit: %)
    'risk_level': ['normal', 'normal', 'attention', 'high_risk']
})
```

### 商業邏輯限制

1. 時序性限制：
  - 申請日期必須在公司成立日之後
  - 核准日期必須在申請日後 1-60 天內
  - 財務追蹤日期必須在核准日之後，且以每季（90天）為間隔

2. 金額限制：
  - 公司資本額必須大於 100 萬元
  - 核准金額通常為申請金額的 60-100%
  - 單筆申請金額不得超過資本額的 200%

3. 風險評估規則：
  - 風險等級是依照獲利率（Profit Ratio）區間評定：
    - 獲利率 > 5%: 正常 (normal)
    - 獲利率 0-5%: 注意或警告 (attention/warning)
    - 獲利率 < 0%: 高風險 (high_risk)
  - 註：此處獲利率以營收除以收入（profit/revenue）表示，此為簡化後的模擬邏輯，實際金融機構的財務風險審查模型可能採用更複雜的評估機制


## `PETsARD` 解決方案

1. **資料整合與品質提升**
   - 運用資料庫反正規化技術將多個資料表整合為單一寬表
   - 透過 `PETsARD` 的資料品質檢測功能，確保整合過程中的資料一致性
   - 針對遺失值與異常值提供系統性的處理方法

2. **高基數類別處理**
   - 對高基數欄位進行分布分析，識別關鍵類別
   - 設計並實作約束條件，確保合成資料符合業務邏輯
   - 避免產生實務上不可能出現的類別組合

3. **時序性資料處理**
   - 採用時間錨點（`TimeAnchor`）技術處理多重時間點
   - 保持時間點之間的邏輯順序關係
   - 合理處理時間序列中的遺失值

### 資料庫反正規化處理

目前的確已有支援多表格的合成資料技術，但開源版本的演算法多半僅支援較少的資料欄位數目以及較少的資料筆數，且對於資料表之間的對應關係並未有明確的指引。經 CAPE 團隊評估，建議依照下游任務目的（此處為每次貸款申請的風險惡化與否），訂定合適的顆粒度（本處挑選一筆申請一筆資料）預先整合成資料倉儲，並由資料擁有者自行規劃合適的集成欄位。

以本示範為例，我們將企業基本資料、融資申請紀錄與財務追蹤等三個資料表，整合為以「申請案」為單位的寬表。其中，企業基本資料（如產業類別、資本額）直接帶入，財務追蹤則計算摘要統計（如三年平均風險等級、最近一次風險等級等），既保留了必要的時序資訊，又避免產生過於複雜的表格結構。

在進行此類資料整合時，需特別注意：
1. 確認資料的主鍵關係，避免重複或遺漏
2. 妥善處理時間序列資訊，例如使用摘要統計保留重要特徵
3. 資料表合併順序會影響最終結果，建議先處理關聯性較強的表格
4. 考量下游任務需求，僅保留必要的欄位以降低合成難度

### 高基數類別的約束處理

由於合成資料是基於機率模型，雖然能學習到資料內隱含的關係結構，但在大量抽樣過程中仍可能產生違反商業邏輯的極端狀況。約束條件的設計正是為了確保合成資料符合業務規範。以產業類別為例，我們的示範雖然僅列舉四個主要產業項下各五個子產業，但實際上根據行政院主計總處的行業統計分類，台灣產業可細分為 19 個大類、88 個中類、249 個小類、527 個細類。更重要的是，不同產業會因應景氣循環表現出不同的融資需求與違約風險，因此維持產業分類的商業邏輯至關重要。

```yaml
Constrainer:
  demo:
    field_combinations:
      -
        - {'industry': 'sub_industry'}   # 產業類別對應關係 (Industry category relationships)
        - {
            '製造業': ['電子零組件', '金屬加工', '紡織', '食品', '塑膠製品'],
            '服務業': ['餐飲', '物流', '教育', '休閒娛樂', '專業諮詢'],
            '批發零售': ['電子商務', '進出口貿易', '零售', '汽機車零件', '民生用品'],
            '營建工程': ['土木工程', '建築工程', '室內裝修', '機電工程', '環保工程']
            }
```

道理也可以推導到非高基數的欄位，對於任何具有明確商業邏輯的欄位，都建議加上約束條件。透過反覆的約束、篩選、重抽樣過程，我們能在保持資料保真性的同時確保合成資料的合理性。以下是更多的約束範例：

```yaml
Constrainer:
 demo:
   nan_groups:
     approval_date:
       erase: ['risk_level_last_risk', 'risk_level_second_last_risk']
     # 若核准日期遺失，清除風險評級相關欄位
     # (If approval date is missing, clear risk rating related fields)

   field_constraints:
     - "established_date <= apply_date"
     # 創立日期不晚於申請日期
     # (Establishment date must not be later than application date)

     - "apply_date <= approval_date"
     # 申請日期不晚於核准日期
     # (Application date must not be later than approval date)

     - "amount_approved <= amount_requested"
     # 核准金額不超過申請金額
     # (Approved amount cannot exceed requested amount)
```

這些約束條件能確保合成資料符合基本的業務邏輯，如時間順序性（公司先成立才能申請）、金額合理性（核准不超過申請）等。

CAPE 團隊建議資料擁有者在合成之前，應充分運用領域專業知識（domain knowledge）進行資料整理。例如，對於已廢止或使用頻率極低的產業類別，建議在資料庫整理階段就進行合併或重新分類。資料品質越精簡乾淨，最終的合成效果就會越好。

### 時間差異的模擬合成

當資料集中包含多個時間欄位時，彼此之間往往存在著潛在的商業邏輯關係。例如在企業融資情境中，不同產業從創立到首次申請融資的時間差（duration）可能有明顯差異：製造業可能需要較長的準備期，而服務業可能較快就需要營運資金。同樣地，從申請到核准的處理時間，也可能因產業特性、景氣循環等因素而有所不同。

雖然時間順序性（如成立日早於申請日）可以透過約束條件來維護，但這些微妙的時間差異模式適合同時使用 `TimeAnchor` 來處理：


```yaml
Preprocessor:
  demo:
    method: 'default'
    config:
      scaler:
        'established_date':
          # 以公司成立日為錨點，計算與申請、核准、追蹤等重要時間點的天數差異
          # (Using company establishment date as anchor to calculate day differences
          #  with application, approval and tracking dates)
          method: 'scaler_timeanchor'
          reference:
            - 'apply_date'
            - 'approval_date'
            - 'tracking_date_last_tracking_date'
          unit: 'D'
```

透過將公司成立日設為時間錨點，並參考後續的申請、核准和追蹤時間，我們能讓合成資料更好地模擬這些時間差異的分布特性，進而產生更符合實際業務邏輯的時序模式。

### 結論與建議

透過此案例，我們展示了處理高基數與多表格資料時的核心概念：

1. **資料整合策略**：
   - 依照下游任務目的選擇適當的資料顆粒度
   - 透過資料反正規化簡化表格結構
   - 運用摘要統計保留時序特徵

2. **保持資料合理性**：
   - 針對高基數類別設計約束條件
   - 維護欄位間的商業邏輯關係
   - 模擬時間差異的分布特性

3. **資料品質建議**：
   - 建議資料擁有者在前處理階段善用領域知識
   - 合併或重新分類低使用頻率的類別
   - 清晰定義資料欄位的業務含義

這些方法不僅適用於金融資料，對於其他具有複雜類別結構與時序性質的資料集，如醫療紀錄、產業研究等，都具有參考價值。

## 完整示範

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/best-practices-high-cardinality-multi-table.ipynb)

```yaml
---
Loader:
  data:
    filepath: 'best-practices-high-cardinality-multi-table.csv'
Preprocessor:
  demo:
    method: 'default'
    config:
      scaler:
        'established_date':
          # 以公司成立日為錨點，計算與申請、核准、追蹤等重要時間點的天數差異
          # (Using company establishment date as anchor to calculate day differences
          #  with application, approval and tracking dates)
          method: 'scaler_timeanchor'
          reference:
            - 'apply_date'
            - 'approval_date'
            - 'tracking_date_last_tracking_date'
          unit: 'D'
Synthesizer:
  demo:
    method: 'default'
Postprocessor:
  demo:
    method: 'default'
Constrainer:
  demo:
    nan_groups:
      company_id: delete
      # 若公司編號遺失，刪除整筆資料
      # (If company ID is missing, delete entire record)

      industry:
        erase: 'sub_industry'
      # 若主要產業別遺失，擦除子產業別
      # (If main industry is missing, erase sub-industry)

      approval_date:
        erase: ['risk_level_last_risk', 'risk_level_second_last_risk']
      # 若核准日期遺失，清除風險評級相關欄位
      # (If approval date is missing, clear risk rating related fields)

    field_constraints:
      - "established_date <= apply_date"
      # 創立日期不晚於申請日期
      - "apply_date <= approval_date"
      # 申請日期不晚於核准日期

      - "capital >= 1000000"
      # 資本額至少 100 萬
      # (Capital must be at least 1 million)

      - "amount_requested <= capital + capital"
      # 申請金額不超過資本額 2 倍
      # (Requested amount cannot exceed 2 times of capital)

      - "amount_approved <= amount_requested"
      # 核准金額不超過申請金額
      # (Approved amount cannot exceed requested amount)

      - "profit_ratio_min_profit_ratio <= profit_ratio_avg_profit_ratio"
      # 獲利率限制在合理範圍
      # (Profit ratio must be within reasonable range)

    field_combinations:
      -
        - {'industry': 'sub_industry'}
        # 產業類別對應關係
        # (Industry category relationships)
        - {
            '製造業': ['電子零組件', '金屬加工', '紡織', '食品', '塑膠製品'],
            '服務業': ['餐飲', '物流', '教育', '休閒娛樂', '專業諮詢'],
            '批發零售': ['電子商務', '進出口貿易', '零售', '汽機車零件', '民生用品'],
            '營建工程': ['土木工程', '建築工程', '室內裝修', '機電工程', '環保工程']
          }
Reporter:
  output:
    method: 'save_data'
    source: 'Constrainer'
...
```