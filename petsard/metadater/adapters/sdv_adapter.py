"""
SDV metadata adapter for converting between PETsARD metadata and SDV format.
"""

import logging
from typing import Any, Dict

from petsard.exceptions import MetadataError
from petsard.metadater.schema.schema_types import SchemaMetadata
from petsard.metadater.types.data_types import DataType, LogicalType


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
            error_msg = "No fields found in SchemaMetadata"
            self._logger.error(error_msg)
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

    def _map_datatype_to_sdv_type(
        self, data_type: DataType, logical_type: LogicalType = None
    ) -> str:
        """
        Map PETsARD DataType to SDV sdtype.

        Args:
            data_type (DataType): The PETsARD data type.
            logical_type (LogicalType, optional): The logical type for additional context.

        Returns:
            str: The corresponding SDV sdtype.
        """
        # Numerical types
        if data_type in [
            DataType.INT8,
            DataType.INT16,
            DataType.INT32,
            DataType.INT64,
            DataType.FLOAT32,
            DataType.FLOAT64,
            DataType.DECIMAL,
        ]:
            return "numerical"

        # Boolean type (SDV treats as categorical)
        elif data_type == DataType.BOOLEAN:
            return "categorical"

        # Date/time types
        elif data_type in [
            DataType.DATE,
            DataType.TIME,
            DataType.TIMESTAMP,
            DataType.TIMESTAMP_TZ,
        ]:
            return "datetime"

        # String/object types
        elif data_type in [DataType.STRING, DataType.BINARY, DataType.OBJECT]:
            # Use logical type for better classification
            if logical_type and logical_type == LogicalType.CATEGORICAL:
                return "categorical"
            else:
                return "categorical"  # Default string/object to categorical for SDV

        # Fallback
        else:
            self._logger.warning(
                f"Unknown data type {data_type}, defaulting to categorical"
            )
            return "categorical"


# Convenience function for backward compatibility and easy access
def convert_petsard_to_sdv_dict(metadata: SchemaMetadata) -> Dict[str, Any]:
    """
    Convert PETsARD metadata to SDV dictionary format.

    This is a convenience function that creates an adapter instance
    and performs the conversion.

    Args:
        metadata (SchemaMetadata): The PETsARD metadata to convert.

    Returns:
        Dict[str, Any]: SDV-compatible metadata dictionary.
    """
    adapter = SDVMetadataAdapter()
    return adapter.convert_to_sdv_dict(metadata)
