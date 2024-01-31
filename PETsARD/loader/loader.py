from importlib import resources
import pathlib
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Union
)

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
from PETsARD.util import df_casting
from PETsARD.util import df_cast_check


class LoaderFileExt():
    """
    Mapping of File extension.
        Replace original _loader_mapping_file_ext().
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
        Get suffixes mapping int value,
            uses division by ten to obtain
            a corresponding higher level of abstraction
            and returns it.
        ...
        Args:
            file_ext (str):
                File extension
        """
        return cls.__dict__[file_ext[1:].upper()] // 10


class Loader:
    """
    Loader
        Check the target file for the Loader,
        implement different Loader instances using a factory method,
        and read files with a module optimized for dtypes and storage.

    ...
    Methods:
        Loader(filepath)
        Returns:
            pandas.DataFrame: A pandas DataFrame
                containing the loaded data which already casting

    ...

    Args:
        filepath (str):
            The fullpath of dataset.

        header_exist (bool ,optional):
            Is header as 1st row of data or NOT. Default is True.
        header_names (list ,optional):
            Header list of data.
            It will be replacement if header_exist is True,
            and generating if header_exist is False. Default is empty list [].
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

    ...
    TODO Duplicated function between dtype n' colnames_xxx
    """

    def __init__(
        self,
        filepath:     str,
        header_exist: bool = True,
        header_names: Optional[List[str]] = None,
        na_values:    Optional[Union[str, List[str], Dict[str, str]]] = None,
        sep: str = ',',
        sheet_name: Union[str, int] = 0,
        colnames_discrete: Optional[List[str]] = None,
        colnames_datetime: Optional[List[str]] = None,
        dtype: Optional[Dict[str, Any]] = None,
    ):
        # organized yaml
        PETSARD_CONFIG = {}
        LIST_YAML = [
            ('benchmark_datasets.yaml', 'benchmark_datasets')
        ]
        for yaml_name, config_name in LIST_YAML:
            with resources.open_text('PETsARD.Loader', yaml_name) as file:
                PETSARD_CONFIG[config_name] = yaml.safe_load(file)

        # Compling PETSARD_CONFIG
        # 1. update benchmark detail - replace _loader_mapping_benchmark()
        #     PETSARD_CONFIG['benchmark_datasets'] (dict):
        #         key (str): benchmark dataset name
        #             filename (str): Its filename
        #             access (str):   Belong to public or private bucket.
        #             region_name (str): Its AWS S3 region.
        #             bucket_name (str): Its AWS S3 bucket.
        #             sha256 (str): Its SHA-256 value.
        REGION_NAME = PETSARD_CONFIG['benchmark_datasets']['region_name']
        BUCKET_NAME = PETSARD_CONFIG['benchmark_datasets']['bucket_name']
        PETSARD_CONFIG['benchmark_datasets']['datasets'] = {
            key: {
                'filename':    value['filename'],
                'access':      value['access'],
                'region_name': REGION_NAME,
                'bucket_name': BUCKET_NAME[value['access']],
                'sha256':      value['sha256']
            }
            for key, value in PETSARD_CONFIG['benchmark_datasets']['datasets'].items()
        }

        self.para = {}
        # Check if file exist
        self.para['Loader'] = self._handle_filepath(
            filepath,
            map_benchmark=PETSARD_CONFIG['benchmark_datasets']['datasets']
        )
        # If benchmark, download benchmark dataset, and execute as local file.
        if self.para['Loader']['benchmark']:
            benchmark_access = self.para['Loader']['benchmark_access']
            if benchmark_access == 'public':
                BenchmarkerRequests(self.para['Loader']).download()
            elif benchmark_access == 'private':
                BenchmarkerBoto3(self.para['Loader']).download()
            else:
                raise ValueError(
                    f"Loader - Unsupported benchmark access type, "
                    f"now is {benchmark_access}."
                )
        # Force define the discrete and date/datetime dtype
        self.para['Loader'].update(
            self._specify_str_dtype(
                colnames_discrete,
                colnames_datetime
            )
        )
        # recoded remain parameter
        # TODO sunset colnames_discrete/datetime, it is duplicated to dtype
        self.para['Loader'].update({
            'header_exist': header_exist,
            'header_names': header_names,
            'sep':          sep,
            'sheet_name':   sheet_name,
            'na_values':    na_values
        })

        # Factory method for implementing the specified Loader class
        file_ext = self.para['Loader']['file_ext'].lower()
        if LoaderFileExt.getext(file_ext) == LoaderFileExt.CSVTYPE:
            self.Loader = LoaderPandasCsv(self.para['Loader'])
        elif LoaderFileExt.getext(file_ext) == LoaderFileExt.EXCELTYPE:
            self.Loader = LoaderPandasExcel(self.para['Loader'])
        else:
            raise ValueError(
                f"Loader: Unsupported file type, now is {file_ext}."
            )

        self.data = self.Loader.load()

        # Define dtype
        # TODO Still consider how to extract dtype from pd.dateframe directly.
        #      Consider to combind to Metadata
        if not dtype:
            self.dtype = {}
        self.dtype.update(df_cast_check(self.data, dtype))

        # Casting data for more efficient storage space
        self.data = df_casting(self.data, self.dtype)

        # metadata
        metadata = Metadata()
        metadata.build_metadata(data=self.data)
        self.metadata = metadata

    @staticmethod
    def _handle_filepath(
        filepath:      str,
        map_benchmark: Dict[str, Dict[str, str]] = None
    ) -> dict:
        """
        _handle_filepath
            Translate filepath setting,
                then return necessary information format.
        ...
        Args:
            filepath (str):
                The fullpath of dataset.
            map_benchmark (Dict[str, Dict[str, str]]):
                The dictionary for benchmark details.
        ...
        Return:
            (dict):
                filepath: for records filepath we use.
                file_ext: file extension of file_ext.
                benchmark-: benchmark related information,
                    see _loader_mapping_benchmark() for details.
        """
        if filepath.lower().startswith("benchmark://"):
            # Benchmark dataset
            benchmark_name = filepath[len("benchmark://"):]
            if benchmark_name.lower() in map_benchmark:
                benchmark_value = map_benchmark[benchmark_name.lower()]
                benchmark_filename = benchmark_value['filename']
                return {
                    'filepath': pathlib.Path('benchmark').joinpath(benchmark_filename),
                    'file_ext': pathlib.Path(benchmark_filename).suffixes[0].lower(),
                    'benchmark': True,
                    'benchmark_filepath':    filepath,
                    'benchmark_name':        benchmark_name,
                    'benchmark_filename':    benchmark_filename,
                    'benchmark_access':      benchmark_value['access'],
                    'benchmark_region_name': benchmark_value['region_name'],
                    'benchmark_bucket_name': benchmark_value['bucket_name'],
                    'benchmark_sha256':      benchmark_value['sha256'],
                }
            else:
                raise FileNotFoundError(
                    f"Loader: The benchmark dataset is not valid: {filepath}"
                )
        else:
            return {
                'benchmark': False,
                'filepath': filepath,
                'file_ext': pathlib.Path(filepath).suffixes[0].lower()
            }

    @staticmethod
    def _specify_str_dtype(
        colnames_discrete: Optional[List[str]],
        colnames_datetime: Optional[List[str]]
    ) -> dict:
        """
        _specify_str_dtype
            Force setting discrete and datetime columns
            been load as str at first.
        ...
        Args:
            colnames_discrete (List[str]):
                The column names of discrete variable.
            colnames_datetime (List[str]):
                The column names of date/datetime variable.
        ...
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
