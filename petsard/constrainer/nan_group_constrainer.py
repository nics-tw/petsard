import warnings
from typing import Dict

import numpy as np
import pandas as pd

from petsard.constrainer.constrainer_base import BaseConstrainer
from petsard.error import ConfigError


class NaNGroupConstrainer(BaseConstrainer):
    """Handle NaN group constraints"""

    def __init__(self, constraints: Dict[str, tuple]):
        """
        Initialize the constrainer with given constraints

        Args:
            constraints: Dictionary of constraint configurations
        """
        self._validate_constraint(constraints)
        self.constraints = constraints

    def _validate_constraint(self, constraints):
        """
        Validate the structure of input constraints

        Args:
            constraints: Dictionary of constraint configurations

        Raises:
            ConfigError: If the constraint configuration is invalid
        """
        if not isinstance(constraints, dict):
            raise ConfigError("Constraints must be a dictionary")

        for main_field, config in constraints.items():
            # Check if config is a tuple with two elements
            if not isinstance(config, tuple) or len(config) != 2:
                raise ConfigError(
                    f"Invalid configuration for field '{main_field}': must be a tuple with two elements"
                )

            action, related = config

            # Check action
            if action not in ["erase", "copy", "delete"]:
                raise ConfigError(f"Invalid action '{action}' for NaN group")

            # Check related field
            if related is None:
                raise ConfigError(
                    f"Related field cannot be None for field '{main_field}'"
                )

            # Ensure related is a list or a string
            if not isinstance(related, (str, list)):
                raise ConfigError(
                    f"Related field must be a string or list for field '{main_field}'"
                )

    def validate_config(self, df: pd.DataFrame) -> None:
        """
        Validate if the configuration is compatible with the given DataFrame

        Args:
            df: Input DataFrame to validate against

        Raises:
            ConfigError: If any required columns are missing
        """
        for main_field, (action, related) in self.constraints.items():
            # Check if main field exists
            if main_field not in df.columns:
                raise ConfigError(
                    f"Main field '{main_field}' does not exist in the DataFrame"
                )

            # Check related fields
            related_cols = [related] if isinstance(related, str) else related
            for col in related_cols:
                if col not in df.columns:
                    raise ConfigError(
                        f"Related field '{col}' does not exist in the DataFrame"
                    )

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply NaN group constraints to DataFrame

        Args:
            df: Input DataFrame to be filtered

        Returns:
            Filtered DataFrame

        Raises:
            ConfigError: If any required columns are missing
        """
        # Perform complete validation before applying constraints
        _ = self.validate_config(df)

        result = df.copy()
        for main, (action, related) in self.constraints.items():
            related_cols = [related] if isinstance(related, str) else related

            if action == "delete":
                # Delete entire row if main field is NaN
                result = result[~result[main].isna()]
            else:
                for col in related_cols:
                    if col == main:
                        warnings.warn(
                            f"Warning: Related field '{col}' cannot be the same as main field"
                        )
                        continue

                    if action == "erase":
                        result.loc[result[main].isna(), col] = np.nan
                    elif action == "copy":
                        if result[col].dtype != result[main].dtype:
                            warnings.warn(
                                f"Warning: Cannot copy values from '{main}' ({result[main].dtype}) to '{col}' ({result[col].dtype})"
                            )
                            continue
                        mask = result[main].notna() & result[col].isna()
                        result.loc[mask, col] = result.loc[mask, main]

        return result.reset_index(drop=True)
