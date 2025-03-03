from datetime import date, datetime

import pandas as pd
import pytest

from petsard.exceptions import ConfigError, UnfittedError
from petsard.processor.encoder import EncoderDate


class TestEncoderDate:
    @pytest.fixture
    def basic_encoder(self):
        return EncoderDate()

    @pytest.fixture
    def minguo_encoder(self):
        return EncoderDate(input_format="%MinguoY-%m-%d")

    def test_init_validation(self):
        # Test valid initialization
        encoder = EncoderDate(date_type="date")
        assert encoder.date_type == "date"

        # Test invalid date_type
        with pytest.raises(ConfigError):
            EncoderDate(date_type="invalid")

        # Test invalid invalid_handling
        with pytest.raises(ValueError):
            EncoderDate(invalid_handling="invalid")

    def test_basic_date_parsing(self, basic_encoder):
        # Test with standard datetime string
        data = pd.Series(["2024-02-12"])
        basic_encoder.fit(data)
        result = basic_encoder.transform(data)
        assert isinstance(result[0], datetime)
        assert result[0].year == 2024
        assert result[0].month == 2
        assert result[0].day == 12

    def test_minguo_date_parsing(self, minguo_encoder):
        # Test with Minguo calendar dates
        data = pd.Series(["113-02-12"])  # 2024-02-12
        minguo_encoder.fit(data)
        result = minguo_encoder.transform(data)
        assert isinstance(result[0], datetime)
        assert result[0].year == 2024
        assert result[0].month == 2
        assert result[0].day == 12

    def test_date_type_output(self):
        # Test date output type
        encoder = EncoderDate(date_type="date")
        data = pd.Series(["2024-02-12"])
        encoder.fit(data)
        result = encoder.transform(data)
        assert isinstance(result[0], date)

        # Test datetime output type
        encoder = EncoderDate(date_type="datetime")
        encoder.fit(data)
        result = encoder.transform(data)
        assert isinstance(result[0], datetime)

    @staticmethod
    def _numpy_datetime_to_python(dt):
        """Convert numpy datetime64 to python datetime"""
        if pd.isna(dt):
            return None
        return pd.Timestamp(dt).to_pydatetime()

    def test_timezone_handling(self):
        # Test timezone aware datetime
        encoder = EncoderDate(date_type="datetime_tz", tz="Asia/Taipei")
        data = pd.Series(["2024-02-12 15:30:00"])
        encoder.fit(data)
        result = encoder.transform(data)
        dt = self._numpy_datetime_to_python(result[0])
        assert dt.tzinfo is not None
        assert str(dt.tzinfo) == "Asia/Taipei"

    def test_invalid_date_handling(self):
        # Test error handling
        encoder = EncoderDate(invalid_handling="error")
        data = pd.Series(["invalid_date"])
        with pytest.raises(ValueError):
            encoder.fit(data)

        # Test erase handling
        encoder = EncoderDate(invalid_handling="erase")
        encoder.fit(pd.Series(["2024-02-12", "invalid_date"]))
        result = encoder.transform(pd.Series(["2024-02-12", "invalid_date"]))
        assert pd.isna(result[1])

    def test_replacement_rules(self):
        rules = [{"%Y": "2024", "%m": "02"}, {"fallback": "erase"}]
        encoder = EncoderDate(
            input_format="%Y-%m-%d", invalid_handling="replace", invalid_rules=rules
        )
        data = pd.Series(["invalid-02-12"])
        encoder.fit(data)
        result = encoder.transform(data)
        assert pd.isna(result[0])

    def test_numeric_conversion(self):
        encoder = EncoderDate(numeric_convert=True)
        timestamp = int(datetime(2024, 2, 12).timestamp())
        data = pd.Series([timestamp])
        encoder.fit(data)
        result = encoder.transform(data)
        assert isinstance(result[0], datetime)
        assert result[0].year == 2024

    def test_inverse_transform(self, minguo_encoder):
        # Test basic inverse transform
        data = pd.Series(["113-02-12"])  # 2024-02-12
        minguo_encoder.fit(data)
        transformed = minguo_encoder.transform(data)
        result = minguo_encoder.inverse_transform(pd.Series(transformed))
        assert result[0] == "113-02-12"

    def test_unfitted_error(self, basic_encoder):
        # Test transform before fit
        with pytest.raises(UnfittedError):
            basic_encoder.transform(pd.Series(["2024-02-12"]))

        # Test inverse_transform before fit
        with pytest.raises(UnfittedError):
            basic_encoder.inverse_transform(pd.Series([datetime.now()]))

    def test_unknown_categories(self, basic_encoder):
        # Fit with one set of dates
        basic_encoder.fit(pd.Series(["2024-02-12"]))

        # Try to transform different dates
        with pytest.raises(ValueError):
            basic_encoder.transform(pd.Series(["2024-02-13"]))

    def test_none_handling(self, basic_encoder):
        data = pd.Series(["2024-02-12", None])
        basic_encoder.fit(data)
        result = basic_encoder.transform(data)
        assert pd.isna(result[1])

    def test_replacement_rules_with_invalid_dates(self):
        """Test replacement rules with various invalid date formats"""
        rules = [
            {"%MinguoY": "113"},
            {"%MinguoY": "113", "%m": "01"},
            {"%MinguoY": "113", "%m": "01", "%d": "01"},
            {"fallback": "erase"},
        ]
        encoder = EncoderDate(
            input_format="%MinguoY%m%d",
            date_type="date",
            invalid_handling="replace",
            invalid_rules=rules,
        )

        test_cases = [
            ("1130024", "1130124"),  # Invalid month (00) -> 01
            ("1130132", "1130101"),  # Invalid day (32) -> 01
            ("1131324", "1130124"),  # Invalid month (13) -> 01
            ("9999999", "1130101"),  # Invalid format -> default
            ("0000000", "1130101"),  # All zeros -> default
        ]

        data = pd.Series([case[0] for case in test_cases])
        encoder.fit(data)
        result = encoder.transform(data)
        back = encoder.inverse_transform(pd.Series(result))

        for (input_val, expected), output in zip(test_cases, back):
            assert output == expected

    def test_inverse_transform_with_edge_dates(self):
        """Test inverse transform with edge case dates"""
        encoder = EncoderDate(input_format="%MinguoY%m%d", date_type="date")

        test_cases = [
            ("1130229", datetime(2024, 2, 29)),  # Leap year
            ("1130228", datetime(2024, 2, 28)),  # Last day of Feb
            ("1130131", datetime(2024, 1, 31)),  # Last day of Jan
        ]

        # Test forward transformation
        input_data = pd.Series([case[0] for case in test_cases])
        encoder.fit(input_data)
        transformed = encoder.transform(input_data)

        # Verify transformed dates
        for (_, expected_date), actual_date in zip(test_cases, transformed):
            assert actual_date.date() == expected_date.date()

        # Test inverse transformation
        back = encoder.inverse_transform(pd.Series(transformed))
        for (expected_str, _), actual_str in zip(test_cases, back):
            assert actual_str == expected_str
