import re

import numpy as np
import pandas as pd
import pytest

from PETsARD import Reporter
from PETsARD.reporter.reporter import (
    ReporterSaveData,
    ReporterSaveReport,
    ReporterSaveReportMap,
)
from PETsARD.reporter.utils import (
    convert_full_expt_tuple_to_name,
    convert_full_expt_name_to_tuple,
    convert_eval_expt_name_to_tuple,
)
from PETsARD.error import (
    ConfigError,
    UnsupportedMethodError,
)


# shared evaluation data
@pytest.fixture
def sample_reporter_input():
    data: dict = {}
    data['data'] = {}
    temp_data = {}

    test1_global_name = ('Evaluator', 'test1_[global]')
    test1_global = pd.DataFrame({
        'Score': [0.9],
        'ScoreA': [0.8],
    })

    test2_global_name = ('Evaluator', 'test2_[global]')
    test2_global = pd.DataFrame({
        'Score': [0.1],
        'ScoreB': [0.2],
    })

    test1_columnwise_name = ('Evaluator', 'test1_[columnwise]')
    test1_columnwise = pd.DataFrame({
        'index': ['col1', 'col2'],
        'Score': [0.9, 0.8],
        'ScoreA': [0.7, 0.6],
    })
    test1_columnwise.set_index('index', inplace=True)

    test2_columnwise_name = ('Evaluator', 'test2_[columnwise]')
    test2_columnwise = pd.DataFrame({
        'index': ['col1', 'col2'],
        'Score': [0.1, 0.2],
        'ScoreB': [0.3, 0.4],
    })
    test2_columnwise.set_index('index', inplace=True)

    test1_pairwise_name = ('Evaluator', 'test1_[pairwise]')
    test1_pairwise = pd.DataFrame({
        'level_0': ['col1', 'col1', 'col2', 'col2'],
        'level_1': ['col1', 'col2', 'col1', 'col2'],
        'Score': [0.9, 0.8, 0.7, 0.6],
        'ScoreA': [0.5, 0.4, 0.3, 0.2],
    })
    test1_pairwise.set_index(['level_0', 'level_1'], inplace=True)

    test2_pairwise_name = ('Evaluator', 'test2_[pairwise]')
    test2_pairwise = pd.DataFrame({
        'level_0': ['col1', 'col1', 'col2', 'col2'],
        'level_1': ['col1', 'col2', 'col1', 'col2'],
        'Score': [0.1, 0.2, 0.3, 0.4],
        'ScoreA': [0.5, 0.6, 0.7, 0.8],
    })
    test2_pairwise.set_index(['level_0', 'level_1'], inplace=True)

    test3_name = ('Postprocessor', 'test3')
    test3 = pd.DataFrame({
        'col1': [0.1, 0.2, 0.3],
        'col2': [0.9, 0.8, 0.7],
    })

    temp_data_dict = {
        test1_global_name: test1_global,
        test2_global_name: test2_global,
        test1_columnwise_name: test1_columnwise,
        test2_columnwise_name: test2_columnwise,
        test1_pairwise_name: test1_pairwise,
        test2_pairwise_name: test2_pairwise,
        test3_name: test3,
    }
    for key, value in temp_data_dict.items():
        temp_data[key] = value
    data['data'] = temp_data

    return data


@pytest.fixture
def sample_reporter_output():
    def _sample_reporter_output(case: str) -> pd.DataFrame:
        if case == 'global-process':
            return pd.DataFrame(data={
                'full_expt_name': ['Evaluator[global]'],
                'Evaluator': ['[global]'],
                'test1_Score': [0.9],
                'test1_ScoreA': [0.8],
                'test2_Score': [0.1],
                'test2_ScoreB': [0.2],
            })
        elif case == 'columnwise-process':
            return pd.DataFrame(data={
                'full_expt_name': [
                    'Evaluator[columnwise]', 'Evaluator[columnwise]',
                ],
                'Evaluator': [
                    '[columnwise]', '[columnwise]',
                ],
                'column': ['col1', 'col2'],
                'test1_Score': [0.9, 0.8],
                'test1_ScoreA': [0.7, 0.6],
                'test2_Score': [0.1, 0.2],
                'test2_ScoreB': [0.3, 0.4],
            })
        elif case == 'pairwise-process':
            return pd.DataFrame(data={
                'full_expt_name': [
                    'Evaluator[pairwise]', 'Evaluator[pairwise]',
                    'Evaluator[pairwise]', 'Evaluator[pairwise]',
                ],
                'Evaluator': [
                    '[pairwise]', '[pairwise]', '[pairwise]', '[pairwise]',
                ],
                'column1': ['col1', 'col1', 'col2', 'col2'],
                'column2': ['col1', 'col2', 'col1', 'col2'],
                'test1_Score': [0.9, 0.8, 0.7, 0.6],
                'test1_ScoreA': [0.5, 0.4, 0.3, 0.2],
                'test2_Score': [0.1, 0.2, 0.3, 0.4],
                'test2_ScoreA': [0.5, 0.6, 0.7, 0.8],
            })
        else:  # case 'global'
            return pd.DataFrame(data={
                'Score': [0.1, 0.9],
                'ScoreA': [np.nan, 0.8],
                'ScoreB': [0.2, np.nan],
            })
    return _sample_reporter_output


@pytest.fixture
def sample_full_expt_tuple():
    def _sample_full_expt_tuple(case: int) -> tuple[str]:
        if case == 2:
            return ('Loader', 'default', 'Preprocessor', 'test_low_dash')
        elif case == 3:
            return ('Loader', 'default', 'Preprocessor', 'default', 'Evaluator', 'test[global]')
        else:  # case 1
            return ('Loader', 'default', 'Preprocessor', 'default')
    return _sample_full_expt_tuple


@pytest.fixture
def sample_full_expt_name():
    def _sample_full_expt_name(case: int) -> tuple[str]:
        if case == 2:
            return 'Loader[default]_Preprocessor[test_low_dash]'
        elif case == 3:
            return ('Loader[default]_Preprocessor[default]_Evaluator[test[global]]')
        else:  # case 1
            return 'Loader[default]_Preprocessor[default]'
    return _sample_full_expt_name


@pytest.fixture
def sample_eval_expt_tuple():
    def _sample_eval_expt_tuple(case: int) -> tuple[str]:
        if case == 2:
            return ('desc', 'columnwise')
        elif case == 3:
            return ('desc', 'pairwise')
        else:  # case 1
            return ('sdmetrics-qual', 'global')
    return _sample_eval_expt_tuple


@pytest.fixture
def sample_eval_expt_name():
    def _sample_eval_expt_name(case: int) -> str:
        if case == 2:
            return 'desc_[columnwise]'
        elif case == 3:
            return 'desc_[pairwise]'
        else:  # case 1
            return 'sdmetrics-qual_[global]'
    return _sample_eval_expt_name


class Test_Reporter:
    """
    A test class for the Reporter class.
    """

    def test_method(self):
        """
        Test case for the arg. `method` of Reporter class.

        - The Reporter.reporter will be created as ReporterSaveData when:
            - method='save_data', source='test'
        - The Reporter.reporter will be created as ReporterSaveReport when:
            - method='save_report', granularity='global', eval='test'
        - The Reporter will raise an UnsupportedMethodError when:
            - method='invalid_method'
        """
        rpt = Reporter(method='save_data', source='test')
        assert isinstance(rpt.reporter, ReporterSaveData) == True

        rpt = Reporter(method='save_report', granularity='global', eval='test')
        assert isinstance(rpt.reporter, ReporterSaveReport) == True

        with pytest.raises(UnsupportedMethodError):
            Reporter(method='invalid_method')

    def test_method_save_data(self):
        """
        Test case for the arg. `method` = 'save_data' of Reporter class.

        - The Reporter will raise an UnsupportedMethodError when:
            - method='save_data' but no source is provided
        """
        with pytest.raises(ConfigError):
            Reporter(method='save_data')

    def test_method_save_report(self):
        """
        Test case for the arg. `method` = 'save_report' of Reporter class.

        - The Reporter will be created when:
            - method='save_report', granularity='global', but no eval is provided
        - The Reporter will raise an UnsupportedMethodError when:
            - method='save_report' but no granularity or eval is provided
            - method='save_report', eval='test', but no granularity is provided
        """
        rpt = Reporter(method='save_report', granularity='global')
        assert isinstance(rpt.reporter, ReporterSaveReport) == True

        with pytest.raises(ConfigError):
            Reporter(method='save_report')
        with pytest.raises(ConfigError):
            Reporter(method='save_report', eval='test')


class Test_ReporterSaveData:
    """
    A test class for the ReporterSaveData class.
    """

    def test_source(self):
        """
        Test case for the arg. `source` of ReporterSaveData class.

        - ReporterSaveData will be created when `source` is set to:
            - a string
            - a list of strings
        - ReporterSaveData will raise a ConfigError when `source` is set to:
            - didn't setting
            - other non-str/List[str] format, e.g.
                - a float value
                - a list containing a float value
                - a tuple
        """
        cfg = {}
        cfg['method'] = 'save_data'

        with pytest.raises(ConfigError):
            ReporterSaveData(config=cfg)

        cfg['source'] = 'test'
        rpt = ReporterSaveData(config=cfg)
        assert isinstance(rpt, ReporterSaveData) == True

        cfg['source'] = ['test1', 'test2']
        rpt = ReporterSaveData(config=cfg)
        assert isinstance(rpt, ReporterSaveData) == True

        with pytest.raises(ConfigError):
            cfg['source'] = 0.8
            ReporterSaveData(config=cfg)

        with pytest.raises(ConfigError):
            cfg['source'] = ['test', 0.8]
            ReporterSaveData(config=cfg)

        with pytest.raises(ConfigError):
            cfg['source'] = ('test1', 'test2')
            ReporterSaveData(config=cfg)


class Test_ReporterSaveReport:
    """
    A test class for the ReporterSaveReport class.
    """

    def test_granularity(self):
        """
        Test case for the arg. `granularity` of ReporterSaveReport class.

        - ReporterSaveReport will be created when `granularity` is set to:
            - 'global'
            - 'columnwise'
            - 'pairwise'
        - ReporterSaveReport will raise a ConfigError when `granularity` is set to:
            - didn't setting
            - other string such as 'invalid_method'
            - other non-str format, e.g. a list
        """
        cfg = {}
        cfg['method'] = 'save_report'
        cfg['eval'] = 'test'

        with pytest.raises(ConfigError):
            ReporterSaveReport(config=cfg)

        cfg['granularity'] = 'global'
        rpt = ReporterSaveReport(config=cfg)
        assert isinstance(rpt, ReporterSaveReport) == True

        cfg['granularity'] = 'columnwise'
        rpt = ReporterSaveReport(config=cfg)
        assert isinstance(rpt, ReporterSaveReport) == True

        cfg['granularity'] = 'pairwise'
        rpt = ReporterSaveReport(config=cfg)
        assert isinstance(rpt, ReporterSaveReport) == True

        with pytest.raises(UnsupportedMethodError):
            cfg['granularity'] = 'invalid_method'
            ReporterSaveReport(config=cfg)

        with pytest.raises(ConfigError):
            cfg['granularity'] = ['global', 'columnwise']
            ReporterSaveReport(config=cfg)

    def test_eval(self):
        """
        Test case for the arg. `eval` of ReporterSaveReport class.

        - ReporterSaveReport will be created when `eval` is set to:
            - a string
            - a list of strings
            - didn't setting
        - ReporterSaveReport will raise a ConfigError when `eval` is set to:
            - other non-str/List[str] format, e.g.
                - a float value
                - a list containing a float value
                - a tuple
        """
        cfg = {}
        cfg['method'] = 'save_report'
        cfg['granularity'] = 'global'

        rpt = ReporterSaveReport(config=cfg)
        assert isinstance(rpt, ReporterSaveReport) == True

        cfg['eval'] = 'test'
        rpt = ReporterSaveReport(config=cfg)
        assert isinstance(rpt, ReporterSaveReport) == True

        cfg['eval'] = ['test1', 'test2']
        rpt = ReporterSaveReport(config=cfg)
        assert isinstance(rpt, ReporterSaveReport) == True

        with pytest.raises(ConfigError):
            cfg['eval'] = 0.8
            ReporterSaveReport(config=cfg)

        with pytest.raises(ConfigError):
            cfg['eval'] = ['test', 0.8]
            ReporterSaveReport(config=cfg)

        with pytest.raises(ConfigError):
            cfg['eval'] = ('test1', 'test2')
            ReporterSaveReport(config=cfg)

    def test_create(self, sample_reporter_input, sample_reporter_output):
        """
        Test case for `create()` function of ReporterSaveReport class.

        - ReporterSaveReport will successfully create a report when:
            - the granularity been set to 'global''
            - the granularity been set to 'columnwise''
            - the granularity been set to 'pairwise''
        """

        def _test_create(
            data: dict, granularity: str
        ) -> tuple[ReporterSaveReport, pd.DataFrame]:
            cfg: dict = {}
            cfg['method'] = 'save_report'
            cfg['granularity'] = granularity

            rpt = ReporterSaveReport(config=cfg)
            rpt.create(data=data['data'])
            expected_rpt = sample_reporter_output(
                case=f"{granularity}-process")

            return (rpt, expected_rpt)

        data: dict = sample_reporter_input
        granularity: str = None

        granularity = 'global'
        rpt, expected_rpt = _test_create(data, granularity)
        assert rpt.result['Reporter']['eval_expt_name'] == f"[{granularity}]"
        assert rpt.result['Reporter']['granularity'] == f"{granularity}"
        pd.testing.assert_frame_equal(
            rpt.result['Reporter']['report'], expected_rpt)

        granularity = 'columnwise'
        rpt, expected_rpt = _test_create(data, granularity)
        assert rpt.result['Reporter']['eval_expt_name'] == f"[{granularity}]"
        assert rpt.result['Reporter']['granularity'] == f"{granularity}"
        pd.testing.assert_frame_equal(
            rpt.result['Reporter']['report'], expected_rpt)

        granularity = 'pairwise'
        rpt, expected_rpt = _test_create(data, granularity)
        assert rpt.result['Reporter']['eval_expt_name'] == f"[{granularity}]"
        assert rpt.result['Reporter']['granularity'] == f"{granularity}"
        pd.testing.assert_frame_equal(
            rpt.result['Reporter']['report'], expected_rpt)

    def test_process_report_data(self, sample_reporter_input):
        """
        Test case for the _process_report_data function.

        - The column names of the input DataFrame will correctly
            rename columns and add column when:
            - the input DataFrame is a global granularity
            - the input DataFrame is a columnwise granularity
            - the input DataFrame is a pairwise granularity
        - The skip_flag will be set to True when:
            - the input DataFrame is a non-Evaluator/Describer e.g. Postprocessor
        """
        def _test_process_report_data(
            report: pd.DataFrame,
            full_expt_tuple: tuple
        ):
            granularity: str = None
            output_eval_name: str = None
            skip_flag: bool = None
            rpt: pd.DataFrame = None

            try:
                granularity = convert_eval_expt_name_to_tuple(
                    full_expt_tuple[1])[1]
            except TypeError:
                granularity = 'global'
            output_eval_name = f"[{granularity}]"
            skip_flag, rpt = ReporterSaveReport._process_report_data(
                report=report,
                full_expt_tuple=full_expt_tuple,
                eval_pattern=re.escape(f"_[{granularity}]") + "$",
                granularity=granularity,
                output_eval_name=output_eval_name,
            )
            return skip_flag, rpt

        data: dict = sample_reporter_input
        full_expt_tuple: tuple = None
        skip_flag: bool = None
        rpt: pd.DataFrame = None

        full_expt_tuple = ('Evaluator', 'test1_[global]')
        skip_flag, rpt = _test_process_report_data(
            report=data['data'][full_expt_tuple],
            full_expt_tuple=full_expt_tuple,
        )
        assert skip_flag == False
        assert rpt.columns.tolist() == [
            'full_expt_name', 'Evaluator', 'test1_Score', 'test1_ScoreA'
        ]

        full_expt_tuple = ('Evaluator', 'test1_[columnwise]')
        skip_flag, rpt = _test_process_report_data(
            report=data['data'][full_expt_tuple],
            full_expt_tuple=full_expt_tuple,
        )
        assert skip_flag == False
        assert rpt.columns.tolist() == [
            'full_expt_name', 'Evaluator', 'column',
            'test1_Score', 'test1_ScoreA'
        ]

        full_expt_tuple = ('Evaluator', 'test1_[pairwise]')
        skip_flag, rpt = _test_process_report_data(
            report=data['data'][full_expt_tuple],
            full_expt_tuple=full_expt_tuple,
        )
        assert skip_flag == False
        assert rpt.columns.tolist() == [
            'full_expt_name', 'Evaluator', 'column1', 'column2',
            'test1_Score', 'test1_ScoreA'
        ]

        full_expt_tuple = ('Postprocessor', 'test3')
        skip_flag, rpt = _test_process_report_data(
            report=data['data'][full_expt_tuple],
            full_expt_tuple=full_expt_tuple,
        )
        assert skip_flag == True
        assert rpt is None

    def test_safe_merge(self, sample_reporter_input, sample_reporter_output):
        """
        Test case for the _safe_merge( function.

        - The FULL OUTER JOIN will correctly
            rename columns and add column when:
            - Pure data with only 'Score' column is overlapping
            - the global granularity after _process_report_data()
            - the same global granularity data with modification
                after _process_report_data()
            - the columnwise granularity after _process_report_data()
            - the pairwise granularity after _process_report_data()
        """
        def _test_safe_merge(
            data: dict,
            granularity: str,
            name1: tuple[str],
            name2: tuple[str],
            process: bool = False,
            modify_test1: bool = False,
        ):
            data1: pd.DataFrame = data['data'][name1].copy()
            data2: pd.DataFrame = data['data'][name2].copy()
            if modify_test1:
                data1['Score'] = 0.66
                name1 = ('Postprocessor', 'Before') + name1
                name2 = ('Postprocessor', 'After') + name2
            if process:
                output_eval_name = f"[{granularity}]"
                skip_flag, data1 = ReporterSaveReport._process_report_data(
                    report=data1,
                    full_expt_tuple=name1,
                    eval_pattern=re.escape(f"_[{granularity}]") + "$",
                    granularity=granularity,
                    output_eval_name=output_eval_name,
                )
                skip_flag, data2 = ReporterSaveReport._process_report_data(
                    report=data2,
                    full_expt_tuple=name2,
                    eval_pattern=re.escape(f"_[{granularity}]") + "$",
                    granularity=granularity,
                    output_eval_name=output_eval_name,
                )
            rpt = ReporterSaveReport._safe_merge(
                data1, data2,
                name1, name2,
            )
            return rpt
        data: dict = sample_reporter_input
        granularity: str = None
        name1: tuple[str] = None
        name2: tuple[str] = None
        rpt: pd.DataFrame = None
        expected_rpt: pd.DataFrame = None

        granularity = 'global'
        name1 = ('Evaluator', f"test1_[{granularity}]")
        name2 = ('Evaluator', f"test2_[{granularity}]")
        rpt = _test_safe_merge(data, granularity, name1, name2)
        expected_rpt = sample_reporter_output(case='global')
        pd.testing.assert_frame_equal(rpt, expected_rpt)

        rpt = _test_safe_merge(data, granularity, name1, name2, process=True)
        expected_rpt = sample_reporter_output(case='global-process')
        pd.testing.assert_frame_equal(rpt, expected_rpt)

        granularity = 'global'
        name1 = ('Evaluator', f"test1_[{granularity}]")
        name2 = ('Evaluator', f"test1_[{granularity}]")
        rpt = _test_safe_merge(data, granularity,
                               name1, name2, process=True, modify_test1=True)
        expected_rpt = pd.DataFrame(data={
            'full_expt_name': [
                'Postprocessor[After]_Evaluator[global]',
                'Postprocessor[Before]_Evaluator[global]',],
            'Postprocessor': ['After', 'Before',],
            'Evaluator': ['[global]', '[global]'],
            'test1_Score': [0.9, 0.66],
            'test1_ScoreA': [0.8, 0.8],
        }) # seems it will rearrange the row order, and cannot close.
        pd.testing.assert_frame_equal(rpt, expected_rpt)

        granularity = 'columnwise'
        name1 = ('Evaluator', f"test1_[{granularity}]")
        name2 = ('Evaluator', f"test2_[{granularity}]")
        rpt = _test_safe_merge(data, granularity, name1, name2, process=True)
        expected_rpt = sample_reporter_output(case='columnwise-process')
        pd.testing.assert_frame_equal(rpt, expected_rpt)

        granularity = 'pairwise'
        name1 = ('Evaluator', f"test1_[{granularity}]")
        name2 = ('Evaluator', f"test2_[{granularity}]")
        rpt = _test_safe_merge(data, granularity, name1, name2, process=True)
        expected_rpt = sample_reporter_output(case='pairwise-process')
        pd.testing.assert_frame_equal(rpt, expected_rpt)


class Test_utils:
    """
    A test class for the utility functions in the reporter module.
    """

    def test_convert_full_expt_tuple_to_name(
        self,
        sample_full_expt_tuple,
        sample_full_expt_name,
    ):
        """
        Test case for the convert_full_expt_tuple_to_name function.

        - convert_full_expt_tuple_to_name(expt_tuple: tuple):
            will be converted to correct format string when:
            - expt_tuple = ('Loader', 'default', 'Preprocessor', 'default')
            - expt_tuple = ('Loader', 'default', 'Preprocessor', 'test_low_dash')
        """
        # ('Loader', 'default', 'Preprocessor', 'default')
        # ('Loader', 'default', 'Preprocessor', 'test_low_dash')
        # ('Loader', 'default', 'Preprocessor', 'default', 'Evaluator', 'test[global]')
        for case in range(1, 3+1, 1):
            full_expt_tuple: tuple = sample_full_expt_tuple(case=case)
            full_expt_name: str = sample_full_expt_name(case=case)
            assert convert_full_expt_tuple_to_name(full_expt_tuple) \
                == full_expt_name

    def test_convert_full_expt_name_to_tuple(
        self,
        sample_full_expt_name,
        sample_full_expt_tuple,
    ):
        """
        Test case for the convert_full_expt_name_to_tuple function.

        - convert_full_expt_name_to_tuple(expt_name: str):
            will be converted to correct format tuple when:
            - expt_name = 'Loader[default]_Preprocessor[default]'
            - expt_name = 'Loader[default]_Preprocessor[test_low_dash]'.
        """
        # 'Loader[default]_Preprocessor[default]'
        # 'Loader[default]_Preprocessor[test_low_dash]'
        # 'Loader[default]_Preprocessor[default]_Evaluator_[test[global]]'
        for case in range(1, 3+1, 1):
            full_expt_name: str = sample_full_expt_name(case=case)
            full_expt_tuple: tuple = sample_full_expt_tuple(case=case)
            assert convert_full_expt_name_to_tuple(full_expt_name) \
                == full_expt_tuple

    def convert_eval_expt_name_to_tuple(
        self,
        sample_eval_expt_name,
        sample_eval_expt_tuple,
    ):
        """
        Test case for the convert_eval_expt_name_to_tuple function.

        - convert_eval_expt_name_to_tuple(expt_name: str):
            will be converted to correct format tuple when:
            - expt_name = 'sdmetrics-qual_[global]'
            - expt_name = 'desc_[columnwise]'
            - expt_name = 'desc_[pairwise]'
        """
        # 'sdmetrics-qual_[global]'
        # 'desc_[columnwise]'
        # 'desc_[pairwise]'
        for case in range(1, 3+1, 1):
            eval_expt_name: str = sample_eval_expt_name(case=case)
            eval_expt_tuple: tuple = sample_eval_expt_tuple(case=case)
            assert convert_eval_expt_name_to_tuple(eval_expt_name) \
                == eval_expt_tuple