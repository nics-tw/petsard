---
title: Test Coverage
type: docs
weight: 88
prev: docs/developer-guide/experiment-name-in-reporter
next: docs/developer-guide
---


### `Executor`

> tests/test_executor.py

Tests for the main Executor functionality:

- `test_default_values`: Verifies default configuration values are set correctly
- `test_update_config`: Tests updating configuration values via the update method
- `test_validation_log_output_type`: Tests validation of log output type settings:
  - Valid values (stdout, file, both) are accepted
  - Invalid values raise ConfigError
- `test_validation_log_level`: Tests validation of log levels:
  - Valid levels (DEBUG, INFO, WARNING, ERROR, CRITICAL) are accepted
  - Invalid levels raise ConfigError
- `test_executor_default_config`: Tests initialization with YAML without Executor section uses default values
- `test_executor_custom_config`: Verifies custom logging settings from YAML are properly applied
- `test_logger_setup`: Tests logger initialization with correct:
  - Log level
  - Multiple handlers (file and console)
  - Handler types
- `test_logger_file_creation`: Tests log file is created in specified directory with timestamp substitution
- `test_logger_reconfiguration`: Tests logger can be reconfigured after initial setup
- `test_get_config`: Tests YAML configuration loading from file



## Data Loading

### `Loader`

> tests/loader/test_loader.py

Tests for the main Loader functionality:

- `test_loader_init_no_config`: Verifies initialization with no config raises ConfigError
- `test_loader_init_with_filepath`: Tests initialization with file path, checks config path and extension are set correctly
- `test_handle_filepath_with_complex_name`: Tests various file path patterns including:
  - Path with multiple dots
  - Relative paths (./ and ../)
  - Absolute paths
  - Mixed case extensions
- `test_loader_init_with_column_types`: Verifies column type specifications are stored correctly in config
- `test_benchmark_loader`: Tests benchmark dataset initialization using mocked configs
- `test_load_csv`: Tests CSV file loading returns proper DataFrame and Metadata tuple
- `test_load_excel`: Tests Excel file loading returns proper DataFrame and Metadata tuple
- `test_benchmark_data_load`: Tests full benchmark data loading process with simulated data
- `test_custom_na_values`: Tests handling of custom NA values in data loading
- `test_custom_header_names`: Tests loading data with custom column headers

#### Ambiguous Data Type Processing Features

Tests for processing data with ambiguous or easily misinterpreted types:

- `test_preserve_raw_data_feature`: Tests preserve_raw_data feature prevents automatic pandas type inference:
  - Verifies dtype=object is used when preserve_raw_data=True
  - Tests integration with other ambiguous data processing features
  - Validates data loading pipeline with raw data preservation
- `test_leading_zero_detection_config`: Tests auto_detect_leading_zeros configuration:
  - Verifies configuration is properly stored
  - Tests both enabled and disabled states
- `test_nullable_integer_config`: Tests force_nullable_integers configuration:
  - Verifies configuration is properly stored
  - Tests both enabled and disabled states
- `test_ambiguous_data_config_combination`: Tests combination of all ambiguous data processing configurations:
  - preserve_raw_data + auto_detect_leading_zeros + force_nullable_integers
  - Verifies all settings work together correctly
- `test_backward_compatibility`: Tests that new features don't break existing functionality:
  - Verifies default values for new parameters
  - Tests normal loading behavior when features are disabled

### `Benchmarker`

> tests/loader/test_benchmarker.py

Tests for benchmark dataset handling:

- `test_basebenchmarker_init`: Verifies BaseBenchmarker cannot be instantiated as it's an abstract class
- `test_benchmarker_requests_init`: Tests BenchmarkerRequests initialization with mocked filesystem operations
- `test_download_success`: Tests successful download scenario with:
  - Mocked HTTP requests
  - Mocked file operations
  - SHA256 verification checks
- `test_verify_file_mismatch`: Tests SHA256 verification failure handling using mocked file content
- `test_download_request_fails`: Tests handling of download request failures (HTTP 404, etc.)
- `test_file_already_exists_hash_match`: Tests scenario where file already exists with matching hash, confirming local file is used
- `test_verify_file_remove_fails`: Tests error handling when file removal fails during verification
- `test_init_file_exists_hash_match`: Tests initialization logic when file exists with matching hash
- `test_file_content_change`: Tests hash verification mechanism after file content changes, ensuring changes are properly detected

## Data Processing

### `Metadater`

#### Field Functions

> tests/metadater/field/test_field_functions.py

Tests for field-level data processing and type analysis:

##### Comprehensive Type Analysis

- `test_leading_zero_detection`: Tests leading zero detection and preservation:
  - Identifies data with leading zeros (e.g., "001", "002")
  - Preserves as string type to maintain leading zeros
- `test_float_detection`: Tests floating point number detection:
  - Identifies decimal numbers in string format
  - Converts to appropriate float32/float64 types
- `test_integer_with_nulls`: Tests integer data with null values:
  - Uses nullable integer types (Int8, Int16, Int32, Int64)
  - Prevents conversion to float64 that would add .0 suffixes
- `test_integer_without_nulls`: Tests pure integer data:
  - Uses regular integer types (int8, int16, int32, int64)
  - Optimizes to smallest suitable integer type
- `test_mixed_non_numeric_data`: Tests non-numeric mixed data:
  - Falls back to category type for text data
- `test_numeric_conversion_threshold`: Tests 80% numeric conversion threshold:
  - Data with <80% numeric values treated as categorical
- `test_integer_dtype_handling`: Tests handling of pd.to_numeric integer results:
  - Properly handles int64 vs float64 type detection

##### Leading Zero Detection

- `test_has_leading_zeros_positive`: Tests positive detection cases:
  - >30% of values have leading zeros pattern
- `test_has_leading_zeros_negative`: Tests negative detection cases:
  - <30% of values have leading zeros pattern
- `test_has_leading_zeros_empty_data`: Tests empty data handling
- `test_has_leading_zeros_all_na`: Tests all-NA data handling
- `test_has_leading_zeros_mixed_types`: Tests mixed data type handling

##### Field Metadata Integration

- `test_build_field_metadata_with_leading_zeros`: Tests field metadata building with leading zero detection:
  - Enabled vs disabled leading zero detection
  - Integration with type analysis pipeline
- `test_build_field_metadata_with_nullable_integers`: Tests nullable integer integration:
  - Enabled vs disabled nullable integer handling
  - Proper type selection based on null presence
- `test_build_field_metadata_dtype_optimization`: Tests dtype optimization:
  - Memory-efficient type selection (int8 vs int64)
  - Float precision optimization (float32 vs float64)

##### Ambiguous Data Scenarios

- `test_id_code_preservation`: Tests preservation of ID codes with leading zeros:
  - Leading zero identification codes (001, 002, etc.)
  - Maintains data integrity for official identifiers
- `test_demographic_data_with_missing_values`: Tests demographic data with missing values:
  - Uses nullable integers to avoid .0 suffixes
  - Maintains data type consistency
- `test_financial_amount_detection`: Tests financial amount data handling:
  - Proper float detection for monetary values
  - Precision preservation for financial calculations
- `test_score_integer_detection`: Tests scoring data:
  - Integer detection for test scores, ratings
- `test_categorical_data_detection`: Tests categorical data:
  - Grade levels, status categories

##### Edge Cases

- `test_empty_series`: Tests empty data series handling
- `test_all_null_series`: Tests all-null data handling
- `test_single_value_series`: Tests single value data
- `test_mixed_numeric_string_data`: Tests mixed data types
- `test_config_none_handling`: Tests default configuration handling

### `Metadata`

> tests/loader/test_metadata.py

Tests for metadata handling and type inference:

- `test_metadata_init`: Verifies empty initialization of Metadata class
- `test_build_metadata`: Tests metadata building with sample DataFrame containing:
  - Numerical values
  - Categorical values
  - Datetime values
  - Boolean values
  - Missing values (None/NaN)
- `test_invalid_dataframe`: Tests error handling for:
  - Non-DataFrame inputs
  - Empty DataFrames
- `test_set_col_infer_dtype`: Tests column type inference:
  - Setting valid types
  - Handling invalid columns
  - Handling invalid types
- `test_to_sdv`: Tests conversion to SDV format with proper type mapping
- `test_convert_dtypes`: Tests type conversion for:
  - Numeric types (int/float)
  - Categorical types
  - Datetime types
  - Boolean types
  - Invalid types

### `Splitter`

> tests/loader/test_splitter.py

Tests for data splitting functionality with enhanced overlap control:

#### Core Functionality Tests
- `test_splitter_init_normal`: Tests normal initialization with new parameters (`max_overlap_ratio`, `max_attempts`)
- `test_splitter_init_invalid_ratio`: Tests handling of invalid split ratios and overlap ratios
- `test_splitter_init_custom_data_valid`: Tests valid custom data method configuration
- `test_splitter_init_custom_data_invalid_method`: Tests error handling for invalid custom methods
- `test_splitter_init_custom_data_invalid_filepath`: Tests error handling for invalid file paths

#### Functional Programming API Tests
- `test_split_normal_method`: Tests normal splitting method with new return format `(split_data, metadata_dict, train_indices)`
- `test_split_normal_method_no_data`: Tests splitting with no data
- `test_split_multiple_samples`: Tests multiple sample splitting with `list[set]` train indices format
- `test_split_custom_data_method`: Tests custom data splitting method with updated metadata structure
- `test_split_basic_functionality`: Tests basic splitting functionality with functional API

#### Overlap Control Features
- `test_max_overlap_ratio_parameter`: Tests `max_overlap_ratio` parameter initialization and validation
- `test_overlap_control_functionality`: Tests overlap control between samples using bootstrap sampling
- `test_exclude_index_functionality`: Tests `exist_train_indices` functionality to avoid overlap with existing samples
- `test_index_bootstrapping_collision_handling`: Tests bootstrap sampling collision handling with configurable attempts

#### Metadata and Architecture Tests
- `test_metadata_update_functional_approach`: Tests metadata updates using functional approach
- `test_create_split_metadata`: Tests creation of split metadata with new dictionary format

> **Architecture Refactoring Note**: In the refactoring on 2025/6/18, all external modules (Loader, Processor, Splitter, Benchmarker) no longer directly import Metadater's internal APIs (`metadater.api`, `metadater.core`, `metadater.types`), and instead use Metadater class's public methods. Related test mock paths have also been updated accordingly to ensure architectural encapsulation and consistency.

## Data Generating

### `Synthesizer`

> tests/synthesizer/test_synthesizer.py

Tests for the main Synthesizer functionality:

- `test_initialization`: Verifies Synthesizer initialization functionality:
  - Checks configuration method is set correctly
  - Validates initial state (_impl is None)
  - Tests custom parameter settings (e.g., sample_num_rows)
- `test_create_basic`: Tests basic functionality of create method:
  - Uses mock objects to simulate SDV synthesizer
  - Verifies _impl state changes before and after create
  - Tests integration with _determine_sample_configuration method
- `test_fit_without_create`: Tests that calling fit before create raises UncreatedError
- `test_fit_without_data_raises_error`: Tests that non-CUSTOM_DATA methods without data raise ConfigError
- `test_sample_without_create`: Tests that sample method returns empty DataFrame when not created

> **Architecture Refactoring Note**: In the refactoring on 2025/6/18, the Synthesizer module has been completely migrated to use the new Metadater architecture. All submodules (synthesizer_base.py, custom_data.py, custom_synthesizer.py, sdv.py) have been updated to use `petsard.metadater.types.SchemaMetadata` instead of the old `petsard.loader.Metadata`. The SDV conversion logic has been adapted to the new SchemaMetadata structure, ensuring compatibility with the new architecture.

### `Constrainer`

> tests/constrainer/test_constrainer.py

Tests for the main Constrainer class:

- `test_basic_initialization`: Tests basic constrainer initialization and config storage
- `test_nan_groups_constraints`: Tests NaN group constraints:
  - Delete action implementation
  - Erase action with multiple targets
  - Copy action with type checking
- `test_field_constraints`: Tests field-level constraints:
  - Numeric range conditions
  - Multiple conditions combined
- `test_field_combinations`: Tests field combination rules:
  - Education-performance mapping
  - Multiple value combinations
- `test_all_constraints_together`: Tests all constraints working together:
  - Constraint interaction
  - Complex filtering scenarios
- `test_resample_functionality`: Tests resample until satisfy:
  - Target row achievement
  - Synthetic data generation
  - Constraint satisfaction
- `test_error_handling`: Tests error cases:
  - Invalid config format
  - Missing columns
- `test_edge_cases`: Tests boundary conditions:
  - Empty DataFrame
  - All NaN values

#### `NaNGroupConstrainer`

> tests/constrainer/test_nan_group_constrainer.py

Tests for NaN value handling constraints:

- `test_invalid_config_initialization`: Tests invalid configuration handling:
  - Non-dictionary inputs
  - Invalid action types
  - Invalid target specifications
  - Delete action combined with other actions
- `test_valid_config_initialization`: Tests valid configurations:
  - Delete action standalone
  - Multiple targets for erase action
  - Single target for copy action
  - Different target formats
- `test_erase_action`: Tests erase action functionality:
  - Sets target fields to NaN when source field is NaN
  - Handles multiple target fields
- `test_copy_action_compatible_types`: Tests value copying between compatible types
- `test_copy_action_incompatible_types`: Tests handling of incompatible type copying
- `test_multiple_constraints`: Tests multiple constraints working together

#### `FieldConstrainer`

> tests/constrainer/test_field_constrainer.py

Tests for field-level constraints:

- `test_invalid_config_structure`: Tests configuration validation:
  - Non-list inputs
  - Invalid constraint formats
  - Empty constraints
- `test_invalid_constraint_syntax`: Tests syntax validation:
  - Unmatched parentheses
  - Invalid operators
  - Missing operators
- `test_field_extraction`: Tests field name extraction from:
  - Addition operations
  - Parenthesized expressions
  - NULL checks
  - Date operations
- `test_complex_expression_validation`: Tests complex constraint combinations

#### `FieldCombinationConstrainer`

> tests/constrainer/test_field_combination_constrainer.py

Tests for field combination constraints:

- `test_validate_config_existing_columns`: Tests column existence validation
- `test_invalid_constraints_not_list`: Tests non-list constraint handling
- `test_invalid_constraint_structure`: Tests invalid tuple structures
- `test_invalid_field_map`: Tests field mapping validation
- `test_invalid_source_fields`: Tests source field type validation
- `test_invalid_target_field`: Tests target field type validation
- `test_multi_field_source_value_length_mismatch`: Tests multi-field value matching

## Data Evaluating

### `Evaluator`


> - All functionality replacements use Metadater's public interface, completely avoiding deep internal functionality calls
> - All original functionality has been preserved with full backward compatibility
> - New Metadater functionality is provided through unified interface via `Metadater` class static methods

#### `MLUtility`

> tests/evaluator/test_mlutility.py

Tests for machine learning utility evaluation:

- `test_classification_of_single_value`: Tests classification with constant target in three scenarios:
  - Original data has single level target
  - Synthetic data has single level target
  - Both datasets have single level target
  - Verifies correct handling of NaN scores and warnings
- `test_classification_normal_case`: Tests normal multi-class classification:
  - Verifies score calculation
  - Checks score ranges
  - Validates statistical metrics
- `test_classification_empty_data`: Tests behavior with empty data:
  - Handles preprocessing of empty data
  - Verifies NaN scores
  - Checks warning messages

#### `MPUCCs`

> tests/evaluator/test_mpuccs.py

Tests for mpUCCs (Maximal Partial Unique Column Combinations) privacy risk assessment:

**Basic Functionality Tests (`TestMPUCCsBasic`):**
- `test_initialization`: Tests MPUCCs evaluator initialization with configuration parameters
- `test_basic_evaluation`: Tests basic evaluation functionality with simple test data
- `test_empty_data`: Tests handling of empty datasets

**Precision Handling Tests (`TestMPUCCsPrecisionHandling`):**
- `test_numeric_precision_auto_detection`: Tests automatic detection of numeric field precision (decimal places)
- `test_numeric_precision_manual_setting`: Tests manual numeric precision configuration
- `test_datetime_precision_auto_detection`: Tests automatic detection of datetime field precision
- `test_datetime_precision_normalization`: Tests case-insensitive datetime precision format normalization

**Entropy Calculation Tests (`TestMPUCCsEntropyCalculation`):**
- `test_renyi_entropy_calculation`: Tests Rényi entropy (α=2, Collision Entropy) calculation with different data distributions:
 - High entropy (uniform distribution)
 - Medium entropy (moderate skew)
 - Low entropy (high skew)
 - Very low entropy (extreme skew)
- `test_entropy_gain_calculation`: Tests conditional entropy gain calculation for field combinations

**Pruning Logic Tests (`TestMPUCCsPruningLogic`):**
- `test_entropy_based_pruning`: Tests entropy-based pruning mechanism with configurable thresholds
- `test_base_combo_pruning_propagation`: Tests pruning propagation from base combinations to supersets

**Integration Tests (`TestMPUCCsIntegration`):**
- `test_complete_workflow`: Tests complete mpUCCs workflow with realistic data scenarios
- `test_skip_ncols_configuration`: Tests skip pattern configuration (e.g., n_cols=[1, 3])
- `test_deduplication_functionality`: Tests automatic data deduplication before analysis

**Edge Cases Tests (`TestMPUCCsEdgeCases`):**
- `test_single_column_data`: Tests single-field datasets
- `test_all_unique_data`: Tests datasets with all unique values but no collisions
- `test_all_identical_data`: Tests datasets with identical values

**Theoretical Validation:**
- `test_renyi_vs_shannon_entropy`: Demonstrates differences between Rényi and Shannon entropy for privacy analysis

> **mpUCCs Architecture**: mpUCCs implements advanced singling-out risk assessment based on maximal partial unique column combinations theory (mpUCCs = QIDs). Key features include progressive tree-based search, entropy-based pruning, precision handling for numeric/datetime fields, and comprehensive progress tracking with dual-layer progress bars.

## Data Reporting

### `Reporter`

> tests/reporter/test_reporter.py


> - All original functionality has been preserved with full backward compatibility
> - Enhanced merge logic in `_safe_merge` method to properly handle columnwise and pairwise data merging

Tests for the main Reporter functionality:

- `test_method`: Tests Reporter initialization with different methods:
  - ReporterSaveData for 'save_data' method
  - ReporterSaveReport for 'save_report' method
  - UnsupportedMethodError for invalid methods
- `test_method_save_data`: Tests save_data method validation:
  - ConfigError when no source is provided
- `test_method_save_report`: Tests save_report method validation:
  - Valid initialization with granularity only
  - ConfigError when required parameters are missing

#### `ReporterSaveData`

Tests for data saving functionality:

- `test_source`: Tests source parameter validation:
  - String and list of strings are accepted
  - ConfigError for invalid types (float, mixed list, tuple)

#### `ReporterSaveReport`

Tests for report generation functionality:

- `test_granularity`: Tests granularity parameter validation:
  - Valid values: 'global', 'columnwise', 'pairwise'
  - ConfigError for missing or invalid granularity
  - ConfigError for non-string types
- `test_eval`: Tests eval parameter validation:
  - String, list of strings, or None are accepted
  - ConfigError for invalid types
- `test_create`: Tests report creation for all granularities:
  - Global granularity report generation
  - Columnwise granularity report generation
  - Pairwise granularity report generation
- `test_process_report_data`: Tests data processing functionality:
  - Column renaming with eval name prefixes
  - Index handling for different granularities
  - Skip flag for non-Evaluator/Describer modules
- `test_safe_merge`: Tests DataFrame merging functionality:
  - Pure data merging with overlapping columns
  - Processed data merging for all granularities
  - Proper handling of common columns including 'column', 'column1', 'column2'
  - Correct row ordering in merged results

#### `Reporter Utils`

Tests for utility functions:

- `test_convert_full_expt_tuple_to_name`: Tests experiment tuple to name conversion
- `test_convert_full_expt_name_to_tuple`: Tests experiment name to tuple conversion
- `test_convert_eval_expt_name_to_tuple`: Tests evaluation experiment name parsing

## System Components

### `Config`

> tests/test_config.py

Tests for configuration management and BaseConfig functionality:

**Config Tests:**
- `test_init_basic_config`: Tests basic configuration initialization with module sequence and queue setup
- `test_config_validation_error`: Tests configuration validation for invalid experiment names with "_[xxx]" suffix
- `test_splitter_handler`: Tests Splitter configuration expansion for multiple samples
- `test_set_flow`: Tests flow setup with correct queue ordering and content
- `test_complete_workflow_setup`: Tests complete multi-module workflow configuration
- `test_operator_creation`: Tests operator instantiation from configuration

**BaseConfig Tests (integrated):**
- `test_init_and_get`: Tests initialization and get method with all attributes including logger
- `test_update`: Tests configuration updates with validation for existing attributes and type checking
- `test_get_params_include`: Tests parameter extraction with INCLUDE action and renaming
- `test_get_params_merge`: Tests parameter merging with MERGE action and dictionary validation
- `test_get_params_combined`: Tests combined parameter operations with multiple actions
- `test_get_params_validation`: Tests validation for non-existent attributes, duplicates, and conflicts
- `test_from_dict`: Tests configuration creation from dictionary with parameter validation
- `test_config_get_param_action_map`: Tests ConfigGetParamActionMap enum functionality

**Status Tests (integrated):**
- `test_init`: Tests Status initialization with config, sequence, and attribute setup
- `test_put_and_get_result`: Tests status storage and result retrieval with metadata tracking
- `test_metadata_management`: Tests metadata setting, retrieval, and error handling for non-existent modules
- `test_get_pre_module`: Tests previous module retrieval in execution sequence
- `test_get_full_expt`: Tests experiment configuration retrieval (full and partial)
- `test_report_management`: Tests report data management and DataFrame comparison
- `test_status_renewal`: Tests status update mechanism when modules are re-executed

### `Status`

> tests/test_status.py

Tests for the enhanced Status snapshot system with Metadater integration:

- `test_snapshot_creation`: Tests ExecutionSnapshot and MetadataChange creation with proper dataclass structure
- `test_change_tracking`: Tests metadata change tracking across pipeline stages
- `test_metadata_evolution`: Tests metadata evolution tracking through multiple operations
- `test_status_summary`: Tests status summary generation with execution history
- `test_snapshot_retrieval`: Tests snapshot retrieval and filtering functionality

> **Enhanced Status Architecture**: The Status system has been redesigned with Metadater at its core, providing comprehensive progress tracking, metadata snapshots, and change history while maintaining full backward compatibility with existing interfaces. Status is now a separate module (`petsard/status.py`) with dedicated snapshot functionality.

## System Components

### `Config`

> tests/test_config.py

Tests for configuration management and BaseConfig functionality:

**Config Tests:**
- `test_init_basic_config`: Tests basic configuration initialization with module sequence and queue setup
- `test_config_validation_error`: Tests configuration validation for invalid experiment names with "_[xxx]" suffix
- `test_splitter_handler`: Tests Splitter configuration expansion for multiple samples
- `test_set_flow`: Tests flow setup with correct queue ordering and content
- `test_complete_workflow_setup`: Tests complete multi-module workflow configuration
- `test_operator_creation`: Tests operator instantiation from configuration

**BaseConfig Tests (integrated):**
- `test_init_and_get`: Tests initialization and get method with all attributes including logger
- `test_update`: Tests configuration updates with validation for existing attributes and type checking
- `test_get_params_include`: Tests parameter extraction with INCLUDE action and renaming
- `test_get_params_merge`: Tests parameter merging with MERGE action and dictionary validation
- `test_get_params_combined`: Tests combined parameter operations with multiple actions
- `test_get_params_validation`: Tests validation for non-existent attributes, duplicates, and conflicts
- `test_from_dict`: Tests configuration creation from dictionary with parameter validation
- `test_config_get_param_action_map`: Tests ConfigGetParamActionMap enum functionality

**Status Tests (integrated):**
- `test_init`: Tests Status initialization with config, sequence, and attribute setup
- `test_put_and_get_result`: Tests status storage and result retrieval with metadata tracking
- `test_metadata_management`: Tests metadata setting, retrieval, and error handling for non-existent modules
- `test_get_pre_module`: Tests previous module retrieval in execution sequence
- `test_get_full_expt`: Tests experiment configuration retrieval (full and partial)
- `test_report_management`: Tests report data management and DataFrame comparison
- `test_status_renewal`: Tests status update mechanism when modules are re-executed

### `Status`

> tests/test_status.py

Tests for the enhanced Status snapshot system with Metadater integration:

- `test_snapshot_creation`: Tests ExecutionSnapshot and MetadataChange creation with proper dataclass structure
- `test_change_tracking`: Tests metadata change tracking across pipeline stages
- `test_metadata_evolution`: Tests metadata evolution tracking through multiple operations
- `test_status_summary`: Tests status summary generation with execution history
- `test_snapshot_retrieval`: Tests snapshot retrieval and filtering functionality

> **Enhanced Status Architecture**: The Status system has been redesigned with Metadater at its core, providing comprehensive progress tracking, metadata snapshots, and change history while maintaining full backward compatibility with existing interfaces. Status is now a separate module (`petsard/status.py`) with dedicated snapshot functionality.