import logging
from abc import ABC, abstractmethod
from typing import Any

import pandas as pd

from petsard.exceptions import ConfigError, UnfittedError
from petsard.loader import Metadata


class BaseSynthesizer(ABC):
    """
    Base class for all synthesizer engine implementations.
    These engines are used by the main Synthesizer to perform the actual data synthesis.
    """

    def __init__(self, config: dict, metadata: Metadata = None):
        """
        Args:
            config (dict): The configuration assign by Synthesizer
            metadata (Metadata, optional): The metadata object.

        Attributes:
            logger (logging.Logger): The logger object.
            config (dict): The configuration of the synthesizer_base.
            _synthesizer (Any): The synthesizer object.
        """
        self.logger: logging.Logger = logging.getLogger(
            f"PETsARD.{self.__class__.__name__}"
        )

        if "syn_method" not in config:
            error_msg: str = (
                "The 'syn_method' parameter is required for the synthesizer."
            )
            self.logger.error(error_msg)
            raise ConfigError(error_msg)
        if "sample_num_rows" not in config:
            error_msg: str = (
                "The 'sample_num_rows' parameter is required for the synthesizer."
            )
            self.logger.error(error_msg)
            raise ConfigError(error_msg)

        self.config: dict = config
        self._synthesizer: Any = None

    def update_config(self, config: dict) -> None:
        """
        Update the synthesizer configuration.

        Args:
            config (dict): The new configuration.
        """
        self.config.update(config)

    @abstractmethod
    def _fit(self, data: pd.DataFrame = None) -> None:
        """
        Fit the synthesizer.
            _synthesizer should be initialized in this method.

        Args:
            data (pd.DataFrame, optional): The data to be fitted.

        Raises:
            NotImplementedError: If the subclass does not implement this method
        """
        self._fit(data)
        error_msg: str = "The '_fit' method must be implemented in the derived class."
        self.logger.error(error_msg)
        raise NotImplementedError

    def fit(self, data: pd.DataFrame = None) -> None:
        """
        Fit the synthesizer to the provided data.

        This method calls the implementation-specific _fit method, which should
        train the synthesizer and prepare it for generating synthetic data.

        Args:
            data (pd.DataFrame, optional): Data to fit the synthesizer on
        """
        self._fit(data)

    @abstractmethod
    def _sample(self) -> pd.DataFrame:
        """
        Sample from the fitted synthesizer.

        Return:
            (pd.DataFrame): The synthesized data.

        Raises:
            NotImplementedError: If the subclass does not implement this method
        """
        error_msg: str = (
            "The '_sample' method must be implemented in the derived class."
        )
        self.logger.error(error_msg)
        raise NotImplementedError

    def sample(self) -> pd.DataFrame:
        """
        Generate synthetic data from the fitted synthesizer.

        This method checks if the synthesizer has been properly fitted,
        then calls the implementation-specific _sample method to generate data.

        Returns:
            pd.DataFrame: Generated synthetic data

        Raises:
            UnfittedError: If the synthesizer has not been fitted yet
        """
        if not hasattr(self, "_synthesizer") or self._synthesizer is None:
            error_msg: str = "The synthesizer has not been fitted."
            self.logger.error(error_msg)
            raise UnfittedError(error_msg)

        return self._sample()
