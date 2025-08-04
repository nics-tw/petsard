"""
Test suite for SchemaConfig functionality.

This test suite covers:
1. SchemaConfig validation with parameters
2. Parameter conflicts detection
3. Edge cases and error handling
"""

import pytest

from petsard.metadater.field.field_types import FieldConfig
from petsard.metadater.schema.schema_types import SchemaConfig


class TestSchemaConfigValidation:
    """Test SchemaConfig validation with parameters"""

    def test_schema_config_with_parameters(self):
        """Test SchemaConfig creation with parameters"""
        field_config = FieldConfig(
            type="str", logical_type="email", leading_zeros="never"
        )

        schema_config = SchemaConfig(
            schema_id="test_schema",
            name="Test Schema",
            description="Test description",
            fields={"email": field_config},
            compute_stats=False,
            infer_logical_types=False,
            optimize_dtypes=True,
            sample_size=1000,
            leading_zeros="never",
            nullable_int="force",
        )

        assert schema_config.schema_id == "test_schema"
        assert schema_config.compute_stats == False
        assert schema_config.leading_zeros == "never"
        assert schema_config.nullable_int == "force"

    def test_schema_config_invalid_leading_zeros(self):
        """Test SchemaConfig with invalid leading_zeros"""
        with pytest.raises(ValueError):
            SchemaConfig(schema_id="test_schema", leading_zeros="invalid_value")

    def test_schema_config_invalid_nullable_int(self):
        """Test SchemaConfig with invalid nullable_int"""
        with pytest.raises(ValueError):
            SchemaConfig(schema_id="test_schema", nullable_int="invalid_value")

    def test_schema_config_logical_type_conflict(self):
        """Test SchemaConfig with logical type conflict"""
        field_config = FieldConfig(type="str", logical_type="email")

        with pytest.raises(ValueError, match="Cannot set infer_logical_types=True"):
            SchemaConfig(
                schema_id="test_schema",
                fields={"email": field_config},
                infer_logical_types=True,
            )


if __name__ == "__main__":
    pytest.main([__file__])
