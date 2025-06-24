---
title: Test Coverage
type: docs
weight: 87
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

Tests for data splitting functionality:

- `test_splitter_init_normal`: Tests normal initialization
- `test_splitter_init_invalid_ratio`: Tests handling of invalid split ratios
- `test_splitter_init_custom_data_valid`: Tests valid custom data method configuration
- `test_splitter_init_custom_data_invalid_method`: Tests error handling for invalid custom methods
- `test_splitter_init_custom_data_invalid_filepath`: Tests error handling for invalid file paths
- `test_split_normal_method`: Tests normal splitting method
- `test_split_normal_method_no_data`: Tests splitting with no data
- `test_split_multiple_samples`: Tests multiple sample splitting
- `test_split_custom_data_method`: Tests custom data splitting method
- `test_split_basic_functionality`: Tests basic splitting functionality
- `test_index_bootstrapping_collision_handling`: Tests index bootstrapping collision handling
- `test_metadata_update_functional_approach`: Tests metadata updates using functional approach
- `test_create_split_metadata`: Tests creation of split metadata

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