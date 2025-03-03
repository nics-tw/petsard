import warnings
from typing import Dict, List, Union

import numpy as np
import pandas as pd

from petsard.constrainer.constrainer_base import BaseConstrainer
from petsard.exceptions import ConfigError


class NaNGroupConstrainer(BaseConstrainer):
    """Handle NaN group constraints"""

    def __init__(self, constraints: Dict[str, Dict[str, Union[str, List[str]]]]):
        """
        Initialize the constrainer with given constraints

        Args:
            constraints: Dictionary of constraint configurations
                Example:
                {
                    'job': {
                        'delete': ['salary'],
                        'erase': ['bonus', 'performance']
                    },
                    'name': {
                        'delete': 'salary'
                    }
                }
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

        valid_actions = ["erase", "copy", "delete"]

        for main_field, actions in constraints.items():
            # Handle case where action is directly a string 'delete'
            if actions == "delete":
                continue

            # For other actions, must be dictionary
            if not isinstance(actions, dict):
                raise ConfigError(
                    f"Actions for field '{main_field}' must be a dictionary"
                )

            # If delete exists in dict, it cannot be combined with other actions
            if "delete" in actions and len(actions) > 1:
                raise ConfigError(
                    f"Delete action for field '{main_field}' cannot be combined with other actions"
                )

            for action, related in actions.items():
                # Check action
                if action not in valid_actions:
                    raise ConfigError(f"Invalid action '{action}' for NaN group")

                # Check related field
                if related is None:
                    raise ConfigError(
                        f"Related field cannot be None for field '{main_field}'"
                    )

                # For erase and copy actions, related must be string or list of strings
                if not isinstance(related, (str, list)):
                    raise ConfigError(
                        f"For {action} action, related field must be a string or list of strings"
                    )
                if isinstance(related, list) and not all(
                    isinstance(r, str) for r in related
                ):
                    raise ConfigError(
                        f"For {action} action, all related fields must be strings"
                    )

    def validate_config(self, df: pd.DataFrame) -> None:
        """
        Validate if the configuration is compatible with the given DataFrame

        Args:
            df: Input DataFrame to validate against

        Raises:
            ConfigError: If any required columns are missing
        """
        for main_field, actions in self.constraints.items():
            # Check if main field exists
            if main_field not in df.columns:
                raise ConfigError(
                    f"Main field '{main_field}' does not exist in the DataFrame"
                )

            # Skip further checks if it's just a delete action
            if actions == "delete":
                continue

            # Check related fields
            for action, related in actions.items():
                related_cols = [related] if isinstance(related, str) else related
                for col in related_cols:
                    if col not in df.columns:
                        raise ConfigError(
                            f"Related field '{col}' does not exist in the DataFrame"
                        )

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply NaN group constraints to DataFrame"""
        _ = self.validate_config(df)
        result = df.copy()

        # First apply all delete actions
        for main_field, actions in self.constraints.items():
            if actions == "delete" or ("delete" in actions):
                result = result[~result[main_field].isna()]

        # Then apply erase and copy actions
        for main_field, actions in self.constraints.items():
            if actions == "delete":  # Skip if it's a direct delete action
                continue

            for action, related in actions.items():
                if action == "delete":
                    continue  # Already handled

                related_cols = [related] if isinstance(related, str) else related
                for col in related_cols:
                    if col == main_field:
                        warnings.warn(
                            f"Warning: Related field '{col}' cannot be the same as main field"
                        )
                        continue

                    if action == "erase":
                        result.loc[result[main_field].isna(), col] = np.nan
                    elif action == "copy":
                        if result[col].dtype != result[main_field].dtype:
                            warnings.warn(
                                f"Warning: Cannot copy values from '{main_field}' ({result[main_field].dtype}) to '{col}' ({result[col].dtype})"
                            )
                            continue
                        mask = result[main_field].notna() & result[col].isna()
                        result.loc[mask, col] = result.loc[mask, main_field]

        return result.reset_index(drop=True)
