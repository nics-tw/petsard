---
title: 測試覆蓋範圍
type: docs
weight: 87
prev: docs/developer-guide/experiment-name-in-reporter
next: docs/developer-guide
---


### `Executor`

> tests/test_executor.py

測試 Executor 的主要功能：

- `test_default_values`：驗證預設配置值是否正確設定
- `test_update_config`：測試透過 update 方法更新配置值
- `test_validation_log_output_type`：測試日誌輸出類型設定的驗證：
  - 有效值（stdout、file、both）被接受
  - 無效值引發 ConfigError
- `test_validation_log_level`：測試日誌等級的驗證：
  - 有效等級（DEBUG、INFO、WARNING、ERROR、CRITICAL）被接受
  - 無效等級引發 ConfigError
- `test_executor_default_config`：測試使用不含 Executor 部分的 YAML 初始化時使用預設值
- `test_executor_custom_config`：驗證 YAML 中的自定義日誌設定是否正確應用
- `test_logger_setup`：測試日誌初始化的正確性：
  - 日誌等級
  - 多個處理器（檔案和控制台）
  - 處理器類型
- `test_logger_file_creation`：測試日誌檔案是否在指定目錄中創建並正確替換時間戳
- `test_logger_reconfiguration`：測試日誌器能否在初始設置後重新配置
- `test_get_config`：測試從檔案載入 YAML 配置

## 資料讀取

### `Loader`

> tests/loader/test_loader.py

測試 Loader 的主要功能：

- `test_loader_init_no_config`：驗證無配置初始化時會觸發 ConfigError
- `test_loader_init_with_filepath`：測試以檔案路徑初始化，檢查配置路徑和副檔名是否正確設定
- `test_handle_filepath_with_complex_name`：測試各種檔案路徑模式，包含：
  - 含多個點的路徑
  - 相對路徑 (./ 和 ../)
  - 絕對路徑
  - 混合大小寫的副檔名
- `test_loader_init_with_column_types`：驗證欄位型態設定是否正確存入配置
- `test_benchmark_loader`：使用模擬配置測試基準資料集初始化
- `test_load_csv`：測試 CSV 檔案載入是否返回正確的 DataFrame 和 Metadata 元組
- `test_load_excel`：測試 Excel 檔案載入是否返回正確的 DataFrame 和 Metadata 元組
- `test_benchmark_data_load`：使用模擬數據測試完整的基準資料載入流程
- `test_custom_na_values`：測試自定義空值的處理
- `test_custom_header_names`：測試使用自定義欄位標題載入資料

#### 容易誤判資料類型處理功能

測試處理容易誤判、型別判斷模糊的資料：

- `test_preserve_raw_data_feature`：測試 preserve_raw_data 功能阻止 pandas 自動類型推斷：
  - 驗證當 preserve_raw_data=True 時使用 dtype=object
  - 測試與其他容易誤判資料處理功能的整合
  - 驗證原始資料保留的資料載入流程
- `test_leading_zero_detection_config`：測試 auto_detect_leading_zeros 配置：
  - 驗證配置是否正確儲存
  - 測試啟用和停用狀態
- `test_nullable_integer_config`：測試 force_nullable_integers 配置：
  - 驗證配置是否正確儲存
  - 測試啟用和停用狀態
- `test_ambiguous_data_config_combination`：測試所有容易誤判資料處理配置的組合：
  - preserve_raw_data + auto_detect_leading_zeros + force_nullable_integers
  - 驗證所有設定能正確協同運作
- `test_backward_compatibility`：測試新功能不會破壞現有功能：
  - 驗證新參數的預設值
  - 測試功能停用時的正常載入行為

### `Benchmarker`

> tests/loader/test_benchmarker.py

測試基準資料集處理：

- `test_basebenchmarker_init`：驗證 BaseBenchmarker 作為抽象類別無法被實例化
- `test_benchmarker_requests_init`：使用模擬的檔案系統操作測試 BenchmarkerRequests 初始化
- `test_download_success`：測試成功下載的情境，包含：
  - 模擬 HTTP 請求
  - 模擬檔案操作
  - SHA256 驗證檢查
- `test_verify_file_mismatch`：使用模擬的檔案內容測試 SHA256 驗證失敗的處理
- `test_download_request_fails`：測試下載請求失敗（HTTP 404 等）的處理方式
- `test_file_already_exists_hash_match`：測試檔案已存在且哈希值匹配的情境，確認直接使用本地檔案
- `test_verify_file_remove_fails`：測試在驗證過程中刪除檔案失敗的處理機制
- `test_init_file_exists_hash_match`：測試初始化時檔案存在且哈希值匹配的處理邏輯
- `test_file_content_change`：測試檔案內容變更後的哈希驗證機制，確保能正確檢測變更

## 資料處理

### `Metadater`

#### 欄位函數

> tests/metadater/field/test_field_functions.py

測試欄位級別的資料處理和類型分析：

##### 完整類型分析

- `test_leading_zero_detection`：測試前導零檢測和保留：
  - 識別含前導零的資料（如 "001"、"002"）
  - 保留為字串類型以維持前導零
- `test_float_detection`：測試浮點數檢測：
  - 識別字串格式的小數
  - 轉換為適當的 float32/float64 類型
- `test_integer_with_nulls`：測試含空值的整數資料：
  - 使用可空整數類型（Int8、Int16、Int32、Int64）
  - 防止轉換為會添加 .0 後綴的 float64
- `test_integer_without_nulls`：測試純整數資料：
  - 使用一般整數類型（int8、int16、int32、int64）
  - 優化為最小適合的整數類型
- `test_mixed_non_numeric_data`：測試混合非數值資料：
  - 文字資料回退為 category 類型
- `test_numeric_conversion_threshold`：測試 80% 數值轉換門檻：
  - 少於 80% 數值的資料視為分類資料
- `test_integer_dtype_handling`：測試 pd.to_numeric 整數結果的處理：
  - 正確處理 int64 與 float64 類型檢測

##### 前導零檢測

- `test_has_leading_zeros_positive`：測試正面檢測案例：
  - 超過 30% 的值具有前導零模式
- `test_has_leading_zeros_negative`：測試負面檢測案例：
  - 少於 30% 的值具有前導零模式
- `test_has_leading_zeros_empty_data`：測試空資料處理
- `test_has_leading_zeros_all_na`：測試全空值資料處理
- `test_has_leading_zeros_mixed_types`：測試混合資料類型處理

##### 欄位元資料整合

- `test_build_field_metadata_with_leading_zeros`：測試含前導零檢測的欄位元資料建立：
  - 啟用與停用前導零檢測
  - 與類型分析流程的整合
- `test_build_field_metadata_with_nullable_integers`：測試可空整數整合：
  - 啟用與停用可空整數處理
  - 根據空值存在選擇適當類型
- `test_build_field_metadata_dtype_optimization`：測試資料類型優化：
  - 記憶體效率的類型選擇（int8 vs int64）
  - 浮點精度優化（float32 vs float64）

##### 容易誤判資料情境

- `test_id_code_preservation`：測試識別代號保留：
  - 前導零識別代號（001、002 等）
  - 維持官方識別碼的資料完整性
- `test_demographic_data_with_missing_values`：測試含缺失值的人口統計資料：
  - 使用可空整數避免 .0 後綴
  - 維持資料類型一致性
- `test_financial_amount_detection`：測試金額資料處理：
  - 金額值的正確浮點檢測
  - 財務計算的精度保留
- `test_score_integer_detection`：測試評分資料：
  - 測試分數、評級的整數檢測
- `test_categorical_data_detection`：測試分類資料：
  - 等級分類、狀態分類

##### 邊界情況

- `test_empty_series`：測試空資料序列處理
- `test_all_null_series`：測試全空值資料處理
- `test_single_value_series`：測試單值資料
- `test_mixed_numeric_string_data`：測試混合資料類型
- `test_config_none_handling`：測試預設配置處理

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

### `Splitter`

> tests/loader/test_splitter.py

測試資料分割功能：

- `test_splitter_init_normal`：測試正常初始化
- `test_splitter_init_invalid_ratio`：測試無效分割比例的處理
- `test_splitter_init_custom_data_valid`：測試自定義資料方法的有效配置
- `test_splitter_init_custom_data_invalid_method`：測試無效自定義方法的錯誤處理
- `test_splitter_init_custom_data_invalid_filepath`：測試無效檔案路徑的錯誤處理
- `test_split_normal_method`：測試正常分割方法
- `test_split_normal_method_no_data`：測試無資料情況下的分割
- `test_split_multiple_samples`：測試多重樣本分割
- `test_split_custom_data_method`：測試自定義資料分割方法
- `test_split_basic_functionality`：測試基本分割功能
- `test_index_bootstrapping_collision_handling`：測試索引自助法碰撞處理
- `test_metadata_update_functional_approach`：測試使用函數式方法更新 metadata
- `test_create_split_metadata`：測試建立分割 metadata

> **架構重構說明**：在 2025/6/18 的重構中，所有外部模組（Loader、Processor、Splitter、Benchmarker）已不再直接導入 Metadater 的內部 API（`metadater.api`、`metadater.core`、`metadater.types`），改為使用 Metadater 類別的公共方法。相關測試的 mock 路徑也已相應更新，確保架構的封裝性和一致性。

## 資料合成

### `Synthesizer`

> tests/synthesizer/test_synthesizer.py

測試 Synthesizer 的主要功能：

- `test_initialization`：驗證 Synthesizer 的初始化功能：
  - 檢查配置方法是否正確設定
  - 驗證初始狀態（_impl 為 None）
  - 測試自定義參數設定（如 sample_num_rows）
- `test_create_basic`：測試 create 方法的基本功能：
  - 使用 mock 物件模擬 SDV synthesizer
  - 驗證 _impl 在 create 前後的狀態變化
  - 測試 _determine_sample_configuration 方法的整合
- `test_fit_without_create`：測試在未呼叫 create 前呼叫 fit 會引發 UncreatedError
- `test_fit_without_data_raises_error`：測試非 CUSTOM_DATA 方法但無資料時引發 ConfigError
- `test_sample_without_create`：測試在未 create 時 sample 方法返回空 DataFrame



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


> - 所有功能替換都使用 Metadater 的公共介面，完全避免調用深層內部功能
> - 保持了所有原有功能的完整性，確保向後相容性
> - 新的 Metadater 功能通過 `Metadater` 類的靜態方法提供統一介面

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

## 資料報告

### `Reporter`

> tests/reporter/test_reporter.py


> - 所有原始功能都已保留，具有完全向後相容性
> - 增強 `_safe_merge` 方法中的合併邏輯，正確處理 columnwise 和 pairwise 資料合併

測試主要 Reporter 功能：

- `test_method`：測試 Reporter 使用不同方法的初始化：
  - 'save_data' 方法使用 ReporterSaveData
  - 'save_report' 方法使用 ReporterSaveReport
  - 無效方法拋出 UnsupportedMethodError
- `test_method_save_data`：測試 save_data 方法驗證：
  - 未提供 source 時拋出 ConfigError
- `test_method_save_report`：測試 save_report 方法驗證：
  - 僅使用 granularity 的有效初始化
  - 缺少必要參數時拋出 ConfigError

#### `ReporterSaveData`

測試資料儲存功能：

- `test_source`：測試 source 參數驗證：
  - 接受字串和字串列表
  - 無效類型（浮點數、混合列表、元組）拋出 ConfigError

#### `ReporterSaveReport`

測試報告生成功能：

- `test_granularity`：測試 granularity 參數驗證：
  - 有效值：'global'、'columnwise'、'pairwise'
  - 缺少或無效 granularity 拋出 ConfigError
  - 非字串類型拋出 ConfigError
- `test_eval`：測試 eval 參數驗證：
  - 接受字串、字串列表或 None
  - 無效類型拋出 ConfigError
- `test_create`：測試所有粒度的報告建立：
  - Global 粒度報告生成
  - Columnwise 粒度報告生成
  - Pairwise 粒度報告生成
- `test_process_report_data`：測試資料處理功能：
  - 使用評估名稱前綴重命名欄位
  - 不同粒度的索引處理
  - 非 Evaluator/Describer 模組的跳過標記
- `test_safe_merge`：測試 DataFrame 合併功能：
  - 具有重疊欄位的純資料合併
  - 所有粒度的處理資料合併
  - 正確處理包括 'column'、'column1'、'column2' 的共同欄位
  - 合併結果中的正確行順序

#### `Reporter Utils`

測試工具函數：

- `test_convert_full_expt_tuple_to_name`：測試實驗元組到名稱的轉換
- `test_convert_full_expt_name_to_tuple`：測試實驗名稱到元組的轉換
- `test_convert_eval_expt_name_to_tuple`：測試評估實驗名稱解析