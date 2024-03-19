from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Optional
import re

import pandas as pd

from PETsARD.error import ConfigError, UnexecutedError, UnsupportedMethodError


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
                    - granularity (str): The granularity of reporting.
                        It should be one of 'global', 'columnwise', or 'pairwise'.
                        Case-insensitive.
                    - eval (str): The evaluation experiment name used for reporting.

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
        self.result = self.reporter.result

    def report(self) -> None:
        """
        Generates and saves the report.
        """
        self.reporter.report()


class ReporterBase(ABC):
    """
    Base class for reporting data.
    """

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
        """
        raise NotImplementedError


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
                - source (Union[str, List[str]]): The source of the data.
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
            data (dict): The data dictionary. Gerenrating by ReporterOperator.set_input()
                The key is the full index tuple of the source,
                    format is (module_name, experiment_name, ), and concat together. e.g.
                    ('Loader', 'default'),
                    ('Loader', 'default', 'Preprocessor', 'default')
                    If there's multiple result in the Operator, e.g. EvaluatorOperator,
                    Their expeirment name will add postfix "_[xxx]" to distinguish. e.g.
                    (..., 'Evaluator', 'default_[global]')
                The value is the data of the source.

        Raises:
            ConfigError: If the index tuple is not an even number.
        """
        # last 1 of index should remove postfix "_[xxx]" to match source
        pattern = re.compile(r'_(\[[^\]]*\])$')
        for index, df in data.items():
            # check if last 2 element of index in source
            last_module_expt_name = [index[-2], re.sub(pattern, '', index[-1])]
            if any(item in self.config['source'] for item in last_module_expt_name):
                # index tuple should be even number
                if len(index) % 2 != 0:
                    raise ConfigError

                full_expt = '_'.join([
                    f"{index[i]}[{index[i+1]}]"
                    for i in range(0, len(index), 2)
                ])
                self.result[full_expt] = df

    def report(self) -> None:
        """
        Generates the report.

        Notes:
            Some of the data may be None, such as Evaluator.get_global/columnwise/pairwise. These will be skipped.
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
                - eval (str): The evaluation experiment name for export reporting.
                    Case-sensitive.

        Raises:
            ConfigError: If the 'source' key is missing in the config
                or if the value of 'source' is not a string or a list of strings.
        """
        super().__init__(config)

        self.ALLOWED_IDX_MODULE: list = [
            'Loader',
            'Splitter',
            'Processor',
            'Preprocessor',
            'Synthesizer',
            'Postprocessor',
            'Evaluator',
            'Describer',
        ]

        # granularity should be whether global/columnwise/pairwise
        if 'granularity' not in self.config:
            raise ConfigError
        granularity_code = ReporterSaveReportMap.map(self.config['granularity'])
        if granularity_code not in [
            ReporterSaveReportMap.GLOBAL,
            ReporterSaveReportMap.COLUMNWISE,
            ReporterSaveReportMap.PAIRWISE
        ]:
            raise ConfigError
        self.config['granularity_code'] = granularity_code

        # set eval to None if not exist
        if 'eval' not in self.config:
            raise ConfigError

    def create(self, data: dict = None) -> None:
        """
        Creating the report data by checking is experiment name of Evaluator exist.

        Args:
            data (dict): The data dictionary. Gerenrating by ReporterOperator.set_input()
                - The key is the full index tuple of the source,
                    format is (module_name, experiment_name, ), and concat together. e.g.
                    ('Loader', 'default'),
                    ('Loader', 'default', 'Preprocessor', 'default')
                    If there's multiple result in the Operator, e.g. EvaluatorOperator,
                    Their expeirment name will add postfix "_[xxx]" to distinguish. e.g.
                    (..., 'Evaluator', 'default_[global]')
                - The value is the data of the source.
                - exist_report (dict, optional): The existing report data.
                    - The key is the full evaluation experiment name: "{eval}_[{granularity}]"
                    - The value is the data of the report, pd.DataFrame.

        Attributes:
            - result (dict): Data for the report.
                - Reporter (dict): The report data for the reporter.
                    - full_expt_name (str): The full experiment name.
                    - expt_name (str): The experiment name.
                    - granularity (str): The granularity of the report.
                    - report (pd.DataFrame): The report data.
        """
        eval: Optional[str] = self.config['eval']
        granularity: str = self.config['granularity'].lower()

        result: dict = {}
        rpt_data: pd.DataFrame = None

        idx_final_module: str = ''
        idx_module_names: list = []
        full_expt_name: str = ''
        eval_expt_name: str = ''

        exist_report: dict = None
        exist_result: pd.DataFrame = None

        if 'exist_report' in data:
            exist_report = data['exist_report']
            del data['exist_report']

        for idx_tuple, rpt_data in data.items():
            idx_module_names = idx_tuple[::2]
            idx_final_module = idx_module_names[-1]

            # found final module is Evaluator/Describer
            if idx_final_module not in ['Evaluator','Describer']:
                continue

            # Ensure Ensure idx_tuple is of even length,
            if len(idx_tuple) % 2 != 0:
                raise ConfigError
            # all are within a given list ALLOWED_IDX_MODULE.
            elif not all(
                module in self.ALLOWED_IDX_MODULE for module in idx_module_names):
                raise ConfigError
            # and its module names are unique
            elif len(idx_module_names) != len(set(idx_module_names)):
                raise ConfigError

            eval_expt_name = idx_tuple[-1]
            # specifiy experiment name
            #   match the expt_name "{eval}_[{granularity}]"
            if eval_expt_name != f"{eval}_[{granularity}]":
                continue

            # match granularity
            if rpt_data is None:
                print(
                    f"There's no {granularity} granularity report in {eval}. "
                    f"Nothing collect."
                )
                continue

            # module1[expt1]_module2[expt2]_..._moduleN[exptN]
            full_expt_name = '_'.join([
                f"{idx_tuple[i]}[{idx_tuple[i+1]}]"
                for i in range(0, len(idx_tuple), 2)
            ])
            result['full_expt_name'] = full_expt_name
            result['eval_expt_name'] = eval_expt_name
            result['expt_name'] = eval
            result['granularity'] = granularity

            # reset index to represent column
            granularity_code = self.config['granularity_code']
            if granularity_code == ReporterSaveReportMap.COLUMNWISE:
                rpt_data = rpt_data.reset_index(drop=False)
                rpt_data = rpt_data.rename(columns={'index': 'column'})
            elif granularity_code == ReporterSaveReportMap.PAIRWISE:
                rpt_data = rpt_data.reset_index(drop=False)
                rpt_data = rpt_data.rename(columns={
                    'level_0': 'column1',
                    'level_1': 'column2'
                })

            # Sequentially insert module names
            #   as column names and expt names as values
            for i in range(len(idx_tuple) - 2, -1, -2):
                rpt_data.insert(0, idx_tuple[i], idx_tuple[i+1])

            # add full_expt_name as first column
            rpt_data.insert(0, 'full_expt_name', full_expt_name)

            # Row append if exist_report exist
            if exist_report is not None:
                if eval_expt_name in exist_report:
                    exist_result = exist_report[eval_expt_name]
                    rpt_data = pd.concat(
                        [exist_result, rpt_data],
                        axis=0
                    )
            result['report'] = deepcopy(rpt_data)

            # should only single Evaluator/Describer matched in the Status.status
            break

        self.result['Reporter'] = result

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

