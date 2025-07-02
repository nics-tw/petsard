import calendar
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Optional, Union

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, OneHotEncoder

from petsard.exceptions import ConfigError, UnfittedError


def dict_get_na(dictionary: dict, key: str) -> Any:
    """
    Get value from dictionary by key, handling NaN keys.

    Args:
        dictionary (dict): The dictionary to search.
        key (str): The key to look for.

    Returns:
        Any: The value associated with the key, or None if not found.
    """
    if pd.isna(key):
        for k, v in dictionary.items():
            if pd.isna(k):
                return v
    return dictionary.get(key, None)


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
        data_set = {x for x in set(data.unique()) if pd.notna(x)}
        labels_set = {x for x in set(self.labels) if pd.notna(x)}
        if not data_set.issubset(labels_set):
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
        normalize_value_counts = data.value_counts(normalize=True, dropna=False).loc[
            lambda x: x > 0.0
        ]
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
                dict_get_na(self.cat_to_val, x)[0],
                dict_get_na(self.cat_to_val, x)[1],
                size=1,
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

        return (
            pd.cut(
                data,
                right=False,
                include_lowest=True,
                bins=bins_val,
                labels=[
                    "pd.NA-PETsARD-impossible" if pd.isna(label) else label
                    for label in self.labels
                ],
                ordered=False,
            )
            .astype("object")
            .replace("pd.NA-PETsARD-impossible", pd.NA)
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


@dataclass
class MinguoDateFixStrategiesConfig:
    """
    Configuration for MinguoDateEncoder fix strategies.

    Attributes:
        year (int): Fixed year value
        month (int): Fixed month value
        day (int): Fixed day value
    """

    fix_strategies: str | list[dict[str, int]] = field(default_factory=list)
    year: int = None
    month: int = None
    day: int = None

    RECOMMEND_FIX_STRATEGIES: list[dict[str, int]] = field(
        default_factory=lambda: [
            {"day": 1},  # Try fixing day first
            {"month": 7, "day": 1},  # Then try fixing month and day
        ]
    )

    def __post_init__(self):
        if self.fix_strategies is None:
            return  # default to empty list

        if isinstance(self.fix_strategies, str):
            if self.fix_strategies.lower() == "recommend":
                self.fix_strategies = self.RECOMMEND_FIX_STRATEGIES
            else:
                raise ConfigError(
                    "Invalid fix strategy. Must be a list of dictionaries or 'recommend'"
                )

        for fix_strategy in self.fix_strategies:
            if not isinstance(fix_strategy, dict):
                raise ConfigError(
                    "Fix strategy must be a dictionary with 'year', 'month', and 'day' keys"
                )
            if not any(key in fix_strategy for key in ["year", "month", "day"]):
                raise ConfigError(
                    "Fix strategy must contain at least one of 'year', 'month', or 'day'"
                )
            if any(
                not isinstance(value, int) or value <= 0
                for strategy in self.fix_strategies
                for key, value in strategy.items()
            ):
                raise ConfigError("All fix strategy values must be positive integers")

            # AD 1677-09-21 00:12:43.145225 ~ 2262-04-11 23:47:16.854775807,
            #   limits by pd.Timestamp
            if "year" in fix_strategy and not 2261 >= fix_strategy["year"] >= 1678:
                raise ConfigError(
                    "Fix strategy year value must be within AD 1678 ~ 2261"
                )
            if "month" in fix_strategy and fix_strategy["month"] > 12:
                raise ConfigError("Fix strategy month value must be between 1 and 12")
            if "day" in fix_strategy and fix_strategy["day"] > 31:
                raise ConfigError("Fix strategy day value must be between 1 and 31")

            if all(key in fix_strategy for key in ["month", "day"]):
                year: int = fix_strategy.get("year", 1)
                if (
                    calendar.monthrange(year, fix_strategy["month"])[1]
                    < fix_strategy["day"]
                ):
                    raise ConfigError(
                        "Fix strategy day value must be valid for the month"
                    )

            for key in ["year", "month", "day"]:
                setattr(self, key, fix_strategy.get(key, None))


class EncoderMinguoDate(Encoder):
    """
    Encoder for converting between Minguo (ROC) dates and Gregorian (AD) dates.

    This encoder supports various input formats:
    - Integer format (YYYMMDD): 1120903
    - String formats: '112-09-03', '112/09/03', '1120903'
    - pandas Timestamp and Python datetime objects

    Attributes:
        input_format (str): Format of the input date
        fix_strategy (List[Dict]): Strategies for fixing invalid dates
    """

    def __init__(
        self,
        input_format: Optional[str] = None,
        output_format: str = "datetime",
        fix_strategies: str | list[dict[str, int]] = None,
    ) -> None:
        """
        Initialize the MinguoDateEncoder.

        Args:
            input_format: Optional format string for parsing input dates
            output_format: Output format, one of: 'datetime', 'date', 'string'
            fix_strategy (str | list[dict[str, int]]): List of strategies for fixing invalid dates
        """
        super().__init__()

        self.input_format = input_format
        self.output_format = output_format

        # Default fix strategy if none provided
        self.fix_strategies: MinguoDateFixStrategiesConfig = (
            MinguoDateFixStrategiesConfig(fix_strategies=fix_strategies)
        )

        # Will be filled during fit
        self.labels = []

    def _convert_minguo_to_ad(self, value: Any) -> Union[date, datetime, str, None]:
        """
        Convert a Minguo date to an AD date.

        Args:
            value: Minguo date in supported formats

        Returns:
            Converted date in the specified output format
        """
        if value is None or pd.isna(value):
            return None

        # Handle pandas Timestamp
        if isinstance(value, pd.Timestamp):
            return self._format_output(value.to_pydatetime().date())

        # Handle datetime objects
        if isinstance(value, datetime):
            return self._format_output(value.date())

        # Already a date object, just format and return
        if isinstance(value, date):
            return self._format_output(value)

        # Process integer and string formats
        roc_year, month, day = None, None, None

        # Handle numpy numeric types or Python float
        if isinstance(value, (np.integer, np.floating, float, int)):
            if isinstance(value, float):
                value = int(value)

            if self.input_format is None:
                self.input_format = "int"

            # Extract year, month, day from integer YYYMMDD format
            roc_year = value // 10000
            month = (value % 10000) // 100
            day = value % 100

        elif isinstance(value, str):
            # Clean the string
            value = value.strip()

            # Try different string formats
            if "-" in value:
                if self.input_format is None:
                    self.input_format = "str-"

                # YYY-MM-DD format
                parts = value.split("-")
                if len(parts) == 3:
                    try:
                        roc_year = int(parts[0])
                        month = int(parts[1])
                        day = int(parts[2])
                    except ValueError:
                        raise ValueError(f"無法解析 YYY-MM-DD 格式: {value}")
                else:
                    raise ValueError(f"無效的 YYY-MM-DD 格式: {value}")

            elif "/" in value:
                if self.input_format is None:
                    self.input_format = "str/"

                # YYY/MM/DD format
                parts = value.split("/")
                if len(parts) == 3:
                    try:
                        roc_year = int(parts[0])
                        month = int(parts[1])
                        day = int(parts[2])
                    except ValueError:
                        raise ValueError(f"無法解析 YYY/MM/DD 格式: {value}")
                else:
                    raise ValueError(f"無效的 YYY/MM/DD 格式: {value}")

            else:
                if self.input_format is None:
                    self.input_format = "str"

                # YYYMMDD format
                match = re.match(r"^(\d{3})(\d{2})(\d{2})$", value)
                if match:
                    roc_year = int(match.group(1))
                    month = int(match.group(2))
                    day = int(match.group(3))
                else:
                    # Try parsing as pure number
                    try:
                        numeric_value = int(value)
                        roc_year = numeric_value // 10000
                        month = (numeric_value % 10000) // 100
                        day = numeric_value % 100
                    except ValueError:
                        raise ValueError(f"無法解析民國年格式: {value}")

        else:
            raise ValueError(f"無法解析日期格式：{value} (類型: {type(value)})")

        # Convert to AD year
        year = roc_year + 1911

        # Try to create valid date
        try:
            # First try with original date
            ad_date = date(year, month, day)
            return self._format_output(ad_date)
        except ValueError:
            fix_strategies: list[dict[str, int]] = self.fix_strategies.fix_strategies
            # Apply fix strategies
            for strategy_level, fix_dict in enumerate(fix_strategies, 1):
                try:
                    # Apply current fix strategy
                    fixed_year = fix_dict.get("year", year)
                    fixed_month = fix_dict.get("month", month)
                    fixed_day = fix_dict.get("day", day)

                    # Check date validity
                    max_day = calendar.monthrange(fixed_year, fixed_month)[1]

                    # Create date object
                    fixed_date = date(fixed_year, fixed_month, min(fixed_day, max_day))

                    # Print fix warning (optional, can be commented out in production)
                    original_str = f"{roc_year:03d}年{month:02d}月{day:02d}日"
                    fixed_str = (
                        f"{fixed_year - 1911:03d}年{fixed_month:02d}月{fixed_date.day:02d}日"
                        if fixed_year >= 1912
                        else f"{fixed_year}年{fixed_month:02d}月{fixed_date.day:02d}日"
                    )
                    print(
                        f"警告：日期 {original_str} 已修正為 {fixed_str} (Level {strategy_level})"
                    )

                    return self._format_output(fixed_date)
                except Exception as e:
                    if strategy_level == len(fix_strategies):
                        # If all strategies fail
                        raise ValueError(
                            f"無法修復日期： {roc_year:03d}年{month:02d}月{day:02d}日，錯誤: {str(e)}"
                        )
                    # Try next strategy
                    continue

    def _convert_ad_to_minguo(
        self, value: Union[date, datetime, str, None]
    ) -> Union[int, str, None]:
        """
        Convert an AD date to a Minguo date.

        Args:
            value: AD date in supported formats

        Returns:
            Minguo date in the format specified by input_format
        """
        if value is None or pd.isna(value):
            return None

        # Handle string input (if not already a date object)
        if isinstance(value, str):
            try:
                value = pd.to_datetime(value).date()
            except Exception:
                raise ValueError(f"無法解析 AD 日期字串: {value}")

        # Handle pandas Timestamp
        if isinstance(value, pd.Timestamp):
            value = value.to_pydatetime().date()

        # Handle datetime
        if isinstance(value, datetime):
            value = value.date()

        # Calculate ROC year
        if not isinstance(value, date):
            raise ValueError(f"無法解析日期格式：{value} (類型: {type(value)})")

        roc_year = value.year - 1911

        # Handle dates before ROC era
        if roc_year < 1:
            fix_strategies: list[dict[str, int]] = self.fix_strategies.fix_strategies
            for strategy_level, fix_dict in enumerate(fix_strategies, 1):
                if "year" in fix_dict:
                    fixed_year = fix_dict["year"]
                    fixed_month = fix_dict.get("month", value.month)
                    fixed_day = fix_dict.get("day", value.day)

                    try:
                        fixed_date = date(fixed_year, fixed_month, fixed_day)
                        roc_year = fixed_year - 1911
                        print(
                            f"警告：日期 {value} 早於民國元年，已修正為 {fixed_date} (Level {strategy_level})"
                        )
                        value = fixed_date
                        break
                    except Exception:
                        if strategy_level == len(fix_strategies):
                            raise ValueError(f"無法修復早於民國元年的日期： {value}")
                        continue

            # If no year fix strategy and not fixed
            if roc_year < 1:
                raise ValueError(
                    f"日期早於民國元年 {value.year}，且未提供有效的年份修復策略"
                )

        # Return formatted according to input_format or default
        if not self.input_format or self.input_format == "int":
            return roc_year * 10000 + value.month * 100 + value.day
        elif self.input_format == "str":
            return f"{roc_year:03d}{value.month:02d}{value.day:02d}"
        elif self.input_format == "str-":
            return f"{roc_year:03d}-{value.month:02d}-{value.day:02d}"
        elif self.input_format == "str/":
            return f"{roc_year:03d}/{value.month:02d}/{value.day:02d}"
        else:
            # Default to int format
            return roc_year * 10000 + value.month * 100 + value.day

    def _format_output(self, date_obj: date) -> Union[date, datetime, str]:
        """
        Format the output date according to output_format.

        Args:
            date_obj: Date object to format

        Returns:
            Formatted date according to output_format
        """
        if self.output_format == "date":
            return date_obj
        elif self.output_format == "datetime":
            return datetime.combine(date_obj, datetime.min.time())
        elif self.output_format == "string":
            return date_obj.strftime("%Y-%m-%d")
        else:
            return date_obj  # Default to date object

    def _fit(self, data: pd.Series) -> None:
        """
        Fit the encoder to the data.

        Args:
            data: Series of dates to encode
        """
        self.labels = data.unique().tolist()
        # Try converting to validate
        try:
            data.apply(self._convert_minguo_to_ad)
        except Exception as e:
            raise ValueError(f"無法解析日期格式，請檢查日期格式是否正確：{str(e)}")

    def _transform(self, data: pd.Series) -> pd.Series:
        """
        Transform a series of Minguo dates to AD dates.

        Args:
            data: Series of Minguo dates

        Returns:
            Series of AD dates
        """
        transformed: pd.Series = data.apply(self._convert_minguo_to_ad)

        # Convert to pandas datetime if not already
        if not pd.api.types.is_datetime64_any_dtype(transformed):
            # Handle out-of-bounds dates
            max_date = pd.Timestamp.max.date()
            min_date = pd.Timestamp.min.date()

            transformed = transformed.apply(
                lambda x: None
                if pd.isna(x)
                or (isinstance(x, date) and (x > max_date or x < min_date))
                else x
            )

            # Convert to pandas datetime
            if self.output_format != "string":
                transformed = pd.to_datetime(transformed, errors="coerce")

        return transformed

    def _inverse_transform(self, data: pd.Series) -> pd.Series:
        """
        Transform a series of AD dates back to Minguo dates.

        Args:
            data: Series of AD dates

        Returns:
            Series of Minguo dates
        """
        try:
            return data.apply(self._convert_ad_to_minguo)
        except Exception as e:
            raise ValueError(f"無法轉換日期：{str(e)}")


class EncoderDateDiff(Encoder):
    """
    Encoder for calculating day differences between dates using a baseline date.

    This encoder takes a baseline date column and related date columns,
    and calculates the difference in days between the baseline date and
    each related date during transformation.

    Attributes:
        baseline_date (str): Name of the column containing the baseline date
        related_date_list (List[str]): List of column names containing dates to compare with baseline
        diff_unit (str): Unit for the difference calculation ('days', 'weeks', 'months', 'years')
        absolute_value (bool): Whether to return absolute differences
    """

    def __init__(
        self,
        baseline_date: str,
        related_date_list: Optional[list[str]] = None,
        diff_unit: str = "days",
        absolute_value: bool = False,
    ) -> None:
        """
        Initialize the DateDiffEncoder.

        Args:
            baseline_date: Name of the column containing the baseline date
            related_date_list: List of column names containing dates to compare
            diff_unit: Unit for difference calculation ('days', 'weeks', 'months', 'years')
            absolute_value: Whether to return absolute differences
        """
        super().__init__()

        self.baseline_date = baseline_date
        self.related_date_list = related_date_list or []
        self.diff_unit = diff_unit
        self.absolute_value = absolute_value

        # Validate diff_unit
        if diff_unit not in ["days", "weeks", "months", "years"]:
            raise ValueError(
                "diff_unit must be one of: 'days', 'weeks', 'months', 'years'"
            )

        # Will be populated during fit
        self._original_dtypes = {}
        self.is_fitted = False

    def _calc_date_diff(self, baseline_date, compare_date) -> Optional[float]:
        """
        Calculate the difference between two dates.

        Args:
            baseline_date: The baseline date
            compare_date: The date to compare with the baseline

        Returns:
            Difference between dates in the specified unit, or None if inputs are invalid
        """
        if pd.isna(baseline_date) or pd.isna(compare_date):
            return None

        # Convert to pandas Timestamp if not already
        if not isinstance(baseline_date, pd.Timestamp):
            try:
                baseline_date = pd.to_datetime(baseline_date)
            except Exception:
                return None

        if not isinstance(compare_date, pd.Timestamp):
            try:
                compare_date = pd.to_datetime(compare_date)
            except Exception:
                return None

        # Calculate difference in days
        diff_days = (compare_date - baseline_date).days

        # Apply absolute value if needed
        if self.absolute_value:
            diff_days = abs(diff_days)

        # Convert to requested unit
        if self.diff_unit == "days":
            return diff_days
        elif self.diff_unit == "weeks":
            return diff_days / 7
        elif self.diff_unit == "months":
            # Approximate months calculation
            return diff_days / 30.44
        elif self.diff_unit == "years":
            # Approximate years calculation
            return diff_days / 365.25
        else:
            return diff_days  # Default to days

    def _calc_date_from_diff(self, baseline_date, diff_value) -> Optional[pd.Timestamp]:
        """
        Calculate a date from a baseline date and a difference value.

        Args:
            baseline_date: The baseline date
            diff_value: The difference value in the specified unit

        Returns:
            Calculated date, or None if inputs are invalid
        """
        if pd.isna(baseline_date) or pd.isna(diff_value):
            return None

        # Convert to pandas Timestamp if not already
        if not isinstance(baseline_date, pd.Timestamp):
            try:
                baseline_date = pd.to_datetime(baseline_date)
            except Exception:
                return None

        # Convert diff_value to days based on the unit
        days = diff_value
        if self.diff_unit == "weeks":
            days = diff_value * 7
        elif self.diff_unit == "months":
            days = diff_value * 30.44  # Approximate
        elif self.diff_unit == "years":
            days = diff_value * 365.25  # Approximate

        # Calculate the date
        return baseline_date + pd.Timedelta(days=days)

    # 在 EncoderDateDiff 中
    def _fit(self, data: pd.Series | pd.DataFrame) -> None:
        """
        適應 Processor 架構的 fit 方法

        Args:
            data: 可能是 pd.Series 或 pd.DataFrame
        """
        # 如果是 Series，將它轉換為只有一列的 DataFrame
        if isinstance(data, pd.Series):
            # 儲存 Series 名稱，以便之後使用
            self._series_name = data.name
            data = pd.DataFrame({data.name: data})

        # 正常的 fit 邏輯...
        # 驗證欄位存在
        if self.baseline_date not in data.columns:
            raise ValueError(
                f"Baseline date column '{self.baseline_date}' not found in data"
            )

        for col in self.related_date_list:
            if col not in data.columns:
                raise ValueError(f"Related date column '{col}' not found in data")

        # 儲存原始資料類型
        self._original_dtypes = {
            col: data[col].dtype
            for col in [self.baseline_date] + self.related_date_list
            if col in data.columns  # 增加安全檢查
        }

        # 標記為已適配
        self.is_fitted = True

    def _transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Transform date columns to difference values.

        Args:
            X: DataFrame containing the date columns

        Returns:
            DataFrame with date differences
        """
        if not self.is_fitted:
            self._fit(X)

        result = X.copy()

        # Ensure baseline date is datetime
        if not pd.api.types.is_datetime64_any_dtype(result[self.baseline_date]):
            result[self.baseline_date] = pd.to_datetime(
                result[self.baseline_date], errors="coerce"
            )

        # Calculate differences for each related date
        for col in self.related_date_list:
            # Ensure current date column is datetime
            if not pd.api.types.is_datetime64_any_dtype(result[col]):
                result[col] = pd.to_datetime(result[col], errors="coerce")

            # Calculate difference
            result[col] = result.apply(
                lambda row: self._calc_date_diff(row[self.baseline_date], row[col]),
                axis=1,
            )

        return result

    def _inverse_transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Transform difference values back to date columns.

        Args:
            X: DataFrame containing the baseline date and difference values

        Returns:
            DataFrame with dates calculated from differences
        """
        if not self.is_fitted:
            raise ValueError("Encoder has not been fitted yet")

        result = X.copy()

        # Ensure baseline date is datetime
        if not pd.api.types.is_datetime64_any_dtype(result[self.baseline_date]):
            result[self.baseline_date] = pd.to_datetime(
                result[self.baseline_date], errors="coerce"
            )

        # Calculate dates from differences
        for col in self.related_date_list:
            if col in result.columns:
                # Calculate date from difference
                result[col] = result.apply(
                    lambda row: self._calc_date_from_diff(
                        row[self.baseline_date], row[col]
                    ),
                    axis=1,
                )

                # Convert back to original dtype if possible
                if col in self._original_dtypes:
                    try:
                        original_dtype = self._original_dtypes[col]
                        if pd.api.types.is_datetime64_any_dtype(original_dtype):
                            # Already datetime, no need to convert
                            pass
                        elif pd.api.types.is_string_dtype(original_dtype):
                            # Convert to string format
                            result[col] = result[col].dt.strftime("%Y-%m-%d")
                        # Add other dtype conversions if needed
                    except Exception:
                        # If conversion fails, keep as datetime
                        pass

        return result
