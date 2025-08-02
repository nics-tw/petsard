"""
Test suite for FieldConfig functionality.

This test suite covers:
1. FieldConfig validation with parameters
2. Parameter validation
3. Edge cases and error handling
"""

import pytest

from petsard.metadater.field.field_types import FieldConfig


class TestFieldConfigValidation:
    """Test FieldConfig validation with parameters"""

    def test_field_config_with_parameters(self):
        """Test FieldConfig creation with parameters"""
        field_config = FieldConfig(
            type_hint="str",
            logical_type="email",
            leading_zeros="leading_5",
            category_method="auto",
        )

        assert field_config.logical_type == "email"
        assert field_config.leading_zeros == "leading_5"
        assert field_config.category_method == "auto"

    def test_field_config_invalid_logical_type(self):
        """Test FieldConfig with invalid logical_type"""
        # logical_type accepts any string, so this should not raise error
        field_config = FieldConfig(logical_type="custom_type")
        assert field_config.logical_type == "custom_type"

    def test_field_config_invalid_leading_zeros(self):
        """Test FieldConfig with invalid leading_zeros"""
        with pytest.raises(ValueError):
            FieldConfig(leading_zeros="invalid_value")

    def test_field_config_invalid_category_method(self):
        """Test FieldConfig with invalid category_method"""
        with pytest.raises(ValueError):
            FieldConfig(category_method="invalid_method")

    def test_field_config_invalid_datetime_precision(self):
        """Test FieldConfig with invalid datetime_precision"""
        with pytest.raises(ValueError):
            FieldConfig(datetime_precision="invalid_precision")


if __name__ == "__main__":
    pytest.main([__file__])
