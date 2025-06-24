"""
PETsARD Metadater Module - 元資料管理模組

提供統一的三層架構元資料管理介面：
- Metadata 層: 多表格資料集管理 (datasets)
- Schema 層: 單表格結構管理 (dataframe)
- Field 層: 單欄位分析管理 (column)

主要使用方式：
    from petsard.metadater import Metadater

    # 最常用：分析單表格
    schema = Metadater.create_schema(dataframe, "my_schema")

    # 分析單欄位
    field = Metadater.create_field(series, "my_field")

    # 分析多表格資料集
    metadata = Metadater.analyze_dataset(tables, "my_dataset")
"""

# 主要介面
# SDV adapter 功能
from petsard.metadater.adapters.sdv_adapter import SDVMetadataAdapter
from petsard.metadater.field.field_types import FieldConfig, FieldMetadata

# 核心類型 (使用者需要的)
from petsard.metadater.metadata.metadata_types import Metadata, MetadataConfig
from petsard.metadater.metadater import Metadater
from petsard.metadater.schema.schema_types import SchemaConfig, SchemaMetadata
from petsard.metadater.types.data_types import safe_round

__all__ = [
    # 主要介面
    "Metadater",
    # 核心類型
    "Metadata",
    "MetadataConfig",
    "SchemaMetadata",
    "SchemaConfig",
    "FieldMetadata",
    "FieldConfig",
    # SDV adapter
    "SDVMetadataAdapter",
    # 工具函數
    "safe_round",
]
