"""
SDV metadata adapter for converting between PETsARD metadata and SDV format.
"""

import logging
from typing import Any, Dict, Optional

import pandas as pd
from sdv.metadata import Metadata as SDV_Metadata

from petsard.exceptions import MetadataError
from petsard.metadater.schema.schema_types import SchemaMetadata


class SDVMetadataAdapter:
    """
    Adapter for converting PETsARD metadata to SDV format.

    This class centralizes all SDV-specific metadata conversion logic,
    following the adapter pattern to separate concerns between PETsARD
    metadata representation and external format requirements.
    """

    def __init__(self):
        """Initialize the SDV metadata adapter."""
        self._logger = logging.getLogger(f"PETsARD.{self.__class__.__name__}")

    def convert_to_sdv_dict(self, metadata: SchemaMetadata) -> Dict[str, Any]:
        """
        Convert PETsARD SchemaMetadata to SDV metadata dictionary format.

        Args:
            metadata (SchemaMetadata): The PETsARD metadata to convert.

        Returns:
            Dict[str, Any]: SDV-compatible metadata dictionary.

        Raises:
            MetadataError: If the metadata is invalid or conversion fails.
        """
        self._logger.debug("Converting PETsARD metadata to SDV dictionary format")

        if not metadata.fields:
            error_msg = (
                f"No fields found in SchemaMetadata (schema_id: {metadata.schema_id}). "
                f"This usually indicates that the metadata was not properly initialized "
                f"or the data loading process failed to detect any columns."
            )
            self._logger.error(error_msg)
            self._logger.debug(f"SchemaMetadata details: {metadata}")
            raise MetadataError(error_msg)

        sdv_metadata = {"columns": {}}

        total_columns = len(metadata.fields)
        processed_columns = 0

        self._logger.debug(f"Processing {total_columns} columns from metadata")

        for field_metadata in metadata.fields:
            sdtype = self._map_datatype_to_sdv_type(
                field_metadata.data_type, field_metadata.logical_type
            )

            self._logger.debug(
                f"Column '{field_metadata.name}': DataType {field_metadata.data_type} -> SDV sdtype: {sdtype}"
            )

            sdv_metadata["columns"][field_metadata.name] = {"sdtype": sdtype}
            processed_columns += 1

        self._logger.info(
            f"Successfully converted {processed_columns}/{total_columns} columns to SDV metadata format"
        )

        return sdv_metadata

    def create_sdv_metadata(
        self,
        metadata: Optional[SchemaMetadata] = None,
        data: Optional[pd.DataFrame] = None,
    ) -> SDV_Metadata:
        """
        Create or convert metadata for SDV compatibility.

        This function either converts existing metadata to SDV format or
        generates new SDV metadata by detecting it from the provided dataframe.

        Args:
            metadata (SchemaMetadata, optional): The metadata of the data.
            data (pd.DataFrame, optional): The data to be fitted.

        Returns:
            SDV_Metadata: The SDV metadata object.

        Raises:
            MetadataError: If both metadata and data are None, or conversion fails.
        """
        self._logger.debug("Creating SDV metadata")
        sdv_metadata: SDV_Metadata = SDV_Metadata()

        if metadata is None:
            if data is None:
                error_msg = (
                    "Both metadata and data are None, cannot create SDV metadata"
                )
                self._logger.error(error_msg)
                raise MetadataError(error_msg)

            self._logger.info(
                f"Detecting metadata from dataframe with shape {data.shape}"
            )
            sdv_metadata_result: SDV_Metadata = sdv_metadata.detect_from_dataframe(data)
            self._logger.debug("Successfully detected metadata from dataframe")
            return sdv_metadata_result
        else:
            self._logger.info("Converting existing metadata to SDV format")

            # Check if metadata has fields before conversion
            if not metadata.fields:
                self._logger.warning(
                    f"Metadata has no fields (schema_id: {metadata.schema_id}). "
                    f"Falling back to auto-detection from data."
                )
                if data is None:
                    error_msg = "Cannot auto-detect metadata: both metadata is empty and data is None"
                    self._logger.error(error_msg)
                    raise MetadataError(error_msg)

                self._logger.info(
                    f"Auto-detecting metadata from dataframe with shape {data.shape}"
                )
                sdv_metadata_result: SDV_Metadata = sdv_metadata.detect_from_dataframe(
                    data
                )
                self._logger.debug("Successfully detected metadata from dataframe")
                return sdv_metadata_result

            # Use SchemaMetadata's to_sdv() method for conversion
            try:
                sdv_metadata = sdv_metadata.load_from_dict(
                    metadata_dict=metadata.to_sdv(),
                    single_table_name="table",
                )
                self._logger.debug("Successfully converted metadata to SDV format")
                return sdv_metadata
            except Exception as e:
                self._logger.error(f"Failed to convert metadata to SDV format: {e}")
                if data is not None:
                    self._logger.info("Falling back to auto-detection from data")
                    sdv_metadata_result: SDV_Metadata = (
                        sdv_metadata.detect_from_dataframe(data)
                    )
                    self._logger.debug(
                        "Successfully detected metadata from dataframe as fallback"
                    )
                    return sdv_metadata_result
                else:
                    raise MetadataError(
                        f"Failed to convert metadata to SDV format: {e}"
                    ) from e

    def _map_datatype_to_sdv_type(self, data_type, logical_type=None) -> str:
        """
        Map PETsARD DataType to SDV sdtype.

        This method handles both DataType enums and string values for backward compatibility.

        Args:
            data_type: The PETsARD data type (DataType enum or string).
            logical_type: The logical type for additional context (LogicalType enum or string).

        Returns:
            str: The corresponding SDV sdtype.
        """
        # Convert to string for unified processing (like the original implementation)
        if hasattr(data_type, "value"):
            data_type_str = data_type.value.lower()
        else:
            data_type_str = str(data_type).lower()

        # Convert logical_type to string if needed
        logical_type_str = None
        if logical_type:
            if hasattr(logical_type, "value"):
                logical_type_str = logical_type.value.lower()
            else:
                logical_type_str = str(logical_type).lower()

        # Map specific DataType values to SDV categories (matching original logic)
        if data_type_str in [
            "int8",
            "int16",
            "int32",
            "int64",
            "float32",
            "float64",
            "decimal",
        ]:
            return "numerical"
        elif data_type_str == "boolean":
            return "categorical"  # SDV treats boolean as categorical
        elif data_type_str in ["date", "time", "timestamp", "timestamp_tz"]:
            return "datetime"
        elif data_type_str in ["string", "binary", "object"]:
            # Check logical type for better classification
            if logical_type_str and logical_type_str == "categorical":
                return "categorical"
            else:
                return "categorical"  # Default string to categorical for SDV
        else:
            self._logger.warning(
                f"Unknown data type {data_type_str}, defaulting to categorical"
            )
            return "categorical"  # Fallback to categorical
