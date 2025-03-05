import logging
import re
import warnings
from typing import Any

import pandas as pd
from scipy.stats._warnings_errors import FitError
from sdv.metadata import Metadata as SDV_Metadata
from sdv.single_table import (
    CopulaGANSynthesizer,
    CTGANSynthesizer,
    GaussianCopulaSynthesizer,
    TVAESynthesizer,
)
from sdv.single_table.base import BaseSingleTableSynthesizer

from petsard.exceptions import (
    MetadataError,
    UnableToSynthesizeError,
    UnsupportedMethodError,
)
from petsard.loader import Metadata
from petsard.synthesizer.synthesizer_base import BaseSynthesizer


class SDVMap:
    """
    Mapping of SDV.
    """

    COPULAGAN: int = 1
    CTGAN: int = 2
    GAUSSIANCOPULA: int = 3
    TVAE: int = 4

    @classmethod
    def map(cls, method: str) -> int:
        """
        Get suffixes mapping int value

        Args:
            method (str): evaluating method

        Return:
            (int): The method code.
        """
        # accept both of "sdv-" or "sdv-single_table-" prefix
        return cls.__dict__[re.sub(r"^(sdv-single_table-|sdv-)", "", method).upper()]


class SDVSingleTableSynthesizer(BaseSynthesizer):
    """
    Factory class for SDV synthesizer.
    """

    def __init__(self, config: dict, metadata: Metadata = None):
        """
        Args:
            config (dict): The configuration assign by Synthesizer
            metadata (Metadata, optional): The metadata object.

        Attributes:
            logger (logging.Logger): The logger object.
            config (dict): The configuration of the synthesizer_base.
            _synthesizer (BaseSingleTableSynthesizer): The synthesizer object if metadata is provided.
        """
        super().__init__(config, metadata)
        self.logger: logging.Logger = logging.getLogger(
            f"PETsARD.{self.__class__.__name__}"
        )
        self.logger.info(
            f"Initializing {self.__class__.__name__} with config: {config}"
        )

        # If metadata is provided, initialize the synthesizer in the init method.
        if metadata is not None:
            self.logger.debug("Metadata provided, initializing synthesizer in __init__")
            self._synthesizer: BaseSingleTableSynthesizer = (
                self._initialize_synthesizer(
                    metadata=self._create_sdv_metadata(
                        metadata=metadata,
                    )
                )
            )
            self.logger.info("Synthesizer initialized with provided metadata")
        else:
            self.logger.debug(
                "No metadata provided, synthesizer will be initialized during fit"
            )

    def _initialize_synthesizer(
        self, metadata: SDV_Metadata
    ) -> BaseSingleTableSynthesizer:
        """
        Initialize the synthesizer.

        Args:
            metadata (Metadata): The metadata of the data.

        Returns:
            (BaseSingleTableSynthesizer): The SDV synthesizer

        Raises:
            UnsupportedMethodError: If the synthesizer method is not supported.
        """
        sdv_map: dict[int, BaseSynthesizer] = {
            SDVMap.COPULAGAN: CopulaGANSynthesizer,
            SDVMap.CTGAN: CTGANSynthesizer,
            SDVMap.GAUSSIANCOPULA: GaussianCopulaSynthesizer,
            SDVMap.TVAE: TVAESynthesizer,
        }

        self.logger.debug(
            f"Initializing synthesizer with method: {self.config['syn_method']}"
        )
        try:
            method_code = SDVMap.map(self.config["syn_method"])
            self.logger.debug(f"Mapped method code: {method_code}")
            synthesizer_class: BaseSingleTableSynthesizer = sdv_map[method_code]
            self.logger.debug(f"Using synthesizer class: {synthesizer_class.__name__}")
        except KeyError:
            error_msg: str = (
                f"Unsupported synthesizer method: {self.config['syn_method']}"
            )
            self.logger.error(error_msg)
            raise UnsupportedMethodError(error_msg)

        # catch warnings during synthesizer initialization:
        # "We strongly recommend saving the metadata using 'save_to_json' for replicability in future SDV versions."
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            synthesizer = synthesizer_class(metadata=metadata)

            for warning in w:
                self.logger.debug(f"Warning during fit: {warning.message}")

        self.logger.debug(f"Successfully created {synthesizer_class.__name__} instance")
        return synthesizer

    def _convert_metadata_from_petsard_to_sdv_dict(self, metadata: Metadata) -> dict:
        """
        Transform the metadata to meet the format of SDV.

        Args:
            metadata (Metadata): The PETsARD metadata of the data.

        Return:
            (dict): The metadata in SDV metadata format.

        Raises:
            MetadataError: If the metadata is invalid.
        """
        self.logger.debug("Starting conversion of PETsARD metadata to SDV format")

        sdv_metadata: dict[str, Any] = {"columns": {}}

        # Determine the appropriate column metadata key
        col_name: str = (
            "col_after_preproc" if "col_after_preproc" in metadata.metadata else "col"
        )
        self.logger.debug(f"Using '{col_name}' as column metadata source")

        # Check if the column metadata exists
        if col_name not in metadata.metadata:
            error_msg: str = f"Column metadata key '{col_name}' not found in metadata"
            self.logger.error(error_msg)
            raise MetadataError(error_msg)

        # Track conversion statistics
        total_columns = len(metadata.metadata[col_name])
        processed_columns = 0

        self.logger.debug(f"Processing {total_columns} columns from metadata")

        for col, val in metadata.metadata[col_name].items():
            # Determine the data type for SDV
            sdtype = val.get("infer_dtype")
            if "infer_dtype_after_preproc" in val:
                sdtype = val.get("infer_dtype_after_preproc")
                self.logger.debug(
                    f"Column '{col}': Using post-processing data type: {sdtype}"
                )
            else:
                self.logger.debug(f"Column '{col}': Using original data type: {sdtype}")

            # Validate the data type
            if sdtype is None or sdtype == "object":
                error_msg: str = f"Column '{col}' has invalid data type"
                self.logger.error(error_msg)
                raise MetadataError(error_msg)

            # Add to SDV metadata
            sdv_metadata["columns"][col] = {"sdtype": sdtype}
            processed_columns += 1

        self.logger.info(
            f"Successfully converted {processed_columns}/{total_columns} columns to SDV metadata format"
        )
        self.logger.debug(
            f"SDV metadata contains {len(sdv_metadata['columns'])} columns"
        )

        return sdv_metadata

    def _create_sdv_metadata(
        self, metadata: Metadata = None, data: pd.DataFrame = None
    ) -> SDV_Metadata:
        """
        Create or convert metadata for SDV compatibility.
            This function either converts existing metadata to SDV format or
            generates new SDV metadata by detecting it from the provided dataframe.

        Args:
            metadata (Metadata, optional): The metadata of the data.
            data (pd.DataFrame, optional): The data to be fitted.

        Returns:
            (SingleTableMetadata): The SDV metadata.
        """
        self.logger.debug("Creating SDV metadata")
        sdv_metadata: SDV_Metadata = SDV_Metadata()

        if metadata is None:
            if data is None:
                self.logger.warning(
                    "Both metadata and data are None, cannot create SDV metadata"
                )
                return sdv_metadata

            self.logger.info(
                f"Detecting metadata from dataframe with shape {data.shape}"
            )
            sdv_metadata_result: SDV_Metadata = sdv_metadata.detect_from_dataframe(data)
            self.logger.debug("Successfully detected metadata from dataframe")
            return sdv_metadata_result
        else:
            self.logger.info("Converting existing metadata to SDV format")
            sdv_metadata = sdv_metadata.load_from_dict(
                metadata_dict=self._convert_metadata_from_petsard_to_sdv_dict(metadata),
                single_table_name="table",
            )
            self.logger.debug("Successfully converted metadata to SDV format")
            return sdv_metadata

    def _fit(self, data: pd.DataFrame) -> None:
        """
        Fit the synthesizer.
            _synthesizer should be initialized in this method.

        Args:
            data (pd.DataFrame): The data to be fitted.

        Attributes:
            _synthesizer (BaseSingleTableSynthesizer): The synthesizer object been fitted.

        Raises:
            UnableToSynthesizeError: If the synthesizer couldn't fit the data. See Issue 454.
        """
        self.logger.info(f"Fitting synthesizer with data shape: {data.shape}")

        # If metadata is not provided, initialize the synthesizer in the fit method.
        if not hasattr(self, "_synthesizer") or self._synthesizer is None:
            self.logger.debug("Initializing synthesizer in fit method")
            self._synthesizer: BaseSingleTableSynthesizer = (
                self._initialize_synthesizer(
                    metadata=self._create_sdv_metadata(
                        data=data,
                    )
                )
            )
            self.logger.info("Synthesizer initialized from data")

        try:
            self.logger.debug("Fitting synthesizer with data")
            self._synthesizer.fit(data)
            self.logger.info("Successfully fitted synthesizer with data")
        except FitError as ex:
            error_msg: str = f"The synthesizer couldn't fit the data. FitError: {ex}."
            self.logger.error(error_msg)
            raise UnableToSynthesizeError(error_msg)

    def _sample(self) -> pd.DataFrame:
        """
        Sample from the fitted synthesizer.

        Return:
            (pd.DataFrame): The synthesized data.

        Raises:
            UnableToSynthesizeError: If the synthesizer couldn't synthesize the data.
        """
        num_rows = self.config["sample_num_rows"]
        self.logger.info(f"Sampling {num_rows} rows from synthesizer")

        batch_size: int = None
        if "batch_size" in self.config:
            self.logger.debug(f"Using batch size: {batch_size}")
            batch_size = int(self.config["batch_size"])

        try:
            synthetic_data = self._synthesizer.sample(
                num_rows=num_rows,
                batch_size=batch_size,
            )
            self.logger.info(f"Successfully sampled {len(synthetic_data)} rows")
            self.logger.debug(f"Generated data shape: {synthetic_data.shape}")
            return synthetic_data
        except Exception as ex:
            error_msg: str = f"SDV synthesizer couldn't sample the data: {ex}"
            self.logger.error(error_msg)
            raise UnableToSynthesizeError(error_msg)
