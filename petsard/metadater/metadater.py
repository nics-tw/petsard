import logging
from typing import Dict, Optional

import pandas as pd

from petsard.metadater.field.field_types import FieldConfig, FieldMetadata
from petsard.metadater.metadata.metadata_types import Metadata, MetadataConfig
from petsard.metadater.schema.schema_types import SchemaConfig, SchemaMetadata


class Metadater:
    """
    統一的元資料管理介面

    提供三層架構的清晰介面：
    - Metadata 層: 多表格資料集管理
    - Schema 層: 單表格結構管理
    - Field 層: 單欄位分析管理

    Usage:
        # Schema 層 (最常用)
        schema = Metadater.create_schema(dataframe, "my_schema")
        schema = Metadater.analyze_dataframe(dataframe, "my_schema")

        # Field 層
        field = Metadater.create_field(series, "my_field")
        field = Metadater.analyze_series(series, "my_field")

        # Metadata 層 (多表格)
        metadata = Metadater.create_metadata("my_dataset")
        metadata = Metadater.analyze_dataset(tables, "my_dataset")
    """

    def __init__(self):
        """Initialize the Metadater"""
        self._logger = logging.getLogger(f"PETsARD.{self.__class__.__name__}")

    # Metadata 層 (多表格資料集)
    @classmethod
    def create_metadata(
        cls, metadata_id: str, config: Optional[MetadataConfig] = None
    ) -> Metadata:
        """
        建立多表格元資料容器

        Args:
            metadata_id: 元資料識別碼
            config: 可選的元資料配置

        Returns:
            Metadata 物件
        """
        from petsard.metadater.metadata.metadata_ops import MetadataOperations

        if config is None:
            config = MetadataConfig(metadata_id=metadata_id)

        return MetadataOperations.create_metadata(config)

    @classmethod
    def analyze_dataset(
        cls,
        tables: Dict[str, pd.DataFrame],
        metadata_id: str,
        config: Optional[MetadataConfig] = None,
    ) -> Metadata:
        """
        分析多表格資料集

        Args:
            tables: 表格字典 {table_name: dataframe}
            metadata_id: 元資料識別碼
            config: 可選的元資料配置

        Returns:
            完整的 Metadata 物件
        """
        from petsard.metadater.metadata.metadata_ops import MetadataOperations

        if config is None:
            config = MetadataConfig(metadata_id=metadata_id)

        return MetadataOperations.analyze_dataset(tables, config)

    # Schema 層 (單表格結構)
    @classmethod
    def create_schema(
        cls,
        dataframe: pd.DataFrame,
        schema_id: str,
        config: Optional[SchemaConfig] = None,
    ) -> SchemaMetadata:
        """
        建立單表格結構描述

        Args:
            dataframe: 要分析的 DataFrame
            schema_id: 結構描述識別碼
            config: 可選的結構描述配置

        Returns:
            SchemaMetadata 物件
        """
        from petsard.metadater.schema.schema_functions import build_schema_metadata
        from petsard.metadater.schema.schema_types import SchemaConfig

        if config is None:
            config = SchemaConfig(schema_id=schema_id)

        return build_schema_metadata(dataframe, config)

    @classmethod
    def analyze_dataframe(
        cls,
        dataframe: pd.DataFrame,
        schema_id: str,
        config: Optional[SchemaConfig] = None,
    ) -> SchemaMetadata:
        """
        分析單表格結構 (create_schema 的別名，語意更清楚)

        Args:
            dataframe: 要分析的 DataFrame
            schema_id: 結構描述識別碼
            config: 可選的結構描述配置

        Returns:
            SchemaMetadata 物件
        """
        return cls.create_schema(dataframe, schema_id, config)

    # Field 層 (單欄位分析)
    @classmethod
    def create_field(
        cls, series: pd.Series, field_name: str, config: Optional[FieldConfig] = None
    ) -> FieldMetadata:
        """
        建立單欄位元資料

        Args:
            series: 要分析的 Series
            field_name: 欄位名稱
            config: 可選的欄位配置

        Returns:
            FieldMetadata 物件
        """
        from petsard.metadater.field.field_functions import build_field_metadata

        return build_field_metadata(series, field_name, config)

    @classmethod
    def analyze_series(
        cls, series: pd.Series, field_name: str, config: Optional[FieldConfig] = None
    ) -> FieldMetadata:
        """
        分析單欄位資料 (create_field 的別名，語意更清楚)

        Args:
            series: 要分析的 Series
            field_name: 欄位名稱
            config: 可選的欄位配置

        Returns:
            FieldMetadata 物件
        """
        return cls.create_field(series, field_name, config)
