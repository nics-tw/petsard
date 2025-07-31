from datetime import datetime

import pytest

from petsard.exceptions import ConfigError
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

    def test_to_standard_edge_cases(self, converter):
        """Test edge cases for conversion involving invalid dates"""
        test_cases = [
            ("1130024", "%MinguoY%m%d"),  # Invalid month (00)
            ("1130132", "%MinguoY%m%d"),  # Invalid day (32)
            ("1131324", "%MinguoY%m%d"),  # Invalid month (13)
            ("9999999", "%MinguoY%m%d"),  # Completely invalid format
            ("0000000", "%MinguoY%m%d"),  # All zeros
        ]
        for value, fmt in test_cases:
            with pytest.raises(ValueError):
                converter.to_standard(value, fmt)

    def test_to_standard_valid_edge_dates(self, converter):
        """Test valid but edge case dates"""
        test_cases = [
            ("1130229", "%MinguoY%m%d", "20240229"),  # Leap year
            ("1130228", "%MinguoY%m%d", "20240228"),  # Last day of Feb
            ("1130131", "%MinguoY%m%d", "20240131"),  # Last day of Jan
        ]
        for minguo, fmt, expected in test_cases:
            assert converter.to_standard(minguo, fmt) == expected

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
