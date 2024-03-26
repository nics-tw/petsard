import pandas as pd
import pytest

from PETsARD import Reporter
from PETsARD.reporter.reporter import (
    ReporterSaveData,
    ReporterSaveReport,
)
from PETsARD.reporter.utils import (
    convert_full_expt_tuple_to_name,
    convert_full_expt_name_to_tuple,
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
    data['data'][('Evaluator', 'test1_[global]')] = \
        pd.DataFrame({
            'Evaluator': ['test1_[global]'],
            'Score': [0.9],
            'ScoreA': [0.8],
        })
    data['data'][('Evaluator', 'test2_[global]')] = \
        pd.DataFrame({
            'Evaluator': ['test2_[global]'],
            'Score': [0.1],
            'ScoreB': [0.2],
        })
    data['data'][('Evaluator', 'test1_[columnwise]')] = \
        pd.DataFrame({
            'Evaluator': ['test1_[columnwise]', 'test1_[columnwise]'],
            'column': ['col1', 'col2'],
            'Score': [0.9, 0.8],
            'ScoreA': [0.7, 0.6],
        })
    data['data'][('Evaluator', 'test2_[columnwise]')] = \
        pd.DataFrame({
            'Evaluator': ['test2_[columnwise]', 'test2_[columnwise]'],
            'column': ['col1', 'col2'],
            'Score': [0.1, 0.2],
            'ScoreB': [0.3, 0.4],
        })

    return data


@pytest.fixture
def sample_full_expt_tuple_1():
    def _sample_full_expt_tuple_1(case: int):
        if case == 2:
            return ('Loader', 'default', 'Preprocessor', 'test_low_dash')
        else: # case 1
            return ('Loader', 'default', 'Preprocessor', 'default')
    return _sample_full_expt_tuple_1


@pytest.fixture
def sample_full_expt_name_1():
    def _sample_full_expt_name_1(case: int):
        if case == 2:
            return 'Loader[default]_Preprocessor[test_low_dash]'
        else: # case 1
            return 'Loader[default]_Preprocessor[default]'
    return _sample_full_expt_name_1


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

class Test_utils:
    """
    A test class for the utility functions in the reporter module.
    """

    def test_convert_full_expt_tuple_to_name(
        self,
        sample_full_expt_tuple_1,
        sample_full_expt_name_1,
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
        for case in range(1,2+1,1):
            full_expt_tuple: tuple = sample_full_expt_tuple_1(case=case)
            full_expt_name: str = sample_full_expt_name_1(case=case)
            assert convert_full_expt_tuple_to_name(full_expt_tuple) \
                == full_expt_name

    def test_convert_full_expt_name_to_tuple(
        self,
        sample_full_expt_name_1,
        sample_full_expt_tuple_1,
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
        for case in range(1,2+1,1):
            full_expt_name: str = sample_full_expt_name_1(case=case)
            full_expt_tuple: tuple = sample_full_expt_tuple_1(case=case)
            assert convert_full_expt_name_to_tuple(full_expt_name) \
                == full_expt_tuple