import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, fields
from typing import Any, Optional

from petsard.exceptions import ConfigError


@dataclass
class BaseConfig(ABC):
    """
    Base configuration class for all config classes.
    """

    def __init__(self):
        self.logger: logging.Logger = logging.getLogger(
            f"PETsARD.{self.__class__.__name__}"
        )

    @abstractmethod
    def __post_init__(self):
        """
        Post-initialization hook that must be implemented by subclasses.
        This method is automatically called after the default __init__ from dataclass.
        """
        pass

    def update(self, config_dict: dict) -> None:
        """
        Update config attributes from a dictionary.

        Args:
            config_dict (dict): Dictionary containing attribute names and values to update

        Raises:
            AttributeError: If an attribute doesn't exist in the config
            TypeError: If the attribute value type is incorrect
        """
        # Get all valid field names from dataclass
        valid_fields = {field.name for field in fields(self.__class__)}
        error_msg: str = ""

        for key, value in config_dict.items():
            # Check if attribute exists
            if key not in valid_fields and not hasattr(self, key):
                error_msg = (
                    f"Attribute '{key}' does not exist in {self.__class__.__name__}"
                )
                self.logger.error(error_msg)
                raise ConfigError(error_msg)

            # Get expected type for the attribute
            expected_type = None
            for field in fields(self.__class__):
                if field.name == key:
                    expected_type = field.type
                    break

            # Handle parameterized generics from typing
            if expected_type is not None:
                # Get the base type from typing (like dict, list, etc.)
                if hasattr(expected_type, "__origin__"):
                    # If it's a parameterized generic (like dict[str, int]), only check the base type
                    base_type = expected_type.__origin__
                    if not isinstance(value, base_type):
                        error_msg = (
                            f"Value for '{key}' has incorrect type. "
                            f"Expected {base_type.__name__}, got {type(value).__name__}"
                        )
                        self.logger.error(error_msg)
                        raise ConfigError(error_msg)
                else:
                    # For regular types, check directly
                    if not isinstance(value, expected_type):
                        error_msg = (
                            f"Value for '{key}' has incorrect type. "
                            f"Expected {expected_type.__name__}, got {type(value).__name__}"
                        )
                        self.logger.error(error_msg)
                        raise ConfigError(error_msg)

            # Update the attribute
            setattr(self, key, value)

    def get(self) -> dict:
        """
        Get all attributes of the LoaderConfig instance as a dictionary.

        Returns:
            (dict): A dictionary containing all instance attributes.
        """
        # Get all instance attributes
        config_dict: dict[str, Any] = {
            key: value
            for key, value in self.__dict__.items()
            # Filter out class variables which start with '__'
            if not key.startswith("__")
        }

        return config_dict

    def get_and_merge_params(
        self, param_dict_name: str, additional_attrs: Optional[str | list[str]] = None
    ) -> dict[str, Any]:
        """
        Extract and merge a base parameter dictionary with additional configuration attributes.

        This function retrieves a dictionary attribute specified by name from the object
        and combines it with additional specified attributes from the config object.
        This is useful for creating customized configuration dictionaries that include
        both base parameters and specific attributes.

        Example:
            ```python
            from petsard.synthesizer.synthesizer import Synthesizer

            # Create a synthesizer instance
            syn = Synthesizer(method='default', test=1, test2={'a': 1, 'b': 2})

            # Merge 'custom_params' dictionary with 'method' and 'syn_method' attributes
            merged_config = syn.config.get_and_merge_params(
                param_dict_name='custom_params',
                additional_attrs=['method', 'syn_method']
            )
            ```

            Result:
            ```
            {
                'test': 1,
                'test2': {'a': 1, 'b': 2},
                'method': 'default',
                'syn_method': 'sdv-single_table-gaussiancopula'
            }
            ```

        Args:
            param_dict_name (str):
                Name of the dictionary attribute to use as the base for merging
            additional_attrs (str | list[str], optional):
                Name(s) of additional attributes to add to the result dictionary.
                Can be a single string or a list of strings.

        Returns:
            dict[str, Any]: A dictionary containing both the base dictionary contents
                           and the additional attribute values

        Raises:
            ConfigError: If the specified base dictionary attribute or any additional
                        attribute does not exist in the config
        """
        config_dict: dict[str, Any] = {}
        error_msg: str = ""

        if not hasattr(self, param_dict_name):
            error_msg = f"The parameter {param_dict_name} does not exist in the config."
            self.logger.error(error_msg)
            raise ConfigError(error_msg)
        config_dict = getattr(self, param_dict_name)

        if additional_attrs is not None:
            attrs: list[str] = (
                [additional_attrs]
                if isinstance(additional_attrs, str)
                else additional_attrs
            )

            for attr in attrs:
                if not hasattr(self, attr):
                    error_msg = f"The attribute {attr} does not exist in the config."
                    self.logger.error(error_msg)
                    raise ConfigError(error_msg)

                config_dict[attr] = getattr(self, attr)

        return config_dict
