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


class MetadataError(Exception):
    """
    Exception raised for errors related to metadata.
    """

    pass


class UnableToLoadError(Exception):
    """
    Exception raised when an object is unable to be loaded.
    """

    pass


class BenchmarkDatasetsError(Exception):
    """
    Exception raised for errors related to benchmark datasets.
    """

    pass


class UnableToFollowMetadataError(Exception):
    """
    Exception raised when an object is unable to follow metadata.
    """

    pass


class UnsupportedMethodError(Exception):
    """
    Exception raised when an unsupported synthesizing/evaluating method is used.
    """

    pass


class UncreatedError(Exception):
    """
    Exception raised when an object is not created.
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


class CustomMethodEvaluatorError(Exception):
    """
    Exception raised when an error occurs in the custom method evaluator.
    """

    pass
