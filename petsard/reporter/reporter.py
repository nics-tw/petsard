from petsard.exceptions import UnsupportedMethodError
from petsard.reporter.reporter_save_data import ReporterSaveData
from petsard.reporter.reporter_save_report import ReporterSaveReport
from petsard.reporter.reporter_save_timing import ReporterSaveTiming


class ReporterMap:
    """
    Mapping of Reporter.
    """

    SAVE_DATA: int = 1
    SAVE_REPORT: int = 2
    SAVE_TIMING: int = 3

    @classmethod
    def map(cls, method: str) -> int:
        """
        Get method mapping int value

        Args:
            method (str): reporting method
        """
        try:
            return cls.__dict__[method.upper()]
        except KeyError as err:
            raise UnsupportedMethodError from err


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
        method_code = ReporterMap.map(method)

        if method_code == ReporterMap.SAVE_DATA:
            return ReporterSaveData(config)
        elif method_code == ReporterMap.SAVE_REPORT:
            return ReporterSaveReport(config)
        elif method_code == ReporterMap.SAVE_TIMING:
            return ReporterSaveTiming(config)
        else:
            raise UnsupportedMethodError(f"Unsupported reporter method: {method}")
