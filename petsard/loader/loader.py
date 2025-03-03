import re
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path
from typing import Optional, Union

import pandas as pd

import yaml
from petsard.config_base import BaseConfig
from petsard.exceptions import ConfigError, UnsupportedMethodError
from petsard.loader.benchmarker import BenchmarkerRequests
from petsard.loader.metadata import Metadata
from petsard.loader.util import casting_dataframe
from petsard.util import (
    ALLOWED_COLUMN_TYPES,
    optimize_dtypes,
)


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

        Raises:
            UnsupportedMethodError: If file extension is not supported
        """
        try:
            return cls.__dict__[file_ext[1:].upper()] // 10
        except KeyError:
            raise UnsupportedMethodError(f"File extension {file_ext} is not supported")


@dataclass
class LoaderConfig(BaseConfig):
    """
    Configuration for the data loader.
    """

    DEFAULT_METHOD_FILEPATH: str = "benchmark://adult-income"
    VALID_COLUMN_TYPES: list = field(default_factory=lambda: ["category", "datetime"])
    YAML_FILENAME: str = "benchmark_datasets.yaml"

    filepath: Optional[str] = None
    method: Optional[str] = None
    column_types: Optional[dict[str, list[str]]] = None
    dtype: Optional[dict[str, str]] = None
    header_names: Optional[list[str]] = None
    na_values: Optional[str | list[str] | dict[str, str]] = None

    # Filepath related
    dir_name: str = None
    base_name: str = None
    file_name: str = None
    file_ext: str = None
    file_ext_type: int = None

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
        # 1. set default method if method = 'default'
        if self.filepath is None and self.method is None:
            raise ConfigError("filepath or method must be specified")
        elif self.method:
            if self.method.lower() == "default":
                # default will use adult-income
                self.filepath = self.DEFAULT_METHOD_FILEPATH
            else:
                raise UnsupportedMethodError(f"Method {self.method} is not supported")

        # 2. check if filepath is specified as a benchmark
        if self.filepath.lower().startswith("benchmark://"):
            self.benchmark = True
            self.benchmark_name = re.sub(
                r"^benchmark://", "", self.filepath, flags=re.IGNORECASE
            ).lower()

        if self.benchmark:
            # 3. if benchmark, load and organized yaml: BENCHMARK_CONFIG
            benchmark_config: dict = self._load_benchmark_config()

            # 4. if benchmark name exist in BENCHMARK_CONFIG, update config with benchmark values
            if self.benchmark_name not in benchmark_config:
                raise UnsupportedMethodError(
                    f"Benchmark dataset {self.benchmark_name} is not supported"
                )
            benchmark_value: dict = benchmark_config[self.benchmark_name]
            self.filepath_raw = self.filepath
            self.filepath = Path("benchmark").joinpath(benchmark_value["filename"])
            self.benchmark_filename = benchmark_value["filename"]
            if benchmark_value["access"] != "public":
                raise UnsupportedMethodError(
                    f"Benchmark access type {benchmark_value['access']} is not supported"
                )
            self.benchmark_access = benchmark_value["access"]
            self.benchmark_region_name = benchmark_value["region_name"]
            self.benchmark_bucket_name = benchmark_value["bucket_name"]
            self.benchmark_sha256 = benchmark_value["sha256"]

        # 5. handle filepath
        filepath_path: Path = Path(self.filepath)
        self.dir_name = str(filepath_path.parent)
        self.base_name = filepath_path.name
        self.file_name = filepath_path.stem
        self.file_ext = filepath_path.suffix.lower()
        self.file_ext_type = LoaderFileExt.get(self.file_ext)

        # 6. validate column_types
        if self.column_types is not None:
            for col_type, columns in self.column_types.items():
                if col_type.lower() not in self.VALID_COLUMN_TYPES:
                    raise UnsupportedMethodError(
                        f"Column type {col_type} on {columns} is not supported"
                    )

    @classmethod
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
        config: dict = {}

        with resources.open_text("petsard.loader", self.YAML_FILENAME) as file:
            config = yaml.safe_load(file)

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

        return config["datasets"]


class Loader:
    """
    Unified data loader using dlt to handle various data sources and formats.
    Completely refactored version that doesn't rely on the old loader classes.
    """

    def __init__(
        self,
        filepath: str = None,
        method: str = None,
        column_types: Optional[dict[str, list[str]]] = None,
        header_names: Optional[list[str]] = None,
        na_values: Optional[Union[str, list[str], dict[str, str]]] = None,
    ):
        """
        Initialize the data loader.

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

        Attributes:
            config (LoaderConfig): Configuration
        """
        self.config: LoaderConfig = LoaderConfig(
            filepath=filepath,
            method=method,
            column_types=column_types,
            header_names=header_names,
            na_values=na_values,
        )

    @classmethod
    def _assign_str_dtype(
        cls, column_types: Optional[dict[str, list[str]]]
    ) -> dict[str, str]:
        """
        Force setting discrete and datetime columns been load as str at first.

        Args:
            column_types (dict):
                The dictionary of column names and their types as format.
                See __init__ for detail.
        Return:
            dtype (dict):
                dtype: particular columns been force assign as string
        """
        str_colname: list[str] = []
        for coltype in ALLOWED_COLUMN_TYPES:
            str_colname.extend(column_types.get(coltype, []))

        return {colname: "str" for colname in str_colname}

    def load(self) -> tuple[pd.DataFrame, Metadata]:
        """
        Load data from the specified file path.

        Returns:
            data (pd.DataFrame): Data been loaded
            metadata (Metadata): Metadata of the data
        """

        # 1. If set as load benchmark
        #    downloading benchmark dataset, and executing on local file.
        if self.config.benchmark:
            BenchmarkerRequests(self.config.get()).download()

        # 2. Setting self.loader as specified Loader class by file extension and load data
        loaders = {
            LoaderFileExt.CSVTYPE: pd.read_csv,
            LoaderFileExt.EXCELTYPE: pd.read_excel,
        }
        if self.config.header_names:
            data: pd.DataFrame = loaders[self.config.file_ext_type](
                self.config.filepath,
                header=0,
                names=self.config.header_names,
                na_values=self.config.na_values,
            )
        else:
            data: pd.DataFrame = loaders[self.config.file_ext_type](
                self.config.filepath,
                header="infer",
                na_values=self.config.na_values,
            )

        # 3. Optimizing dtype
        self.config.dtype = optimize_dtypes(
            data=data,
            column_types=self.config.column_types,
        )

        # 4. Casting data for more efficient storage space
        data = casting_dataframe(data, self.config.dtype)

        # 5. Setting metadata
        metadata: Metadata = Metadata()
        metadata.build_metadata(data=data)

        return data, metadata
