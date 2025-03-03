import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, fields

from petsard.exceptions import ConfigError


@dataclass
class BaseConfig(ABC):
    def __init__(self):
        """
        Initialize the LoaderConfig instance.
        """
        self.logger = logging.getLogger(f"PETsARD.{self.__class__.__name__}")

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

        for key, value in config_dict.items():
            # Check if attribute exists
            if key not in valid_fields and not hasattr(self, key):
                raise ConfigError(
                    f"Attribute '{key}' does not exist in {self.__class__.__name__}"
                )

            # Get expected type for the attribute
            expected_type = None
            for field in fields(self.__class__):
                if field.name == key:
                    expected_type = field.type
                    break

            # Check if type is correct (if we could determine the expected type)
            if expected_type is not None and not isinstance(value, expected_type):
                raise ConfigError(
                    f"Value for '{key}' has incorrect type. "
                    f"Expected {expected_type.__name__}, got {type(value).__name__}"
                )

            # Update the attribute
            setattr(self, key, value)

    def get(self) -> dict:
        """
        Get all attributes of the LoaderConfig instance as a dictionary.

        Returns:
            dict: A dictionary containing all instance attributes.
        """
        # Get all instance attributes
        config_dict = {
            key: value
            for key, value in self.__dict__.items()
            # Filter out class variables which start with '__'
            if not key.startswith("__")
        }

        return config_dict
