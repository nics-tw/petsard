from abc import ABC, abstractmethod
from copy import deepcopy
from typing import (
    List,
    Optional,
    Tuple,
)
import re

import pandas as pd

from PETsARD.reporter.utils import (
    convert_full_expt_tuple_to_name,
    convert_eval_expt_name_to_tuple,
)
from PETsARD.error import (
    ConfigError,
    UnexecutedError,
    UnsupportedMethodError
)


class ReporterMap():
    """
    Mapping of Reporter.
    """
    SAVE_DATA:   int = 10
    SAVE_REPORT: int = 11

    @classmethod
    def map(cls, method: str) -> int:
        """
        Get suffixes mapping int value

        Args:
            method (str): reporting method
        """
        try:
            return cls.__dict__[method.upper()]
        except KeyError:
            raise UnsupportedMethodError


class ReporterSaveReportMap():
    """
    Mapping of ReportSaveReport.
    """
    GLOBAL:     int = 1
    COLUMNWISE: int = 2
    PAIRWISE:   int = 3

    @classmethod
    def map(cls, granularity: str) -> int:
        """
        Get suffixes mapping int value

        Args:
            granularity (str): reporting granularity
        """
        try:
            return cls.__dict__[granularity.upper()]
        except KeyError:
            raise UnsupportedMethodError


class Reporter:
    """
    A class that represents a reporter.
    """

    def __init__(self, method: str, **kwargs):
        """
        Args:
            method (str): The method used for reporting.
            **kwargs: Additional configuration parameters.
                - All Reporter
                    - output (str, optional):
                        The output filename prefix for the report. Default is 'PETsARD'.
                - ReporterSaveData
                    - source (Union[str, List[str]]): The source of the data.
                - ReporterSaveReport
                    - eval (str): The evaluation experiment name used for reporting.
                    - granularity (str): The granularity of reporting.
                        It should be one of 'global', 'columnwise', or 'pairwise'.
                        Case-insensitive.
                    - eval (str | List[str], optional):
                        The evaluation method used for reporting.

        Attributes:
            config (dict): A dictionary containing the configuration parameters.
            reporter (object): An object representing the specific reporter based on the method.
            result (dict): A dictionary containing the data for the report.
        """
        self.config = kwargs
        self.config['method'] = method.lower()
        self.reporter = None
        self.result: dict = {}

        method_code: int = ReporterMap.map(self.config['method'])
        self.config['method_code'] = method_code
        if method_code == ReporterMap.SAVE_DATA:
            self.reporter = ReporterSaveData(config=self.config)
        elif method_code == ReporterMap.SAVE_REPORT:
            self.reporter = ReporterSaveReport(config=self.config)
        else:
            raise UnsupportedMethodError

    def create(self, data: dict) -> None:
        """
        Creates a report using the specified data.

        Args:
            data (dict): The data used for creating the report.
        """
        self.reporter.create(data=data)

    def report(self) -> None:
        """
        Generates and saves the report.
        """
        self.reporter.report()
        self.result = self.reporter.result


class ReporterBase(ABC):
    """
    Base class for reporting data.
    """
    ALLOWED_IDX_MODULE: list = [
        'Loader',
        'Splitter',
        'Processor',
        'Preprocessor',
        'Synthesizer',
        'Postprocessor',
        'Evaluator',
        'Describer',
        'Reporter',
    ]
    SAVE_REPORT_AVAILABLE_MODULE: list = ['Evaluator', 'Describer']

    def __init__(self, config: dict):
        """
        Args:
            config (dict): Configuration settings for the report.
                - method (str): The method used for reporting.
                - output (str, optional): The output filename prefix for the report.
                    Default is 'PETsARD'.

        Attributes:
            config (dict): Configuration settings for the report.
            result (dict): Data for the report.
        """
        self.config: dict = config
        self.result: dict = {}

        if 'method' not in self.config:
            raise ConfigError
        if not isinstance(self.config.get('output'), str) \
                or not self.config['output']:
            self.config['output'] = 'PETsARD'

    @abstractmethod
    def create(self, data: dict) -> None:
        """
        Abstract method for creating the report.

        Args:
            data (dict): The data used for creating the report.
                See ReporterBase._verify_create_input() for format requirement.
        """
        raise NotImplementedError

    @classmethod
    def _verify_create_input(cls, data: dict) -> None:
        """
        Verify the input data for the create method.

        Validates the structure and type of input data intended for creating a report.

        Args:
            data (dict): Input data for report creation, where:
                - The key represents the full index tuple of the source,
                    formatted as (module_name, experiment_name, ...)
                    concatenated together.
                    - For multiple results in an operator,
                        such as EvaluatorOperator, experiment names will
                        include a postfix "_[xxx]" to distinguish them. e.g.:
                        ('Loader', 'default'),
                        ('Loader', 'default', 'Preprocessor', 'default'),
                        (..., 'Evaluator', 'default_[global]').
                    - The value is the source data (pd.DataFrame).
                - 'exist_report' (optional, dict):
                    Existing report data, where the key is
                    the full evaluation experiment name
                    formatted as "{eval}_[{granularity}]",
                    and the value is the report data (pd.DataFrame).

        Raises:
            ConfigError: If any validation check fails.
        """
        for idx, value in data.items():
            # 1. The 'exist_report' must be a dict with pd.DataFrame values.
            if idx == 'exist_report':
                if not isinstance(value, dict) \
                        or not all(isinstance(v, pd.DataFrame) for v in value.values()):
                    raise ConfigError
                continue

            # 2. Index must have an even number of elements.
            if len(idx) % 2 != 0:
                raise ConfigError
            module_names, experiment_names = idx[::2], idx[1::2]

            # 3. Every module names should be in ALLOWED_IDX_MODULE.
            if not all(module in cls.ALLOWED_IDX_MODULE for module in module_names):
                raise ConfigError

            # 4. Module names in the index must be unique.
            if len(module_names) != len(set(module_names)):
                raise ConfigError

            # 5. Each value must be a pd.DataFrame or None.
            if value is not None and not isinstance(value, pd.DataFrame):
                raise ConfigError

    @staticmethod
    def get_full_expt_name(full_expt_tuple: tuple) -> str:
        """
        Get the full experiment name.

        Args:
            full_expt_tuple (tuple): The full experiment tuple.

        Returns:
            (str): The full experiment name.
                format as "module1[expt1]_module2[expt2]_..._moduleN[exptN]"
        """
        return '_'.join([
            f"{full_expt_tuple[i]}[{full_expt_tuple[i+1]}]"
            for i in range(0, len(full_expt_tuple), 2)
        ])

    @abstractmethod
    def report(self) -> None:
        """
        Abstract method for reporting the data.
        """
        raise NotImplementedError

    def _save(self, data: pd.DataFrame, full_output: str) -> None:
        """
        Save the data to a CSV file.

        Args:
            data (pd.DataFrame): The data to be saved.
            full_output (str): The full output path for the CSV file.
        """
        print(f"Now is {full_output} save to csv...")
        data.to_csv(
            path_or_buf=f"{full_output}.csv",
            index=False,
            encoding='utf-8'
        )


class ReporterSaveData(ReporterBase):
    """
    Save raw/processed data to file.
    """

    def __init__(self, config: dict):
        """
        Args:
            config (dict): The configuration dictionary.
                - method (str): The method used for reporting.
                - source (str | List[str]): The source of the data.
                - output (str, optional): The output filename prefix for the report.
                    Default is 'PETsARD'.

        Raises:
            ConfigError: If the 'source' key is missing in the config
                or if the value of 'source' is not a string or a list of strings.
        """
        super().__init__(config)

        # source should be string or list of string: Union[str, List[str]]
        if 'source' not in self.config:
            raise ConfigError
        elif not isinstance(self.config['source'], (str, list)) \
            or (isinstance(self.config['source'], list)
                and not all(isinstance(item, str) for item in self.config['source'])
                ):
            raise ConfigError

        # convert source to list if it is string
        if isinstance(self.config['source'], str):
            self.config['source'] = [self.config['source']]

    def create(self, data: dict) -> None:
        """
        Creates the report data.

        Args:
            data (dict): The data dictionary.
                Gerenrating by ReporterOperator.set_input()
                See ReporterBase._verify_create_input() for format requirement.

        Raises:
            ConfigError: If the index tuple is not an even number.
        """
        # verify input data
        self._verify_create_input(data)

        # last 1 of index should remove postfix "_[xxx]" to match source
        pattern = re.compile(r'_(\[[^\]]*\])$')
        for full_expt_tuple, df in data.items():
            # check if last 2 element of index in source
            last_module_expt_name = [
                full_expt_tuple[-2], re.sub(pattern, '', full_expt_tuple[-1])
            ]
            if any(item in self.config['source'] for item in last_module_expt_name):
                full_expt_name = self.get_full_expt_name(full_expt_tuple)
                self.result[full_expt_name] = df

    def report(self) -> None:
        """
        Generates the report.

        Notes:
            Some of the data may be None,
            such as Evaluator.get_global/columnwise/pairwise.
            These will be skipped.
        """
        for expt_name, df in self.result.items():
            # Some of the data may be None.
            #   e.g. Evaluator.get_global/columnwise/pairwise
            #   just skip it
            if df is None:
                continue

            # PETsARD_{expt_name}
            full_output = f"{self.config['output']}_{expt_name}"
            self._save(data=df, full_output=full_output)


class ReporterSaveReport(ReporterBase):
    """
    Save evaluating/describing data to file.
    """
    DEFAULT_FIXED_COLUMNS: list = [
        'full_expt_name',
        'Loader',
        'Splitter',
        'Preprocessor',
        'Synthesizer',
        'Postprocessor',
        'Evaluator',
        'Describer',
        'column',
        'column1',
        'column2',
    ]

    def __init__(self, config: dict):
        """
        Args:
            config (dict): The configuration dictionary.
                - method (str): The method used for reporting.
                - output (str, optional): The output filename prefix for the report.
                    Default is 'PETsARD'.
                - granularity (str): The granularity of reporting.
                    It should be one of 'global', 'columnwise', or 'pairwise'.
                    Case-insensitive.
                - eval (str | List[str], optional):
                    The evaluation experiment name for export reporting.
                    Case-sensitive. Default is None

        Raises:
            ConfigError: If the 'source' key is missing in the config
                or if the value of 'source' is not a string or a list of strings.
        """
        super().__init__(config)

        # granularity should be whether global/columnwise/pairwise
        if 'granularity' not in self.config:
            raise ConfigError
        if not isinstance(self.config['granularity'], str):
            raise ConfigError
        self.config['granularity'] = self.config['granularity'].lower()
        granularity_code = ReporterSaveReportMap.map(
            self.config['granularity'])

        if granularity_code not in [
            ReporterSaveReportMap.GLOBAL,
            ReporterSaveReportMap.COLUMNWISE,
            ReporterSaveReportMap.PAIRWISE
        ]:
            raise ConfigError
        self.config['granularity_code'] = granularity_code

        # set eval to None if not exist,
        #   otherwise verify it should be str or List[str]
        eval = self.config.get('eval')
        if isinstance(eval, str):
            eval = [eval]
        if not isinstance(eval, list)\
                or not all(isinstance(item, str) for item in eval):
            if eval is not None:
                raise ConfigError
        self.config['eval'] = eval

    def create(self, data: dict = None) -> None:
        """
        Creating the report data by checking is experiment name of Evaluator exist.

        If config['eval'] have been given,
            it will only collect the report data of the specified evaluation experiment name.
        Otherwise,
            it will collect all the report data of the evaluation experiment name.

        Args:
            data (dict): The data used for creating the report.
                See ReporterBase._verify_create_input() for format requirement.
                - exist_report (dict, optional): The existing report data.
                    - The key is the full evaluation experiment name:
                        "{eval}_[{granularity}]"
                    - The value is the data of the report, pd.DataFrame.

        Attributes:
            - result (dict): Data for the report.
                - Reporter (dict): The report data for the reporter.
                    - expt_name (str): The matching experiment name.
                    - granularity (str): The granularity of the report.
                    - report (pd.DataFrame): The report data.

        TODO Log record if rpt_data is None
        """
        # verify input data
        self._verify_create_input(data)

        eval: Optional[List[str]] = self.config['eval']
        granularity: str = self.config['granularity']
        output_eval_name: str = ''

        exist_report: dict = data.pop('exist_report', None)

        eval_expt_name: str = ''

        if eval is None:
            # match every ends of f"_[{granularity}]"
            eval_pattern = re.escape(f"_[{granularity}]") + "$"
            output_eval_name = f"[{granularity}]"
        else:
            # it should be match f"{eval}_[{granularity}]", where eval is a list
            eval_pattern = (
                "^("
                + "|".join([re.escape(eval_item) for eval_item in eval])
                + ")"
                + re.escape(f"_[{granularity}]")
                + "$"
            )
            output_eval_name = (
                "-".join([eval_item for eval_item in eval])
                + f"_[{granularity}]"
            )

        for full_expt_tuple, rpt_data in data.items():
            # 1. Found final module is Evaluator/Describer
            if full_expt_tuple[-2] not in self.SAVE_REPORT_AVAILABLE_MODULE:
                continue

            # 2. matching granularity (also eval if provided)
            if not re.search(eval_pattern, eval_expt_name):
                continue

            # 3. match granularity
            if rpt_data is None:
                print(
                    f"Reporter: "
                    f"There's no {granularity} granularity report in {eval}. "
                    f"Nothing collect."
                )
                continue

            rpt_data = self._process_report_data(
                report=rpt_data,
                full_expt_tuple=full_expt_tuple,
                granularity_code=self.config['granularity_code'],
            )

            # 4. Row append if exist_report exist
            if exist_report is not None:
                if eval_expt_name in exist_report:
                    rpt_data = pd.concat(
                        [exist_report[eval_expt_name].copy(), rpt_data],
                        axis=0,
                        ignore_index=True,
                    )

            # 5. Collect result
            self.result['Reporter'] = {
                'full_expt_name': self.get_full_expt_name(full_expt_tuple),
                'eval_expt_name': eval_expt_name,
                'expt_name': eval,
                'granularity': granularity,
                'report': deepcopy(rpt_data)
            }

    @classmethod
    def _process_report_data(
        cls,
        report: pd.DataFrame,
        full_expt_tuple: Tuple[str],
        granularity_code: int,
        rename: bool = True
    ) -> pd.DataFrame:
        """
        Process the report data by performing the following steps:

        1. Rename the columns as f"{eval_name}_{original column}" if assigned.
        2-1. Reset the index if the granularity is COLUMNWISE.
            Rename the index column to 'column'.
        2-2. Reset the index if the granularity is PAIRWISE.
            Rename the level_0 and level_1 columns to 'column1' and 'column2' respectively.
        3. Sequentially insert module names as column names and expt names as values.
        4. Add the full_expt_name as the first column.

        Args:
            - report (pd.DataFrame):
                The report data to be processed.
            - full_expt_tuple (tuple):
                The tuple containing module names and expt names.
            - rename (bool, optional):
                A flag to indicate whether to rename the columns.
                Default is True.

        Returns:
            - rpt_data (pd.DataFrame): The processed report data.
        """

        # 1. Rename columns as f"{eval_name}_{original column}" if assigned
        #   eval_name: "sdmetrics-qual[default]" <- get "sdmetrics-qual"
        if rename:
            eval_expt_tuple = convert_eval_expt_name_to_tuple(full_expt_tuple[-1])
            eval_name = eval_expt_tuple[0]
            for col in report.columns:
                report.rename(
                    columns={col: f"{eval_name}_{col}"},
                    inplace=True,
                )

        # 2. reset index to represent column
        if granularity_code == ReporterSaveReportMap.COLUMNWISE:
            report = report.reset_index(drop=False)
            report = report.rename(columns={'index': 'column'})
        elif granularity_code == ReporterSaveReportMap.PAIRWISE:
            report = report.reset_index(drop=False)
            report = report.rename(columns={
                'level_0': 'column1',
                'level_1': 'column2'
            })

        # 3. Sequentially insert module names
        #   as column names and expt names as values
        for i in range(len(full_expt_tuple) - 2, -1, -2):
            report.insert(0, full_expt_tuple[i], full_expt_tuple[i+1])

        # 4. Add full_expt_name as first column
        report.insert(
            0, 'full_expt_name', cls.get_full_expt_name(full_expt_tuple)
        )

        return report

    def report(self) -> None:
        """
        Generates a report based on the provided report data.
            The report is saved to the specified output location.
        """
        if 'Reporter' not in self.result:
            raise UnexecutedError

        if 'eval_expt_name' not in self.result['Reporter']:
            # no {granularity} granularity report in {eval}
            return

        eval_expt_name: str = self.result['Reporter']['eval_expt_name']

        # PETsARD[Report]_{eval_expt_name}
        full_output = f"{self.config['output']}[Report]_{eval_expt_name}"
        self._save(
            data=self.result['Reporter']['report'],
            full_output=full_output
        )
