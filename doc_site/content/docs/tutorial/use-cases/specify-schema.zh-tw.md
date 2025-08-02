---
title: 指定資料表架構
type: docs
weight: 16
prev: docs/tutorial/use-cases
next: docs/tutorial/use-cases/data-description
---

在處理真實世界的資料時，我們經常遇到資料品質問題：自訂的缺失值標記（如 '?' 或 'unknown'）、需要保留前導零的識別碼、數值精度不一致等。傳統的資料載入方式依賴 pandas 的自動型別推斷，但面對複雜資料時經常出現誤判。

`Loader` 的 `schema` 參數讓您能夠在資料載入階段就精確指定每個欄位的資料型別、缺失值定義和數值精度，確保資料品質從源頭開始就得到保障。

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/tutorial/use-cases/specify-schema.ipynb)

```yaml
---
Loader:
  data:
    filepath: 'benchmark/adult-income.csv'
  data-w-schema:
    filepath: 'benchmark/adult-income.csv'
    schema:
      # 全域參數
      optimize_dtypes: true
      nullable_int: 'force'

      # 欄位參數
      fields:
        # 數值型欄位
        age:
          type: 'int'
        fnlwgt:
          type: 'int'
        # 字串型欄位
        gender:
          type: 'str'
          category_method: 'force'
        # 含自訂缺失值的欄位
        native-country:
          type: 'str'
          na_values: '?'
        workclass:
          type: 'str'
          na_values: '?'
        occupation:
          type: 'str'
          na_values: '?'
Describer:
  summary:
    method: 'default'
Reporter:
  save_report_columnwise:
    method: 'save_report'
    granularity: 'columnwise'
...
```

## 配置說明

### 兩層架構設計

上述 YAML 配置採用了兩層架構設計，將欄位定義與全域參數分離：

**欄位定義 (`fields`)**：
- 每個欄位都明確指定邏輯型別（`logical_type`）
- 例如：`logical_type: 'string'` 表示這是字串型別，`logical_type: 'category'` 表示分類資料
- `fields` 中的欄位順序可以任意排列，不需要對應資料表中的欄位順序
- 只需要指定您關心的欄位，未指定的欄位會自動進行型別推斷

**全域參數**：
- 可在 `schema` 層級設定全域控制參數，如 `compute_stats`、`optimize_dtypes` 等
- 全域參數會影響整個資料載入和處理過程
- 個別欄位參數可以覆蓋全域設定

**自訂缺失值處理**：
- 透過全域或欄位層級的參數可以控制缺失值處理
- 這對於處理真實世界資料中的非標準缺失值標記非常有用
- 可以針對每個欄位單獨設定，提供更精確的缺失值處理

## 全域參數

### 處理控制參數

#### `optimize_dtypes` (bool, 預設: `true`)
全表記憶體優化，自動將資料型別優化以節省記憶體。

- `true`: 自動將 int64 → int32、float64 → float32 等
- `false`: 保持原始型別

#### `sample_size` (int, 預設: `null`)
型別推斷的樣本大小。

- `null`: 使用全部資料
- 正整數: 使用指定樣本數（會驗證不超過實際資料筆數）

### 推斷控制參數

#### `infer_logical_types` (bool, 預設: `false`)
全表邏輯型別推斷，會覆蓋個別欄位的 `logical_type` 設定。

⚠️ **注意**：與個別欄位的 `logical_type` 設定同時存在時會報錯。

#### `leading_zeros` (str, 預設: `"never"`)
前導字元處理方式：

- `"never"`: 不處理前導字元
- `"num-auto"`: 數值型別有前導字元時轉為字串保留
- `"leading_n"`: 補齊到指定位數（如 `"leading_5"` 補到5位）

⚠️ **重要**：此設定會將所有非數值欄位視作 `str`，因此 `datetime` 相關欄位會被當作字串處理。

#### `nullable_int` (str, 預設: `"force"`)
整數 NULL 處理方式：

- `"force"`: int 型別自動轉為支援 NULL 的 Int64
- `"never"`: 遇到 NULL 自動轉為 float

### 描述性參數

- **`schema_id`** (str): Schema 唯一識別碼
- **`name`** (str): Schema 人類可讀名稱
- **`description`** (str): Schema 描述

## 欄位層級參數

### `logical_type` (str, 預設: `"never"`)
個別欄位邏輯型別推斷：

- `"never"`: 不推斷邏輯型別
- `"infer"`: 自動推斷邏輯型別
- 指定型別: 如 `"email"`, `"phone"`, `"url"` 等

```yaml
schema:
  fields:
    email:
      type: 'str'
      logical_type: 'email'
    phone:
      type: 'str'
      logical_type: 'phone'
```

### `leading_zeros` (欄位層級)
個別欄位可覆蓋全域的 `leading_zeros` 設定：

```yaml
schema:
  leading_zeros: "never"  # 全域設定
  fields:
    user_id:
      type: 'int'
      leading_zeros: "leading_8"  # 覆蓋全域設定，補齊到8位
```

## Schema 五大核心功能

### 1. 型別控制 (`type`)
精確指定每個欄位的基本資料型別，避免 pandas 自動推斷錯誤：

- `'int'`：整數型別
- `'float'`：浮點數型別
- `'str'`：字串型別
- `'bool'`：布林型別
- `'datetime'`：日期時間型別

**語義型別 (`logical_type`)**：
用於指定欄位的語義含義，如：
- `'email'`：電子郵件地址
- `'phone'`：電話號碼
- `'url'`：網址
- `'infer'`：自動推斷語義型別

### 2. 記憶體優化 (`category_method`)
智慧判斷是否將欄位轉換為分類型別以節省記憶體：

- `str-auto`（預設）：僅對字串型別欄位使用 ASPL 判斷
- `auto`：對所有型別欄位使用 ASPL 判斷
- `force`：強制轉換為分類型別
- `never`：永不轉換為分類型別

**ASPL 判斷機制**：當 `ASPL = 樣本數 / 唯一值數量 ≥ 100` 時，轉換為分類型別。

### 3. 數值精度操控 (`precision`)
控制浮點數的小數位數，確保數值格式一致：

- 僅適用於 `float` 型別：`precision: 2`
- **注意**：`int` 型別使用 `precision` 會報錯

### 4. 類別變項優化
基於 Zhu et al. (2024) 研究的智慧分類判斷：

- **理論依據**：確保每個類別有足夠樣本數支持有效編碼
- **避免問題**：防止稀疏類別造成的效能問題
- **記憶體效益**：可節省 50-90% 記憶體使用量

### 5. 日期型態讀取
支援靈活的日期時間處理：

#### 日期精度控制 (`datetime_precision`)
- `s`（預設）：秒級精度
- `ms`：毫秒級精度
- `us`：微秒級精度
- `ns`：奈秒級精度

#### 日期格式解析 (`datetime_format`)
- `auto`（預設）：自動偵測格式
- 自訂格式：使用 Python strftime 格式字串

**Python 原生支援的常見日期格式**：
- `%Y-%m-%d`：2024-01-15
- `%Y/%m/%d`：2024/01/15
- `%d/%m/%Y`：15/01/2024
- `%Y-%m-%d %H:%M:%S`：2024-01-15 14:30:00
- `%Y-%m-%dT%H:%M:%S`：2024-01-15T14:30:00（ISO 8601）

### 缺失值定義 (`na_values`)
支援多種資料型別的自訂缺失值標記：

- 單一值：`na_values: '?'`
- 多重值：
  ```yaml
  na_values:
    - '?'
    - 'unknown'
    - 'N/A'
  ```
- 針對每個欄位單獨定義，提供精確的缺失值處理

## 類別型態的儲存優勢與使用時機

### 儲存優勢

**記憶體效率**：
- 類別型態 (Category) 將重複的字串值只儲存一次，使用整數索引來參照
- 對於重複值多的欄位，可節省 50-90% 的記憶體使用量
- 例如：1,000 萬筆資料中只有 10 個不同的地區名稱

**運算效率**：
- 分組操作（groupby）和比較運算更快
- 排序操作可利用類別順序進行優化
- 字串比較轉換為整數比較

### 何時使用類別型態

**建議使用的情況**：
- 重複值多的字串欄位（如性別、地區、狀態）
- 有序分類資料（如評級：低、中、高）
- 整數編碼的分類資料（如狀態碼：1, 2, 3）
- 唯一值數量遠小於總資料量的欄位

**不建議使用的情況**：
- 唯一值很多的欄位（如用戶ID、交易ID）
- 需要頻繁進行字串操作的欄位
- 數值計算頻繁的欄位
- 臨時或一次性分析的資料

### 設計理念

我們的設計將分類處理視為一種儲存優化策略，而非基礎資料型別：
- `type: 'string', category_method: force` 明確表達「強制將字串型別轉為分類資料」
- `type: 'int', category_method: force` 表達「強制將整數型別轉為分類資料」
- `category_method: str-auto` 預設只對字串型別進行智慧判斷，避免不必要的轉換
- 概念上類似於 Pandas 的 `category[dtype]` 但提供更精細的控制

## 實際效果

使用新的 `schema` 參數後，您將獲得：

1. **精確的型別控制**：避免 pandas 自動推斷錯誤
2. **統一的缺失值處理**：將 `'?'` 等自訂標記正確識別為缺失值
3. **一致的數值格式**：透過 `precision` 參數統一數值精度
4. **智慧的記憶體優化**：透過 `category_method` 選擇性優化儲存
5. **可重現的資料處理**：明確的架構定義確保每次載入結果一致
6. **清晰的概念分離**：資料型別與儲存優化分離，概念更清晰

透過精確指定資料表架構，您可以確保資料從載入階段就符合預期格式，為後續的前處理、合成和評估奠定堅實基礎。新的兩層架構設計讓概念更清晰，使用更靈活。

## 參考文獻

Zhu, W., Qiu, R., & Fu, Y. (2024). Comparative study on the performance of categorical variable encoders in classification and regression tasks. *arXiv preprint arXiv:2401.09682*. https://arxiv.org/abs/2401.09682