from petsard.exceptions import UnsupportedMethodError
from petsard.reporter.base_reporter import ReporterMethod
from petsard.reporter.reporter_save_data import ReporterSaveData
from petsard.reporter.reporter_save_report import ReporterSaveReport
from petsard.reporter.reporter_save_timing import ReporterSaveTiming


class ReporterMap:
    """
    Mapping of Reporter.

    Note: This class is deprecated. Use ReporterMethod enum directly instead.
    """

    SAVE_DATA: int = ReporterMethod.SAVE_DATA
    SAVE_REPORT: int = ReporterMethod.SAVE_REPORT
    SAVE_TIMING: int = ReporterMethod.SAVE_TIMING

    @classmethod
    def map(cls, method: str) -> int:
        """
        Get method mapping int value

        Args:
            method (str): reporting method
        """
        return ReporterMethod.map(method)


class Reporter:
    """
    Factory class for creating different types of reporters.
    """

    def __new__(cls, **kwargs):
        """
        Create a reporter instance based on the method specified in kwargs.

        Args:
            **kwargs: Configuration parameters including 'method' key.

        Returns:
            BaseReporter: An instance of the appropriate reporter class.

        Raises:
            UnsupportedMethodError: If the method is not supported.
        """
        config = kwargs
        method = config.get("method", "").upper()
        method_code = ReporterMethod.map(method)

        if method_code == ReporterMethod.SAVE_DATA:
            return ReporterSaveData(config)
        elif method_code == ReporterMethod.SAVE_REPORT:
            return ReporterSaveReport(config)
        elif method_code == ReporterMethod.SAVE_TIMING:
            return ReporterSaveTiming(config)
        else:
            raise UnsupportedMethodError(f"Unsupported reporter method: {method}")
