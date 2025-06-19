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
from petsard.metadater import SchemaMetadata
from petsard.synthesizer.synthesizer_base import BaseSynthesizer


class SDVSingleTableMap:
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

    SDV_SINGLETABLE_MAP: dict[int, BaseSynthesizer] = {
        SDVSingleTableMap.COPULAGAN: CopulaGANSynthesizer,
        SDVSingleTableMap.CTGAN: CTGANSynthesizer,
        SDVSingleTableMap.GAUSSIANCOPULA: GaussianCopulaSynthesizer,
        SDVSingleTableMap.TVAE: TVAESynthesizer,
    }

    def __init__(self, config: dict, metadata: SchemaMetadata = None):
        """
        Args:
            config (dict): The configuration assign by Synthesizer
            metadata (SchemaMetadata, optional): The metadata object.

        Attributes:
            _logger (logging.Logger): The logger object.
            config (dict): The configuration of the synthesizer_base.
            _impl (BaseSingleTableSynthesizer): The synthesizer object if metadata is provided.
        """
        super().__init__(config, metadata)
        self._logger: logging.Logger = logging.getLogger(
            f"PETsARD.{self.__class__.__name__}"
        )
        self._logger.info(
            f"Initializing {self.__class__.__name__} with config: {config}"
        )

        # If metadata is provided, initialize the synthesizer in the init method.
        if metadata is not None:
            self._logger.debug(
                "Metadata provided, initializing synthesizer in __init__"
            )
            self._impl: BaseSingleTableSynthesizer = self._initialize_impl(
                metadata=self._create_sdv_metadata(
                    metadata=metadata,
                )
            )
            self._logger.info("Synthesizer initialized with provided metadata")
        else:
            self._logger.debug(
                "No metadata provided, synthesizer will be initialized during fit"
            )

    def _initialize_impl(self, metadata: SDV_Metadata) -> BaseSingleTableSynthesizer:
        """
        Initialize the synthesizer.

        Args:
            metadata (Metadata): The metadata of the data.

        Returns:
            (BaseSingleTableSynthesizer): The SDV synthesizer

        Raises:
            UnsupportedMethodError: If the synthesizer method is not supported.
        """

        self._logger.debug(
            f"Initializing synthesizer with method: {self.config['syn_method']}"
        )
        try:
            method_code = SDVSingleTableMap.map(self.config["syn_method"])
            self._logger.debug(f"Mapped method code: {method_code}")
            synthesizer_class: Any = self.SDV_SINGLETABLE_MAP[method_code]
            self._logger.debug(f"Using synthesizer class: {synthesizer_class.__name__}")
        except KeyError:
            error_msg: str = (
                f"Unsupported synthesizer method: {self.config['syn_method']}"
            )
            self._logger.error(error_msg)
            raise UnsupportedMethodError(error_msg) from None

        # catch warnings during synthesizer initialization:
        # "We strongly recommend saving the metadata using 'save_to_json' for replicability in future SDV versions."
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            synthesizer: BaseSingleTableSynthesizer = synthesizer_class(
                metadata=metadata
            )

            for warning in w:
                self._logger.debug(f"Warning during fit: {warning.message}")

        self._logger.debug(
            f"Successfully created {synthesizer_class.__name__} instance"
        )
        return synthesizer

    def _convert_metadata_from_petsard_to_sdv_dict(
        self, metadata: SchemaMetadata
    ) -> dict:
        """
        Transform the metadata to meet the format of SDV.

        Args:
            metadata (SchemaMetadata): The PETsARD metadata of the data.

        Return:
            (dict): The metadata in SDV metadata format.

        Raises:
            MetadataError: If the metadata is invalid.
        """
        self._logger.debug("Starting conversion of PETsARD metadata to SDV format")

        sdv_metadata: dict[str, Any] = {"columns": {}}

        # Check if fields exist
        if not metadata.fields:
            error_msg: str = "No fields found in SchemaMetadata"
            self._logger.error(error_msg)
            raise MetadataError(error_msg)

        # Track conversion statistics
        total_columns = len(metadata.fields)
        processed_columns = 0

        self._logger.debug(f"Processing {total_columns} columns from metadata")

        for field_metadata in metadata.fields:
            # Convert DataType enum to SDV sdtype
            from petsard.metadater.datatype import DataType, LogicalType

            data_type = field_metadata.data_type

            # Map DataType to SDV sdtype
            if data_type in [
                DataType.INT8,
                DataType.INT16,
                DataType.INT32,
                DataType.INT64,
                DataType.FLOAT32,
                DataType.FLOAT64,
                DataType.DECIMAL,
            ]:
                sdtype = "numerical"
            elif data_type == DataType.BOOLEAN:
                sdtype = "categorical"  # SDV treats boolean as categorical
            elif data_type in [
                DataType.DATE,
                DataType.TIME,
                DataType.TIMESTAMP,
                DataType.TIMESTAMP_TZ,
            ]:
                sdtype = "datetime"
            elif data_type in [DataType.STRING, DataType.BINARY]:
                # Check logical type for better classification
                if (
                    field_metadata.logical_type
                    and field_metadata.logical_type == LogicalType.CATEGORICAL
                ):
                    sdtype = "categorical"
                else:
                    sdtype = (
                        "categorical"  # Default string/object to categorical for SDV
                    )
            else:
                sdtype = "categorical"  # Fallback to categorical

            self._logger.debug(
                f"Column '{field_metadata.name}': DataType {data_type} -> SDV sdtype: {sdtype}"
            )

            # Add to SDV metadata
            sdv_metadata["columns"][field_metadata.name] = {"sdtype": sdtype}
            processed_columns += 1

        self._logger.info(
            f"Successfully converted {processed_columns}/{total_columns} columns to SDV metadata format"
        )
        self._logger.debug(
            f"SDV metadata contains {len(sdv_metadata['columns'])} columns"
        )

        return sdv_metadata

    def _create_sdv_metadata(
        self, metadata: SchemaMetadata = None, data: pd.DataFrame = None
    ) -> SDV_Metadata:
        """
        Create or convert metadata for SDV compatibility.
            This function either converts existing metadata to SDV format or
            generates new SDV metadata by detecting it from the provided dataframe.

        Args:
            metadata (SchemaMetadata, optional): The metadata of the data.
            data (pd.DataFrame, optional): The data to be fitted.

        Returns:
            (SingleTableMetadata): The SDV metadata.
        """
        self._logger.debug("Creating SDV metadata")
        sdv_metadata: SDV_Metadata = SDV_Metadata()

        if metadata is None:
            if data is None:
                self._logger.warning(
                    "Both metadata and data are None, cannot create SDV metadata"
                )
                return sdv_metadata

            self._logger.info(
                f"Detecting metadata from dataframe with shape {data.shape}"
            )
            sdv_metadata_result: SDV_Metadata = sdv_metadata.detect_from_dataframe(data)
            self._logger.debug("Successfully detected metadata from dataframe")
            return sdv_metadata_result
        else:
            self._logger.info("Converting existing metadata to SDV format")
            # Use SchemaMetadata's to_sdv() method instead of custom conversion
            sdv_metadata = sdv_metadata.load_from_dict(
                metadata_dict=metadata.to_sdv(),
                single_table_name="table",
            )
            self._logger.debug("Successfully converted metadata to SDV format")
            return sdv_metadata

    def _fit(self, data: pd.DataFrame) -> None:
        """
        Fit the synthesizer.
            _impl should be initialized in this method.

        Args:
            data (pd.DataFrame): The data to be fitted.

        Attributes:
            _impl (BaseSingleTableSynthesizer): The synthesizer object been fitted.

        Raises:
            UnableToSynthesizeError: If the synthesizer couldn't fit the data. See Issue 454.
        """
        self._logger.info(f"Fitting synthesizer with data shape: {data.shape}")

        # If metadata is not provided, initialize the synthesizer in the fit method.
        if not hasattr(self, "_impl") or self._impl is None:
            self._logger.debug("Initializing synthesizer in _fit method")
            self._impl: BaseSingleTableSynthesizer = self._initialize_impl(
                metadata=self._create_sdv_metadata(
                    data=data,
                )
            )
            self._logger.info("Synthesizer initialized from data")

        try:
            self._logger.debug("Fitting synthesizer with data")
            self._impl.fit(data)
            self._logger.info("Successfully fitted synthesizer with data")
        except FitError as ex:
            error_msg: str = f"The synthesizer couldn't fit the data. FitError: {ex}."
            self._logger.error(error_msg)
            raise UnableToSynthesizeError(error_msg) from ex

    def _sample(self) -> pd.DataFrame:
        """
        Sample from the fitted synthesizer.

        Return:
            (pd.DataFrame): The synthesized data.

        Raises:
            UnableToSynthesizeError: If the synthesizer couldn't synthesize the data.
        """
        num_rows = self.config["sample_num_rows"]
        self._logger.info(f"Sampling {num_rows} rows from synthesizer")

        batch_size: int = None
        if "batch_size" in self.config:
            self._logger.debug(f"Using batch size: {batch_size}")
            batch_size = int(self.config["batch_size"])

        try:
            synthetic_data = self._impl.sample(
                num_rows=num_rows,
                batch_size=batch_size,
            )
            self._logger.info(f"Successfully sampled {len(synthetic_data)} rows")
            self._logger.debug(f"Generated data shape: {synthetic_data.shape}")
            return synthetic_data
        except Exception as ex:
            error_msg: str = f"SDV synthesizer couldn't sample the data: {ex}"
            self._logger.error(error_msg)
            raise UnableToSynthesizeError(error_msg) from ex
