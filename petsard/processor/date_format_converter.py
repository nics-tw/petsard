from datetime import date, datetime
from typing import Optional, Union

import pandas as pd

from petsard.exceptions import ConfigError


class DateFormatConverter:
    """Base class for date format converters"""

    def __init__(self, custom_format: str, standard_format: str, default_length: int):
        self.custom_format = custom_format
        self.standard_format = standard_format
        self.default_length = default_length

    def to_standard_only(self, value: str, format_str: str) -> str:
        """from customer format to standard format (that precision only)"""
        raise NotImplementedError

    def to_standard(self, value: str, format_str, str) -> str:
        """from customer format to standard format"""
        raise NotImplementedError

    def from_standard(self, value: datetime) -> str:
        """from standard format to customer format"""
        raise NotImplementedError

    def find_custom_position(self, value: str, format_str: str) -> tuple[int, int]:
        """
        Find the start and end position of custom format segment in the value string.

        Args:
            value: Input string
            format_str: Format string containing the custom format

        Returns:
            tuple[int, int]: Start and end position of custom format segment

        Example:
            For custom_format="%MinguoY":
            "01-113-15" with "%m-%MinguoY-%d"  -> (3, 6)
            "113-01-15" with "%MinguoY-%m-%d"  -> (0, 3)
            "01-15-113" with "%m-%d-%MinguoY"  -> (6, 9)
        """
        # Split format by custom_format
        parts = format_str.split(self.custom_format)
        if len(parts) != 2:
            raise ConfigError(f"Format must contain exactly one {self.custom_format}")

        prefix_fmt, suffix_fmt = parts

        try:
            # Case 1: custom format at start
            if not prefix_fmt:
                # Try to parse remaining part
                for i in range(2, 5):  # Try different lengths
                    try:
                        remaining = value[i:]
                        datetime.strptime(remaining, suffix_fmt)
                        return 0, i
                    except ValueError:
                        continue

            # Case 2: custom format at end
            elif not suffix_fmt:
                # Try to parse prefix
                for i in range(len(value) - 2, len(value) - 5, -1):
                    try:
                        prefix = value[:i]
                        datetime.strptime(prefix, prefix_fmt)
                        return i, len(value)
                    except ValueError:
                        continue

            # Case 3: custom format in middle
            else:
                for mid_start in range(len(value)):
                    for mid_len in range(2, 5):
                        try:
                            mid_end = mid_start + mid_len
                            prefix = value[:mid_start]
                            suffix = value[mid_end:]

                            if prefix:
                                datetime.strptime(prefix, prefix_fmt)
                            if suffix:
                                datetime.strptime(suffix, suffix_fmt)

                            return mid_start, mid_end
                        except ValueError:
                            continue

            # If all parsing attempts fail, use default_length
            if not prefix_fmt:  # At start
                return 0, self.default_length
            elif not suffix_fmt:  # At end
                return len(value) - self.default_length, len(value)
            else:  # In middle - assume immediately after prefix pattern
                pos = len(format_str[: format_str.find(self.custom_format)])
                return pos, pos + self.default_length

        except Exception:
            # Fallback to default_length based positioning
            if not prefix_fmt:  # At start
                return 0, self.default_length
            elif not suffix_fmt:  # At end
                return len(value) - self.default_length, len(value)
            else:  # In middle
                pos = len(format_str[: format_str.find(self.custom_format)])
                return pos, pos + self.default_length


class MinguoYConverter(DateFormatConverter):
    """Converter for handling Taiwan's Minguo calendar format"""

    def __init__(self):
        super().__init__("%MinguoY", "%Y", default_length=3)

    def _validate_minguo_year(self, year_str: str) -> int:
        """
        Validate and convert Minguo year string to integer.

        Args:
            year_str: Year string to validate

        Returns:
            int: Validated Minguo year

        Raises:
            ValueError: If year string is invalid
        """
        # Check if the year string contains only digits
        if not year_str.isdigit() and not (
            year_str.startswith("-") and year_str[1:].isdigit()
        ):
            raise ValueError(f"Invalid year format: {year_str}")

        minguo_year = int(year_str)
        gregorian_year = minguo_year + 1911

        if gregorian_year < 1912:
            raise ValueError(f"Year {gregorian_year} is before Minguo calendar era")

        return minguo_year

    def to_standard_only(self, value: str, format_str: str) -> str:
        """
        Convert from Minguo year to Gregorian year based on format string

        Args:
            value: Date string containing Minguo year
            format_str: Format string containing %MinguoY

        Returns:
            Date string with Gregorian year

        Raises:
            ConfigError: If %MinguoY not found in format string
            ValueError: If year string is invalid
        """
        try:
            # Find the position of Minguo year in the value string
            start_pos, end_pos = self.find_custom_position(value, format_str)

            # Extract and validate the year
            minguo_year = self._validate_minguo_year(value[start_pos:end_pos])
            gregorian_year = minguo_year + 1911

            # Return converted year
            return str(gregorian_year)

        except ValueError as e:
            raise ValueError(f"Failed to convert Minguo year: {e}")

    def to_standard(self, value: str, format_str: str) -> str:
        """
        Convert from Minguo year to Gregorian year based on format string

        Args:
            value: Date string containing Minguo year
            format_str: Format string containing %MinguoY

        Returns:
            Date string with Gregorian year

        Raise:
            ConfigError: If %MinguoY not found in format string
            ValueError: If year string is invalid
        """
        try:
            # Find positions for each format token
            positions = []
            current_pos = 0

            # Parse format string to find token positions
            i = 0
            while i < len(format_str):
                if format_str[i:].startswith(self.custom_format):
                    positions.append(
                        ("year", current_pos, current_pos + self.default_length)
                    )
                    current_pos += self.default_length
                    i += len(self.custom_format)
                elif format_str[i:].startswith("%m"):
                    positions.append(("month", current_pos, current_pos + 2))
                    current_pos += 2
                    i += 2
                elif format_str[i:].startswith("%d"):
                    positions.append(("day", current_pos, current_pos + 2))
                    current_pos += 2
                    i += 2
                else:
                    i += 1
                    current_pos += 1

            # Extract and validate components
            for token_type, start, end in positions:
                component = value[start:end]
                if token_type == "month":
                    month = int(component)
                    if month < 1 or month > 12:
                        raise ValueError(f"Invalid month: {month}")
                elif token_type == "day":
                    day = int(component)
                    if day < 1 or day > 31:  # Basic validation
                        raise ValueError(f"Invalid day: {day}")
                elif token_type == "year":
                    year = int(component)

            # Only convert year if all components are valid
            gregorian_year = year + 1911
            return str(gregorian_year) + value[self.default_length :]

        except ValueError as e:
            raise ValueError(f"Invalid date component: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to convert date: {str(e)}")

    def from_standard(self, value: Union[datetime, date, None]) -> Optional[str]:
        """Convert from Gregorian year to Minguo year

        Args:
            value: datetime object or None

        Returns:
            Minguo year string or None if input is None/NaN
        """
        if pd.isna(value) or value is None:
            return None

        try:
            if isinstance(value, (datetime, date)):
                minguo_year = value.year - 1911
                if minguo_year < 0:
                    raise ValueError(f"Year {value.year} is before Minguo calendar era")
                return str(f"{minguo_year:03d}")
            raise ValueError(f"Invalid datetime/date object: {value}")

        except AttributeError:
            raise ValueError(f"Invalid datetime object: {value}")
        except Exception as e:
            raise ValueError(f"Error converting to Minguo year: {e}")
