---
title: Test Coverage
type: docs
weight: 86
prev: docs/developer-guide/experiment-name-in-reporter
next: docs/developer-guide
---

## Data Loading

### `Loader`

> tests/loader/test_loader.py

Tests for the main Loader functionality:

- `test_loader_init_no_config`: Verifies initialization with no config raises NoConfigError
- `test_loader_init_with_filepath`: Tests initialization with file path, checks config path and extension are set correctly
- `test_handle_filepath_with_complex_name`: Tests various file path patterns including:
  - Path with multiple dots
  - Relative paths (./ and ../)
  - Absolute paths
  - Mixed case extensions
- `test_loader_init_with_column_types`: Verifies column type specifications are stored correctly in config
- `test_benchmark_loader`: Tests benchmark dataset loading functionality using mocked BenchmarkerRequests
- `test_load_csv`: Tests CSV file loading and metadata creation using a temporary test file
- `test_invalid_file_extension`: Verifies invalid file extensions raise UnsupportedMethodError
- `test_custom_na_values`: Tests handling of custom NA values in data loading

### `Benchmarker`

> tests/loader/test_benchmark.py

Tests for benchmark dataset handling:

- `test_basebenchmarker_init`: Verifies BaseBenchmarker cannot be instantiated as it's an abstract class
- `test_benchmarker_requests_init`: Tests BenchmarkerRequests initialization with mocked filesystem operations
- `test_download_success`: Tests successful download scenario with:
  - Mocked HTTP requests
  - Mocked file operations
  - SHA256 verification checks
- `test_verify_file_mismatch`: Tests SHA256 verification failure handling using mocked file content

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

## Data Generating

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