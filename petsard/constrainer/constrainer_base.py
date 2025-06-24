import warnings
from abc import ABC, abstractmethod

import pandas as pd


class BaseConstrainer(ABC):
    """Base interface for constraints"""

    def __init__(self, config: dict):
        """Initialize constraint with configuration"""
        self.config = config

    @abstractmethod
    def validate_config(self) -> bool:
        """Validate if the configuration is legal"""
        pass

    @abstractmethod
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply the constraint to the data"""
        pass

    def _check_columns_exist(self, df: pd.DataFrame, columns: list[str]) -> bool:
        """
        Check if all columns exist in DataFrame

        Args:
            df: DataFrame to check
            columns: list of column names to verify

        Returns:
            True if all columns exist
        """
        missing = [col for col in columns if col not in df.columns]
        if missing:
            warnings.warn(
                f"Warning: Columns {missing} do not exist in DataFrame", stacklevel=2
            )
            return False
        return True
