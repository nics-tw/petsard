import pandas as pd

from petsard.evaluator.evaluator_base import BaseEvaluator
from petsard.exceptions import ConfigError
from petsard.utils import load_external_module


class CustomEvaluator(BaseEvaluator):
    """
    Adapter class for Custom evaluator as method = 'custom_method'
    """

    REQUIRED_METHODS: dict[str, str] = {
        "__init__": ["config"],
        "eval": ["data"],
    }

    def __init__(self, config: dict):
        """
        Args:
            config (dict): The configuration assign by Synthesizer

        Attributes:
            _logger (logging.Logger): The logger object.
            config (dict): The configuration of the evaluator_base.
            _impl (Any): The evaluator
            REQUIRED_INPUT_KEYS (list[str]): The required input keys for the evaluator.
            AVAILABLE_SCORES_GRANULARITY (list[str]): The available scores granularity.
        """
        super().__init__(config)

        if "module_path" not in self.config:
            error_msg: str = (
                "Module path (module_path) is not provided in the configuration."
            )
            self._logger.error(error_msg)
            raise ConfigError(error_msg)

        if "class_name" not in self.config:
            error_msg: str = (
                "Class name (class_name) is not provided in the configuration."
            )
            self._logger.error(error_msg)
            raise ConfigError(error_msg)

        evaluator_class: callable = None

        # Use demo-specific module loading for better path resolution
        try:
            from demo.utils import load_demo_module

            _, evaluator_class = load_demo_module(
                module_path=self.config["module_path"],
                class_name=self.config["class_name"],
                logger=self._logger,
                required_methods=self.REQUIRED_METHODS,
            )
        except ImportError:
            # Fallback to core function if demo utils not available
            _, evaluator_class = load_external_module(
                module_path=self.config["module_path"],
                class_name=self.config["class_name"],
                logger=self._logger,
                required_methods=self.REQUIRED_METHODS,
            )

        self.REQUIRED_INPUT_KEYS: list[str] = evaluator_class.REQUIRED_INPUT_KEYS
        self.AVAILABLE_SCORES_GRANULARITY: list[str] = (
            evaluator_class.AVAILABLE_SCORES_GRANULARITY
        )

        self._impl = evaluator_class(config=config)

    def _eval(self, data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        """
        Evaluating the evaluator.
            _impl should be initialized in this method.

        Args:
            data (dict[str, pd.DataFrame]): The data to be evaluated.

        Return:
            (dict[str, pd.DataFrame]): The evaluation result
        """
        return self._impl.eval(data=data)
