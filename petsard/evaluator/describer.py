from dataclasses import dataclass

from petsard.evaluator.data_describer import DataDescriber
from petsard.evaluator.evaluator import Evaluator, EvaluatorConfig, EvaluatorMap
from petsard.evaluator.evaluator_base import BaseEvaluator
from petsard.exceptions import UnsupportedMethodError


@dataclass
class DescriberConfig(EvaluatorConfig):
    """
    Configuration for the describer.
        Inherits from EvaluatorConfig.

    Attributes:
        _logger (logging.Logger): The logger object.
        DEFAULT_EVALUATING_METHOD (str): The default method for evaluating the data.
        DEFAULT_DESCRIBING_METHOD (str): The default method for describing the data.
        method (str): The method to be used for evaluating the data.
        method_code (int): The code of the evaluator method.
        eval_method (str): The name of the evaluator method.
            The difference between 'method' and 'eval_method' is that 'method' is the user input,
            while 'eval_method' is the actual method used for evaluating the data
        custom_params (dict): Any additional parameters to be stored in custom_params.

    """

    DEFAULT_DESCRIBING_METHOD: str = "describe"

    def __post_init__(self):
        super().__post_init__()

    def _init_eval_method(self) -> None:
        """
        Initialize the eval_method attribute based on the method_code.
            Overridden EvaluatorConfig's _init_eval_method().
        """
        error_msg: str = None

        try:
            method_code: int = EvaluatorMap.map(self.method.lower())

            # Filter method from EvaluatorMap.
            #   Remember 'default' in Describer means 'describe',
            #   but 'default' in Evaluator means 'sdmetrics-single_table-qualityreport'
            if method_code not in (EvaluatorMap.DEFAULT, EvaluatorMap.DESCRIBE):
                error_msg = f"Unsupported describer method: {self.method}"
                self._logger.error(error_msg)
                raise UnsupportedMethodError(error_msg)

            self.method_code: int = method_code
            self._logger.debug(
                f"Mapped evaluating method '{self.method}' to code {self.method_code}"
            )
        except KeyError:
            error_msg = f"Unsupported describer method: {self.method}"
            self._logger.error(error_msg)
            raise UnsupportedMethodError(error_msg)

        # Set the default
        self.eval_method: str = (
            self.DEFAULT_DESCRIBING_METHOD
            if self.method_code == EvaluatorMap.DEFAULT
            else self.method
        )
        self._logger.info(
            f"DescriberConfig initialized with method: {self.method}, eval_method: {self.eval_method}"
        )


class Describer(Evaluator):
    """
    The Describer class is responsible generate statistical summaries
    and insights from datasets.
    """

    DESCIRBER_MAP: dict[int, BaseEvaluator] = {
        EvaluatorMap.DEFAULT: DataDescriber,
        EvaluatorMap.DESCRIBE: DataDescriber,
    }

    def __init__(self, method: str, **kwargs):
        """
        Args:
            method (str): The method to be used for evaluating the data.
            **kwargs: Any additional parameters to be stored in custom_params.

        Attr:
            _logger (logging.Logger): The logger object.
            config (DescriberConfig): The configuration parameters for the describer.
            _impl (BaseEvaluator): The evaluator object.
        """
        super().__init__(method, **kwargs)

    def _configure_implementation(self, method: str, **kwargs) -> None:
        """
        Configure the describer's implementation based on the specified method.
            Overridden Evaluator's _configure_implementation().

        Args:
            method (str): The method to be used for describe the data.
            **kwargs: Any additional parameters to be stored in custom_params.
        """
        # Initialize the EvaluatorConfig object
        self.config: DescriberConfig = DescriberConfig(method=method)
        self._logger.debug("DescriberConfig successfully initialized")

        # Add custom parameters to the config
        if kwargs:
            self._logger.debug(
                f"Additional keyword arguments provided: {list(kwargs.keys())}"
            )
            self.config.update({"custom_params": kwargs})
            self._logger.debug("Config successfully updated with custom parameters")
        else:
            self._logger.debug("No additional parameters provided")

    def _create_evaluator_class(self) -> BaseEvaluator:
        """
        Create a Evaluator object with the configuration parameters.
            Overridden Evaluator's _create_evaluator_class().

        Returns:
            BaseEvaluator: The evaluator object.
        """
        return self.DESCIRBER_MAP[self.config.method_code]
        return self.DESCIRBER_MAP[self.config.method_code]
        return self.DESCIRBER_MAP[self.config.method_code]
