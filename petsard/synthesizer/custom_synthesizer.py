import logging
from typing import Any

import pandas as pd

from petsard.exceptions import ConfigError
from petsard.loader import Metadata
from petsard.synthesizer.synthesizer_base import BaseSynthesizer
from petsard.util import load_external_module


class CustomSynthesizer(BaseSynthesizer):
    """
    Adapter class for Custom synthesizer as method = 'custom_method'
    """

    REQUIRED_METHODS: dict[str, str] = {
        "__init__": ["config", "metadata"],
        "fit": ["data"],
        "sample": [],
    }

    def __init__(self, config: dict, metadata: Metadata = None):
        """
        Args:
            config (dict): The configuration assign by Synthesizer
            metadata (Metadata, optional): The metadata object.

        Attributes:
            logger (logging.Logger): The logger object.
            config (dict): The configuration of the synthesizer_base.
        """
        super().__init__(config, metadata)
        self.logger: logging.Logger = logging.getLogger(
            f"PETsARD.{self.__class__.__name__}"
        )

        if "module_path" not in self.config:
            error_msg: str = (
                "Module path (module_path) is not provided in the configuration."
            )
            self.logger.error(error_msg)
            raise ConfigError(error_msg)

        if "class_name" not in self.config:
            error_msg: str = (
                "Class name (class_name) is not provided in the configuration."
            )
            self.logger.error(error_msg)
            raise ConfigError(error_msg)

        synthesizer_class: Any = None
        _, synthesizer_class = load_external_module(
            module_path=self.config["module_path"],
            class_name=self.config["class_name"],
            logger=self.logger,
            required_methods=self.REQUIRED_METHODS,
        )
        self._synthesizer = synthesizer_class(config=config, metadata=metadata)

    def _fit(self, data: pd.DataFrame) -> None:
        """
        Fit the synthesizer.
            _synthesizer should be initialized in this method.

        Args:
            data (pd.DataFrame): The data to be fitted.
        """
        self._synthesizer.fit(data)

    def _sample(self) -> pd.DataFrame:
        """
        Sample from the fitted synthesizer.

        Return:
            (pd.DataFrame): The synthesized data.
        """
        return self._synthesizer.sample()
