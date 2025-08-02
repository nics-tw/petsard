---
title: Loader
type: docs
weight: 52
prev: docs/api/executor
next: docs/api/metadater
---


```python
Loader(
    filepath=None,
    method=None,
    column_types=None,
    header_names=None,
    na_values=None,
    schema=None
)
```

用於載入表格式資料的模組。

## 參數

- `filepath` (`str`, optional)：資料集檔案路徑，不可與 `method` 同時使用
  - 預設值：無
  - 若使用基準資料集，格式為 `benchmark://{dataset_name}`
- `method` (`str`, optional)：載入方法，不可與 `filepath` 同時使用
  - 預設值：無
  - 可用值：'default' - 載入 PETsARD 預設資料集 'adult-income'
- `column_types` (`dict`, optional)：**⚠️ v2.0.0 版本將下架移除** 欄位型態定義
  - 預設值：無
  - 格式：`{type: [colname]}`
  - 支援型態（不分大小寫）：
    - 'category'：類別型欄位
    - 'datetime'：日期時間型欄位
- `header_names` (`list`, optional)：無標題資料的欄位名稱列
  - 預設值：無
- `na_values` (`str` | `list` | `dict`, optional)：**⚠️ v2.0.0 版本將下架移除** 指定要視為 NA/NaN 的值
  - 預設值：無
  - 若為字串或列表：套用於所有欄位
  - 若為字典：以 `{colname: na_values}` 格式指定各欄位
  - 範例：`{'workclass': '?', 'age': [-1]}`
- `schema` (`SchemaConfig`, optional)：架構設定物件
  - 預設值：無
  - 用於定義欄位型別、處理規則和驗證邏輯
  - 詳細用法請參考 [Metadater API 文檔](../metadater)
  - **衝突檢測**：若 `schema` 和 `column_types` 同時定義相同欄位，將拋出 `ConfigError`

## 範例

```python
from petsard import Loader


# 基本用法
load = Loader('data.csv')
data, meta = load.load()

# 使用基準資料集
load = Loader('benchmark://adult-income')
data, meta = load.load()

# 使用 schema 參數進行進階欄位處理
from petsard.metadater import SchemaConfig, FieldConfig

# 建立 schema 配置（詳細用法請參考 Metadater 文檔）
schema_config = SchemaConfig(
    schema_id='my_schema',
    fields={
        'age': FieldConfig(type='int'),
        'salary': FieldConfig(type='float', precision=2)
    }
)

load = Loader('data.csv', schema=schema_config)
data, meta = load.load()
```

## 方法

### `load()`

讀取與載入資料。

**參數**

無

**回傳值**

- `data` (`pd.DataFrame`)：載入的 DataFrame
- `schema` (`SchemaMetadata`)：包含欄位資訊和統計資料的資料集架構詮釋資料

```python
loader = Loader('data.csv')
data, meta = loader.load()  # 得到載入的資料
```

## 屬性

- `config` (`LoaderConfig`)：設定物件，包含：
  - `filepath` (`str`)：本地端資料檔案路徑
  - `method` (`str`)：載入方法
  - `file_ext` (`str`)：檔案副檔名
  - `benchmark` (`bool`)：是否使用基準資料集
  - `dtypes` (`dict`)：欄位資料型態
  - `column_types` (`dict`)：使用者定義的欄位型態（已棄用）
  - `header_names` (`list`)：欄位標題
  - `na_values` (`str` | `list` | `dict`)：NA 值定義（已棄用）
  - `schema_config` (`SchemaConfig` | `None`)：架構設定物件
  - 僅用於基準資料集：
    - `filepath_raw` (`str`)：原始輸入檔案路徑
    - `benchmark_name` (`str`)：基準資料集名稱
    - `benchmark_filename` (`str`)：基準資料集檔名
    - `benchmark_access` (`str`)：基準資料集存取類型
    - `benchmark_region_name` (`str`)：亞馬遜區域名稱
    - `benchmark_bucket_name` (`str`)：亞馬遜儲存桶名稱
    - `benchmark_sha256` (`str`)：基準資料集的 SHA-256 校驗值