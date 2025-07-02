import logging
import re
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any, Optional, Union

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
class LoaderConfig(BaseConfig):
    """
    Configuration for the data loader.

    Attributes:
        _logger (logging.Logger): The logger object.
        DEFAULT_METHOD_FILEPATH (str): The default method filepath.
        YAML_FILENAME (str): The benchmark datasets YAML filename.
        filepath (str): The fullpath of dataset.
        method (str): The method of Loader.
        column_types (dict): The dictionary of column types and their corresponding column names.
        header_names (list): Specifies a list of headers for the data without header.
        na_values (str | list | dict): Extra string to recognized as NA/NaN.
        dir_name (str): The directory name of the file path.
        base_name (str): The base name of the file path.
        file_name (str): The file name of the file path.
        file_ext (str): The file extension of the file path.
        file_ext_code (int): The file extension code.
        benchmark (bool): The flag to indicate if the file path is a benchmark.
        filepath_raw (str): The raw file path.
        benchmark_name (str): The benchmark name.
        benchmark_filename (str): The benchmark filename.
        benchmark_access (str): The benchmark access type.
        benchmark_region_name (str): The benchmark region name.
        benchmark_bucket_name (str): The benchmark bucket name.
        benchmark_sha256 (str): The benchmark SHA-256 value.
    """

    DEFAULT_METHOD_FILEPATH: str = "benchmark://adult-income"
    YAML_FILENAME: str = "benchmark_datasets.yaml"

    filepath: Optional[str] = None
    method: Optional[str] = None
    column_types: Optional[dict[str, list[str]]] = None
    header_names: Optional[list[str]] = None
    na_values: Optional[Union[str, list[str], dict[str, str]]] = None

    # 新增：處理容易誤判、型別判斷模糊資料的參數
    preserve_raw_data: bool = False  # 是否保留原始資料格式，避免 pandas 自動類型推斷
    auto_detect_leading_zeros: bool = False  # 是否自動檢測前導零並保留為字串
    force_nullable_integers: bool = False  # 是否強制使用 nullable integers 避免 .0 後綴

    # Filepath related
    dir_name: Optional[str] = None
    base_name: Optional[str] = None
    file_name: Optional[str] = None
    file_ext: Optional[str] = None
    file_ext_code: Optional[int] = None

    # Benchmark related
    benchmark: bool = False
    filepath_raw: Optional[str] = None
    benchmark_name: Optional[str] = None
    benchmark_filename: Optional[str] = None
    benchmark_access: Optional[str] = None
    benchmark_region_name: Optional[str] = None
    benchmark_bucket_name: Optional[str] = None
    benchmark_sha256: Optional[str] = None

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
            self.benchmark = True
            self.benchmark_name = re.sub(
                r"^benchmark://", "", self.filepath, flags=re.IGNORECASE
            ).lower()
            self._logger.debug(f"Extracted benchmark name: {self.benchmark_name}")

        if self.benchmark:
            # 3. if benchmark, load and organized yaml: BENCHMARK_CONFIG
            self._logger.info("Loading benchmark configuration")
            benchmark_config: dict = self._load_benchmark_config()

            # 4. if benchmark name exist in BENCHMARK_CONFIG, update config with benchmark values
            if self.benchmark_name not in benchmark_config:
                error_msg = f"Benchmark dataset {self.benchmark_name} is not supported"
                self._logger.error(error_msg)
                raise UnsupportedMethodError(error_msg)

            benchmark_value: dict = benchmark_config[self.benchmark_name]
            self._logger.debug(
                f"Found benchmark configuration for {self.benchmark_name}"
            )
            self.filepath_raw = self.filepath
            self.filepath = Path("benchmark").joinpath(benchmark_value["filename"])
            self.benchmark_filename = benchmark_value["filename"]

            if benchmark_value["access"] != "public":
                error_msg = f"Benchmark access type {benchmark_value['access']} is not supported"
                self._logger.error(error_msg)
                raise UnsupportedMethodError(error_msg)

            self.benchmark_access = benchmark_value["access"]
            self.benchmark_region_name = benchmark_value["region_name"]
            self.benchmark_bucket_name = benchmark_value["bucket_name"]
            self.benchmark_sha256 = benchmark_value["sha256"]
            self._logger.info(
                f"Configured benchmark dataset: {self.benchmark_name}, filename: {self.benchmark_filename}"
            )

        # 5. handle filepath
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

        # 6. validate column_types (using new Metadater architecture)
        if self.column_types is not None:
            self._logger.debug(f"Validating column types: {self.column_types}")
            valid_column_types = ["category", "datetime"]
            for col_type, columns in self.column_types.items():
                if col_type.lower() not in valid_column_types:
                    error_msg = f"Column type {col_type} on {columns} is not supported"
                    self._logger.error(error_msg)
                    raise UnsupportedMethodError(error_msg)
            self._logger.debug("Column types validation passed")

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


class Loader:
    """
    The Loader class is responsible for creating and configuring a data loader,
    as well as retrieving and processing data from the specified sources.
    """

    def __init__(
        self,
        filepath: str = None,
        method: str = None,
        column_types: Optional[dict[str, list[str]]] = None,
        header_names: Optional[list[str]] = None,
        na_values: Optional[Union[str, list[str], dict[str, str]]] = None,
        preserve_raw_data: bool = False,
        auto_detect_leading_zeros: bool = False,
        force_nullable_integers: bool = False,
    ):
        """
        Args:
            filepath (str, optional): The fullpath of dataset.
            method (str, optional): The method of Loader.
                Default is None, indicating only filepath is specified.
            column_types (dict ,optional):
                The dictionary of column types and their corresponding column names,
                formatted as {type: [colname]}
                Only the following types are supported (case-insensitive):
                - 'category': The column(s) will be treated as categorical.
                - 'datetime': The column(s) will be treated as datetime.
                Default is None, indicating no custom column types will be applied.
            header_names (list ,optional):
                Specifies a list of headers for the data without header.
                Default is None, indicating no custom headers will be applied.
            na_values (str | list | dict ,optional):
                Extra string to recognized as NA/NaN.
                If dictionary passed, value will be specific per-column NA values.
                Format as {colname: na_values}.
                Default is None, means no extra.
                Check pandas document for Default NA string list.
            preserve_raw_data (bool, optional):
                Whether to preserve raw data format and avoid pandas automatic type inference.
                When True, all columns are initially loaded as object type to prevent misinterpretation.
                Useful for data with ambiguous types. Default is False.
            auto_detect_leading_zeros (bool, optional):
                Whether to automatically detect and preserve leading zeros in string data.
                Prevents codes like "001" from being converted to integer 1. Default is False.
            force_nullable_integers (bool, optional):
                Whether to force use of nullable integer types for integer data with missing values.
                Prevents integers with NaN from becoming floats with .0 suffixes. Default is False.

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
            preserve_raw_data=preserve_raw_data,
            auto_detect_leading_zeros=auto_detect_leading_zeros,
            force_nullable_integers=force_nullable_integers,
        )
        self._logger.debug("LoaderConfig successfully initialized")

    def load(self) -> tuple[pd.DataFrame, SchemaMetadata]:
        """
        Load data from the specified file path.

        Returns:
            data (pd.DataFrame): Data been loaded
            schema (SchemaMetadata): Schema metadata of the data
        """
        self._logger.info(f"Loading data from {self.config.filepath}")
        error_msg: str = ""

        # 1. If set as load benchmark
        #    downloading benchmark dataset, and executing on local file.
        if self.config.benchmark:
            self._logger.info(
                f"Downloading benchmark dataset: {self.config.benchmark_name}"
            )
            try:
                BenchmarkerRequests(self.config.get()).download()
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

        # 2.5 Prepare dtype dictionary based on configuration
        dtype_dict = {}

        if self.config.preserve_raw_data:
            # 當 preserve_raw_data=True 時，強制所有欄位為 object 類型
            # 這樣可以避免 pandas 自動類型推斷
            self._logger.debug(
                "Preserving raw data format - loading all columns as object type"
            )
            dtype_dict = "object"  # 這會讓所有欄位都載入為 object
        else:
            # 傳統模式：只對指定的 category 欄位設定類型
            if self.config.column_types and "category" in self.config.column_types:
                category_columns = self.config.column_types["category"]
                if isinstance(category_columns, list) and category_columns:
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

            if self.config.preserve_raw_data:
                self._logger.debug(
                    "Raw data preserved - all columns loaded as object type"
                )

        except Exception as e:
            error_msg = f"Failed to load data: {str(e)}"
            self._logger.error(error_msg)
            raise UnableToLoadError(error_msg) from e

        # 3. Build schema configuration using new Metadater
        self._logger.info("Building schema configuration")

        # Create field configurations based on column_types
        fields_config = {}
        if self.config.column_types:
            for col_type, columns in self.config.column_types.items():
                for col in columns:
                    # Create FieldConfig with type_hint directly since it's frozen
                    fields_config[col] = FieldConfig(type_hint=col_type)

        # Create schema configuration
        schema_config = SchemaConfig(
            schema_id=self.config.file_name or "default_schema",
            name=self.config.base_name or "default Schema",
            fields=fields_config,
            compute_stats=True,
            infer_logical_types=True,
            optimize_dtypes=True,
            # 傳遞新的配置參數
            auto_detect_leading_zeros=self.config.auto_detect_leading_zeros,
            force_nullable_integers=self.config.force_nullable_integers,
        )

        # 4. Build schema metadata using Metadater public API
        self._logger.info("Building schema metadata from dataframe")
        try:
            schema: SchemaMetadata = Metadater.create_schema(
                dataframe=data, schema_id=schema_config.schema_id, config=schema_config
            )
            self._logger.debug(f"Built schema with {len(schema.fields)} fields")
        except Exception as e:
            error_msg = f"Failed to build schema metadata: {str(e)}"
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
