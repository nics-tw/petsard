import pytest

from PETsARD import Reporter
from PETsARD.reporter.reporter import (
    ReporterSaveData,
    ReporterSaveReport,
)
from PETsARD.error import (
    ConfigError,
    UnsupportedMethodError,
)

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

        - The Reporter will raise an UnsupportedMethodError when:
            - method='save_report' but no granularity or eval is provided
            - method='save_report', granularity='global', but no eval is provided
            - method='save_report', eval='test', but no granularity is provided
        """
        with pytest.raises(ConfigError):
            Reporter(method='save_report')
        with pytest.raises(ConfigError):
            Reporter(method='save_report', granularity='global')
        with pytest.raises(ConfigError):
            Reporter(method='save_report', eval='test')


class Test_ReporterSaveData:
    """
    A test class for the ReporterSaveData class.
    """

    def test_save_data_source(self):
        """
        Test case for the arg. `source` of ReporterSaveData class.

        - ReporterSaveData will be created when `source` is set to:
            - a string
            - a list of strings
        - ReporterSaveData will raise a ConfigError when `source` is set to:
            - a float value
            - a list containing a float value
            - a tuple
        """
        cfg = {}
        cfg['method'] = 'save_data'

        cfg['source'] = 'test'
        rpt = ReporterSaveData(config=cfg)
        assert isinstance(rpt.reporter, ReporterSaveData) == True

        cfg['source'] = ['test1','test2']
        rpt = ReporterSaveData(config=cfg)
        assert isinstance(rpt.reporter, ReporterSaveData) == True

        with pytest.raises(ConfigError):
            cfg['source'] = 0.8
            ReporterSaveData(config=cfg)

        with pytest.raises(ConfigError):
            cfg['source'] = ['test', 0.8]
            ReporterSaveData(config=cfg)

        with pytest.raises(ConfigError):
            cfg['source'] = ('test1','test2')
            ReporterSaveData(config=cfg)


class Test_ReporterSaveReport:
    """
    A test class for the ReporterSaveReport class.
    """