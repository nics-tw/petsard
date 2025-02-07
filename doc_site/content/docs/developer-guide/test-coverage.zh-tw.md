---
title: 測試覆蓋範圍
type: docs
weight: 54
prev: docs/developer-guide/experiment-name-in-reporter
next: docs/developer-guide
sidebar:
  open: true
---

## 資料讀取

### `Loader`

> tests/loader/test_loader.py

測試 Loader 的主要功能：

- `test_loader_init_no_config`：驗證無配置初始化時會觸發 NoConfigError
- `test_loader_init_with_filepath`：測試以檔案路徑初始化，檢查配置路徑和副檔名是否正確設定
- `test_handle_filepath_with_complex_name`：測試各種檔案路徑模式，包含：
  - 含多個點的路徑
  - 相對路徑 (./ 和 ../)
  - 絕對路徑
  - 混合大小寫的副檔名
- `test_loader_init_with_column_types`：驗證欄位型態設定是否正確存入配置
- `test_benchmark_loader`：使用模擬的 BenchmarkerRequests 測試基準資料集載入功能
- `test_load_csv`：使用暫存測試檔案測試 CSV 檔案載入和 metadata 建立
- `test_invalid_file_extension`：驗證無效的副檔名會觸發 UnsupportedMethodError
- `test_custom_na_values`：測試自定義空值的處理

### `Benchmarker`

> tests/loader/test_benchmark.py

測試基準資料集處理：

- `test_basebenchmarker_init`：驗證 BaseBenchmarker 作為抽象類別無法被實例化
- `test_benchmarker_requests_init`：使用模擬的檔案系統操作測試 BenchmarkerRequests 初始化
- `test_download_success`：測試成功下載的情境，包含：
  - 模擬 HTTP 請求
  - 模擬檔案操作
  - SHA256 驗證檢查
- `test_verify_file_mismatch`：使用模擬的檔案內容測試 SHA256 驗證失敗的處理

### `Metadata`

> tests/loader/test_metadata.py

測試 metadata 處理和型態推斷：

- `test_metadata_init`：驗證 Metadata 類別的空初始化
- `test_build_metadata`：測試 metadata 建立，樣本 DataFrame 包含：
  - 數值型態
  - 類別型態
  - 日期時間型態
  - 布林型態
  - 缺失值 (None/NaN)
- `test_invalid_dataframe`：測試錯誤處理：
  - 非 DataFrame 輸入
  - 空的 DataFrame
- `test_set_col_infer_dtype`：測試欄位型態推斷：
  - 設定有效型態
  - 處理無效欄位
  - 處理無效型態
- `test_to_sdv`：測試轉換為 SDV 格式時的型態對應
- `test_convert_dtypes`：測試型態轉換：
  - 數值型態 (int/float)
  - 類別型態
  - 日期時間型態
  - 布林型態
  - 無效型態

## 資料合成

### `Constrainer`

> tests/constrainer/test_constrainer.py

測試主要約束器類別：

- `test_basic_initialization`：測試基本約束器初始化和配置儲存
- `test_nan_groups_constraints`：測試空值群組約束：
  - 刪除動作實作
  - 多目標的清除動作
  - 含型別檢查的複製動作
- `test_field_constraints`：測試欄位級別約束：
  - 數值範圍條件
  - 多重條件組合
- `test_field_combinations`：測試欄位組合規則：
  - 教育程度與績效對應
  - 多重值組合
- `test_all_constraints_together`：測試所有約束共同運作：
  - 約束之間的互動
  - 複雜的過濾情境
- `test_resample_functionality`：測試重複採樣直到滿足：
  - 達成目標列數
  - 合成資料生成
  - 約束條件滿足
- `test_error_handling`：測試錯誤情況：
  - 無效的配置格式
  - 缺少欄位
- `test_edge_cases`：測試邊界條件：
  - 空的資料框
  - 全部為空值

#### `NaNGroupConstrainer`

> tests/constrainer/test_nan_group_constrainer.py

測試空值處理約束：

- `test_invalid_config_initialization`：測試無效配置處理：
  - 非字典輸入
  - 無效的動作類型
  - 無效的目標設定
  - 刪除動作與其他動作的組合
- `test_valid_config_initialization`：測試有效配置：
  - 獨立的刪除動作
  - 多目標的清除動作
  - 單目標的複製動作
  - 不同目標格式
- `test_erase_action`：測試清除動作功能：
  - 當來源欄位為空值時設定目標欄位為空值
  - 處理多個目標欄位
- `test_copy_action_compatible_types`：測試相容類型間的值複製
- `test_copy_action_incompatible_types`：測試不相容類型複製的處理
- `test_multiple_constraints`：測試多個約束同時運作

#### `FieldConstrainer`

> tests/constrainer/test_field_constrainer.py

測試欄位級別約束：

- `test_invalid_config_structure`：測試配置驗證：
  - 非列表輸入
  - 無效的約束格式
  - 空約束
- `test_invalid_constraint_syntax`：測試語法驗證：
  - 不匹配的括號
  - 無效的運算子
  - 缺少運算子
- `test_field_extraction`：測試欄位名稱提取：
  - 加法運算
  - 括號表達式
  - 空值檢查
  - 日期運算
- `test_complex_expression_validation`：測試複雜約束組合

#### `FieldCombinationConstrainer`

> tests/constrainer/test_field_combination_constrainer.py

測試欄位組合約束：

- `test_validate_config_existing_columns`：測試欄位存在性驗證
- `test_invalid_constraints_not_list`：測試非列表約束處理
- `test_invalid_constraint_structure`：測試無效的元組結構
- `test_invalid_field_map`：測試欄位映射驗證
- `test_invalid_source_fields`：測試來源欄位類型驗證
- `test_invalid_target_field`：測試目標欄位類型驗證
- `test_multi_field_source_value_length_mismatch`：測試多欄位值匹配

## 資料評測

### `Evaluator`

#### `MLUtility`

> tests/evaluator/test_mlutility.py

測試機器學習效用評估：

- `test_classification_of_single_value`：測試單一值分類目標的三種情境：
  - 原始資料有單一層級目標
  - 合成資料有單一層級目標
  - 兩個資料集都有單一層級目標
  - 驗證 NaN 分數和警告的正確處理
- `test_classification_normal_case`：測試正常多分類情況：
  - 驗證分數計算
  - 檢查分數範圍
  - 驗證統計指標
- `test_classification_empty_data`：測試空資料的行為：
  - 處理空資料的預處理
  - 驗證 NaN 分數
  - 檢查警告訊息