import logging
from typing import Any, Optional

import pandas as pd

from petsard.metadater.field_ops import FieldOperations
from petsard.metadater.metadata import Metadata
from petsard.metadater.metadata_ops import MetadataOperations
from petsard.metadater.schema_meta import SchemaMetadata
from petsard.metadater.schema_ops import SchemaOperations


class Metadater:
    """
    Main class for metadata management

    Usage:
        meta = Metadater()
        metadata = meta.build_metadata_from_datasets(datasets, config)
        aligned_data = meta.apply_field_config(data, schema)
    """

    CONFIG_KEYS: list[str] = [
        "column_types",
        "cast_errors",
        "descriptions",
    ]

    def __init__(self):
        """Initialize the Metadater"""
        self._logger = logging.getLogger(f"PETsARD.{self.__class__.__name__}")
        self.field_ops = FieldOperations()
        self.schema_ops = SchemaOperations()
        self.metadata_ops = MetadataOperations()

    # Delegation methods for backward compatibility
    @classmethod
    def build_field_from_series(cls, *args, **kwargs):
        """Delegate to FieldOperations"""
        field_ops = FieldOperations()
        return field_ops.build_field_from_series(*args, **kwargs)

    @classmethod
    def build_schema_from_dataframe(cls, *args, **kwargs):
        """Delegate to SchemaOperations"""
        schema_ops = SchemaOperations()
        return schema_ops.build_schema_from_dataframe(*args, **kwargs)

    @classmethod
    def build_metadata_from_datasets(cls, *args, **kwargs):
        """Delegate to MetadataOperations"""
        metadata_ops = MetadataOperations()
        return metadata_ops.build_metadata_from_datasets(*args, **kwargs)

    @classmethod
    def apply_field_config(cls, *args, **kwargs):
        """Delegate to SchemaOperations"""
        return SchemaOperations.apply_field_config(*args, **kwargs)

    @classmethod
    def validate_against_schema(cls, *args, **kwargs):
        """Delegate to SchemaOperations"""
        return SchemaOperations.validate_against_schema(*args, **kwargs)

    # Static utility methods
    @staticmethod
    def create_schema_config(
        column_types: Optional[dict[str, str]] = None,
        cast_errors: Optional[dict[str, str]] = None,
        descriptions: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """Create a configuration dictionary for schema metadata"""
        config: dict[str, Any] = {}

        fields_config: dict[str, Any] = {}
        for param_dict, param_key in [
            (column_types, "type_hint"),
            (cast_errors, "cast_error"),
            (descriptions, "description"),
        ]:
            if param_dict:
                for field_name, value in param_dict.items():
                    fields_config.setdefault(field_name, {})[param_key] = value
        config["fields"] = fields_config

        return config

    # Convenience class methods
    @classmethod
    def get_metadata_to_dataframe(cls, metadata: Metadata) -> pd.DataFrame:
        """Convert Metadata to DataFrame"""
        return MetadataOperations.get_metadata_to_dataframe(metadata)

    @classmethod
    def get_schema_to_dataframe(cls, schema: SchemaMetadata) -> pd.DataFrame:
        """Convert SchemaMetadata to DataFrame"""
        return MetadataOperations.get_schema_to_dataframe(schema)

    @classmethod
    def get_fields_to_dataframe(cls, schema: SchemaMetadata) -> pd.DataFrame:
        """Convert fields to DataFrame"""
        return MetadataOperations.get_fields_to_dataframe(schema)
