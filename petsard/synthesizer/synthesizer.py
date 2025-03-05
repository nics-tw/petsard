import logging
import re
import time
from dataclasses import dataclass, field
from typing import Any, Optional

import pandas as pd

from petsard.config_base import BaseConfig
from petsard.exceptions import ConfigError, UncreatedError, UnsupportedMethodError
from petsard.loader import Metadata
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
        method (str): The method to be used for synthesizing the data.
        method_code (int): The code of the synthesizer method.
        syn_method (str): The name of the synthesizer method.
        sample_from (str): The source of the sample number of rows.
        sample_num_rows (int): The number of rows to be sampled.
    """

    DEFAULT_SYNTHESIS_METHOD: str = "sdv-single_table-gaussiancopula"

    method: str = "Undefined"
    method_code: int = None
    syn_method: str = None

    sample_from: str = "Undefined"
    sample_num_rows: int = 0

    custom_params: dict[Any, Any] = field(default_factory=dict)

    reset_sampling: bool = None
    output_file_path: str = None

    def __post_init__(self):
        # Set up logger for this class
        self.logger: logging.Logger = logging.getLogger(
            f"PETsARD.{self.__class__.__name__}"
        )
        self.logger.debug("Initializing SynthesizerConfig")
        error_msg: str = ""

        try:
            self.method_code: int = SynthesizerMap.map(self.method.lower())
            self.logger.debug(
                f"Mapped method '{self.method}' to code {self.method_code}"
            )
        except KeyError:
            error_msg = f"Unsupported synthesizer method: {self.method}"
            self.logger.error(error_msg)
            raise UnsupportedMethodError(error_msg)

        # Set the default
        self.syn_method: str = (
            self.DEFAULT_SYNTHESIS_METHOD
            if self.method_code == SynthesizerMap.DEFAULT
            else self.method
        )
        self.logger.debug(f"Set syn_method to '{self.syn_method}'")
        self.logger.info(
            f"SynthesizerConfig initialized with method: {self.method}, syn_method: {self.syn_method}"
        )


class Synthesizer:
    """
    The Synthesizer class is responsible for creating and fitting a synthesizer model,
    as well as generating synthetic data based on the fitted model.
    """

    def __init__(self, method: str, sample_num_rows: int = None, **kwargs) -> None:
        """
        Args:
            method (str): The method to be used for synthesizing the data.
            sample_num_rows (int, optional): The number of rows to be sampled.
            **kwargs: Any additional parameters to be stored in custom_params.

        Attributes:
            logger (logging.Logger): The logger object.
            config (dict):
                A dictionary containing the configuration parameters for the synthesizer.
            _synthesizer (BaseSynthesizer): The synthesizer object.
        """
        self.logger: logging.Logger = logging.getLogger(
            f"PETsARD.{self.__class__.__name__}"
        )
        self.logger.info(
            f"Initializing Synthesizer with method: {method}, sample_num_rows: {sample_num_rows}"
        )

        self.config: SynthesizerConfig = (
            SynthesizerConfig(method=method)
            if sample_num_rows is None
            else SynthesizerConfig(method=method, sample_num_rows=sample_num_rows)
        )
        self.logger.debug("SynthesizerConfig successfully initialized")

        # Add custom parameters to the config
        if kwargs:
            self.logger.debug(
                f"Additional keyword arguments provided: {list(kwargs.keys())}"
            )
            self.config.update({"custom_params": kwargs})
            self.logger.debug(
                "SynthesizerConfig successfully updated with custom parameters"
            )
        else:
            self.logger.debug("No additional parameters provided")

        self._synthesizer: BaseSynthesizer = None
        self.logger.info("Synthesizer initialization completed")

    def _determine_sample_configuration(
        self, metadata: Metadata = None
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
            metadata (Metadata, optional): The metadata containing information about the dataset

        Returns:
            (tuple[str, Optional[int]]): A tuple containing:
                - sample_from (str): Description of where the sample size was determined from
                - sample_num_rows (Optional[int]): Number of rows to sample, or None if undetermined
        """
        self.logger.debug("Determining sample configuration")
        sample_from: str = self.config.sample_from
        sample_num_rows: Optional[int] = self.config.sample_num_rows

        # 1. If manual input, use the sample number of rows from the input
        if self.config.sample_num_rows is not None:
            sample_from = "Manual input"
            sample_num_rows = self.config.sample_num_rows
            self.logger.debug(
                f"Using manually specified sample size: {sample_num_rows}"
            )

        # 2. If no manual input, get the sample number of rows from metadata
        elif metadata is not None:
            self.logger.debug("Checking metadata for sample size information")
            # 2-1. if Splitter information exist, use row_num after split
            if hasattr(metadata, "metadata") and "global" in metadata.metadata:
                if (
                    "row_num_after_split" in metadata.metadata["global"]
                    and "train" in metadata.metadata["global"]["row_num_after_split"]
                ):
                    sample_from = "Splitter data"
                    sample_num_rows = metadata.metadata["global"][
                        "row_num_after_split"
                    ]["train"]
                    self.logger.debug(
                        f"Using splitter train data count: {sample_num_rows}"
                    )
                # 2-2. if Loader only, assume data didn't been split
                elif "row_num" in metadata.metadata["global"]:
                    sample_from = "Loader data"
                    sample_num_rows = metadata.metadata["global"]["row_num"]
                    self.logger.debug(f"Using loader data count: {sample_num_rows}")
                else:
                    self.logger.debug("No row count information found in metadata")
            else:
                self.logger.debug("Metadata lacks global information structure")

        # 3. if sample_from didn't been assign, means no effective metadata been used
        if self.config.sample_from == "Undefined":
            sample_from = "Source data"
            self.logger.debug(
                "Using source data as sample source (will be determined during fit)"
            )

        self.logger.info(
            f"Sample configuration determined: source={sample_from}, rows={sample_num_rows}"
        )
        return sample_from, sample_num_rows

    def create(self, metadata: Metadata = None) -> None:
        """
        Create a synthesizer object with the given data.

        Args.:
            metadata (Metadata, optional): The metadata class of the data.
        """
        self.logger.info("Creating synthesizer instance")
        if metadata is not None:
            self.logger.debug("Metadata provided for synthesizer creation")
        else:
            self.logger.debug("No metadata provided for synthesizer creation")

        # Determine sample configuration using internal method
        sample_from, sample_num_rows = self._determine_sample_configuration(metadata)

        self.logger.debug(
            f"Sample configuration: source={sample_from}, rows={sample_num_rows}"
        )
        self.config.update(
            {
                "sample_from": sample_from,
                "sample_num_rows": sample_num_rows,
            }
        )

        synthesizer_map: dict[int, BaseSynthesizer] = {
            SynthesizerMap.DEFAULT: SDVSingleTableSynthesizer,
            SynthesizerMap.SDV: SDVSingleTableSynthesizer,
            SynthesizerMap.CUSTOM_DATA: CustomDataSynthesizer,
            SynthesizerMap.CUSTOM_METHOD: CustomSynthesizer,
        }

        synthesizer_class = synthesizer_map[self.config.method_code]
        self.logger.debug(f"Using synthesizer class: {synthesizer_class.__name__}")

        merged_config = self.config.get_and_merge_params(
            param_dict_name="custom_params",
            additional_attrs=["syn_method", "sample_num_rows"],
        )
        self.logger.debug(f"Merged config keys: {list(merged_config.keys())}")

        self.logger.info(f"Creating {synthesizer_class.__name__} instance")
        self._synthesizer = synthesizer_class(
            config=merged_config,
            metadata=metadata,
        )
        self.logger.info(f"Successfully created {synthesizer_class.__name__} instance")

    def fit(self, data: pd.DataFrame = None) -> None:
        """
        Fits the synthesizer model with the given parameters.

        Args:
            data (pd.DataFrame):
                The data to be fitted.
                Only 'CUSTOM_DATA' method doesn't need data to fit.
        """
        if self._synthesizer is None:
            error_msg: str = "Synthesizer not created yet, call create() first"
            self.logger.warning(error_msg)
            raise UncreatedError(error_msg)

        if data is None:
            # Should only happen for 'CUSTOM_DATA' method
            if self.config.method_code != SynthesizerMap.CUSTOM_DATA:
                error_msg: str = (
                    f"Data must be provided for fitting in {self.config.method}"
                )
                self.logger.error(error_msg)
                raise ConfigError(error_msg)

            self.logger.info("Fitting synthesizer without data")
        else:
            # In other methods, update the sample_num_rows in the synthesizer config
            self.logger.info(f"Fitting synthesizer with data shape: {data.shape}")

            if self.config.sample_from == "Source data":
                old_value: int = self.config.sample_num_rows
                self.config.update({"sample_num_rows": data.shape[0]})
                self.logger.debug(
                    f"Updated sample_num_rows from {old_value} to {data.shape[0]}"
                )

            self._synthesizer.update_config({"sample_num_rows": data.shape[0]})
            self.logger.debug(
                f"Updated synthesizer config with sample_num_rows={data.shape[0]}"
            )

        time_start: time = time.time()

        self.logger.info(f"Starting fit process for {self.config.syn_method}")
        try:
            self._synthesizer.fit(data=data)
            time_spent = round(time.time() - time_start, 4)
            self.logger.info(f"Fitting completed successfully in {time_spent} seconds")
        except Exception as e:
            self.logger.error(f"Error during fitting: {str(e)}")
            raise

    def sample(self) -> pd.DataFrame:
        """
        This method generates a sample using the Synthesizer object.

        Return:
            pd.DataFrame: The synthesized data.
        """
        if self._synthesizer is None:
            self.logger.warning("Synthesizer not created or fitted yet")
            return pd.DataFrame()

        time_start: time = time.time()

        self.logger.info(
            f"Sampling {self.config.sample_num_rows} rows using {self.config.syn_method}"
        )

        try:
            data: pd.DataFrame = self._synthesizer.sample()
            time_spent = round(time.time() - time_start, 4)

            sample_info: str = (
                f" (same as {self.config.sample_from})"
                if self.config.sample_from != "Source data"
                else ""
            )

            self.logger.info(
                f"Successfully sampled {len(data)} rows{sample_info} in {time_spent} seconds"
            )
            self.logger.debug(
                f"Sampled data shape: {data.shape}, dtypes: {data.dtypes.value_counts().to_dict()}"
            )

            return data
        except Exception as e:
            self.logger.error(f"Error during sampling: {str(e)}")
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
