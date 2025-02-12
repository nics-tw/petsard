from datetime import datetime

import pandas as pd
import pytest

from petsard.error import ConfigError
from petsard.processor.date_format_converter import (
    DateFormatConverter,
    MinguoYConverter,
)


class TestMinguoYConverter:
    @pytest.fixture
    def converter(self):
        return MinguoYConverter()

    def test_init(self, converter):
        # Test initialization
        assert converter.custom_format == "%MinguoY"
        assert converter.standard_format == "%Y"
        assert converter.default_length == 3

    def test_to_standard_only_valid_cases(self, converter):
        # Test converting Minguo year to Gregorian year
        test_cases = [
            ("112", "%MinguoY", "2023"),
            ("001", "%MinguoY", "1912"),
            ("099", "%MinguoY", "2010"),
        ]
        for minguo, fmt, expected in test_cases:
            assert converter.to_standard_only(minguo, fmt) == expected

    def test_to_standard_valid_cases(self, converter):
        # Test converting complete date strings
        test_cases = [
            ("112-01-01", "%MinguoY-%m-%d", "2023-01-01"),
            ("01-112-01", "%m-%MinguoY-%d", "01-2023-01"),
            ("01-01-112", "%m-%d-%MinguoY", "01-01-2023"),
        ]
        for minguo, fmt, expected in test_cases:
            assert converter.to_standard(minguo, fmt) == expected

    def test_invalid_year_format(self, converter):
        # Test invalid year formats
        with pytest.raises(Exception):
            # Invalid characters in year
            converter.to_standard("abc-01-01", "%MinguoY-%m-%d")

        with pytest.raises(Exception):
            # Negative year
            converter.to_standard("-01-01-01", "%MinguoY-%m-%d")

        with pytest.raises(Exception):
            # Year that would result in pre-1912 Gregorian date
            converter.to_standard("000-01-01", "%MinguoY-%m-%d")

    def test_invalid_format_string(self, converter):
        # Test invalid format strings
        with pytest.raises(ConfigError):
            converter.to_standard("112-01-01", "%Y-%m-%d")  # No %MinguoY

        with pytest.raises(ConfigError):
            converter.to_standard(
                "112-01-01", "%MinguoY-%MinguoY-%m-%d"
            )  # Multiple %MinguoY

    def test_from_standard_valid_cases(self, converter):
        # Test converting from Gregorian dates
        test_cases = [
            (datetime(2023, 1, 1), "112"),
            (datetime(1912, 1, 1), "001"),
            (datetime(2010, 12, 31), "099"),
        ]
        for dt, expected in test_cases:
            assert converter.from_standard(dt) == expected

    def test_from_standard_edge_cases(self, converter):
        # Test handling of None and NaT values
        assert converter.from_standard(None) is None
        assert converter.from_standard(pd.NaT) is None

        # Test pre-1912 dates - accepting conversion
        result = converter.from_standard(datetime(1911, 12, 31))
        assert result == "000"  # Year 1911 maps to Minguo year 0

        # Test invalid input types
        with pytest.raises(Exception):
            converter.from_standard("2023")  # String input instead of datetime

    def test_find_custom_position(self, converter):
        # Test finding position of MinguoY in different formats
        test_cases = [
            ("112-01-01", "%MinguoY-%m-%d", (0, 3)),
            ("01-112-01", "%m-%MinguoY-%d", (3, 6)),
            ("01-01-112", "%m-%d-%MinguoY", (6, 9)),
        ]
        for value, fmt, expected in test_cases:
            assert converter.find_custom_position(value, fmt) == expected

    def test_find_custom_position_edge_cases(self, converter):
        # Test edge cases for position finding
        with pytest.raises(ConfigError):
            converter.find_custom_position("112-01-01", "%Y-%m-%d")  # No custom format

        with pytest.raises(ConfigError):
            converter.find_custom_position(
                "112-01-01", "%MinguoY-%MinguoY-%m-%d"
            )  # Multiple custom formats


class TestDateFormatConverter:
    def test_base_class_methods(self):
        # Test that base class methods raise NotImplementedError
        converter = DateFormatConverter("%test", "%std", 3)

        with pytest.raises(NotImplementedError):
            converter.to_standard_only("value", "format")

        with pytest.raises(NotImplementedError):
            converter.to_standard("value", "format", "format")

        with pytest.raises(NotImplementedError):
            converter.from_standard(datetime.now())
