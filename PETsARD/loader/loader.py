from importlib import resources
import pathlib
import re
from typing import (
    Any,
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
from PETsARD.error import ConfigError, UnsupportedMethodError
from PETsARD.util import df_casting, df_cast_check


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
    Loader

    Check the target file for the Loader,
        implement different Loader instances using a factory method,
        and read files with a module optimized for dtypes and storage.
    """

    def __init__(
        self,
        filepath: str = None,
        method:   str = None,
        header_names: Optional[List[str]] = None,
        sep: str = ',',
        sheet_name: Union[str, int] = 0,
        colnames_discrete: Optional[List[str]] = None,
        colnames_datetime: Optional[List[str]] = None,
        dtype: Optional[Dict[str, Any]] = {},

        na_values:    Optional[Union[str, List[str], Dict[str, str]]] = None,
    ):
        """
        Args:
            filepath (str): The fullpath of dataset.
            method (str): The method of Loader.

            header_names (list ,optional):
                Specifies a list of headers for the data.
                If set, this list will replace the existing headers.
                Default is None, indicating no custom headers will be applied.

            sep (str ,optional):
                Character or regex pattern to treat as the delimiter.
                Default is comma ",".
            sheet_name (str | int ,optional):
                Strings are used for sheet names.
                Integers are used in zero-indexed sheet positions
                (chart sheets do not count as a sheet position).
                Specify None to get all worksheets.
            colnames_discrete (list ,optional):
                List of column names that are discrete.
                They will be forcibly treated as strings,
                and convert to categorical later. Default is empty list [].
            colnames_datetime (list ,optional):
                List of column names that are date/datetime.
                They will be forcibly treated as strings,
                and convert to date or datetime later. Default is empty list [].
            dtype (dict ,optional):
                Dictionary of columns data type force assignment.
                Format as {colname: col_dtype}.
                Default is None, means no se empty dict {}.

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
                ###### from _handle_filepath() ######
                file_ext (str): file extension of file_ext.
                benchmark (bool): True if filepath is benchmark dataset.
                    ###### only included if benchmark is True. ######
                filepath_raw (str): keep original filepath input by user.
                benchmark_name (str): The name of benchmark dataset by user
                benchmark_filename (str): The filename of benchmark dataset
                benchmark_access (str): The access type of benchmark dataset
                benchmark_region_name (str): The Amazon region name of benchmark dataset
                benchmark_bucket_name (str): The Amazon bucket name of benchmark dataset
                benchmark_sha256 (str): The SHA-256 value of benchmark dataset


            loader (LoaderPandasCsv | LoaderPandasExcel):
                The instance of LoaderPandasCsv or LoaderPandasExcel.

        TODO combine method and filepath to one parameter.
        TODO Duplicated function between dtype n' colnames_xxx
        """
        self.config: dict = None
        self.loader = None
        self.dtype = dtype

        # 1. Load filepath config
        self.config = self._handle_filepath(filepath=filepath, method=method)

        # Force define the discrete and date/datetime dtype
        self.config.update(
            self._specify_str_dtype(
                colnames_discrete,
                colnames_datetime
            )
        )
        # recoded remain parameter
        # TODO sunset colnames_discrete/datetime, it is duplicated to dtype
        self.config.update({
            'header_exist': header_exist,
            'header_names': header_names,
            'sep':          sep,
            'sheet_name':   sheet_name,
            'na_values':    na_values
        })

    def load(self):
        """
        load
            load data, dtype confirm and casting, and build metadata
        """
        # If benchmark, download benchmark dataset, and execute as local file.
        if self.config['benchmark']:
            benchmark_access = self.config['benchmark_access']
            if benchmark_access == 'public':
                BenchmarkerRequests(self.config).download()
            elif benchmark_access == 'private':
                BenchmarkerBoto3(self.config).download()
            else:
                raise UnsupportedMethodError

        # Factory method for implementing the specified Loader class
        file_ext = self.config['file_ext'].lower()
        if LoaderFileExt.getext(file_ext) == LoaderFileExt.CSVTYPE:
            self.loader = LoaderPandasCsv(self.config)
        elif LoaderFileExt.getext(file_ext) == LoaderFileExt.EXCELTYPE:
            self.loader = LoaderPandasExcel(self.config)
        else:
            raise UnsupportedMethodError

        self.data: pd.DataFrame = self.loader.load()

        # Define dtype
        # TODO Still consider how to extract dtype from pd.dateframe directly.
        #      Consider to combind to Metadata
        self.dtype.update(df_cast_check(self.data, self.dtype))

        # Casting data for more efficient storage space
        self.data = df_casting(self.data, self.dtype)

        # metadata
        metadata = Metadata()
        metadata.build_metadata(data=self.data)
        self.metadata: Metadata = metadata

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
            raise ConfigError
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
        config['file_ext'] = pathlib.Path(config['filepath']).suffixes[0].lower()

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


    @staticmethod
    def _specify_str_dtype(
        colnames_discrete: Optional[List[str]],
        colnames_datetime: Optional[List[str]]
    ) -> dict:
        """
        _specify_str_dtype
            Force setting discrete and datetime columns
            been load as str at first.

        Args:
            colnames_discrete (List[str]):
                The column names of discrete variable.
            colnames_datetime (List[str]):
                The column names of date/datetime variable.

        Return:
            self.para['Loader'] (dict):
                dtype: particular columns been force assign as string
        """
        colnames_discrete = colnames_discrete or []
        colnames_datetime = colnames_datetime or []

        return {
            'colnames_discrete': colnames_discrete,
            'colnames_datetime': colnames_datetime,
            'dtype': {
                colname: str for colname
                in colnames_discrete + colnames_datetime
            }
        }
