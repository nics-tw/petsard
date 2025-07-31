import logging
import re
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from petsard.config_base import BaseConfig
from petsard.exceptions import (
    BenchmarkDatasetsError,
    ConfigError,
    UnableToFollowMetadataError,
    UnableToLoadError,
    UnsupportedMethodError,
)
from petsard.loader.benchmarker import BenchmarkerRequests
from petsard.metadater import FieldConfig, Metadater, SchemaConfig, SchemaMetadata


class LoaderFileExt:
    """
    Mapping of File extension.
    """

    CSVTYPE: int = 1
    EXCELTYPE: int = 2

    CSV: int = 10
    XLS: int = 20
    XLSX: int = 21
    XLSM: int = 22
    XLSB: int = 23
    ODF: int = 24
    ODS: int = 25
    ODT: int = 26

    @classmethod
    def get(cls, file_ext: str) -> int:
        """
        Get suffixes mapping int value of file extension.

        Args:
            file_ext (str): File extension
        """
        return cls.__dict__[file_ext[1:].upper()] // 10


@dataclass
class BenchmarkerConfig(BaseConfig):
    """
    Configuration for the benchmarker.

    Attributes:
        _logger (logging.Logger): The logger object.
        YAML_FILENAME (str): The benchmark datasets YAML filename.
        benchmark_name (str): The benchmark name.
        benchmark_filename (str): The benchmark filename.
        benchmark_access (str): The benchmark access type.
        benchmark_region_name (str): The benchmark region name.
        benchmark_bucket_name (str): The benchmark bucket name.
        benchmark_sha256 (str): The benchmark SHA-256 value.
        filepath_raw (str): The raw file path.
    """

    YAML_FILENAME: str = "benchmark_datasets.yaml"

    benchmark_name: str | None = None
    benchmark_filename: str | None = None
    benchmark_access: str | None = None
    benchmark_region_name: str | None = None
    benchmark_bucket_name: str | None = None
    benchmark_sha256: str | None = None
    filepath_raw: str | None = None

    def __post_init__(self):
        super().__post_init__()
        self._logger.debug("Initializing BenchmarkerConfig")

        if not self.benchmark_name:
            error_msg = "benchmark_name must be specified for BenchmarkerConfig"
            self._logger.error(error_msg)
            raise ConfigError(error_msg)

        # Load and organize yaml: BENCHMARK_CONFIG
        self._logger.info("Loading benchmark configuration")
        benchmark_config: dict = self._load_benchmark_config()

        # Check if benchmark name exists in BENCHMARK_CONFIG
        if self.benchmark_name not in benchmark_config:
            error_msg = f"Benchmark dataset {self.benchmark_name} is not supported"
            self._logger.error(error_msg)
            raise UnsupportedMethodError(error_msg)

        benchmark_value: dict = benchmark_config[self.benchmark_name]
        self._logger.debug(f"Found benchmark configuration for {self.benchmark_name}")

        self.benchmark_filename = benchmark_value["filename"]

        if benchmark_value["access"] != "public":
            error_msg = (
                f"Benchmark access type {benchmark_value['access']} is not supported"
            )
            self._logger.error(error_msg)
            raise UnsupportedMethodError(error_msg)

        self.benchmark_access = benchmark_value["access"]
        self.benchmark_region_name = benchmark_value["region_name"]
        self.benchmark_bucket_name = benchmark_value["bucket_name"]
        self.benchmark_sha256 = benchmark_value["sha256"]
        self._logger.info(
            f"Configured benchmark dataset: {self.benchmark_name}, filename: {self.benchmark_filename}"
        )

    def _load_benchmark_config(self) -> dict:
        """
        Load benchmark datasets configuration.

        Return:
            config (dict):
                key (str): benchmark dataset name
                    filename (str): Its filename
                    access (str): Belong to public or private bucket.
                    region_name (str): Its AWS S3 region.
                    bucket_name (str): Its AWS S3 bucket.
                    sha256 (str): Its SHA-256 value.
        """
        self._logger.debug(f"Loading benchmark configuration from {self.YAML_FILENAME}")

        config: dict = {}
        error_msg: str = ""

        try:
            with resources.open_text("petsard.loader", self.YAML_FILENAME) as file:
                config = yaml.safe_load(file)
                self._logger.debug("Successfully loaded benchmark YAML configuration")
        except Exception as e:
            error_msg = f"Failed to load benchmark configuration: {str(e)}"
            self._logger.error(error_msg)
            raise BenchmarkDatasetsError(error_msg) from e

        REGION_NAME = config["region_name"]
        BUCKET_NAME = config["bucket_name"]

        config["datasets"] = {
            key: {
                "filename": value["filename"],
                "access": value["access"],
                "region_name": REGION_NAME,
                "bucket_name": BUCKET_NAME[value["access"]],
                "sha256": value["sha256"],
            }
            for key, value in config["datasets"].items()
        }

        self._logger.debug(f"Processed {len(config['datasets'])} benchmark datasets")
        return config["datasets"]

    def get_benchmarker_config(self) -> dict:
        """
        Get configuration dictionary for BenchmarkerRequests.

        Returns:
            dict: Configuration dictionary with required keys for BenchmarkerRequests
        """
        return {
            "benchmark_filename": self.benchmark_filename,
            "benchmark_bucket_name": self.benchmark_bucket_name,
            "benchmark_sha256": self.benchmark_sha256,
            "filepath": Path("benchmark").joinpath(self.benchmark_filename),
        }


@dataclass
class LoaderConfig(BaseConfig):
    """
    Configuration for the data loader.

    Attributes:
        _logger (logging.Logger): The logger object.
        DEFAULT_METHOD_FILEPATH (str): The default method filepath.
        filepath (str): The fullpath of dataset.
        method (str): The method of Loader.
        column_types (dict): The dictionary of column types and their corresponding column names.
        header_names (list): Specifies a list of headers for the data without header.
        na_values (str | list | dict): Extra string to recognized as NA/NaN.
        schema (dict): Field schema configuration with type, na_values, and precision.
        dir_name (str): The directory name of the file path.
        base_name (str): The base name of the file path.
        file_name (str): The file name of the file path.
        file_ext (str): The file extension of the file path.
        file_ext_code (int): The file extension code.
        benchmarker_config (BenchmarkerConfig): Optional benchmarker configuration.
    """

    DEFAULT_METHOD_FILEPATH: str = "benchmark://adult-income"

    filepath: str | None = None
    method: str | None = None
    column_types: dict[str, list[str]] | None = (
        None  # TODO: Deprecated in v2.0.0 - will be removed
    )
    header_names: list[str] | None = None
    na_values: str | list[str] | dict[str, str] | None = (
        None  # TODO: Deprecated in v2.0.0 - will be removed
    )
    schema: dict[str, dict[str, Any]] | None = None

    # Filepath related
    dir_name: str | None = None
    base_name: str | None = None
    file_name: str | None = None
    file_ext: str | None = None
    file_ext_code: int | None = None

    # Benchmarker configuration
    benchmarker_config: BenchmarkerConfig | None = None

    def __post_init__(self):
        super().__post_init__()
        self._logger.debug("Initializing LoaderConfig")
        error_msg: str = ""

        # 1. set default method if method = 'default'
        if self.filepath is None and self.method is None:
            error_msg = "filepath or method must be specified"
            self._logger.error(error_msg)
            raise ConfigError(error_msg)
        elif self.method:
            if self.method.lower() == "default":
                # default will use adult-income
                self._logger.info("Using default method: adult-income")
                self.filepath = self.DEFAULT_METHOD_FILEPATH
            else:
                error_msg = f"Unsupported method: {self.method}"
                self._logger.error(error_msg)
                raise UnsupportedMethodError(error_msg)

        # 2. check if filepath is specified as a benchmark
        if self.filepath.lower().startswith("benchmark://"):
            self._logger.info(f"Detected benchmark filepath: {self.filepath}")
            benchmark_name = re.sub(
                r"^benchmark://", "", self.filepath, flags=re.IGNORECASE
            ).lower()
            self._logger.debug(f"Extracted benchmark name: {benchmark_name}")

            # Create BenchmarkerConfig
            self.benchmarker_config = BenchmarkerConfig(
                benchmark_name=benchmark_name, filepath_raw=self.filepath
            )

            # Update filepath to local benchmark path
            self.filepath = Path("benchmark").joinpath(
                self.benchmarker_config.benchmark_filename
            )
            self._logger.info(
                f"Configured benchmark dataset: {benchmark_name}, filepath: {self.filepath}"
            )

        # 3. handle filepath
        filepath_path: Path = Path(self.filepath)
        self.dir_name = str(filepath_path.parent)
        self.base_name = filepath_path.name
        self.file_name = filepath_path.stem
        self.file_ext = filepath_path.suffix.lower()
        try:
            self.file_ext_code = LoaderFileExt.get(self.file_ext)
        except KeyError as e:
            error_msg = f"Unsupported file extension: {self.file_ext}"
            self._logger.error(error_msg)
            raise UnsupportedMethodError(error_msg) from e
        self._logger.debug(
            f"File path information - dir: {self.dir_name}, name: {self.file_name}, ext: {self.file_ext}, ext code: {self.file_ext_code}"
        )

        # 4. validate column_types (using new Metadater architecture)
        if self.column_types is not None:
            self._logger.debug(f"Validating column types: {self.column_types}")
            valid_column_types = ["category", "datetime"]
            for col_type, columns in self.column_types.items():
                if col_type.lower() not in valid_column_types:
                    error_msg = f"Column type {col_type} on {columns} is not supported"
                    self._logger.error(error_msg)
                    raise UnsupportedMethodError(error_msg)
            self._logger.debug("Column types validation passed")

        # 5. validate schema parameter
        if self.schema is not None:
            self._logger.debug(f"Validating schema configuration: {self.schema}")
            if not isinstance(self.schema, dict):
                error_msg = "schema must be a dictionary"
                self._logger.error(error_msg)
                raise ConfigError(error_msg)

            for field_name, field_config in self.schema.items():
                if not isinstance(field_config, dict):
                    error_msg = f"schema['{field_name}'] must be a dictionary"
                    self._logger.error(error_msg)
                    raise ConfigError(error_msg)

                # Validate allowed keys
                allowed_keys = {"type", "na_values", "precision"}
                invalid_keys = set(field_config.keys()) - allowed_keys
                if invalid_keys:
                    error_msg = f"schema['{field_name}'] contains invalid keys: {invalid_keys}. Allowed keys: {allowed_keys}"
                    self._logger.error(error_msg)
                    raise ConfigError(error_msg)

                # Validate type
                if "type" in field_config:
                    if not isinstance(field_config["type"], str):
                        error_msg = f"schema['{field_name}']['type'] must be a string"
                        self._logger.error(error_msg)
                        raise ConfigError(error_msg)

                # Validate na_values
                if "na_values" in field_config:
                    na_values = field_config["na_values"]
                    if not isinstance(na_values, (str, list)):
                        error_msg = (
                            f"schema['{field_name}']['na_values'] must be str or list"
                        )
                        self._logger.error(error_msg)
                        raise ConfigError(error_msg)
                    if isinstance(na_values, list):
                        if not all(isinstance(val, str) for val in na_values):
                            error_msg = f"All values in schema['{field_name}']['na_values'] must be strings"
                            self._logger.error(error_msg)
                            raise ConfigError(error_msg)

                # Validate precision
                if "precision" in field_config:
                    precision = field_config["precision"]
                    if not isinstance(precision, int) or precision < 0:
                        error_msg = f"schema['{field_name}']['precision'] must be a non-negative integer"
                        self._logger.error(error_msg)
                        raise ConfigError(error_msg)

            self._logger.debug("Schema configuration validation passed")


class Loader:
    """
    The Loader class is responsible for creating and configuring a data loader,
    as well as retrieving and processing data from the specified sources.
    """

    def __init__(
        self,
        filepath: str = None,
        method: str = None,
        column_types: dict[str, list[str]] | None = None,  # TODO: Deprecated in v2.0.0
        header_names: list[str] | None = None,
        na_values: str
        | list[str]
        | dict[str, str]
        | None = None,  # TODO: Deprecated in v2.0.0
        schema: dict[str, dict[str, Any]] | None = None,
    ):
        """
        Args:
            filepath (str, optional): The fullpath of dataset.
            method (str, optional): The method of Loader.
                Default is None, indicating only filepath is specified.
            column_types (dict ,optional): **DEPRECATED in v2.0.0 - will be removed**
                The dictionary of column types and their corresponding column names,
                formatted as {type: [colname]}
                Only the following types are supported (case-insensitive):
                - 'category': The column(s) will be treated as categorical.
                - 'datetime': The column(s) will be treated as datetime.
                Default is None, indicating no custom column types will be applied.
            header_names (list ,optional):
                Specifies a list of headers for the data without header.
                Default is None, indicating no custom headers will be applied.
            na_values (str | list | dict ,optional): **DEPRECATED in v2.0.0 - will be removed**
                Extra string to recognized as NA/NaN.
                If dictionary passed, value will be specific per-column NA values.
                Format as {colname: na_values}.
                Default is None, means no extra.
                Check pandas document for Default NA string list.
            schema (dict, optional): Field schema configuration.
                Dictionary with field names as keys and configuration as values.
                Each field configuration can contain:
                - 'type': Data type hint (str)
                - 'na_values': Custom NA values for this field (str or list)
                - 'precision': Decimal precision for numeric fields (int)
                Example: {
                    'age': {'type': 'int', 'na_values': ['unknown', 'N/A']},
                    'salary': {'type': 'float', 'precision': 2}
                }

        Attributes:
            _logger (logging.Logger): The logger object.
            config (LoaderConfig): Configuration
        """
        self._logger: logging.Logger = logging.getLogger(
            f"PETsARD.{self.__class__.__name__}"
        )
        self._logger.info("Initializing Loader")
        self._logger.debug(
            f"Loader parameters - filepath: {filepath}, method: {method}, column_types: {column_types}"
        )

        self.config: LoaderConfig = LoaderConfig(
            filepath=filepath,
            method=method,
            column_types=column_types,
            header_names=header_names,
            na_values=na_values,
            schema=schema,
        )
        self._logger.debug("LoaderConfig successfully initialized")

    def load(self) -> tuple[pd.DataFrame, SchemaMetadata]:
        """
        Load data from the specified file path.

        Returns:
            data (pd.DataFrame): Data been loaded
            schema (SchemaMetadata): Schema schema of the data
        """
        self._logger.info(f"Loading data from {self.config.filepath}")
        error_msg: str = ""

        # 1. If set as load benchmark
        #    downloading benchmark dataset, and executing on local file.
        if self.config.benchmarker_config:
            self._logger.info(
                f"Downloading benchmark dataset: {self.config.benchmarker_config.benchmark_name}"
            )
            try:
                BenchmarkerRequests(
                    self.config.benchmarker_config.get_benchmarker_config()
                ).download()
                self._logger.debug("Benchmark dataset downloaded successfully")
            except Exception as e:
                error_msg = f"Failed to download benchmark dataset: {str(e)}"
                self._logger.error(error_msg)
                raise BenchmarkDatasetsError(error_msg) from e

        # 2. Setting loaders map by file extension and load data
        self._logger.info(f"Loading data using file extension: {self.config.file_ext}")
        loaders_map: dict[int, Any] = {
            LoaderFileExt.CSVTYPE: pd.read_csv,
            LoaderFileExt.EXCELTYPE: pd.read_excel,
        }

        # 2.5 Prepare dtype dictionary for category columns only
        dtype_dict = None
        if self.config.column_types and "category" in self.config.column_types:
            category_columns = self.config.column_types["category"]
            if isinstance(category_columns, list) and category_columns:
                dtype_dict = {}
                self._logger.debug(
                    f"Setting category columns to string type: {category_columns}"
                )
                for col in category_columns:
                    dtype_dict[col] = str

        try:
            if self.config.header_names:
                self._logger.debug(
                    f"Using custom header names: {self.config.header_names}"
                )
            else:
                self._logger.debug("Using inferred headers")

            # 載入資料
            load_params = {
                "header": 0 if self.config.header_names else "infer",
                "names": self.config.header_names,
                "na_values": self.config.na_values,
            }

            # 只有在有 dtype 設定時才加入 dtype 參數
            if dtype_dict:
                load_params["dtype"] = dtype_dict

            data: pd.DataFrame = loaders_map[self.config.file_ext_code](
                self.config.filepath, **load_params
            ).fillna(pd.NA)

            self._logger.info(f"Successfully loaded data with shape: {data.shape}")

        except Exception as e:
            error_msg = f"Failed to load data: {str(e)}"
            self._logger.error(error_msg)
            raise UnableToLoadError(error_msg) from e

        # 2.7 Apply schema transformations if specified
        if self.config.schema:
            self._logger.info("Applying schema transformations")
            from petsard.metadater.field.field_functions import (
                apply_field_transformations,
            )

            for field_name, field_config_dict in self.config.schema.items():
                if field_name in data.columns:
                    # Create FieldConfig for transformation
                    field_config_params = {}

                    if "type" in field_config_dict:
                        field_config_params["type_hint"] = field_config_dict["type"]

                    if "na_values" in field_config_dict:
                        field_config_params["na_values"] = field_config_dict[
                            "na_values"
                        ]

                    if "precision" in field_config_dict:
                        field_config_params["precision"] = field_config_dict[
                            "precision"
                        ]

                    field_config = FieldConfig(**field_config_params)

                    # Apply transformations to the field
                    try:
                        original_series = data[field_name]
                        transformed_series = apply_field_transformations(
                            original_series, field_config, field_name
                        )
                        data[field_name] = transformed_series
                        self._logger.debug(
                            f"Applied transformations to field '{field_name}'"
                        )
                    except Exception as e:
                        self._logger.warning(
                            f"Failed to apply transformations to field '{field_name}': {str(e)}"
                        )
                        # Continue with other fields even if one fails
                else:
                    self._logger.warning(
                        f"Field '{field_name}' specified in schema not found in data columns"
                    )

            self._logger.debug("Metadata transformations completed")

        # 3. Build schema configuration using new Metadater
        self._logger.info("Building schema configuration")

        # Create field configurations based on column_types and schema
        fields_config = {}

        # Handle legacy column_types (deprecated)
        if self.config.column_types:
            for col_type, columns in self.config.column_types.items():
                for col in columns:
                    # Create FieldConfig with type_hint directly since it's frozen
                    fields_config[col] = FieldConfig(type_hint=col_type)

        # Handle new schema parameter (takes precedence over column_types)
        if self.config.schema:
            self._logger.debug(
                f"Processing schema configuration for {len(self.config.schema)} fields"
            )
            for field_name, field_config_dict in self.config.schema.items():
                # Create FieldConfig from dictionary
                field_config_params = {}

                if "type" in field_config_dict:
                    field_config_params["type_hint"] = field_config_dict["type"]

                if "na_values" in field_config_dict:
                    field_config_params["na_values"] = field_config_dict["na_values"]

                if "precision" in field_config_dict:
                    field_config_params["precision"] = field_config_dict["precision"]

                fields_config[field_name] = FieldConfig(**field_config_params)
                self._logger.debug(
                    f"Created FieldConfig for '{field_name}': {field_config_params}"
                )

        # Create schema configuration - Metadater 使用自己的預設值
        schema_config = SchemaConfig(
            schema_id=self.config.file_name or "default_schema",
            name=self.config.base_name or "default Schema",
            fields=fields_config,
            compute_stats=True,
            infer_logical_types=True,
            optimize_dtypes=True,
        )

        # 4. Build schema schema using Metadater public API
        self._logger.info("Building schema schema from dataframe")
        try:
            schema: SchemaMetadata = Metadater.create_schema(
                dataframe=data, schema_id=schema_config.schema_id, config=schema_config
            )
            self._logger.debug(f"Built schema with {len(schema.fields)} fields")
        except Exception as e:
            error_msg = f"Failed to build schema schema: {str(e)}"
            self._logger.error(error_msg)
            raise UnableToFollowMetadataError(error_msg) from e

        # 5. Apply schema transformations using schema functions
        self._logger.info("Applying schema transformations to optimize data")
        try:
            from petsard.metadater.schema.schema_functions import (
                apply_schema_transformations,
            )

            data = apply_schema_transformations(
                data=data, schema=schema, include_fields=None, exclude_fields=None
            )
            self._logger.debug("Schema transformations applied successfully")
        except Exception as e:
            error_msg = f"Failed to apply schema transformations: {str(e)}"
            self._logger.error(error_msg)
            raise UnableToFollowMetadataError(error_msg) from e

        self._logger.info("Data loading completed successfully")
        return data, schema
