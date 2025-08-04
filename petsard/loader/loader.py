import logging
import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import yaml

from petsard.config_base import BaseConfig
from petsard.exceptions import (
    BenchmarkDatasetsError,
    ConfigError,
    UnableToFollowMetadataError,
    UnsupportedMethodError,
)
from petsard.loader.benchmarker import BenchmarkerConfig, BenchmarkerRequests
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
        schema (SchemaConfig): Schema configuration object with field definitions and global parameters.
        schema_path (str): The path to schema file if loaded from YAML file.
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
    schema: SchemaConfig | None = None
    schema_path: str | None = None  # 記錄 schema 來源路徑（如果從檔案載入）

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

        # 5. validate schema parameter and check for conflicts
        if self.schema is not None:
            self._logger.debug("Schema configuration provided")
            # SchemaConfig validation is handled by its own dataclass validation
            self._logger.debug("Schema configuration validation passed")

            # Check for conflicts between schema and column_types
            if self.column_types is not None:
                self._logger.debug(
                    "Checking for conflicts between schema and column_types"
                )
                # Use hasattr to avoid depending on schema internal structure
                if hasattr(self.schema, "fields") and self.schema.fields:
                    schema_fields = set(self.schema.fields.keys())
                    column_type_fields = set()
                    for columns in self.column_types.values():
                        column_type_fields.update(columns)

                    conflicting_fields = schema_fields.intersection(column_type_fields)
                    if conflicting_fields:
                        error_msg = (
                            f"Conflict detected: Fields {list(conflicting_fields)} are defined in both "
                            f"schema and column_types. Please use only schema for these fields."
                        )
                        self._logger.error(error_msg)
                        raise ConfigError(error_msg)
                    self._logger.debug(
                        "No conflicts found between schema and column_types"
                    )


class Loader:
    """
    The Loader class is responsible for creating and configuring a data loader,
    as well as retrieving and processing data from the specified sources.

    The Loader is designed to be passive and focuses on four core functions:
    1. Benchmark handling: Download benchmark datasets when needed
    2. Schema processing: Pass schema parameters to metadater for validation
    3. Legacy compatibility: Update legacy column_types and na_values to schema
    4. Data reading: Use pandas reader module to load data with proper configuration
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
        schema: SchemaConfig | dict | str | None = None,
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
            schema (SchemaConfig | dict | str, optional): Schema configuration.
                Can be one of:
                - SchemaConfig object: Direct schema configuration
                - dict: Dictionary that will be converted to SchemaConfig using from_dict()
                - str: Path to YAML file containing schema configuration
                Contains field definitions and global parameters for data processing.

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

        # Process schema parameter - handle different input types
        processed_schema, schema_path = self._process_schema_parameter(schema)

        self.config: LoaderConfig = LoaderConfig(
            filepath=filepath,
            method=method,
            column_types=column_types,
            header_names=header_names,
            na_values=na_values,
            schema=processed_schema,
            schema_path=schema_path,
        )
        self._logger.debug("LoaderConfig successfully initialized")

    def _process_schema_parameter(
        self, schema: SchemaConfig | dict | str | None
    ) -> tuple[SchemaConfig | None, str | None]:
        """
        Process schema parameter and convert it to SchemaConfig object.

        Args:
            schema: Schema parameter that can be SchemaConfig, dict, str (path), or None

        Returns:
            tuple: (processed_schema, schema_path)
                - processed_schema: SchemaConfig object or None
                - schema_path: Path to schema file if loaded from file, None otherwise
        """
        if schema is None:
            self._logger.debug("No schema provided")
            return None, None

        if isinstance(schema, SchemaConfig):
            self._logger.debug("Schema provided as SchemaConfig object")
            return schema, None

        if isinstance(schema, dict):
            self._logger.debug(
                "Schema provided as dictionary, converting to SchemaConfig"
            )
            try:
                # Ensure schema_id is present - generate one if missing
                schema_dict = schema.copy()
                if "schema_id" not in schema_dict:
                    schema_dict["schema_id"] = "auto_generated_schema"
                    self._logger.debug("Auto-generated schema_id for dictionary schema")

                schema_config = SchemaConfig.from_dict(schema_dict)
                return schema_config, None
            except Exception as e:
                error_msg = f"Failed to convert dictionary to SchemaConfig: {str(e)}"
                self._logger.error(error_msg)
                raise ConfigError(error_msg) from e

        if isinstance(schema, str):
            self._logger.info(f"Loading schema from YAML file: {schema}")
            try:
                schema_path = Path(schema)
                if not schema_path.exists():
                    error_msg = f"Schema file not found: {schema}"
                    self._logger.error(error_msg)
                    raise ConfigError(error_msg)

                with open(schema_path, encoding="utf-8") as f:
                    schema_dict = yaml.safe_load(f)

                if not isinstance(schema_dict, dict):
                    error_msg = f"Schema file must contain a dictionary, got {type(schema_dict)}"
                    self._logger.error(error_msg)
                    raise ConfigError(error_msg)

                # Ensure schema_id is present - generate one if missing
                if "schema_id" not in schema_dict:
                    # Use filename (without extension) as schema_id
                    schema_dict["schema_id"] = schema_path.stem
                    self._logger.debug(
                        f"Auto-generated schema_id from filename: {schema_path.stem}"
                    )

                schema_config = SchemaConfig.from_dict(schema_dict)
                self._logger.debug(f"Successfully loaded schema from {schema}")
                return schema_config, str(schema_path)

            except yaml.YAMLError as e:
                error_msg = f"Failed to parse YAML file {schema}: {str(e)}"
                self._logger.error(error_msg)
                raise ConfigError(error_msg) from e
            except Exception as e:
                error_msg = f"Failed to load schema from file {schema}: {str(e)}"
                self._logger.error(error_msg)
                raise ConfigError(error_msg) from e

        error_msg = f"Unsupported schema type: {type(schema)}"
        self._logger.error(error_msg)
        raise ConfigError(error_msg)

    def load(self) -> tuple[pd.DataFrame, SchemaMetadata]:
        """
        Load data from the specified file path.

        This method implements four core functions:
        1. Benchmark handling: Download benchmark datasets when needed
        2. Schema processing: Merge legacy parameters into schema and validate
        3. Data reading: Use pandas reader module for file loading
        4. Metadater integration: Pass schema to metadater for processing

        Returns:
            data (pd.DataFrame): Data been loaded
            schema (SchemaMetadata): Schema metadata of the data
        """
        self._logger.info(f"Loading data from {self.config.filepath}")

        # 1: Benchmark handling
        if self.config.benchmarker_config:
            self._handle_benchmark_download()

        # 2: Schema processing - merge legacy parameters into schema
        merged_schema_config = self._merge_legacy_to_schema()

        # 3: Data reading using pandas reader module
        data = self._read_data_with_pandas_reader(merged_schema_config)

        # 4: Pass schema to metadater for validation and processing
        schema_metadata = self._process_with_metadater(data, merged_schema_config)

        self._logger.info("Data loading completed successfully")
        return data, schema_metadata

    def _handle_benchmark_download(self):
        """Handle benchmark dataset download."""
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

    def _merge_legacy_to_schema(self) -> SchemaConfig:
        """
        Merge legacy column_types and na_values into SchemaConfig.

        Returns:
            SchemaConfig: Merged schema configuration
        """
        # Start with existing schema or create a new one
        if self.config.schema:
            # Use existing schema as base - avoid accessing internal structure
            self._logger.debug("Using existing schema configuration")
            return self.config.schema
        else:
            # Create new schema_config with defaults
            fields_config = {}
            schema_config_params = {
                "schema_id": self.config.file_name or "default_schema",
                "name": self.config.base_name or "default_schema",
                "description": None,
                "fields": fields_config,
                "compute_stats": True,
                "infer_logical_types": False,
                "optimize_dtypes": True,
                "sample_size": None,
                "leading_zeros": "never",
                "nullable_int": "force",
                "properties": {},
            }

            # Merge legacy column_types
            if self.config.column_types:
                self._logger.debug(
                    f"Merging legacy column_types: {self.config.column_types}"
                )
                for col_type, columns in self.config.column_types.items():
                    for col in columns:
                        if col not in fields_config:
                            fields_config[col] = FieldConfig()
                        # Update the field config with the column type
                        field_params = {
                            "type": col_type,
                            "na_values": fields_config[col].na_values,
                            "precision": fields_config[col].precision,
                            "category": fields_config[col].category,
                            "category_method": fields_config[col].category_method,
                            "datetime_precision": fields_config[col].datetime_precision,
                            "datetime_format": fields_config[col].datetime_format,
                            "logical_type": fields_config[col].logical_type,
                            "leading_zeros": fields_config[col].leading_zeros,
                        }
                        fields_config[col] = FieldConfig(**field_params)

            # Merge legacy na_values
            if self.config.na_values:
                self._logger.debug(f"Merging legacy na_values: {self.config.na_values}")
                if isinstance(self.config.na_values, dict):
                    # Column-specific na_values
                    for col, na_val in self.config.na_values.items():
                        if col not in fields_config:
                            fields_config[col] = FieldConfig()
                        # Update the field config with na_values
                        field_params = {
                            "type": fields_config[col].type,
                            "na_values": na_val,
                            "precision": fields_config[col].precision,
                            "category": fields_config[col].category,
                            "category_method": fields_config[col].category_method,
                            "datetime_precision": fields_config[col].datetime_precision,
                            "datetime_format": fields_config[col].datetime_format,
                            "logical_type": fields_config[col].logical_type,
                            "leading_zeros": fields_config[col].leading_zeros,
                        }
                        fields_config[col] = FieldConfig(**field_params)
                else:
                    # Global na_values - store in properties for now
                    schema_config_params["properties"]["global_na_values"] = (
                        self.config.na_values
                    )

            # Update fields in schema_config_params
            schema_config_params["fields"] = fields_config

            merged_schema_config = SchemaConfig(**schema_config_params)
            self._logger.debug("Created merged schema config")
            return merged_schema_config

    def _read_data_with_pandas_reader(
        self, schema_config: SchemaConfig
    ) -> pd.DataFrame:
        """
        Read data using the pandas loader classes.

        Args:
            schema_config: Merged schema configuration

        Returns:
            pd.DataFrame: Loaded dataframe
        """
        from petsard.loader.loader_pandas import LoaderPandasCsv, LoaderPandasExcel

        self._logger.info("Reading data using pandas loader classes")

        # Map file extension codes to loader classes
        loaders_map = {
            LoaderFileExt.CSVTYPE: LoaderPandasCsv,
            LoaderFileExt.EXCELTYPE: LoaderPandasExcel,
        }

        if self.config.file_ext_code not in loaders_map:
            error_msg = f"Unsupported file extension code: {self.config.file_ext_code}"
            self._logger.error(error_msg)
            raise UnsupportedMethodError(error_msg)

        loader_class = loaders_map[self.config.file_ext_code]

        # Build configuration for the loader
        config = {
            "filepath": str(self.config.filepath),
            "header_names": self.config.header_names,
        }

        # Handle legacy na_values (takes precedence over schema na_values for backward compatibility)
        if self.config.na_values is not None:
            config["na_values"] = self.config.na_values
            self._logger.debug(f"Using legacy na_values: {self.config.na_values}")

        # Handle legacy column_types for dtype parameter
        dtype_dict = {}
        if self.config.column_types and "category" in self.config.column_types:
            category_columns = self.config.column_types["category"]
            if isinstance(category_columns, list) and category_columns:
                self._logger.debug(
                    f"Setting category columns to string type: {category_columns}"
                )
                for col in category_columns:
                    dtype_dict[col] = str

        # Handle schema-based dtype configuration
        if schema_config and hasattr(schema_config, "fields") and schema_config.fields:
            for field_name, field_config in schema_config.fields.items():
                if hasattr(field_config, "type") and field_config.type:
                    field_type = field_config.type
                    # Map schema types to pandas dtypes
                    if field_type == "str":
                        dtype_dict[field_name] = str
                    elif field_type == "int":
                        # Use object type for int to handle NA values properly
                        dtype_dict[field_name] = "Int64"
                    elif field_type == "float":
                        dtype_dict[field_name] = float
                    elif field_type == "bool":
                        dtype_dict[field_name] = "boolean"
                    # datetime will be handled post-loading

        # Only add dtype parameter if we have dtype specifications
        if dtype_dict:
            config["dtype"] = dtype_dict
            self._logger.debug(f"Using dtype configuration: {dtype_dict}")

        # Handle schema-based na_values (only if legacy na_values not provided)
        if (
            self.config.na_values is None
            and schema_config
            and hasattr(schema_config, "fields")
            and schema_config.fields
        ):
            na_values_dict = {}
            for field_name, field_config in schema_config.fields.items():
                if (
                    hasattr(field_config, "na_values")
                    and field_config.na_values is not None
                ):
                    na_values_dict[field_name] = field_config.na_values
            if na_values_dict:
                config["na_values"] = na_values_dict
                self._logger.debug(f"Using schema-based na_values: {na_values_dict}")

        try:
            # Create loader instance and load data
            loader = loader_class(config)
            data = loader.load().fillna(pd.NA)
            self._logger.info(f"Successfully loaded data with shape: {data.shape}")
            return data

        except Exception as e:
            error_msg = f"Failed to load data from {self.config.filepath}: {str(e)}"
            self._logger.error(error_msg)
            raise UnableToFollowMetadataError(error_msg) from e

    def _process_with_metadater(
        self, data: pd.DataFrame, schema_config: SchemaConfig
    ) -> SchemaMetadata:
        """
        Process data and schema with metadater.

        Args:
            data: Loaded dataframe
            schema_config: Merged schema configuration

        Returns:
            SchemaMetadata: Schema metadata
        """
        self._logger.info("Processing with metadater")

        # Build schema metadata using Metadater with the SchemaConfig directly
        try:
            # Get schema_id safely without depending on internal structure
            schema_id = getattr(schema_config, "schema_id", "default_schema")
            schema_metadata: SchemaMetadata = Metadater.create_schema(
                dataframe=data, schema_id=schema_id, config=schema_config
            )
            self._logger.debug("Built schema metadata successfully")
        except Exception as e:
            error_msg = f"Failed to build schema metadata: {str(e)}"
            self._logger.error(error_msg)
            raise UnableToFollowMetadataError(error_msg) from e

        # Apply schema transformations
        try:
            from petsard.metadater.schema.schema_functions import (
                apply_schema_transformations,
            )

            data = apply_schema_transformations(
                data=data,
                schema=schema_metadata,
                include_fields=None,
                exclude_fields=None,
            )
            self._logger.debug("Schema transformations applied successfully")
        except Exception as e:
            error_msg = f"Failed to apply schema transformations: {str(e)}"
            self._logger.error(error_msg)
            raise UnableToFollowMetadataError(error_msg) from e

        return schema_metadata
