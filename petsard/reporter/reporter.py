from abc import ABC, abstractmethod
from copy import deepcopy
from typing import (
    List,
    Optional,
)
import re

import pandas as pd

from petsard.reporter.utils import (
    convert_full_expt_tuple_to_name,
    convert_eval_expt_name_to_tuple,
    full_expt_tuple_filter,
)
from petsard.error import (
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
                        The output filename prefix for the report.
                        Default is 'petsard'.
                - ReporterSaveData
                    - source (Union[str, List[str]]): The source of the data.
                - ReporterSaveReport
                    - granularity (str): The granularity of reporting.
                        It should be one of 'global', 'columnwise', or 'pairwise'.
                        Case-insensitive.

        Attributes:
            config (dict): A dictionary containing the configuration parameters.
            reporter (object):
                An object representing the specific reporter based on the method.
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
                - output (str, optional):
                    The output filename prefix for the report.
                    Default is 'petsard'.

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
            self.config['output'] = 'petsard'

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
                - output (str, optional):
                    The output filename prefix for the report.
                    Default is 'petsard'.

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
                full_expt_name = convert_full_expt_tuple_to_name(full_expt_tuple)
                self.result[full_expt_name] = df

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

            # petsard_{expt_name}
            full_output = f"{self.config['output']}_{expt_name}"
            self._save(data=df, full_output=full_output)


class ReporterSaveReport(ReporterBase):
    """
    Save evaluating/describing data to file.
    """
    SAVE_REPORT_KEY: str = 'full_expt_name'

    def __init__(self, config: dict):
        """
        Args:
            config (dict): The configuration dictionary.
                - method (str): The method used for reporting.
                - output (str, optional): The output filename prefix for the report.
                    Default is 'petsard'.
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

        # granularity should be whether global/columnwise/pairwise
        if 'granularity' not in self.config:
            raise ConfigError
        self.config['granularity'] = self.config['granularity'].lower()
        granularity_code = ReporterSaveReportMap.map(
            self.config['granularity']
        )
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
                    - full_expt_name (str): The full experiment name.
                    - expt_name (str): The experiment name.
                    - granularity (str): The granularity of the report.
                    - report (pd.DataFrame): The report data.
        """
        # verify input data
        self._verify_create_input(data)

        eval: str = self.config['eval']
        granularity: str = self.config['granularity']
        output_eval_name: str = ''
        skip_flag: bool = False
        first_rpt_data: bool = True
        final_rpt_data: pd.DataFrame = None

        exist_report: dict = data.pop('exist_report', None)
        exist_report_done: bool = False

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
            # processing single data
            skip_flag, rpt_data = self._process_report_data(
                report=rpt_data,
                full_expt_tuple=full_expt_tuple,
                eval_pattern=eval_pattern,
                granularity=granularity,
                output_eval_name=output_eval_name,
            )
            # skip if skip_flag return True
            if skip_flag:
                continue

            # 4. safe_merge exist_report and current report if non-merge
            if not exist_report_done:
                if exist_report is not None and output_eval_name in exist_report:
                    rpt_data = self._safe_merge(
                        df1 = exist_report[output_eval_name],
                        df2 = rpt_data,
                        name1 = ('exist_report',),
                        name2 = full_expt_tuple,
                    )
                exist_report_done = True

            # 5. safe_merge
            if first_rpt_data:
                final_rpt_data = rpt_data.copy()
                first_rpt_data = False
            else:
                final_rpt_data = self._safe_merge(
                    df1 = final_rpt_data,
                    df2 = rpt_data,
                    name1 = ('Append report'),
                    name2 = full_expt_tuple,
                )

            # 6. Collect result
            self.result['Reporter'] = {
                'eval_expt_name': output_eval_name,
                'granularity': granularity,
                'report': deepcopy(final_rpt_data)
            }

        # 7. exception handler
        if 'Reporter' not in self.result:
            self.result['Reporter'] = {
                'eval_expt_name': output_eval_name,
                'granularity': granularity,
                'report': None,
                'warnings': (
                    f"There is no report data to save "
                    f"under {granularity} granularity."
                )
            }

    @classmethod
    def _process_report_data(
        cls,
        report: pd.DataFrame,
        full_expt_tuple: tuple[str],
        eval_pattern: str,
        granularity: str,
        output_eval_name: str,
    ) -> tuple[bool, pd.DataFrame]:
        """
        Process the report data by performing the following steps:

        1. Check if the final module is Evaluator/Describer.
        2. Check if the evaluation experiment name matches the granularity.
        3. Check if the report data exists.
        4. Rename the columns as f"{eval_name}_{original column}" if assigned.
        5-1. Reset the index if the granularity is COLUMNWISE.
            Rename the index column to 'column'.
        5-2. Reset the index if the granularity is PAIRWISE.
            Rename the level_0 and level_1 columns to 'column1' and 'column2' respectively.
        6. Sequentially insert module names as column names and expt names as values.
            Avoid different, the non-evalualtion module name will be move,
            and keep granularity from input only.
        7. Add the full_expt_name as the first column.

        Args:
            - report (pd.DataFrame):
                The report data to be processed.
            - full_expt_tuple (tuple):
                The tuple containing module names and expt names.
            - eval_pattern (str):
                The pattern to match the evaluation experiment name.
            - granularity (str):
                The granularity of the report.
            - output_eval_name (str):
                The output evaluation experiment name.

        Returns:
            - skip_flag (bool): True if the report data should be skipped.
            - rpt_data (pd.DataFrame): The processed report data.
        """
        full_expt_name: str = None
        full_expt_name_postfix: str = ''

        # 1. Found final module is Evaluator/Describer
        if full_expt_tuple[-2] not in cls.SAVE_REPORT_AVAILABLE_MODULE:
            return True, None

        # 2. eval_expt_name matching granularity (also eval if provided)
        if not re.search(eval_pattern, full_expt_tuple[-1]):
            return True, None

        # 3. match granularity, if exist, copy()
        if report is None:
            print(
                f"Reporter: "
                f"There's no {granularity} granularity report "
                f"in {full_expt_tuple[-2]} "
                f"{convert_eval_expt_name_to_tuple(full_expt_tuple[-1])[0]}. "
                f"Nothing collect."
            )
            return True, None
        report = report.copy()

        # 4. Rename columns as f"{eval_name}_{original column}" if assigned
        #   eval_name: "sdmetrics-qual[default]" <- get "sdmetrics-qual"
        eval_expt_tuple = convert_eval_expt_name_to_tuple(full_expt_tuple[-1])
        eval_name = eval_expt_tuple[0]
        for col in report.columns:
            report.rename(
                columns={col: f"{eval_name}_{col}"},
                inplace=True,
            )

        # 5. reset index to represent column
        granularity_code: int = ReporterSaveReportMap.map(granularity)
        if granularity_code == ReporterSaveReportMap.COLUMNWISE:
            report = report.reset_index(drop=False)
            report = report.rename(columns={'index': 'column'})
        elif granularity_code == ReporterSaveReportMap.PAIRWISE:
            report = report.reset_index(drop=False)
            report = report.rename(columns={
                'level_0': 'column1',
                'level_1': 'column2'
            })

        # 6. Sequentially insert module names
        #   as column names and expt names as values
        for i in range(len(full_expt_tuple) - 2, -1, -2):
            if full_expt_tuple[i] in cls.SAVE_REPORT_AVAILABLE_MODULE:
                report.insert(0, full_expt_tuple[i], output_eval_name)
                full_expt_name_postfix += full_expt_tuple[i]
                full_expt_name_postfix += output_eval_name
            else:
                report.insert(0, full_expt_tuple[i], full_expt_tuple[i+1])

        # 7. Add full_expt_name as first column
        full_expt_name = convert_full_expt_tuple_to_name(
            full_expt_tuple_filter(
                full_expt_tuple=full_expt_tuple,
                method='exclude',
                target=cls.SAVE_REPORT_AVAILABLE_MODULE,
            )
        )
        full_expt_name = '_'.join(
            component for component in
            [full_expt_name, full_expt_name_postfix]
            if component != ''
        )
        report.insert(0, 'full_expt_name', full_expt_name)

        return False, report

    @classmethod
    def _safe_merge(
        cls,
        df1: pd.DataFrame,
        df2: pd.DataFrame,
        name1: str,
        name2: str,
    ) -> pd.DataFrame:
        """
        FULL OUTER JOIN two DataFrames safely.
            We will confirm the common columns dtype is same or change to object.
                Then, FULL OUTER JOIN based on common columns,
                and column order based on df1 than df2.
            Please aware common_columns JOIN based on format assumption,
                if join different allow_module and/or granularity,
                it will be wrong.

        Args:
            df1 (pd.DataFrame): The first DataFrame.
            df2 (pd.DataFrame): The second DataFrame.
            name1 (str): The name of the first DataFrame.
            name2 (str): The name of the second DataFrame.

        Returns:
            pd.DataFrame: The concatenated DataFrame.
        """
        df: pd.DataFrame = None
        common_columns: List[str] = None
        allow_common_columns: List[str] = cls.ALLOWED_IDX_MODULE + [cls.SAVE_REPORT_KEY]
        df1_common_dtype: dict = None
        df2_common_dtype: dict = None
        colname_replace: str = '_petsard|_replace' # customized name for non-conflict
        colname_suffix: str = '|_petsard|_right' # customized suffix for non-conflict
        right_col: str = None

        # 1. record common_columns and their dtype
        #   common_columns should belong
        #   'full_expt_name' (SAVE_REPORT_KEY)
        #   or ALLOWED_IDX_MODULE
        common_columns = [
            col for col in df1.columns if col in df2.columns
        ]
        common_columns = [
            col for col in common_columns if col in allow_common_columns
        ]
        df1_common_dtype = {col: df1[col].dtype for col in common_columns}
        df2_common_dtype = {col: df2[col].dtype for col in common_columns}

        # 2. confirm common_columns dtype is same,
        #   if not, change dtype to object, and print warning
        for col in common_columns:
            if df1_common_dtype[col] != df2_common_dtype[col]:
                print(
                    f"Reporter: Column '{col}' in "
                    f"'{name1}' ({df1_common_dtype[col]}) and "
                    f"'{name2}' ({df2_common_dtype[col]}) "
                    f"have different dtype. Change dtype to object."
                )
                df1[col] = df1[col].astype('object')
                df2[col] = df2[col].astype('object')

        # 3. FULL OUTER JOIN df1 and df2,
        #   kept column order based on df1 than df2
        df2[colname_replace] = colname_replace
        df = pd.merge(
            df1,
            df2,
            on=common_columns,
            how='outer',
            suffixes=('', colname_suffix),
        ).reset_index(drop=True)

        # 4. replace df1 column with df2 column if replace tag is labeled
        for col in df1.columns:
            if col in allow_common_columns: # skip common_columns
                continue

            right_col = col + colname_suffix
            if right_col in df.columns:
                df.loc[
                    df[colname_replace] == colname_replace,
                    col
                ] = df[right_col]

                df.drop(columns=[right_col], inplace=True)

        df.drop(columns=[colname_replace], inplace=True) # drop replace tag

        return df

    def report(self) -> None:
        """
        Generates a report based on the provided report data.
            The report is saved to the specified output location.
        """
        if 'Reporter' not in self.result:
            raise UnexecutedError
        reporter: dict = self.result['Reporter']

        if 'warnings' in reporter:
            print(
                f"Reporter: No CSV file will be saved. "
                f"This warning can be ignored "
                f"if running with different granularity config."
            )
            return

        if not all(key in reporter for key in ['eval_expt_name', 'report']):
            raise ConfigError
        eval_expt_name: str = reporter['eval_expt_name']
        # petsard[Report]_{eval_expt_name}
        full_output: str = f"{self.config['output']}[Report]_{eval_expt_name}"

        report: pd.DataFrame = reporter['report']
        if report is None:
            # the unexpected report is None without warnings
            raise UnexecutedError

        self._save(
            data=report,
            full_output=full_output
        )
