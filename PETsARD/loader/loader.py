from importlib import resources
import pathlib
import re
from typing import (
    Dict,
    List,
    Optional,
    Union
)

import pandas as pd
import yaml

from PETsARD.loader.benchmark import (
    BenchmarkerBoto3,
    BenchmarkerRequests,
)
from PETsARD.loader.loader_pandas import (
    LoaderPandasCsv,
    LoaderPandasExcel,
)
from PETsARD.loader.metadata import Metadata
from PETsARD.loader.util import casting_dataframe
from PETsARD.util import (
    ALLOWED_COLUMN_TYPES,
    optimize_dtypes,
    verify_column_types,
)
from PETsARD.error import (
    ConfigError,
    NoConfigError,
    UnsupportedMethodError,
)


class LoaderFileExt():
    """
    Mapping of File extension.
    """
    CSVTYPE: int = 1
    EXCELTYPE: int = 2
    CSV:  int = 10
    XLS:  int = 20
    XLSX: int = 21
    XLSM: int = 22
    XLSB: int = 23
    ODF:  int = 24
    ODS:  int = 25
    ODT:  int = 26

    @classmethod
    def getext(cls, file_ext: str) -> int:
        """
        Get suffixes mapping int value of file extension.

        Args:
            file_ext (str): File extension
        """
        return cls.__dict__[file_ext[1:].upper()] // 10


class Loader:
    """
    Check the target file for the Loader,
        implement different Loader instances using a factory method,
        and read files with a module optimized for dtypes and storage.
    """

    def __init__(
        self,
        filepath: str = None,
        method: str = None,
        column_types: Optional[Dict[str, List[str]]] = None,
        header_names: Optional[List[str]] = None,
        na_values: Optional[Union[str, List[str], Dict[str, str]]] = None,
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

        Attr:
            config (dict): The dictionary of necessary information for Loader.
                    filepath (str): The fullpath of dataset.
                    method (str): The method of Loader.
                    file_ext (str): file extension of file_ext.
                    benchmark (bool): True if filepath is benchmark dataset.
                    dtypes (dict):
                        The dictionary of column names and their types as format.
                    column_types (dict, optional):
                        The dictionary of special column type and their column names.
                    header_names (list ,optional):
                        Specifies a list of headers for the data.
                    na_values (str | list | dict ,optional):
                        Extra string to recognized as NA/NaN.
                - from _handle_filepath(): only included if benchmark is True.
                    filepath_raw (str): Keep original filepath input by user.
                    benchmark_name (str): The name of benchmark dataset by user.
                    benchmark_filename (str): The filename of benchmark dataset.
                    benchmark_access (str): The access type of benchmark dataset.
                    benchmark_region_name (str): The Amazon region name of benchmark dataset.
                    benchmark_bucket_name (str): The Amazon bucket name of benchmark dataset.
                    benchmark_sha256 (str): The SHA-256 value of benchmark dataset.
            loader (LoaderPandasCsv | LoaderPandasExcel):
                The instance of LoaderPandasCsv or LoaderPandasExcel.
            data (pd.DataFrame): The dataset been loaded.
            metadata (Metadata): The metadata of dataset.

        TODO combine method and filepath to one parameter.
        TODO support Minguo calendar (民國紀元)
        """
        self.config: dict = None
        self.loader = None
        self.data: pd.DataFrame = None
        self.metadata: Metadata = None

        # 1. Load filepath config
        self.config = self._handle_filepath(filepath=filepath, method=method)

        # 2. Define the category (discrete), and datetime columns
        #    set dtype for these columns as str at first.
        self.config['column_types'] = None
        self.config['dtype'] = None
        if column_types is not None:
            if not verify_column_types(column_types):
                raise ConfigError
            self.config['column_types'] = column_types
            self.config['dtype'] = self._assign_str_dtype(column_types)

        # 3. Collect remain configuration (for loader_pandas)
        self.config['header_names'] = header_names
        self.config['na_values'] = na_values

    def load(self):
        """
        load data, dtype confirm and casting, and build metadata
        """

        # 1. If set as load benchmark
        #       downloading benchmark dataset, and executing on local file.
        if self.config['benchmark']:
            benchmark_access = self.config['benchmark_access']
            if benchmark_access == 'public':
                BenchmarkerRequests(self.config).download()
            elif benchmark_access == 'private':
                BenchmarkerBoto3(self.config).download()
            else:
                raise UnsupportedMethodError

        # 2. Setting self.loader as specified Loader class by file extension
        file_ext = self.config['file_ext'].lower()
        if LoaderFileExt.getext(file_ext) == LoaderFileExt.CSVTYPE:
            self.loader = LoaderPandasCsv(config=self.config)
        elif LoaderFileExt.getext(file_ext) == LoaderFileExt.EXCELTYPE:
            self.loader = LoaderPandasExcel(config=self.config)
        else:
            raise UnsupportedMethodError

        # 3. Loading data
        data: pd.DataFrame = self.loader.load()

        # 4. Optimizing dtype
        self.config['dtype'] = optimize_dtypes(
            data=data,
            column_types=self.config['column_types'],
        )

        # 5. Casting data for more efficient storage space
        self.data = casting_dataframe(data, self.config['dtype'])

        # 6. Setting metadata
        metadata = Metadata()
        metadata.build_metadata(data=self.data)
        self.metadata = metadata

    @classmethod
    def _handle_filepath(cls, filepath: str, method: str) -> dict:
        """
        Translate filepath setting, then return necessary information format.

        Args:
            filepath (str): The fullpath of dataset.
            method (str): The method of Loader.

            map_benchmark (Dict[str, Dict[str, str]]):
                The dictionary for benchmark details.

        Return:
            (dict): See __init__ also.
                filepath (str): The fullpath of dataset.
                method (str): The method of Loader.
                file_ext (str): file extension of file_ext.
                benchmark (bool): True if filepath is benchmark dataset.
                filepath_raw (str): keep original filepath input by user.
                ###### only included if benchmark is True. ######
                benchmark_name (str): The name of benchmark dataset by user
                filepath_raw (str): keep original filepath input by user.
                benchmark_name (str): The name of benchmark dataset by user
                benchmark_filename (str): The filename of benchmark dataset
                benchmark_access (str): The access type of benchmark dataset
                benchmark_region_name (str): The Amazon region name of benchmark dataset
                benchmark_bucket_name (str): The Amazon bucket name of benchmark dataset
                benchmark_sha256 (str): The SHA-256 value of benchmark dataset
        """
        config: dict = {
            'filepath': filepath,
            'method': method,
            'file_ext': None,
            'benchmark': False,
        }

        # 1. set default method if method = 'default'
        if filepath is None and method is None:
            raise NoConfigError
        elif method:
            if method.lower() == 'default':
                # default will use adult-income
                config['filepath'] = 'benchmark://adult-income'
            else:
                raise UnsupportedMethodError

        # 2. check if filepath is specified as a benchmark
        if filepath.lower().startswith("benchmark://"):
            config['benchmark'] = True
            config['benchmark_name'] = re.sub(
                r'^benchmark://', '',
                config['filepath'],
                flags=re.IGNORECASE
            ).lower()

        if config['benchmark']:
            # 3. if benchmark, load and organized yaml: BENCHMARK_CONFIG
            BENCHMARK_CONFIG = cls._load_benchmark_config()

            # 4. if benchmark name exist in BENCHMARK_CONFIG, update config
            if config['benchmark_name'] not in BENCHMARK_CONFIG:
                raise FileNotFoundError
            benchmark_value = BENCHMARK_CONFIG[config['benchmark_name']]
            benchmark_filename = benchmark_value['filename']
            config.update({
                'filepath_raw': filepath,
                'filepath': pathlib.Path('benchmark').joinpath(benchmark_filename),
                'benchmark_filename':    benchmark_filename,
                'benchmark_access':      benchmark_value['access'],
                'benchmark_region_name': benchmark_value['region_name'],
                'benchmark_bucket_name': benchmark_value['bucket_name'],
                'benchmark_sha256':      benchmark_value['sha256'],
            })

        # 5. extract file extension
        config['file_ext'] = pathlib.Path(config['filepath']).suffix.lower()

        return config

    @classmethod
    def _load_benchmark_config(cls) -> dict:
        """
        Load benchmark datasets configuration.

        Return:
            BENCHMARK_CONFIG['datasets'] (dict):
                key (str): benchmark dataset name
                    filename (str): Its filename
                    access (str): Belong to public or private bucket.
                    region_name (str): Its AWS S3 region.
                    bucket_name (str): Its AWS S3 bucket.
                    sha256 (str): Its SHA-256 value.
        """
        BENCHMARK_CONFIG = {}

        YAML_FILENAME = 'benchmark_datasets.yaml'
        with resources.open_text('PETsARD.loader', YAML_FILENAME) as file:
            BENCHMARK_CONFIG = yaml.safe_load(file)

        REGION_NAME = BENCHMARK_CONFIG['region_name']
        BUCKET_NAME = BENCHMARK_CONFIG['bucket_name']

        BENCHMARK_CONFIG['datasets'] = {
            key: {
                'filename':    value['filename'],
                'access':      value['access'],
                'region_name': REGION_NAME,
                'bucket_name': BUCKET_NAME[value['access']],
                'sha256':      value['sha256']
            }
            for key, value in BENCHMARK_CONFIG['datasets'].items()
        }

        return BENCHMARK_CONFIG['datasets']

    @classmethod
    def _assign_str_dtype(
        cls,
        column_types: Optional[Dict[str, List[str]]]
    ) -> Dict[str, str]:
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
        str_colname: List[str] = []
        for coltype in ALLOWED_COLUMN_TYPES:
            str_colname.extend(column_types.get(coltype, []))

        return {colname: 'str' for colname in str_colname}
