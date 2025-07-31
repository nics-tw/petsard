---
title: 多表格資料 - 反正規化
type: docs
weight: 41
prev: docs/best-practices
next: docs/best-practices/multi-timestamp
---

## 個案背景

某政策性金融機構擁有豐富的企業融資相關數據，包含企業基本資訊、融資申請、財務變化等多面向歷史紀錄。機構希望透過合成資料技術來推動與金融科技業者的創新合作，讓第三方能在確保資料隱私的前提下，利用這些資料開發風險預測模型，協助機構提升風險管理效能。

### 資料特性與挑戰

- **複雜的表格結構**：原始資料分散在多個業務系統的資料表中，涉及企業基本資料、申請紀錄、財務追蹤等不同面向
- **時序性資料**：包含多個關鍵時間點（如申請日期、核准日期、追蹤時間等），且這些時間點之間具有邏輯順序關係
  - 處理方法見 [多時間點資料 - 時間定錨](docs/best-practices/multi-timestamp)

## 資料表關聯與業務意義

本案例的資料結構反映了企業融資的完整業務流程，主要包含三個核心資料表：

- 企業基本資料表：

  - 包含企業識別碼、產業類別、子產業、地理位置和資本額等靜態資訊
  - 每筆記錄代表一個獨立的企業實體
  - 此表作為主表，與其他資料表形成一對多的關係

- 融資申請紀錄表：

  - 記錄企業向金融機構提出的每一次融資申請詳情
  - 包含申請類型、申請日期、核准日期、申請狀態及金額等資訊
  - 一個企業可能有多次融資申請，時間跨度可達數年
  - 申請日期與核准日期之間的時間差反映了審核處理時間
  - 申請結果分為核准、拒絕和撤回三種狀態

- 財務追蹤紀錄表：

  - 記錄企業獲得融資後的財務表現追蹤資料
  - 包含利潤率指標、追蹤時間範圍、營收指標及風險等級評估
  - 每個融資申請可能產生多筆追蹤紀錄，代表不同時間點的財務狀況
  - 風險等級評估反映了企業還款能力的變化趨勢

這三個資料表之間形成層次性的關聯結構：企業基本資料(1) → 融資申請紀錄(N) → 財務追蹤紀錄(N)。在實際業務流程中，企業首先建立基本檔案，隨後提交融資申請，而每筆申請案件均會觸發財務追蹤機制。特別值得注意的是，不僅在申請初期會進行評估，申請通過後的期中階段也會執行定期或不定期的財務狀況追蹤，從而構成一個完整且持續更新的資料鏈。這種多層次、多時間點的一對多關聯架構，大幅提高了資料合成的難度，尤其在必須同時保留資料間關聯性與時間序列特性的情況下，挑戰更為顯著。

### 模擬資料示範

考量資料隱私，以下使用模擬資料展示資料結構與商業邏輯。這些資料雖然是模擬的，但保留了原始資料的關鍵特性與業務限制：

#### 企業基本資料

| company_id | industry | sub_industry | city | district | established_date | capital |
|------------|----------|--------------|------|----------|------------------|---------|
| C000001 | 營建工程 | 環保工程 | 新北市 | 板橋區 | 2019-11-03 | 19899000 |
| C000002 | 營建工程 | 建築工程 | 臺北市 | 內湖區 | 2017-01-02 | 17359000 |
| C000003 | 製造業 | 金屬加工 | 臺北市 | 內湖區 | 2012-05-29 | 5452000 |
| C000004 | 營建工程 | 環保工程 | 桃園市 | 中壢區 | 2010-09-24 | 20497000 |
| C000005 | 批發零售 | 零售 | 臺北市 | 內湖區 | 2010-07-24 | 17379000 |

#### 融資申請紀錄

| application_id | company_id | loan_type | apply_date | approval_date | status | amount_requested | amount_approved |
|----------------|------------|-----------|------------|---------------|--------|------------------|-----------------|
| A00000001 | C000001 | 廠房擴充 | 2022-01-21 | 2022-03-19 | approved | 12848000 | 12432000.0 |
| A00000002 | C000001 | 營運週轉金 | 2025-01-05 | 2025-02-11 | approved | 2076000 | 1516000.0 |
| A00000003 | C000001 | 創新研發 | 2025-01-05 | 2025-01-30 | approved | 11683000 | 10703000.0 |
| A00000004 | C000002 | 營運週轉金 | 2020-12-12 | NaN | rejected | 5533000 | NaN |
| A00000005 | C000002 | 廠房擴充 | 2026-02-14 | NaN | rejected | 1433000 | NaN |

#### 財務追蹤紀錄

| application_id | profit_ratio_avg_profit_ratio | profit_ratio_min_profit_ratio | profit_ratio_profit_ratio_std | profit_ratio_negative_profit_count | tracking_date_tracking_months | tracking_date_last_tracking_date | revenue_avg_revenue | revenue_revenue_growth | risk_level_last_risk | risk_level_second_last_risk |
|----------------|-----------------------------|-------------------------------|------------------------------|-----------------------------------|-------------------------------|--------------------------------|---------------------|------------------------|----------------------|----------------------------|
| A00000001 | 0.033225 | -0.096496 | 0.084001 | 4 | 3.0 | 2024-09-04 | 1.840486e+07 | -0.026405 | high_risk | normal |
| A00000002 | -0.002636 | -0.080580 | 0.074297 | 6 | 3.0 | 2027-07-31 | 1.926350e+07 | 1.284445 | normal | warning |
| A00000003 | 0.009984 | -0.087006 | 0.084297 | 6 | 3.0 | 2027-07-19 | 2.470124e+07 | 1.561825 | attention | severe |
| A00000007 | 0.002074 | -0.091077 | 0.093598 | 4 | 21.0 | 2024-09-26 | 2.388020e+07 | 0.090593 | attention | normal |
| A00000008 | 0.038045 | -0.033057 | 0.053279 | 3 | 3.0 | 2018-12-16 | 2.390215e+07 | -0.516376 | high_risk | normal |

## 多表格資料合成方案比較

在進行資料合成方案設計前，針對現有的多表格合成技術進行了深入研究評估。以 SDV 生態系為準（截至 2025 年 2 月）[^1]，目前公開可用的多表格合成器主要有以下幾種：

1. 獨立合成 (Independent)：獨立針對各表格建立 Copulas，無法學習表間模式
2. HMA (Hierarchical Modeling Algorithm)：分層式機器學習方法，使用遞歸技術對多表資料集的父子關係進行建模
3. HSA：使用分段演算法，對大型多表格提供高效合成，支援多種單表合成方法
4. Day Z：從無到有的 Level 5 校準模擬 (Calibrated simulation) [^2]，僅使用詮釋資料即可合成

以下是這些方法的功能比較（僅部分）：

| **特徵**             | Day Z | Independent | HMA | HSA |
|---------------------|--|--|--|--|
| 僅使用詮釋資料進行合成  | ✔️ | | | |
| 應用約束條件          | | ✔️ | ✔️ | ✔️ |
| 維持參照完整性        | ✔️ | ✔️ | ✔️ | ✔️ |
| 學習表內模式          | | ✔️ | ✔️ | ✔️ |
| 學習表間模式          | | | ✔️ | ✔️ |
| 可擴展性              | ✔️ | ✔️ | | ✔️ |
| 可用性               | 限企業 | 限企業 | 開放 | 限企業 |

經評估，我們發現 HMA 雖為開源可用的最佳且唯一選項，但仍有明顯限制：

1. **規模與複雜度限制**：HMA 最適合不超過五個表格且僅有一層父子關係的結構
2. **數值欄位限制**：HMA 僅能用於數值欄位的合成，類別欄位都必須經過前處理轉換
3. **統計模型限制**：HMA 僅適用於預定義參數數量的母數統計分配，對於多峰分配的無母數估計僅在付費版可用
4. **約束處理限制**：某些重要約束條件僅在付費版可用
5. **欄位數量限制**：在官方的簡化模型功能 `simplify_schema()` 中，會將總欄位限制在 1,000 個以下
6. **筆數限制**：官方表明 HMA 不適用於大量資料，唯未明確宣告限制筆數

其他亦有全體 SDV 多表合成器的限制：

6. **單一外鍵限制**：詮釋資料僅能宣告父表單一欄位對應著子表的單一欄位，而無法支援多欄位組合甚至結合條件
7. **一對多關係限制**：父表對應子表的關係必須是一對多，不支援多對多、甚至是一對一。

上述的限制均列在 SDV 的使用說明。但本團隊進一步，以 SDV 官方的 `fake_hotels` 小型測試資料集進行測試，父表飯店表 5 個欄位 10 筆資料、子表客人表 10 個欄位 658 筆，實際測試發現，HMA 的確能在約 2 秒內完成處理，但模型品質存在顯著問題：

- 跨表相關性低下（如服務費相關性僅 0.14）
- 類別變數間的關聯度不足（如城市與評級的相似度僅 0.20）
- 部分資料項目無法正確建立關聯（如服務費與入住日期）

經觀察，主因是原始資料有大量雙峰分配，有一大部分人未給小費 (amenities_fee = 0)。而這個母數統計的限制，加上類別欄位編碼後失去的約束條件限制，都使得我們理解到 HMA 不適用做為產品或服務使用。

## 資料庫反正規化處理的必要性

基於上述研究，我們認為目前開源的多表格合成技術尚未成熟到能直接處理複雜的企業融資資料。開源版本的演算法多半僅支援較少的資料欄位數目以及較少的資料筆數，且對於資料表之間的對應關係並未有明確的指引。對於複雜的多表格資料，我們需要將傳統的資料庫技術、有系統有架構的應用在合成資料流程中。

經 CAPE 團隊評估，我們建議：

1. **預先整合成資料倉儲**：依照下游任務目的，訂定合適的顆粒度。例如我們關心的是每家公司最新一次財務狀況的增減，比較適合的顆粒度便會是一筆資料一家公司
2. **以專業知識規劃合適的集成方式**：當不同顆粒度表格需要整合時，便需要資料擁有者從領域知識出發，規劃最適合的整合方法

以本示範為例，我們將企業基本資料、融資申請紀錄與財務追蹤等三個資料表，整合為以「申請案」為單位的寬表。其中，企業基本資料（如產業類別、資本額）直接帶入，融資申請則取第一次跟最新一次申請紀錄，財務追蹤則取最新一次追蹤，既保留了必要的時序資訊，又避免產生過於複雜的表格結構。

這邊以 `pandas.merge` 做示範，但整合的方法不限於 Python，考慮到資料量，建議在資料庫系統內使用 SQL 等方式預先處理。並且對於多表資料，我們只建議在 PETsARD 外是先整備承擔一表格，PETsARD 無計劃支援反正規化功能．

```python
# 標記每個公司的第一次和最新一次申請
applications['sort_tuple'] = list(zip(applications['apply_date'], applications['application_id']))

# 找出每個公司的最早申請
min_tuples = applications.groupby('company_id')['sort_tuple'].transform('min')
applications['is_first_application'] = (applications['sort_tuple'] == min_tuples)

# 找出每個公司的最晚申請
max_tuples = applications.groupby('company_id')['sort_tuple'].transform('max')
applications['is_latest_application'] = (applications['sort_tuple'] == max_tuples)

applications.drop(columns=['sort_tuple'], inplace=True, errors='ignore')


# 將財務追蹤資料串接上申請資料，以獲得公司編號
tracking_w_company = tracking\
    .merge(
        applications[['company_id', 'application_id']],
        how='left',
        left_on='application_id',
        right_on='application_id'
    )

# 標記每個公司的最新一次財務追蹤
tracking_w_company['sort_tuple'] = list(zip(tracking_w_company['tracking_date_last_tracking_date'], tracking_w_company['application_id']))

max_tuples = tracking_w_company.groupby('company_id')['sort_tuple'].transform('max')
tracking_w_company['is_latest_tracking'] = (tracking_w_company['sort_tuple'] == max_tuples)

tracking_w_company.drop(columns=['sort_tuple'], inplace=True, errors='ignore')


# 合併企業資料與申請資料 (Merge company and application data)
denorm_data: pd.DataFrame = companies\
    .merge(
        applications[applications['is_first_application']].add_prefix('first_apply_'),
        how='left',
        left_on='company_id',
        right_on='first_apply_company_id'
    ).drop(columns=['first_apply_company_id', 'first_apply_is_first_application', 'first_apply_is_latest_application'])\
    .merge(
        applications[applications['is_latest_application']].add_prefix('latest_apply_'),
        how='left',
        left_on='company_id',
        right_on='latest_apply_company_id'
    ).drop(columns=['latest_apply_company_id', 'latest_apply_is_first_application', 'latest_apply_is_latest_application'])

# 加入彙整後的追蹤資料 (Add summarized tracking data)
denorm_data = denorm_data\
   .merge(
       tracking_w_company[tracking_w_company['is_latest_tracking']].drop(columns=['sort_tuple'], errors='ignore').add_prefix('latest_track_'),
       how='left',
       left_on='company_id',
       right_on='latest_track_company_id'
   ).drop(columns=['latest_track_company_id', 'latest_track_is_latest_tracking'])
```

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/best-practices/multi-table.ipynb)


PETsARD 簡單地用最預設的設定執行

```yaml
---
Loader:
  data:
    filepath: 'best-practices_multi-table.csv'
Preprocessor:
  demo:
    method: 'default'
Synthesizer:
  demo:
    method: 'default'
Postprocessor:
  demo:
    method: 'default'
Reporter:
  output:
    method: 'save_data'
    source: 'Postprocessor'
...
```

在進行此類資料整合時，需特別注意：

1. **確認資料的主鍵關係**：避免重複或遺漏
2. **妥善處理時間序列資訊**：例如使用摘要統計保留重要特徵
3. **資料表合併順序**：會影響最終結果，建議先處理關聯性較強的表格
4. **下游任務需求**：為了降低合成複雜度，可以僅保留必要的欄位

透過預先的反正規化處理，我們能夠：

- 明確保留業務邏輯關係
- 降低合成過程中的資料失真
- 提升最終合成資料的實用性與品質

## 小結

在這部分文章，我們探討了多表格資料合成的研究現況與其局限性，並說明了為何進行傳統的資料庫反正規化處理對於複雜金融資料至關重要。預先的資料整合不僅能克服現有合成技術的限制，還能更有效地保留業務邏輯與時序特性。

下集將深入探討如何處理整合後產生的多時間點資料。

## 參考資料

[^1]: https://docs.sdv.dev/sdv/multi-table-data/modeling/synthesizers
[^2]: Balch, T., Potluru, V. K., Paramanand, D., & Veloso, M. (2024). Six Levels of Privacy: A Framework for Financial Synthetic Data. arXiv preprint. arXiv:2403.14724 [cs.CR]. https://doi.org/10.48550/arXiv.2403.14724
