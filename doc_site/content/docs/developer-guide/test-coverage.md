---
title: Test Coverage
type: docs
weight: 88
prev: docs/developer-guide/experiment-name-in-reporter
next: docs/developer-guide/docker-development
---


## PETsARD End-to-End Functional Tests

### `PETsARD Functional Workflows`

> tests/test_petsard.py

Tests for complete PETsARD end-to-end workflows using realistic YAML configurations. These tests verify that the entire system works correctly from data loading through synthesis and evaluation.

#### Core Workflow Tests

**`test_default_synthesis_workflow`**: Tests basic data synthesis pipeline
- **YAML Configuration**:
  - `Loader`: Loads benchmark adult-income dataset
  - `Preprocessor`: Uses default preprocessing method
  - `Synthesizer`: Uses default synthesis method
  - `Postprocessor`: Uses default postprocessing method
  - `Reporter`: Saves synthesized data to output directory
- **Expected Results**:
  - Execution completes successfully with `is_execution_completed() == True`
  - Synthesized data contains all 15 expected columns (age, workclass, fnlwgt, education, etc.)
  - Output data is a valid pandas DataFrame with >0 rows
  - Data maintains adult-income dataset structure

**`test_data_preprocessing_workflow`**: Tests data preprocessing with missing value handling
- **YAML Configuration**:
  - `Loader`: Loads adult-income with custom NA values ('?')
  - `Preprocessor`: Custom sequence with missing value handling and encoding
  - `Synthesizer`: Default synthesis method
  - `Postprocessor`: Default postprocessing
  - `Reporter`: Saves processed data
- **Expected Results**:
  - Missing values are properly handled before synthesis
  - Encoding is applied to categorical variables
  - Final synthetic data maintains data quality

**`test_data_constraining_workflow`**: Tests synthesis with data constraints
- **YAML Configuration**:
  - `Loader`: Standard adult-income dataset
  - `Preprocessor`: Default preprocessing
  - `Synthesizer`: Default synthesis
  - `Postprocessor`: Default postprocessing
  - `Constrainer`: Field constraints (age 18-65, hours-per-week 20-60) and field proportions for education
  - `Reporter`: Saves constrained data
- **Expected Results**:
  - Age values are constrained to 18-65 range
  - Hours-per-week values are constrained to 20-60 range
  - Education field proportions are maintained within tolerance
  - Constraints are properly applied to synthetic data

**`test_evaluation_workflow`**: Tests synthesis with evaluation metrics
- **YAML Configuration**:
  - `Loader`: Adult-income dataset
  - `Splitter`: 80/20 train/test split with 1 sample
  - `Preprocessor`: Default preprocessing
  - `Synthesizer`: Default synthesis
  - `Postprocessor`: Default postprocessing
  - `Evaluator`: SDMetrics quality report evaluation
  - `Reporter`: Saves evaluation report with global granularity
- **Expected Results**:
  - Data is properly split for evaluation
  - Quality metrics are computed and available
  - Timing information is captured and accessible
  - Evaluation report is generated successfully

**`test_minimal_workflow`**: Tests minimal pipeline with just data loading
- **YAML Configuration**:
  - `Loader`: Adult-income dataset only
  - `Reporter`: Saves loaded data directly
- **Expected Results**:
  - Data loads successfully without processing
  - Original dataset structure is preserved
  - Demonstrates minimal viable PETsARD workflow

**`test_custom_sequence_preprocessing`**: Tests custom preprocessing pipeline
- **YAML Configuration**:
  - `Loader`: Adult-income dataset
  - `Preprocessor`: Custom 4-step sequence (missing → outlier → scaler → encoder)
  - `Synthesizer`: Default synthesis
  - `Postprocessor`: Default postprocessing
  - `Reporter`: Saves final processed data
- **Expected Results**:
  - All preprocessing steps execute in correct order
  - Data transformations are applied sequentially
  - Final data is ready for downstream analysis

#### Parameterized Module Execution Tests

**`test_workflow_module_execution`**: Tests different workflow configurations
- **Test Cases**:
  - `default-synthesis`: Full pipeline (Loader → Preprocessor → Synthesizer → Postprocessor)
  - `minimal`: Basic pipeline (Loader only)
  - `with-splitter`: Extended pipeline (Loader → Splitter → Preprocessor → Synthesizer → Postprocessor)
- **Expected Results**: Each workflow executes expected modules and produces valid results

#### Configuration Validation Tests

**`test_invalid_yaml_config`**: Tests error handling for invalid configurations
- **YAML Configuration**: Contains invalid module (InvalidModule) that doesn't exist
- **Expected Results**: Raises NameError, ValueError, KeyError, or AttributeError appropriately

**`test_missing_required_config`**: Tests error handling for empty configurations
- **YAML Configuration**: Empty configuration file
- **Expected Results**: Raises appropriate error for missing required components

#### Key Features

- **Executor API Integration**: Tests use new `is_execution_completed()` method to check execution status
- **Result Extraction**: Uses helper method `_extract_module_data()` to handle nested result structures
- **Real Data Testing**: Uses actual benchmark datasets (adult-income) for realistic testing
- **Configuration Variety**: Tests multiple YAML configuration patterns and module combinations
- **Error Handling**: Validates proper error handling for invalid configurations
- **End-to-End Validation**: Ensures complete workflows work from configuration to final output

> **Architecture Note**: These tests validate the complete PETsARD system using the new Executor API with `is_execution_completed()` status tracking. The `run()` method returns `None` in the current version, with plans to return success/failed status codes in v2.0.0. Results are accessed via `get_result()` method and processed through nested workflow structures.

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

#### Logical Type System Testing

Tests for the comprehensive logical type inference and validation system:

**Redesigned Logical Type System (2025 Update):**
Our logical type system has been completely redesigned to avoid overlap with basic data types and provide clear semantic meaning detection.

**Available Logical Types:**
- **Text-based**: `email`, `url`, `uuid`, `categorical`, `ip_address` (require string data type)
- **Numeric**: `percentage`, `currency`, `latitude`, `longitude` (require numeric data types)
- **Identifier**: `primary_key` (requires uniqueness validation)
- **Removed**: `datetime`, `date`, `time`, `duration`, `integer`, `decimal`, `text`, `foreign_key` (to avoid type overlap)

**Logical Type Detection Tests (`tests/metadater/field/test_field_functions.py`):**
- `test_email_logical_type_detection`: Tests email pattern detection with regex validation (80% threshold)
- `test_url_logical_type_detection`: Tests URL pattern detection with HTTP/HTTPS protocol validation (80% threshold)
- `test_uuid_logical_type_detection`: Tests UUID format detection in 8-4-4-4-12 hexadecimal format (95% threshold)
- `test_ip_address_detection`: Tests IPv4/IPv6 pattern recognition with comprehensive address validation (90% threshold)
- `test_categorical_detection_via_cardinality`: Tests ASPL-based categorical detection using cardinality analysis with dynamic thresholds
- `test_primary_key_uniqueness_validation`: Tests 100% uniqueness requirement for primary keys with duplicate detection
- `test_percentage_range_validation`: Tests 0-100 range validation for percentage values (95% threshold)
- `test_currency_symbol_detection`: Tests monetary value detection with currency symbols and positive value validation (80% threshold)
- `test_latitude_longitude_detection`: Tests geographic coordinate range validation (-90/90 for latitude, -180/180 for longitude, 95% threshold)

**Type Compatibility System Tests:**
- `test_compatible_type_logical_combinations`: Tests valid combinations:
  - `string` + `email`, `url`, `uuid`, `categorical`, `ip_address` ✅
  - `numeric` + `percentage`, `currency`, `latitude`, `longitude` ✅
  - `int/string` + `primary_key` ✅
- `test_incompatible_type_logical_combinations`: Tests invalid combinations that trigger warnings:
  - `numeric` + `email`, `url`, `uuid`, `ip_address` ❌
  - `string` + `percentage`, `currency`, `latitude`, `longitude` ❌
- `test_logical_type_fallback_on_conflict`: Tests automatic fallback to inference when types conflict
- `test_logical_type_priority_handling`: Tests priority system (data type constraints > logical type hints)

**Logical Type Configuration Tests:**
- `test_logical_type_never_mode`: Tests disabling logical type inference with "never" setting
- `test_logical_type_infer_mode`: Tests automatic inference with "infer" setting
- `test_logical_type_explicit_specification`: Tests forcing specific logical types via configuration with compatibility validation
- `test_logical_type_validation_thresholds`: Tests confidence thresholds (80% for text patterns, 90-95% for numeric ranges)

**Pattern Matching and Validation Tests:**
- `test_regex_pattern_validation`: Tests updated regex patterns for email, URL, UUID, IP address detection
- `test_numeric_range_validation`: Tests range validation for latitude, longitude, percentage values
- `test_special_validator_functions`: Tests custom validation functions for geographic coordinates
- `test_pattern_confidence_scoring`: Tests confidence scoring and threshold-based classification
- `test_primary_key_duplicate_detection`: Tests duplicate detection mechanism for primary key validation

**Error Handling and Conflict Resolution Tests:**
- `test_compatibility_warning_generation`: Tests warning generation for incompatible type/logical_type combinations
- `test_automatic_fallback_mechanism`: Tests fallback to automatic inference when conflicts occur
- `test_logging_incompatibility_messages`: Tests detailed logging of incompatibility reasons

> **Redesigned Logical Type System**: Our proprietary logical type inference system has been redesigned to focus exclusively on semantic meaning detection without overlapping with basic data types. The system uses pattern recognition, statistical analysis, and validation functions with strict type compatibility rules and comprehensive conflict resolution mechanisms.

#### Schema Parameters Testing

Tests for comprehensive functionality of the schema parameter system:

**Global Parameters Tests (`TestSchemaGlobalParameters`):**
- `test_compute_stats_parameter`: Tests `compute_stats` global parameter boolean validation
- `test_optimize_dtypes_parameter`: Tests `optimize_dtypes` global parameter boolean validation
- `test_sample_size_parameter`: Tests `sample_size` global parameter positive integer validation
- `test_sample_size_null`: Tests `sample_size` parameter accepts null values
- `test_leading_zeros_parameter`: Tests `leading_zeros` global parameter valid values ("never", "num-auto", "leading_n")
- `test_leading_zeros_invalid`: Tests `leading_zeros` parameter invalid value handling
- `test_nullable_int_parameter`: Tests `nullable_int` global parameter boolean validation
- `test_nullable_int_invalid`: Tests `nullable_int` parameter invalid value handling
- `test_infer_logical_types_parameter`: Tests `infer_logical_types` global parameter boolean validation
- `test_descriptive_parameters`: Tests descriptive parameters (`title`, `description`, `version`) string validation

**Field Parameters Tests (`TestSchemaFieldParameters`):**
- `test_logical_type_parameter`: Tests field-level `logical_type` parameter valid value validation
- `test_leading_zeros_field_level`: Tests field-level `leading_zeros` parameter overriding global settings
- `test_leading_zeros_field_invalid`: Tests field-level `leading_zeros` parameter invalid value handling

**Parameter Conflicts Tests (`TestSchemaParameterConflicts`):**
- `test_infer_logical_types_conflict`: Tests conflict detection between `infer_logical_types=true` and field-level `logical_type`

**Loader Schema Parameters Tests (`tests/loader/test_loader.py`):**
- `TestLoaderSchemaParameters`: Tests global schema parameters in Loader
- `TestLoaderSchemaFieldParameters`: Tests field-level schema parameters in Loader
- `TestLoaderSchemaParameterConflicts`: Tests parameter conflict detection in Loader
- `TestLoaderSchemaEdgeCases`: Tests schema edge cases in Loader

**SchemaConfig Validation Tests (`tests/metadater/test_schema_types.py`):**
- `test_schema_config_with_parameters`: Tests SchemaConfig initialization with parameters
- `test_schema_config_invalid_leading_zeros`: Tests SchemaConfig error handling for invalid `leading_zeros` values
- `test_schema_config_invalid_nullable_int`: Tests SchemaConfig error handling for invalid `nullable_int` values
- `test_schema_config_logical_type_conflict`: Tests SchemaConfig logical type conflict detection

**FieldConfig Validation Tests (`tests/metadater/field/test_field_types.py`):**
- `test_field_config_with_parameters`: Tests FieldConfig initialization with parameters
- `test_field_config_invalid_logical_type`: Tests FieldConfig error handling for invalid `logical_type` values
- `test_field_config_invalid_leading_zeros`: Tests FieldConfig error handling for invalid `leading_zeros` values
- `test_field_config_invalid_category_method`: Tests FieldConfig error handling for invalid `category_method` values
- `test_field_config_invalid_datetime_precision`: Tests FieldConfig error handling for invalid `datetime_precision` values

**Edge Cases Tests (`TestEdgeCases`):**
- `test_empty_schema`: Tests empty schema handling
- `test_schema_with_only_global_params`: Tests schema with only global parameters
- `test_invalid_global_parameter`: Tests invalid global parameter error handling
- `test_invalid_field_parameter`: Tests invalid field parameter error handling
- `test_mixed_legacy_and_schema`: Tests compatibility with mixed legacy and schema syntax

**Key Features:**
- **Two-layer Architecture Validation**: Tests hierarchical structure of global and field parameters
- **Parameter Conflict Detection**: Automatic detection and reporting of logical conflicts (e.g., `infer_logical_types` vs field `logical_type`)
- **Backward Compatibility**: Ensures parameter system is fully compatible with legacy schema syntax
- **Comprehensive Validation**: Covers parameter value ranges, types, and logical consistency checks
- **Edge Case Coverage**: Tests empty schemas, mixed syntax, invalid parameter combinations, and other extreme scenarios

> **Schema Parameter System**: Implements a two-layer schema parameter architecture providing flexible configuration through global parameters (such as `compute_stats`, `optimize_dtypes`, `sample_size`) and field-level parameters (such as `logical_type`, `leading_zeros`), with complete parameter conflict detection and backward compatibility guarantees.

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

#### Stress Testing

Tests for large file processing and edge case type inference:

**TestLoaderStress** - Progressive file size testing with timeout mechanisms:
- `test_medium_file_1gb`: Tests 1GB files (120s timeout)
- `test_xlarge_file_5gb`: Tests 5GB files (600s timeout)

**TestLoaderTypeInference** - Edge case type inference with 99.9% normal data, 0.1% exceptions at end:
- `test_int_with_string_exception`: Tests integer data with string exceptions
- `test_float_with_null_exception`: Tests float data with null exceptions
- `test_string_with_numeric_exception`: Tests string data with numeric exceptions

**Key Features:**
- **Memory monitoring**: Real-time memory usage tracking with psutil
- **Timeout protection**: Automatic test failure if loading exceeds time limits
- **Type inference validation**: Ensures 99.9% normal data with 0.1% exceptions placed at file end
- **Performance metrics**: Throughput measurement (MB/s) and memory efficiency tracking

**Usage:**
```bash
# Run all stress tests
pytest tests/loader/ -m stress -v

# Run specific stress test categories
pytest tests/loader/test_loader.py::TestLoaderStress -v
pytest tests/loader/test_loader.py::TestLoaderTypeInference -v

# Run stress test demo
python -c "from tests.loader.test_loader import run_stress_demo; run_stress_demo()"
```

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

#### `BenchmarkerConfig`

> tests/loader/test_loader.py::TestBenchmarkerConfig

Tests for the BenchmarkerConfig class that manages benchmark dataset configuration:

- `test_benchmarker_config_requires_benchmark_name`: Tests that benchmark_name parameter is required for initialization
- `test_benchmarker_config_initialization`: Tests BenchmarkerConfig initialization with proper attribute setting:
  - Benchmark name, filename, access type
  - Region name, bucket name, SHA256 hash
  - Integration with benchmark YAML configuration loading
- `test_benchmarker_config_get_benchmarker_config`: Tests get_benchmarker_config method:
  - Returns proper dictionary format for BenchmarkerRequests
  - Includes all required keys (benchmark_filename, benchmark_bucket_name, benchmark_sha256, filepath)
  - Constructs correct local benchmark file path
- `test_benchmarker_config_unsupported_benchmark`: Tests error handling for unsupported benchmark datasets
- `test_benchmarker_config_private_access_unsupported`: Tests error handling for private benchmark access attempts

> **Architecture Refactoring**: BenchmarkerConfig has been extracted from LoaderConfig to provide clear separation of concerns. LoaderConfig now contains an optional benchmarker_config attribute, allowing for two distinct states: with or without benchmark functionality. This refactoring improves code maintainability and follows the single responsibility principle.

## Data Processing

### `Processor`

#### Missing Value Handlers

> tests/processor/test_missing.py

Tests for missing value handling with comprehensive type compatibility:

**MissingMean Tests (4 tests):**
- `test_mean_no_missing_values`: Tests mean imputation with no missing values
- `test_mean_with_missing_values`: Tests mean imputation with missing values
- `test_mean_with_integer_dtype`: Tests mean imputation with pandas nullable integer types (Int32, Int64):
  - Verifies proper handling of integer data types without TypeError
  - Tests automatic rounding of mean values for integer compatibility
  - Validates dtype preservation after transformation
- `test_mean_with_integer_dtype_fractional_mean`: Tests mean imputation when mean has fractional part:
  - Tests banker's rounding (20.5 → 20) for integer types
  - Ensures proper type conversion for fractional means

**MissingMedian Tests (4 tests):**
- `test_median_no_missing_values`: Tests median imputation with no missing values
- `test_median_with_missing_values`: Tests median imputation with missing values
- `test_median_with_integer_dtype`: Tests median imputation with pandas nullable integer types (Int32, Int64):
  - Verifies proper handling of integer data types without TypeError
  - Tests automatic rounding of median values for integer compatibility
  - Validates dtype preservation after transformation
- `test_median_with_integer_dtype_fractional_median`: Tests median imputation when median has fractional part:
  - Tests banker's rounding (20.5 → 20) for integer types
  - Ensures proper type conversion for fractional medians

**MissingSimple Tests (2 tests):**
- `test_simple_no_missing_values`: Tests simple value imputation with no missing values
- `test_simple_with_missing_values`: Tests simple value imputation with missing values

**MissingDrop Tests (2 tests):**
- `test_drop_no_missing_values`: Tests drop strategy with no missing values
- `test_drop_with_missing_values`: Tests drop strategy with missing values

> **Integer Type Compatibility**: Enhanced missing value handlers now properly support pandas nullable integer types (Int8, Int16, Int32, Int64) by automatically rounding float imputation values to integers, preventing TypeError during fillna operations. This ensures seamless integration with schema-specified integer types while maintaining data integrity.

#### Outlier Detection Handlers

Enhanced outlier detection with pandas nullable integer array compatibility:

**OutlierHandler Base Class:**
- Enhanced `fit()` and `transform()` methods with `np.asarray()` conversion
- Proper handling of pandas nullable integer arrays to prevent broadcasting errors
- Maintains compatibility with numpy operations in outlier detection algorithms

> **Pandas Array Compatibility**: Outlier handlers now use `np.asarray()` instead of `.values` to ensure proper conversion of pandas nullable integer arrays to numpy arrays, preventing ValueError during logical operations in outlier detection algorithms.

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

Tests for the main Constrainer factory class (18 tests):

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
- `test_empty_config`: Tests constrainer with empty configuration
- `test_unknown_constraint_type_warning`: Tests warning for unknown constraint types
- `test_resample_trails_attribute`: Tests resample trails tracking functionality
- `test_register_custom_constraint`: Tests custom constraint registration
- `test_register_invalid_constraint_class`: Tests error handling for invalid constraint classes

**Field Proportions Integration Tests (5 tests):**
- `test_field_proportions_integration`: Tests field proportions constrainer integration with new architecture:
  - Single field proportions with updated configuration format
  - Missing value proportions maintenance
  - Field combination proportions handling
- `test_field_proportions_with_other_constraints`: Tests field proportions working with other constraint types:
  - Combined field proportions and field constraints
  - Multi-constraint interaction validation
- `test_field_proportions_comprehensive_integration`: Tests comprehensive field proportions integration based on real-world scenarios:
  - Education, income, and workclass data distribution maintenance
  - Multiple constraint modes (all, missing, field combinations)
  - New architecture validation with `target_rows` parameter
- `test_field_proportions_multiple_modes`: Tests field proportions with multiple constraint modes:
  - Category proportions ('all' mode)
  - Missing value proportions ('missing' mode)
  - Region proportions validation
- `test_field_proportions_edge_cases_integration`: Tests field proportions edge cases:
  - Small dataset handling
  - Target rows larger than available data
  - Empty field proportions list handling

#### `NaNGroupConstrainer`

> tests/constrainer/test_nan_group_constrainer.py

Tests for NaN value handling constraints (18 tests):

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
- `test_delete_action_edge_case`: Tests delete action with edge cases
- `test_erase_action_multiple_targets`: Tests erase action with multiple target fields
- `test_copy_action_type_validation`: Tests copy action with type validation
- `test_invalid_action_type`: Tests handling of invalid action types
- `test_invalid_target_specification`: Tests invalid target field specifications
- `test_empty_config_handling`: Tests empty configuration handling
- `test_mixed_action_validation`: Tests validation of mixed action configurations

#### `FieldConstrainer`

> tests/constrainer/test_field_constrainer.py

Tests for field-level constraints (12 tests):

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
- `test_empty_constraint_list`: Tests empty constraint list handling
- `test_null_check_operations`: Tests NULL value check operations
- `test_date_operation_constraints`: Tests date-based constraint operations
- `test_parentheses_validation`: Tests parentheses matching validation
- `test_operator_validation`: Tests operator syntax validation

#### `FieldCombinationConstrainer`

> tests/constrainer/test_field_combination_constrainer.py

Tests for field combination constraints (15 tests):

- `test_validate_config_existing_columns`: Tests column existence validation
- `test_invalid_constraints_not_list`: Tests non-list constraint handling
- `test_invalid_constraint_structure`: Tests invalid tuple structures
- `test_invalid_field_map`: Tests field mapping validation
- `test_invalid_source_fields`: Tests source field type validation
- `test_invalid_target_field`: Tests target field type validation
- `test_multi_field_source_value_length_mismatch`: Tests multi-field value matching
- `test_single_field_constraint`: Tests single field constraint validation
- `test_multi_field_constraint`: Tests multi-field constraint scenarios
- `test_constraint_tuple_validation`: Tests constraint tuple structure validation
- `test_field_mapping_edge_cases`: Tests field mapping edge cases
- `test_value_length_validation`: Tests value length matching validation
- `test_complex_field_combinations`: Tests complex field combination scenarios

#### `FieldProportionsConstrainer`

> tests/constrainer/test_field_proportions_constrainer.py

Tests for field proportion maintenance constraints (33 tests):

**FieldProportionsConfig Tests (6 tests):**
- `test_valid_config_initialization`: Tests valid configuration initialization with field proportions only
- `test_invalid_field_proportions_structure`: Tests invalid field proportions structure (missing tolerance, invalid mode)
- `test_invalid_tolerance_values`: Tests invalid tolerance values (>1, <0)
- `test_verify_data_with_valid_data`: Tests data verification with valid DataFrame and provided target_n_rows
- `test_verify_data_with_missing_columns`: Tests error handling for missing columns in data
- `test_check_proportions`: Tests proportion checking with good and bad filtered data

**FieldProportionsConstrainer Tests (14 tests):**
- `test_constrainer_initialization`: Tests constrainer initialization with valid configuration
- `test_invalid_constrainer_config`: Tests constrainer with invalid configuration (invalid mode)
- `test_apply_with_empty_dataframe`: Tests apply method with empty DataFrame
- `test_apply_with_valid_data`: Tests apply method with valid data and known proportions
- `test_field_combination_proportions`: Tests field combination proportions with tuple field keys
- `test_missing_value_proportions`: Tests missing value proportions maintenance
- `test_edge_case_all_same_values`: Tests edge case where all values are identical
- `test_edge_case_target_larger_than_data`: Tests edge case where target exceeds available data

**Extreme Edge Cases Tests (19 tests):**
- `test_extreme_case_single_row_data`: Tests single row data handling
- `test_extreme_case_very_large_tolerance`: Tests very large tolerance values (0.9)
- `test_extreme_case_zero_tolerance`: Tests zero tolerance with perfect proportions
- `test_extreme_case_all_missing_values`: Tests all missing values scenario
- `test_extreme_case_no_missing_values`: Tests no missing values scenario
- `test_extreme_case_very_small_target`: Tests very small target rows (1 row)
- `test_extreme_case_huge_data_small_target`: Tests large dataset with small target
- `test_extreme_case_many_unique_values`: Tests many unique values (each appears once)
- `test_extreme_case_complex_field_combinations`: Tests complex multi-field combinations
- `test_extreme_case_mixed_data_types`: Tests mixed data types (int, string, float, None, bool)
- `test_extreme_case_empty_field_proportions_list`: Tests empty field proportions list
- `test_extreme_case_duplicate_field_rules`: Tests duplicate field rules handling
- `test_extreme_case_very_unbalanced_data`: Tests very unbalanced data (99% vs 1%)
- `test_extreme_case_numerical_precision`: Tests numerical precision issues with small tolerance
- `test_extreme_case_unicode_and_special_characters`: Tests unicode and special characters
- `test_extreme_case_datetime_objects`: Tests datetime objects as field values
- `test_extreme_case_large_string_values`: Tests very large string values (1000+ chars)
- `test_extreme_case_nested_tuple_combinations`: Tests deeply nested tuple combinations (5 fields)
- `test_apply_without_target_rows_should_fail`: Tests that apply without target_rows parameter fails appropriately

**Architecture Integration:**
- Field proportions constrainer now follows the unified Constrainer architecture
- Target rows are provided by the main Constrainer during resampling process
- Removed date name mapping functionality for simplified configuration
- All tests updated to reflect the new parameter passing mechanism

> **Total Constrainer Tests**: 97 tests across 5 test files covering comprehensive constraint functionality including factory pattern implementation, NaN group handling, field-level constraints, field combination rules, and field proportion maintenance with extensive edge case coverage and integration testing.

## Data Evaluating

### `Evaluator`

#### `SDMetrics`

> tests/evaluator/test_sdmetrics.py

Tests for SDMetrics single-table evaluation functionality:

- `test_eval_diagnostic_report`: Tests DiagnosticReport evaluation with mocked SDMetrics components
- `test_eval_quality_report`: Tests QualityReport evaluation with comprehensive mock setup
- `test_init`: Tests SDMetricsSingleTable initialization and configuration validation
- `test_invalid_method`: Tests error handling for unsupported evaluation methods

**Key Features:**
- **Data Type Consistency**: Enhanced BaseEvaluator now detects data type mismatches between datasets and provides clear error messages instead of automatic type alignment
- **Error Handling**: Improved error messaging directs users to handle type alignment at the Executor level
- **Mock Integration**: Comprehensive mocking of SDMetrics components for reliable testing

> **Architecture Enhancement**: BaseEvaluator has been modified to remove automatic data type alignment functionality. Instead of silently "fixing" type mismatches, it now raises ValueError with detailed mismatch information, ensuring Data Structure evaluation accuracy and maintaining data integrity.

#### `Stats`

> tests/evaluator/test_stats.py

Tests for statistical evaluation functionality:

- `test_eval_basic`: Tests basic statistical evaluation with mocked field metadata creation
- `test_eval_with_different_data`: Tests evaluation with different original and synthetic datasets
- `test_init`: Tests Stats evaluator initialization and configuration validation
- `test_invalid_compare_method`: Tests error handling for invalid comparison methods
- `test_invalid_stats_method`: Tests error handling for invalid statistical methods

**Key Features:**
- **Metadater Integration**: Updated to use `Metadater.create_field` for field metadata creation
- **Type Inference**: Proper handling of data type inference through mocked field metadata
- **Configuration Validation**: Comprehensive validation of statistical method configurations

#### `CustomEvaluator`

> tests/evaluator/test_custom_evaluator.py

Tests for custom evaluator functionality:

- `test_init`: Tests CustomEvaluator initialization with external module loading
- `test_eval`: Tests evaluation method execution with custom evaluator instances
- `test_missing_module_path`: Tests error handling for missing module path configuration

**Key Features:**
- **External Module Loading**: Integration with `petsard.utils.load_external_module` for dynamic evaluator loading
- **Mock Integration**: Comprehensive mocking of external module loading and custom evaluator execution
- **Error Handling**: Proper validation of module path and class name requirements

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

Tests for the main Reporter functionality with **functional design architecture**:

- `test_method`: Tests Reporter initialization with different methods:
  - ReporterSaveData for 'save_data' method
  - ReporterSaveReport for 'save_report' method
  - ReporterSaveTiming for 'save_timing' method
  - UnsupportedMethodError for invalid methods
- `test_method_save_data`: Tests save_data method validation:
  - ConfigError when no source is provided
- `test_method_save_report`: Tests save_report method validation:
  - Valid initialization with granularity only
  - ConfigError when required parameters are missing
- `test_method_save_timing`: Tests save_timing method validation:
  - Valid initialization with optional parameters
  - Proper handling of time_unit and module filtering

#### `ReporterSaveData`

Tests for data saving functionality with functional design:

- `test_source`: Tests source parameter validation:
  - String and list of strings are accepted
  - ConfigError for invalid types (float, mixed list, tuple)
- `test_functional_create_and_report`: Tests functional "throw out and throw back in" pattern:
  - `create()` processes data without storing in instance variables
  - `report()` receives processed data and generates output files
  - No internal state maintained between calls

#### `ReporterSaveReport`

Tests for report generation functionality with **multi-granularity support**:

- `test_granularity`: Tests granularity parameter validation:
  - **Single granularity**: 'global', 'columnwise', 'pairwise', 'details', 'tree'
  - **Multi-granularity**: ['global', 'columnwise'], ['details', 'tree']
  - ConfigError for missing or invalid granularity
  - ConfigError for non-string/non-list types
- `test_multi_granularity_support`: Tests multi-granularity functionality:
  - Processing multiple granularities in single operation
  - Separate report generation for each granularity
  - Proper handling of granularity-specific data structures
- `test_new_granularity_types`: Tests new granularity types (v2.0+):
  - 'details': Detailed breakdown with additional metrics
  - 'tree': Hierarchical tree structure analysis
- `test_eval`: Tests eval parameter validation:
  - String, list of strings, or None are accepted
  - ConfigError for invalid types
- `test_create`: Tests functional report creation for all granularities:
  - Global granularity report generation
  - Columnwise granularity report generation
  - Pairwise granularity report generation
  - Details granularity report generation
  - Tree granularity report generation
  - Multi-granularity processing
- `test_functional_design_pattern`: Tests functional "throw out and throw back in" pattern:
  - `create()` returns processed data without storing internally
  - `report()` accepts processed data and generates files
  - Memory optimization through stateless design
- `test_process_report_data`: Tests data processing functionality:
  - Column renaming with eval name prefixes
  - Index handling for different granularities
  - Skip flag for non-Evaluator/Describer modules
- `test_safe_merge`: Tests DataFrame merging functionality:
  - Pure data merging with overlapping columns
  - Processed data merging for all granularities
  - Proper handling of common columns including 'column', 'column1', 'column2'
  - Correct row ordering in merged results

#### `ReporterSaveTiming`

Tests for timing information reporting functionality:

- `test_timing_data_processing`: Tests timing data processing:
  - Time unit conversion (seconds, minutes, hours, days)
  - Module filtering functionality
  - Timing metadata extraction
- `test_functional_timing_workflow`: Tests functional timing workflow:
  - Processing timing data without internal storage
  - Generating timing reports with proper formatting

#### `Reporter Utils`

Tests for utility functions:

- `test_convert_full_expt_tuple_to_name`: Tests experiment tuple to name conversion
- `test_convert_full_expt_name_to_tuple`: Tests experiment name to tuple conversion
- `test_convert_eval_expt_name_to_tuple`: Tests evaluation experiment name parsing

> **Functional Design Architecture**: Reporter has been completely refactored to use a functional "throw out and throw back in" design pattern for memory optimization. The `create()` method processes data but doesn't store it in instance variables (`self.result`, `self._processed_data`), while `report()` receives the processed data and generates output files. This stateless approach significantly reduces memory consumption while maintaining full backward compatibility.

> **Multi-Granularity Support**: Reporter now supports both single granularity (`str`) and multi-granularity (`list[str]`) configurations, allowing users to process multiple granularities in a single operation. New granularity types 'details' and 'tree' have been added alongside the traditional 'global', 'columnwise', and 'pairwise' options.

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