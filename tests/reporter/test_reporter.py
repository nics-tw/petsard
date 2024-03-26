import pytest

from PETsARD import Reporter
from PETsARD.reporter.reporter import (
    ReporterSaveData, ReporterSaveReport
)
from PETsARD.error import UnsupportedMethodError


class Test_Reporter:

    def test_method(self):
        rpt = Reporter(method='save_data', source='test')
        assert isinstance(rpt.reporter, ReporterSaveData) == True

        rpt = Reporter(method='save_report', granularity='global', eval='test')
        assert isinstance(rpt.reporter, ReporterSaveReport) == True

        with pytest.raises(UnsupportedMethodError):
            rpt = Reporter(method='invalid_method')