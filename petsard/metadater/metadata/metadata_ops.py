"""Metadata-level operations and transformations"""

import logging
from typing import Any, Optional, Union

import pandas as pd

from petsard.metadater.metadata.metadata_types import Metadata, MetadataConfig
from petsard.metadater.schema.schema_functions import build_schema_metadata
from petsard.metadater.schema.schema_types import SchemaMetadata


class MetadataOperations:
    """Operations for metadata-level management"""

    SCHEMA_TO_DF_SPECIAL_HANDLERS: dict[str, dict[str, str | list[str]]] = {
        "quantiles": {
            "type": "dict",
            "handler": "expand_dict",
            "prefix": "quantile_",
        },
        "most_frequent": {
            "type": "list_of_tuples",
            "handler": "expand_list_of_tuples",
            "prefix": "most_frequent_",
            "suffixes": ["value", "count"],
        },
    }

    def __init__(self):
        self._logger = logging.getLogger(f"PETsARD.{self.__class__.__name__}")

    @classmethod
    def build_metadata_from_datasets(
        cls,
        datasets: dict[str, pd.DataFrame],
        config: Optional[Union[MetadataConfig, dict[str, Any]]] = None,
    ) -> Metadata:
        """Build Metadata instance from dictionary of DataFrames"""
        instance = cls()
        instance._logger.info(f"Building metadata for {len(datasets)} DataFrames")

        # Convert dict to MetadataConfig if needed
        if config is not None and not isinstance(config, MetadataConfig):
            if isinstance(config, dict):
                config = MetadataConfig.from_dict(config)
            else:
                raise TypeError(
                    f"config must be MetadataConfig or dict, got {type(config)}"
                )

        if config is None:
            config = MetadataConfig(metadata_id="default", name="Default Metadata")

        # Create metadata container
        metadata = Metadata(
            metadata_id=config.metadata_id,
            name=config.name,
            description=config.description,
            properties=config.properties,
        )

        # Build schemas from each DataFrame
        for schema_id, data in datasets.items():
            schema_config = config.get_schema_config(schema_id)
            if schema_config is None:
                schema_config = config.create_schema_config(
                    schema_id=schema_id, inherit_globals=True
                )

            # Build schema
            schema = build_schema_metadata(data=data, config=schema_config)
            metadata.add_schema(schema)

            instance._logger.info(
                f"Successfully built metadata for schema '{schema_id}' "
                f"with {len(schema.fields)} fields"
            )

        # Auto-detect relations if configured
        if config.auto_detect_relations:
            instance._logger.info("Auto-detecting schema relations...")
            # TODO: Implement relation detection logic

        return metadata

    @classmethod
    def get_metadata_to_dataframe(cls, metadata: Metadata) -> pd.DataFrame:
        """Convert Metadata to DataFrame for viewing"""
        data_dict = {}
        for k, v in metadata.__dict__.items():
            if k in {"schemas", "relations", "properties"}:
                continue
            data_dict.update({k: v})

        df = pd.DataFrame.from_dict(data_dict, orient="index")
        return df

    @classmethod
    def get_schema_to_dataframe(cls, schema: SchemaMetadata) -> pd.DataFrame:
        """Convert SchemaMetadata to DataFrame for viewing"""
        data_dict = {}
        for k, v in schema.__dict__.items():
            if k in {"fields", "properties"}:
                continue
            data_dict.update({k: v})

        df = pd.DataFrame.from_dict(data_dict, orient="index")
        return df

    @classmethod
    def get_fields_to_dataframe(cls, schema: SchemaMetadata) -> pd.DataFrame:
        """
        Convert fields in SchemaMetadata to a DataFrame
            for easy viewing and analysis.

        Args:
            schema (SchemaMetadata): The schema metadata to convert

        Returns:
            pd.DataFrame: A DataFrame where columns are fields and rows are different settings
        """
        if not schema.fields:
            return pd.DataFrame()

        # Initialize data dictionary
        data_dict = {}

        # Helper function to handle special cases
        def handle_special_value(
            key: str, value: Any, field_name: str, parent_prefix: str = ""
        ):
            """Handle special value types based on SCHEMA_TO_DF_SPECIAL_HANDLERS"""
            full_key = f"{parent_prefix}{key}" if parent_prefix else key

            # Check if this key needs special handling
            if key in cls.SCHEMA_TO_DF_SPECIAL_HANDLERS:
                handler_config = cls.SCHEMA_TO_DF_SPECIAL_HANDLERS[key]
                handler_type = handler_config["handler"]

                if handler_type == "expand_dict" and isinstance(value, dict):
                    # Expand dictionary into multiple rows
                    prefix = handler_config.get("prefix", f"{key}_")
                    for sub_key, sub_value in value.items():
                        new_key = f"{parent_prefix}{prefix}{sub_key}"
                        if new_key not in data_dict:
                            data_dict[new_key] = {}
                        data_dict[new_key][field_name] = sub_value

                elif handler_type == "expand_list_of_tuples" and isinstance(
                    value, list
                ):
                    # Expand list of tuples into multiple rows
                    prefix = handler_config.get("prefix", f"{key}_")
                    suffixes = handler_config.get("suffixes", ["item1", "item2"])

                    for i, item in enumerate(value):
                        if isinstance(item, (tuple, list)) and len(item) >= len(
                            suffixes
                        ):
                            for j, suffix in enumerate(suffixes):
                                new_key = f"{parent_prefix}{prefix}{i}_{suffix}"
                                if new_key not in data_dict:
                                    data_dict[new_key] = {}
                                data_dict[new_key][field_name] = item[j]
            else:
                # Normal handling
                if full_key not in data_dict:
                    data_dict[full_key] = {}
                # Handle Enum types
                if hasattr(value, "value"):
                    data_dict[full_key][field_name] = value.value
                else:
                    data_dict[full_key][field_name] = value

        # Process each field
        for schema_field in schema.fields:
            field_name = schema_field.name

            # Process field attributes
            for key, value in schema_field.__dict__.items():
                # Skip private attributes and None values for stats
                if key.startswith("_") or (key == "stats" and value is None):
                    continue

                # Handle stats object specially
                if key == "stats" and value is not None:
                    # Process stats attributes
                    for stats_key, stats_value in value.__dict__.items():
                        if not stats_key.startswith("_"):
                            handle_special_value(
                                stats_key, stats_value, field_name, "stats_"
                            )

                # Handle properties dictionary
                elif key == "properties" and isinstance(value, dict):
                    for prop_key, prop_value in value.items():
                        prop_full_key = f"properties_{prop_key}"
                        if prop_full_key not in data_dict:
                            data_dict[prop_full_key] = {}
                        data_dict[prop_full_key][field_name] = prop_value

                # Handle other attributes
                else:
                    handle_special_value(key, value, field_name)

        # Fill missing values with None
        all_field_names = [schema_field.name for schema_field in schema.fields]
        for key in data_dict:
            for field_name in all_field_names:
                if field_name not in data_dict[key]:
                    data_dict[key][field_name] = None

        # Create DataFrame
        df = pd.DataFrame.from_dict(data_dict, orient="index")

        # Add index name for clarity
        df.index.name = "setting"

        # Reorder columns to match the order of fields in schema
        df = df[all_field_names]

        # Sort index for better readability
        df = df.sort_index()

        return df
