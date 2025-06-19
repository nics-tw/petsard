import logging
from typing import Any

import pandas as pd

from petsard.exceptions import ConfigError
from petsard.loader import Loader
from petsard.metadater import SchemaMetadata
from petsard.synthesizer.synthesizer_base import BaseSynthesizer


class CustomDataSynthesizer(BaseSynthesizer):
    """
    Adapter class for Custom synthesizer as method = 'custom_data'
    """

    LOADER_REQUIRED_CONFIGS: list[str] = ["filepath", "method"]
    EXCLUDED_CONFIGS_FROM_SYNTHESIZER_REQUIRED: list[str] = [
        "syn_method",
        "sample_num_rows",
    ]

    def __init__(self, config: dict, metadata: SchemaMetadata = None):
        """
        Args:
            config (dict): The configuration assign by Synthesizer
            metadata (SchemaMetadata, optional): The schema metadata object.

        Attributes:
            _logger (logging.Logger): The logger object.
            config (dict): The configuration of the synthesizer_base.
            _impl (Any): The synthesizer object.
        """
        super().__init__(config, metadata)
        self._logger: logging.Logger = logging.getLogger(
            f"PETsARD.{self.__class__.__name__}"
        )

    def _load_by_loader(self) -> pd.DataFrame:
        """
        Load data from the given filepath and config by PETsARD Loader.

        Return:
            (pd.DataFrame): The loaded

        Raises:
            ConfigError: If the 'filepath' or 'method' parameter is not provided, or the configuration is invalid.
        """
        if not any(key in self.config for key in self.LOADER_REQUIRED_CONFIGS):
            error_msg: str = "The 'filepath' or 'method' parameter is required for the 'custom_data' method."
            self._logger.error(error_msg)
            raise ConfigError(error_msg)

        filtered_config: dict = {
            k: v
            for k, v in self.config.items()
            if k not in self.EXCLUDED_CONFIGS_FROM_SYNTHESIZER_REQUIRED
            and v is not None
        }
        try:
            loader = Loader(**filtered_config)
        except Exception as e:
            error_msg: str = f"Unable to load data from the given filepath and config {filtered_config}: {e}"
            self._logger.error(error_msg)
            raise ConfigError(error_msg)

        data: pd.DataFrame = None
        data, _ = loader.load()
        if "sample_num_rows" in self.config and self.config["sample_num_rows"] > 0:
            sample_num_rows: int = self.config["sample_num_rows"]
            error_msg: str = (
                f"The 'sample_num_rows' parameter is not required for the 'custom_data' method, "
                f"but you have provided it with a value of {sample_num_rows}. "
                f"If the input data exceeds this number of rows, "
                f"PETsARD will only use the first {sample_num_rows} rows."
            )
            self._logger.warning(error_msg)

            if sample_num_rows < data.shape[0]:
                data = data.iloc[:sample_num_rows]

        return data

    def _fit(self, data: pd.DataFrame) -> None:
        """
        Fit the synthesizer.
            _impl should be initialized in this method.

        Args:
            data (pd.DataFrame): The data to be fitted.
        """
        self._impl: Any = object()  # avoid check

    def _sample(self) -> pd.DataFrame:
        """
        Sample from the fitted synthesizer.

        Return:
            (pd.DataFrame): The synthesized data.
        """
        return self._load_by_loader()
