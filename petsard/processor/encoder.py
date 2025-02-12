from datetime import date, datetime
from typing import Any, Optional, Union

import numpy as np
import pandas as pd
from dateutil import parser
from sklearn.preprocessing import LabelEncoder, OneHotEncoder

from petsard.error import ConfigError, UnfittedError
from petsard.processor.date_format_converter import MinguoYConverter


class Encoder:
    """
    Base class for all Encoder classes.
    """

    PROC_TYPE = ("encoder",)

    def __init__(self) -> None:
        # Mapping dict
        self.cat_to_val = None

        # Labels
        self.labels = None

        self._is_fitted = False

    def fit(self, data: pd.Series) -> None:
        """
        Base method of `fit`.

        Args:
            data (pd.Series): The data to be fitted.
        """
        self._fit(data)

        self._is_fitted = True

    def _fit():
        """
        _fit method is implemented in subclasses.

        fit method is responsible for general action defined by the base class.
        _fit method is for specific procedure conducted by each subclasses.
        """
        raise NotImplementedError(
            "_fit method should be implemented " + "in subclasses."
        )

    def transform(self, data: pd.Series) -> np.ndarray:
        """
        Base method of `transform`.

        Args:
            data (pd.Series): The data to be transformed.

        Return:
            (np.ndarray): The transformed data.
        """
        # Check the object is fitted
        if not self._is_fitted:
            raise UnfittedError("The object is not fitted. Use .fit() first.")

        # Check whether the categories of the column are
        # included in the fitted instance
        if not set(data.unique()).issubset(set(self.labels)):
            raise ValueError(
                "The data contains categories that the object hasn't seen",
                " in the fitting process.",
                " Please check the data categories again.",
            )

        return self._transform(data)

    def _transform():
        """
        _transform method is implemented in subclasses.

        transform method is responsible for general action
            defined by the base class.
        _transform method is for specific procedure
            conducted by each subclasses.
        """
        raise NotImplementedError(
            "_transform method should be implemented " + "in subclasses."
        )

    def inverse_transform(self, data: pd.Series) -> pd.Series | np.ndarray:
        """
        Base method of `inverse_transform`.

        Args:
            data (pd.Series): The data to be inverse transformed.

        Return:
            (pd.Series | np.ndarray): The inverse transformed data.
        """
        # Check the object is fitted
        if not self._is_fitted:
            raise UnfittedError("The object is not fitted. Use .fit() first.")

        return self._inverse_transform(data)

    def _inverse_transform():
        """
        _inverse_transform method is implemented in subclasses.

        inverse_transform method is responsible for general action
            defined by the base class.
        _inverse_transform method is for specific procedure
            conducted by each subclasses.
        """
        raise NotImplementedError(
            "_inverse_transform method should be " + "implemented in subclasses."
        )


class EncoderUniform(Encoder):
    """
    Implement a uniform encoder.
    """

    def __init__(self) -> None:
        super().__init__()

        # Lower and upper values
        self.upper_values = None
        self.lower_values = None

        # Initiate a random generator
        self._rgenerator = np.random.default_rng()

    def _fit(self, data: pd.Series) -> None:
        """
        Gather information for transformation and reverse transformation.

        Args:
            data (pd.Series): The categorical data needed to be transformed.
        """
        # Filter the counts > 0
        normalize_value_counts = data.value_counts(normalize=True).loc[lambda x: x > 0]
        # Get keys (original labels)
        self.labels = normalize_value_counts.index.get_level_values(0).to_list()
        # Get values (upper and lower bounds)
        self.upper_values = np.cumsum(normalize_value_counts.values)
        self.lower_values = np.roll(self.upper_values, 1)
        # To make sure the range of the data is in [0, 1].
        # That is, the range of an uniform dist.
        self.upper_values[-1] = 1.0
        self.lower_values[0] = 0.0

        self.cat_to_val = dict(
            zip(self.labels, list(zip(self.lower_values, self.upper_values)))
        )

    def _transform(self, data: pd.Series) -> np.ndarray:
        """
        Transform categorical data to a uniform distribution.
            For example, a column with two categories (e.g., 'Male', 'Female')
                  can be mapped to [0.0, 0.5) and [0.5, 1], respectively.

        Args:
            data (pd.Series): The categorical data needed to be transformed.

        Return:
            (np.ndarray): The transformed data.
        """

        if isinstance(data.dtype, pd.api.types.CategoricalDtype):
            data_obj = data.astype(object)
        else:
            data_obj = data.copy()

        return data_obj.map(
            lambda x: self._rgenerator.uniform(
                self.cat_to_val[x][0], self.cat_to_val[x][1], size=1
            )[0]
        ).values

    def _inverse_transform(self, data: pd.Series) -> pd.Series:
        """
        Inverse the transformed data to the categorical data.

        Args:
            data (pd.Series): The categorical data needed to
            be transformed inversely.

        Return:
            (pd.Series): The inverse transformed data.
        """

        # Check the range of the data is valid
        if data.max() > 1 or data.min() < 0:
            raise ValueError(
                "The range of the data is out of range.",
                " Please check the data again.",
            )

        bins_val = np.append(self.lower_values, 1.0)

        return pd.cut(
            data,
            right=False,
            include_lowest=True,
            bins=bins_val,
            labels=self.labels,
            ordered=False,
        )


class EncoderLabel(Encoder):
    """
    Implement a label encoder.
    """

    PROC_TYPE = ("encoder", "discretizing")

    def __init__(self) -> None:
        super().__init__()
        self.model = LabelEncoder()

    def _fit(self, data: pd.Series) -> None:
        """
        Gather information for transformation and reverse transformation.

        Args:
            data (pd.Series): The categorical data needed to be transformed.
        """
        self.model.fit(data)

        # Get keys (original labels)
        self.labels = list(self.model.classes_)

        self.cat_to_val = dict(
            zip(self.labels, list(self.model.transform(self.model.classes_)))
        )

    def _transform(self, data: pd.Series) -> np.ndarray:
        """
        Transform categorical data to a series of integer labels.

        Args:
            data (pd.Series): The categorical data needed to be transformed.

        Return:
            (np.ndarray): The transformed data.
        """

        return self.model.transform(data)

    def _inverse_transform(self, data: pd.Series) -> np.ndarray:
        """
        Inverse the transformed data to the categorical data.

        Args:
            data (pd.Series): The categorical data needed to
            be transformed inversely.

        Return:
            (np.ndarray): The inverse transformed data.
        """

        return self.model.inverse_transform(data)


class EncoderOneHot(Encoder):
    """
    Implement a one-hot encoder.
    """

    def __init__(self) -> None:
        super().__init__()
        self.model = OneHotEncoder(sparse_output=False, drop="first")

        # for the use in Mediator
        self._transform_temp: np.ndarray = None

    def _fit(self, data: pd.Series) -> None:
        """
        Gather information for transformation and reverse transformation.

        Args:
            data (pd.Series): The categorical data needed to be transformed.
        """
        self.model.fit(data.values.reshape(-1, 1))

        # Set original labels
        self.labels = self.model.categories_[0].tolist()

    def _transform(self, data: pd.Series) -> None:
        """
        Transform categorical data to a one-hot numeric array.

        Args:
            data (pd.Series): The categorical data needed to be transformed.

        Return:
            None: The transformed data is stored in _transform_temp.
            data (pd.Series): Original data (dummy).
        """

        self._transform_temp = self.model.transform(data.values.reshape(-1, 1))

        return data

    def _inverse_transform(self, data: pd.Series) -> None:
        """
        Inverse the transformed data to the categorical data.
        This is a dummy method, and it is implemented in MediatorEncoder.

        Args:
            data (pd.Series): The categorical data needed to
            be transformed inversely.

        Return:
            data (pd.Series): Original data (dummy).
        """

        return data


class EncoderDate(Encoder):
    """
    Flexible date encoder for transforming various date formats
    """

    def __init__(
        self,
        input_format: Optional[str] = None,
        date_type: str = "datetime",
        tz: Optional[str] = None,
        numeric_convert: bool = False,
        invalid_handling: str = "error",
        invalid_rules: Optional[list[dict[str, str]]] = None,
    ) -> None:
        super().__init__()

        # Validate inputs
        self._validate_init_params(date_type, invalid_handling)

        # Store parameters
        self.input_format = input_format
        self.date_type = date_type
        self.tz = tz
        self.numeric_convert = numeric_convert
        self.invalid_handling = invalid_handling
        self.invalid_rules = invalid_rules or []

        # Register built-in format converters
        self._custom_format_converters = {
            converter.custom_format: converter
            for converter in [
                MinguoYConverter(),
            ]
        }

    def _validate_init_params(self, date_type: str, invalid_handling: str) -> None:
        """Validate initialization parameters"""
        if date_type not in ["date", "datetime", "datetime_tz"]:
            raise ConfigError("date_type must be 'date', 'datetime', or 'datetime_tz'")

        if invalid_handling not in ["error", "erase", "replace"]:
            raise ValueError("invalid_handling must be 'error', 'erase', or 'replace'")

    def _convert_to_standard_format(
        self, value: str, format_str: str
    ) -> tuple[str, str]:
        """Convert custom format to standard format"""
        current_value = str(value)
        current_format = format_str

        for fmt, converter in self._custom_format_converters.items():
            if fmt in current_format:
                current_value = converter.to_standard(current_value, self.input_format)
                current_format = current_format.replace(fmt, converter.standard_format)

        return current_value, current_format

    def _format_output(self, parsed_date: datetime) -> Union[date, datetime]:
        """Format output according to specified date_type"""
        if parsed_date is None:
            return None

        if self.date_type == "date":
            return parsed_date.date()
        elif self.date_type == "datetime_tz" and self.tz:
            try:
                import zoneinfo

                return parsed_date.replace(tzinfo=zoneinfo.ZoneInfo(self.tz))
            except ImportError:
                raise ImportError("zoneinfo module required for timezone support")
        return parsed_date.replace(tzinfo=None)

    def _apply_replacement_rules(self, value: str) -> Union[datetime, None]:
        """Apply replacement rules for invalid dates"""
        for index, rule in enumerate(self.invalid_rules):
            is_last_rule = index == len(self.invalid_rules) - 1
            if "fallback" in rule:
                return self._handle_invalid_date(
                    value, invalid_handling=rule["fallback"]
                )
            elif is_last_rule:
                return self._handle_invalid_date(value, invalid_handling="erase")

            current_value = str(value)
            current_format = self.input_format

            try:
                # Try applying value in custom format
                for fmt, repl in rule.items():
                    # replace custom format
                    if fmt in self._custom_format_converters:
                        current_value = self._custom_format_converters[fmt].to_standard(
                            current_value, self.input_format
                        )
                        current_format = current_format.replace(
                            fmt, self._custom_format_converters[fmt].standard_format
                        )

                # Try replacing the value in standard strptime format
                new_date_value = list(current_value)

                # Calculate cumulative position for each format token
                fmt_positions = {}
                current_pos = 0
                for fmt in ["%Y", "%m", "%d", "%H", "%M", "%S"]:
                    if fmt in current_format:
                        fmt_positions[fmt] = current_pos
                        # Use standard length for common tokens
                        current_pos += {
                            "%Y": 4,
                            "%m": 2,
                            "%d": 2,
                            "%H": 2,
                            "%M": 2,
                            "%S": 2,
                        }.get(fmt, len(str(fmt)))

                for fmt, repl in rule.items():
                    if fmt not in self._custom_format_converters:
                        # Find the starting position using cumulative calculation
                        fmt_index = fmt_positions[fmt]

                        try:
                            # Use standard length for common tokens
                            length = {
                                "%Y": 4,
                                "%m": 2,
                                "%d": 2,
                                "%H": 2,
                                "%M": 2,
                                "%S": 2,
                            }.get(fmt, len(repl))

                            # Replace the corresponding portion of the date string
                            new_date_value[fmt_index : fmt_index + length] = list(
                                str(repl).zfill(length)[:length]
                            )
                        except ValueError:
                            # Raise an error if the replacement is incompatible with the format
                            raise ConfigError(
                                f"Cannot replace {fmt} with {repl} in the given format"
                            )
                current_value = "".join(new_date_value)

                # Try parsing with the modified value
                return datetime.strptime(current_value, current_format)

            except Exception:
                continue

        return None

    def _handle_invalid_date(
        self, value: Any, invalid_handling: str
    ) -> Union[datetime, None]:
        """Handle invalid dates according to specified strategy"""
        if invalid_handling == "error":
            raise ValueError(f"Invalid date format: {value}")
        elif invalid_handling in ["drop", "erase"]:
            return None
        elif invalid_handling == "replace":
            return self._apply_replacement_rules(value)
        else:
            raise ValueError(f"Invalid handling strategy: {invalid_handling}")

    def _parse_date(self, value: Union[str, int, float]) -> Union[datetime, date, None]:
        """Main date parsing method"""
        if value is None:
            return None

        if self.numeric_convert and isinstance(value, (int, float)):
            value = str(int(value))

        try:
            if self.input_format:
                # Handle custom formats first
                current_value, current_format = self._convert_to_standard_format(
                    value, self.input_format
                )
                # Then use standard strptime
                parsed = datetime.strptime(current_value, current_format)
            else:
                # Use fuzzy parsing if no format specified
                try:
                    parsed = parser.parse(str(value), fuzzy=True)
                except Exception:
                    if isinstance(value, (int, float)):
                        parsed = pd.to_datetime(float(value), unit="s")
                    else:
                        parsed = pd.to_datetime(value)

            return self._format_output(parsed)
        except Exception:
            return self._handle_invalid_date(value, self.invalid_handling)

    def _fit(self, data: pd.Series) -> None:
        """Fit the encoder to the data"""
        self.labels = data.unique().tolist()
        # Validate parsing
        data.apply(self._parse_date)

    def _inverse_transform(self, data: pd.Series) -> pd.Series:
        """Transform dates back to original format"""
        if not self.input_format:
            format_str = {
                "date": "%Y-%m-%d",
                "datetime": "%Y-%m-%d %H:%M:%S",
                "datetime_tz": "%Y-%m-%d %H:%M:%S %Z"
                if self.tz
                else "%Y-%m-%d %H:%M:%S",
            }[self.date_type]
            return data.apply(lambda x: x.strftime(format_str) if pd.notna(x) else None)

        def format_date(x: Optional[datetime]) -> Optional[str]:
            """Format a single date value"""
            if pd.isna(x):
                return None

            result = self.input_format
            for fmt, converter in self._custom_format_converters.items():
                if fmt in self.input_format:
                    custom_part = converter.from_standard(x)
                    if custom_part is None:
                        return None
                    pos = result.find(fmt)
                    if pos >= 0:
                        result = (
                            x.strftime(result[:pos])
                            + custom_part
                            + x.strftime(result[pos + len(fmt) :])
                        )

            return result if "%" not in result else x.strftime(result)

        return data.apply(format_date)

    def _transform(self, data: pd.Series) -> np.ndarray:
        """Convert single column of data to date format"""
        return data.apply(self._parse_date).values
