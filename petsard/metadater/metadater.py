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

    # 處理器相關的元資料調整方法
    @classmethod
    def adjust_metadata_after_processing(
        cls,
        mode: str,
        data: pd.Series | pd.DataFrame,
        original_metadata: "SchemaMetadata",
        col: str = None,
    ) -> Optional["SchemaMetadata"]:
        """
        在資料處理後調整元資料

        Args:
            mode (str): 調整模式
                'columnwise': 基於單欄位調整元資料
                'global': 基於整個資料框調整元資料
            data (pd.Series | pd.DataFrame): 處理後的資料
            original_metadata (SchemaMetadata): 原始元資料
            col (str): 欄位名稱 (columnwise 模式需要)

        Returns:
            Optional[SchemaMetadata]: 調整後的元資料 (如果適用)

        Raises:
            ValueError: 如果參數無效
        """
        from datetime import datetime

        logger = logging.getLogger(f"PETsARD.{cls.__name__}")
        logger.debug(f"Starting metadata adjustment, mode: {mode}")

        try:
            if mode == "columnwise":
                if not isinstance(data, pd.Series):
                    logger.warning("Input data must be pd.Series for columnwise mode")
                    raise ValueError("data should be pd.Series in columnwise mode.")
                if col is None:
                    logger.warning("Column name not specified")
                    raise ValueError("col is not specified.")
                if not original_metadata.get_field(col):
                    raise ValueError(f"{col} is not in the metadata.")

                logger.debug(f"Adjusting metadata for column '{col}'")

                # Calculate optimized dtype information
                # Use Metadater's public API to analyze the field
                temp_field_config = FieldConfig()
                temp_field_metadata = cls.create_field(
                    series=data,
                    field_name=col,
                    config=temp_field_config,
                )
                dtype_after_preproc: str = temp_field_metadata.target_dtype or str(
                    data.dtype
                )

                # Map data type to legacy categories using the field metadata
                data_type = temp_field_metadata.data_type
                if hasattr(data_type, "value"):
                    data_type_str = data_type.value.lower()
                else:
                    data_type_str = str(data_type).lower()

                # Map to legacy categories
                if data_type_str in [
                    "int8",
                    "int16",
                    "int32",
                    "int64",
                    "float32",
                    "float64",
                    "decimal",
                ]:
                    infer_dtype_after_preproc = "numerical"
                elif data_type_str in ["string", "binary"]:
                    infer_dtype_after_preproc = "categorical"
                elif data_type_str == "boolean":
                    infer_dtype_after_preproc = "categorical"
                elif data_type_str in ["date", "time", "timestamp", "timestamp_tz"]:
                    infer_dtype_after_preproc = "datetime"
                else:
                    infer_dtype_after_preproc = "object"

                # Note: SchemaMetadata is immutable, so we can't directly update it
                # In a full refactor, we might want to create a new SchemaMetadata
                # or track these changes separately. For now, we'll log the information.
                logger.debug(
                    f"Column '{col}' dtype after preprocessing: {dtype_after_preproc}, "
                    f"inferred type: {infer_dtype_after_preproc}"
                )
                return None  # No new metadata returned for columnwise mode

            elif mode == "global":
                if not isinstance(data, pd.DataFrame):
                    raise ValueError("data should be pd.DataFrame in global mode.")

                logger.debug("Performing global metadata adjustment")

                # Create new schema metadata for the transformed data
                new_schema_metadata = cls.create_schema(
                    dataframe=data,
                    schema_id=f"processor_adjusted_{datetime.now().isoformat()}",
                )

                # Note: In the original design, this would update col_after_preproc
                # Since SchemaMetadata is immutable, we log this information instead
                logger.debug(
                    f"Created new schema metadata for transformed data with "
                    f"{len(new_schema_metadata.fields)} fields"
                )
                return new_schema_metadata

            else:
                raise ValueError("Invalid mode. Must be 'columnwise' or 'global'.")

        except Exception as e:
            logger.error(f"Metadata adjustment failed: {str(e)}")
            raise

    @staticmethod
    def apply_dtype_conversion(
        series: pd.Series, target_dtype: str, cast_error: str = "raise"
    ) -> pd.Series:
        """
        應用資料類型轉換

        Args:
            series: 要轉換的 Series
            target_dtype: 目標資料類型
            cast_error: 錯誤處理方式 ('raise', 'coerce', 'ignore')

        Returns:
            轉換後的 Series
        """
        try:
            if cast_error == "coerce":
                return pd.to_numeric(series, errors="coerce").astype(
                    target_dtype, errors="ignore"
                )
            elif cast_error == "ignore":
                return series.astype(target_dtype, errors="ignore")
            else:
                return series.astype(target_dtype)
        except Exception:
            if cast_error == "raise":
                raise
            return series
