---
title: Test Coverage
type: docs
weight: 54
prev: docs/developer-guide/experiment-name-in-reporter
next: docs/developer-guide
sidebar:
  open: true
---

## Data Loading

### Loader

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

### Benchmark

> tests/loader/test_benchmark.py

Tests for benchmark dataset handling:

- `test_basebenchmarker_init`: Verifies BaseBenchmarker cannot be instantiated as it's an abstract class
- `test_benchmarker_requests_init`: Tests BenchmarkerRequests initialization with mocked filesystem operations
- `test_download_success`: Tests successful download scenario with:
  - Mocked HTTP requests
  - Mocked file operations
  - SHA256 verification checks
- `test_verify_file_mismatch`: Tests SHA256 verification failure handling using mocked file content

### Metadata

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

## Data Evaluating

### MLUtility

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