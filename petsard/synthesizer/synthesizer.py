import logging
import re
import time
from dataclasses import dataclass, field
from typing import Any, Optional

import pandas as pd

from petsard.config_base import BaseConfig
from petsard.exceptions import ConfigError, UncreatedError, UnsupportedMethodError
from petsard.metadater import SchemaMetadata
from petsard.synthesizer.custom_data import CustomDataSynthesizer
from petsard.synthesizer.custom_synthesizer import CustomSynthesizer
from petsard.synthesizer.sdv import SDVSingleTableSynthesizer
from petsard.synthesizer.synthesizer_base import BaseSynthesizer


class SynthesizerMap:
    """
    Mapping of Synthesizer.
    """

    DEFAULT: int = 1
    SDV: int = 10

    CUSTOM_DATA: int = 2
    CUSTOM_METHOD: int = 3

    @classmethod
    def map(cls, method: str) -> int:
        """
        Get suffixes mapping int value before 1st dash (-)

        Args:
            method (str): synthesizing method
        """
        # Get the string before 1st dash, if not exist, get emply ('').
        libname_match = re.match(r"^[^-]*", method)
        libname = libname_match.group() if libname_match else ""
        return cls.__dict__[libname.upper()]


@dataclass
class SynthesizerConfig(BaseConfig):
    """
    Configuration for the synthesizer.

    Attributes:
        _logger (logging.Logger): The logger object.
        DEFAULT_SYNTHESIS_METHOD (str): The default synthesizer method.
        method (str): The method to be used for synthesizing the data.
        method_code (int): The code of the synthesizer method.
        syn_method (str): The name of the synthesizer method.
            The difference between 'method' and 'syn_method' is that 'method' is the user input,
            while 'syn_method' is the actual method used for synthesizing the data
        sample_from (str): The source of the sample number of rows.
        sample_num_rows (int): The number of rows to be sampled.
        custom_params (dict): Any additional parameters to be stored in custom_params.
    """

    DEFAULT_SYNTHESIS_METHOD: str = "sdv-single_table-gaussiancopula"

    method: str = "default"
    method_code: int = None
    syn_method: str = None
    sample_from: str = "Undefined"
    sample_num_rows: int = 0
    custom_params: dict[Any, Any] = field(default_factory=dict)
    _logger: logging.Logger = None

    def __post_init__(self):
        super().__post_init__()
        self._logger.debug("Initializing SynthesizerConfig")

        try:
            self.method_code: int = SynthesizerMap.map(self.method.lower())
            self._logger.debug(
                f"Mapped synthesizing method '{self.method}' to code {self.method_code}"
            )
        except KeyError:
            error_msg: str = f"Unsupported synthesizer method: {self.method}"
            self._logger.error(error_msg)
            raise UnsupportedMethodError(error_msg)

        # Set the default
        self.syn_method: str = (
            self.DEFAULT_SYNTHESIS_METHOD
            if self.method_code == SynthesizerMap.DEFAULT
            else self.method
        )
        self._logger.info(
            f"SynthesizerConfig initialized with method: {self.method}, syn_method: {self.syn_method}"
        )


class Synthesizer:
    """
    The Synthesizer class is responsible for creating and fitting a synthesizer model,
    as well as generating synthetic data based on the fitted model.
    """

    SYNTHESIZER_MAP: dict[int, BaseSynthesizer] = {
        SynthesizerMap.DEFAULT: SDVSingleTableSynthesizer,
        SynthesizerMap.SDV: SDVSingleTableSynthesizer,
        SynthesizerMap.CUSTOM_DATA: CustomDataSynthesizer,
        SynthesizerMap.CUSTOM_METHOD: CustomSynthesizer,
    }

    def __init__(self, method: str, sample_num_rows: int = None, **kwargs) -> None:
        """
        Args:
            method (str): The method to be used for synthesizing the data.
            sample_num_rows (int, optional): The number of rows to be sampled.
            **kwargs: Any additional parameters to be stored in custom_params.

        Attributes:
            _logger (logging.Logger): The logger object.
            config (SynthesizerConfig): The configuration parameters for the synthesizer.
            _impl (BaseSynthesizer): The synthesizer object.
        """
        self._logger: logging.Logger = logging.getLogger(
            f"PETsARD.{self.__class__.__name__}"
        )
        self._logger.info(
            f"Initializing Synthesizer with method: {method}, sample_num_rows: {sample_num_rows}"
        )

        # Initialize the SynthesizerConfig object
        self.config: SynthesizerConfig = (
            SynthesizerConfig(method=method)
            if sample_num_rows is None
            else SynthesizerConfig(method=method, sample_num_rows=sample_num_rows)
        )
        self._logger.debug("SynthesizerConfig successfully initialized")

        # Add custom parameters to the config
        if kwargs:
            self._logger.debug(
                f"Additional keyword arguments provided: {list(kwargs.keys())}"
            )
            self.config.update({"custom_params": kwargs})
            self._logger.debug(
                "SynthesizerConfig successfully updated with custom parameters"
            )
        else:
            self._logger.debug("No additional parameters provided")

        self._impl: BaseSynthesizer = None
        self._logger.info("Synthesizer initialization completed")

    def _determine_sample_configuration(
        self, metadata: SchemaMetadata = None
    ) -> tuple[str, Optional[int]]:
        """
        Determine the sample configuration based on available metadata and configuration.

        This method implements a hierarchy of decision rules to determine the sampling source
        and number of rows:
        1. Use manually configured sample size if provided
        2. Extract from metadata's split information if available
        3. Use metadata's total row count if available
        4. Fall back to source data if no other information is available

        Args:
            metadata (SchemaMetadata, optional): The schema metadata containing information about the dataset

        Returns:
            (tuple[str, Optional[int]]): A tuple containing:
                - sample_from (str): Description of where the sample size was determined from
                - sample_num_rows (Optional[int]): Number of rows to sample, or None if undetermined
        """
        self._logger.debug("Determining sample configuration")
        sample_from: str = self.config.sample_from
        sample_num_rows: Optional[int] = self.config.sample_num_rows

        # 1. If manual input, use the sample number of rows from the input
        if self.config.sample_num_rows is not None:
            sample_from = "Manual input"
            sample_num_rows = self.config.sample_num_rows
            self._logger.debug(
                f"Using manually specified sample size: {sample_num_rows}"
            )

        # 2. If no manual input, get the sample number of rows from metadata
        elif metadata is not None:
            self._logger.debug("Checking metadata for sample size information")
            # Check if metadata has stats with row count information
            if metadata.stats and metadata.stats.row_count > 0:
                # Check if this is split data (look for split info in properties)
                if (
                    "split_info" in metadata.properties
                    and "train_rows" in metadata.properties["split_info"]
                ):
                    sample_from = "Splitter data"
                    sample_num_rows = metadata.properties["split_info"]["train_rows"]
                    self._logger.debug(
                        f"Using splitter train data count: {sample_num_rows}"
                    )
                else:
                    # Use total row count from schema stats
                    sample_from = "Loader data"
                    sample_num_rows = metadata.stats.row_count
                    self._logger.debug(f"Using schema row count: {sample_num_rows}")
            else:
                self._logger.debug("No row count information found in metadata stats")

        # 3. if sample_from didn't been assign, means no effective metadata been used
        if self.config.sample_from == "Undefined":
            sample_from = "Source data"
            self._logger.debug(
                "Using source data as sample source (will be determined during fit)"
            )

        self._logger.info(
            f"Sample configuration determined: source={sample_from}, rows={sample_num_rows}"
        )
        return sample_from, sample_num_rows

    def create(self, metadata: SchemaMetadata = None) -> None:
        """
        Create a synthesizer object with the given data.

        Args.:
            metadata (SchemaMetadata, optional): The schema metadata of the data.
        """
        self._logger.info("Creating synthesizer instance")
        if metadata is not None:
            self._logger.debug("Metadata provided for synthesizer creation")
        else:
            self._logger.debug("No metadata provided for synthesizer creation")

        # Determine sample configuration using internal method
        sample_from, sample_num_rows = self._determine_sample_configuration(metadata)

        self._logger.debug(
            f"Sample configuration: source={sample_from}, rows={sample_num_rows}"
        )
        self.config.update(
            {
                "sample_from": sample_from,
                "sample_num_rows": sample_num_rows,
            }
        )

        synthesizer_class = self.SYNTHESIZER_MAP[self.config.method_code]
        self._logger.debug(f"Using synthesizer class: {synthesizer_class.__name__}")

        merged_config: dict = self.config.get_params(
            param_configs=[
                {"syn_method": {"action": "include"}},
                {"sample_num_rows": {"action": "include"}},
                {"custom_params": {"action": "merge"}},
            ]
        )
        self._logger.debug(f"Merged config keys: {list(merged_config.keys())}")

        self._logger.info(f"Creating {synthesizer_class.__name__} instance")
        self._impl = synthesizer_class(
            config=merged_config,
            metadata=metadata,
        )
        self._logger.info(f"Successfully created {synthesizer_class.__name__} instance")

    def fit(self, data: pd.DataFrame = None) -> None:
        """
        Fits the synthesizer model with the given data.

        Args:
            data (pd.DataFrame):
                The data to be fitted.
                Only 'CUSTOM_DATA' method doesn't need data to fit.
        """
        if self._impl is None:
            error_msg: str = "Synthesizer not created yet, call create() first"
            self._logger.warning(error_msg)
            raise UncreatedError(error_msg)

        if data is None:
            # Should only happen for 'CUSTOM_DATA' method
            if self.config.method_code != SynthesizerMap.CUSTOM_DATA:
                error_msg: str = (
                    f"Data must be provided for fitting in {self.config.method}"
                )
                self._logger.error(error_msg)
                raise ConfigError(error_msg)

            self._logger.info("Fitting synthesizer without data")
        else:
            # In other methods, update the sample_num_rows in the synthesizer config
            self._logger.info(f"Fitting synthesizer with data shape: {data.shape}")

            if self.config.sample_from == "Source data":
                old_value: int = self.config.sample_num_rows
                self.config.update({"sample_num_rows": data.shape[0]})
                self._logger.debug(
                    f"Updated sample_num_rows from {old_value} to {data.shape[0]}"
                )

            self._impl.update_config({"sample_num_rows": data.shape[0]})
            self._logger.debug(
                f"Updated synthesizer config with sample_num_rows={data.shape[0]}"
            )

        time_start: time = time.time()

        self._logger.info(f"Starting fit process for {self.config.syn_method}")
        try:
            self._impl.fit(data=data)
            time_spent = round(time.time() - time_start, 4)
            self._logger.info(f"Fitting completed successfully in {time_spent} seconds")
        except Exception as e:
            self._logger.error(f"Error during fitting: {str(e)}")
            raise

    def sample(self) -> pd.DataFrame:
        """
        This method generates a sample using the Synthesizer object.

        Return:
            pd.DataFrame: The synthesized data.
        """
        if self._impl is None:
            self._logger.warning("Synthesizer not created or fitted yet")
            return pd.DataFrame()

        time_start: time = time.time()

        self._logger.info(
            f"Sampling {self.config.sample_num_rows} rows using {self.config.syn_method}"
        )

        try:
            data: pd.DataFrame = self._impl.sample()
            time_spent: float = round(time.time() - time_start, 4)

            sample_info: str = (
                f" (same as {self.config.sample_from})"
                if self.config.sample_from != "Source data"
                else ""
            )

            self._logger.info(
                f"Successfully sampled {len(data)} rows{sample_info} in {time_spent} seconds"
            )
            self._logger.debug(
                f"Sampled data shape: {data.shape}, dtypes: {data.dtypes.value_counts().to_dict()}"
            )

            return data.reset_index(drop=True)
        except Exception as e:
            self._logger.error(f"Error during sampling: {str(e)}")
            raise

    def fit_sample(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Fit and sample from the synthesizer.
        The combination of the methods `fit()` and `sample()`.

        Return:
            pd.DataFrame: The synthesized data.
        """

        self.fit(data=data)
        return self.sample()
