class NoConfigError(Exception):
    """
    Exception raised when there is no configuration available.
    """

    pass


class ConfigError(Exception):
    """
    Exception raised for errors related to configuration.
    """

    pass


class BenchmarkDatasetsError(Exception):
    """
    Exception raised for errors related to benchmark datasets.
    """

    pass


class UnsupportedMethodError(Exception):
    """
    Exception raised when an unsupported synthesizing/evaluating method is used.
    """

    pass


class UnfittedError(Exception):
    """
    Exception raised when an operation is performed on an object that has not been fitted yet.
    """

    pass


class UnableToSynthesizeError(Exception):
    """
    Exception raised when an object is unable to be synthesized.
    """

    pass


class UnableToEvaluateError(Exception):
    """
    Exception raised when an object is unable to be evaluated.
    """

    pass


class UnexecutedError(Exception):
    """
    Exception raised when an action is not executed.
    """

    pass
