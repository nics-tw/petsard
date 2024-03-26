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

    def test_method(self):
        rpt = Reporter(method='save_data', source='test')
        assert isinstance(rpt.reporter, ReporterSaveData) == True

        rpt = Reporter(method='save_report', granularity='global', eval='test')
        assert isinstance(rpt.reporter, ReporterSaveReport) == True

        with pytest.raises(UnsupportedMethodError):
            Reporter(method='invalid_method')


    def test_save_data_without_source(self):
        with pytest.raises(ConfigError):
            Reporter(method='save_data')


    def test_save_report_without_granularity_or_eval(self):
        with pytest.raises(ConfigError):
            Reporter(method='save_report')
        with pytest.raises(ConfigError):
            Reporter(method='save_report', granularity='global')
        with pytest.raises(ConfigError):
            Reporter(method='save_report', eval='test')


class Test_ReporterSaveData:

    def test_save_data_source_is_str_or_list_of_str(self):
        cfg = {}
        cfg['method'] = 'save_data'

        cfg['source'] = 'test'
        rpt = Reporter(**cfg)
        assert isinstance(rpt.reporter, ReporterSaveData) == True

        cfg['source'] = ['test1','test2']
        rpt = Reporter(**cfg)
        assert isinstance(rpt.reporter, ReporterSaveData) == True

        with pytest.raises(ConfigError):
            cfg['source'] = 0.8
            Reporter(**cfg)

        with pytest.raises(ConfigError):
            cfg['source'] = ['test', 0.8]
            Reporter(**cfg)

        with pytest.raises(ConfigError):
            cfg['source'] = ('test1','test2')
            Reporter(**cfg)


