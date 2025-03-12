import logging
from abc import ABC, abstractmethod
from dataclasses import _MISSING_TYPE, dataclass, fields
from enum import Enum, auto
from typing import Any, Optional

from petsard.exceptions import ConfigError


class ConfigGetParamActionMap(Enum):
    """Enumeration for BaseConfig.get_param() configuration processing actions"""

    INCLUDE = auto()  # Add as a single value to the result dictionary
    MERGE = auto()  # Merge as a dictionary into the result


@dataclass
@dataclass
class ConfigGetParamConfig:
    """
    Data class for BaseConfig.get_param() configuration

    Attributes:
        action (ConfigGetParamActionMap): The action to perform
        rename (dict, optional): Dictionary for renaming:
            - For INCLUDE action: {attr_name: new_name}
            - For MERGE action: {original_key1: new_key1, original_key2: new_key2, ...}
    """

    action: ConfigGetParamActionMap
    rename: Optional[dict] = None

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> "ConfigGetParamConfig":
        """Create parameter configuration from a dictionary"""
        _logger = logging.getLogger(f"PETsARD.{cls.__name__}")

        error_msg: str = ""

        if "action" not in config_dict:
            error_msg = "BaseConfig.get_param() configuration must include 'action' key"
            _logger.error(error_msg)
            raise ConfigError(error_msg)

        action_str = config_dict["action"].upper()
        if not hasattr(ConfigGetParamActionMap, action_str):
            error_msg = f"Invalid action: {action_str}"
            _logger.error(error_msg)
            raise ConfigError(error_msg)

        # Validate rename is a dictionary if provided
        rename = config_dict.get("rename")
        if rename is not None and not isinstance(rename, dict):
            error_msg = "The 'rename' parameter must be a dictionary"
            _logger.error(error_msg)
            raise ConfigError(error_msg)

        return cls(
            action=getattr(ConfigGetParamActionMap, action_str),
            rename=rename,
        )


@dataclass
class BaseConfig(ABC):
    """
    Base configuration class for all config classes.
    """

    @abstractmethod
    def __post_init__(self):
        """
        Post-initialization hook that must be implemented by subclasses.
        This method is automatically called after the default __init__ from dataclass.
        """
        self._logger: logging.Logger = logging.getLogger(
            f"PETsARD.{self.__class__.__name__}"
        )

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
                self._logger.error(error_msg)
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
                        self._logger.error(error_msg)
                        raise ConfigError(error_msg)
                else:
                    # For regular types, check directly
                    if not isinstance(value, expected_type):
                        error_msg = (
                            f"Value for '{key}' has incorrect type. "
                            f"Expected {expected_type.__name__}, got {type(value).__name__}"
                        )
                        self._logger.error(error_msg)
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

    # get_and_merge_params
    def get_params(
        self, param_configs: list[dict[str, dict[str, Any]]]
    ) -> dict[str, Any]:
        """
        Extract parameters from an object and merge them into a result dictionary.

        Args:
            param_configs (list[dict[str, dict[str, Any]]]):
                List of parameter configurations in the format:
                [
                    {'attr_name': {'action': 'INCLUDE|MERGE', 'rename': {key: new_name}}},
                    ...
                ]
                where:
                - attr_name: Name of the object attribute
                - action: 'INCLUDE' to add as a single value, 'MERGE' to merge as a dictionary
                - rename:
                    - For INCLUDE: {attr_name: new_name}
                    - For MERGE: {original_key1: new_key1, original_key2: new_key2, ...}

        Returns:
            (dict[str, Any]) Dictionary containing all extracted parameters

        Raises:
            ConfigError: When parameter configuration is invalid or attributes don't exist
        """
        params: dict[str, Any] = {}

        # For checking if attribute names are used more than once
        used_attr_names: set[str] = set()
        # For checking if target keys are duplicated
        used_target_keys: set[str] = set()

        # Return empty dict if no configurations
        if not param_configs:
            return params

        for config_item in param_configs:
            # Each config item should be a dictionary with a single key-value pair
            if len(config_item) != 1:
                error_msg = "Each parameter config item must be a dictionary with a single key-value pair"
                self._logger.error(error_msg)
                raise ConfigError(error_msg)

            attr_name, config_dict = next(iter(config_item.items()))

            # Check 1: Ensure attribute exists
            if not hasattr(self, attr_name):
                error_msg = f"Attribute '{attr_name}' does not exist"
                self._logger.error(error_msg)
                raise ConfigError(error_msg)

            # Check 2: Ensure attribute is not used multiple times
            if attr_name in used_attr_names:
                error_msg = f"Attribute '{attr_name}' is used more than once in the configuration"
                self._logger.error(error_msg)
                raise ConfigError(error_msg)

            used_attr_names.add(attr_name)

            try:
                # Parse configuration
                param_config = ConfigGetParamConfig.from_dict(config_dict)

                # Get attribute value
                attr_value = getattr(self, attr_name)

                # Process attribute value
                if param_config.action == ConfigGetParamActionMap.INCLUDE:
                    # Handle INCLUDE action
                    if param_config.rename:
                        # Check for single key in rename dictionary matching the attribute name
                        if attr_name not in param_config.rename:
                            error_msg = f"For INCLUDE action, rename dictionary must have '{attr_name}' as a key"
                            self._logger.error(error_msg)
                            raise ConfigError(error_msg)

                        target_key = param_config.rename[attr_name]
                    else:
                        target_key = attr_name

                    # Check target key doesn't conflict
                    if target_key in used_target_keys:
                        error_msg = f"Target key '{target_key}' is used more than once in the configuration"
                        self._logger.error(error_msg)
                        raise ConfigError(error_msg)

                    used_target_keys.add(target_key)
                    params[target_key] = attr_value

                elif param_config.action == ConfigGetParamActionMap.MERGE:
                    # Check if it's a dictionary
                    if not isinstance(attr_value, dict):
                        error_msg = f"Attribute '{attr_name}' is not a dictionary, cannot perform MERGE operation"
                        self._logger.error(error_msg)
                        raise ConfigError(error_msg)

                    # Handle rename for merge action
                    if param_config.rename:
                        # Verify all keys in rename_map exist in the source dictionary
                        missing_keys = [
                            k for k in param_config.rename.keys() if k not in attr_value
                        ]
                        if missing_keys:
                            error_msg = f"Keys {missing_keys} in rename map don't exist in attribute '{attr_name}'"
                            self._logger.error(error_msg)
                            raise ConfigError(error_msg)

                        # Check for conflicts with renamed keys
                        for new_key in param_config.rename.values():
                            if new_key in used_target_keys:
                                error_msg = f"Renamed key '{new_key}' conflicts with an existing key"
                                self._logger.error(error_msg)
                                raise ConfigError(error_msg)
                            used_target_keys.add(new_key)

                        # Check for conflicts with non-renamed keys
                        for key in attr_value.keys():
                            if (
                                key not in param_config.rename
                                and key in used_target_keys
                            ):
                                error_msg = f"Merge key '{key}' would conflict with an existing key"
                                self._logger.error(error_msg)
                                raise ConfigError(error_msg)
                            if key not in param_config.rename:
                                used_target_keys.add(key)

                        # Merge with renaming
                        for orig_key, value in attr_value.items():
                            if orig_key in param_config.rename:
                                params[param_config.rename[orig_key]] = value
                            else:
                                params[orig_key] = value
                    else:
                        # Check for key conflicts when merging directly
                        for key in attr_value.keys():
                            if key in used_target_keys:
                                error_msg = f"Merge key '{key}' would conflict with an existing key"
                                self._logger.error(error_msg)
                                raise ConfigError(error_msg)
                            used_target_keys.add(key)

                        # Merge directly
                        params.update(attr_value)

            except ValueError as e:
                error_msg = f"Configuration error: {e}"
                self._logger.error(error_msg)
                raise ConfigError(error_msg)

        return params

    @classmethod
    def from_dict(cls, params: dict[str, Any]) -> "BaseConfig":
        """
        Create an instance from a dictionary.

        Args:
            data (dict[str, Any]):
                A dictionary with keys matching the class attributes.

        Returns:
            An instance of ConfigBase.

        Raises:
            ConfigError:
                - If required attributes are missing.
                - If there are unexpected attributes.
                - If instantiation fails for other reasons.
        """
        _logger = logging.getLogger(f"PETsARD.{cls.__name__}")

        class_fields = {f.name: f for f in fields(cls)}
        error_msg: str = ""

        # Check for missing required attributes of params
        missing_required: list[str] = []
        for field_name, field in class_fields.items():
            if (
                field.default == field.default_factory == _MISSING_TYPE
                and field_name not in params
            ):
                missing_required.append(field_name)

        if missing_required:
            error_msg = f"Missing required attributes: {', '.join(missing_required)}"
            _logger.error(error_msg)
            raise ConfigError(error_msg)

        # Check for unexpected attributes from params
        unexpected: set = set(params.keys()) - set(class_fields.keys())
        if unexpected:
            error_msg = f"Unexpected attributes: {', '.join(unexpected)}"
            _logger.error(error_msg)
            raise ConfigError(error_msg)

        # After checking required and unexpected parameters, add type checking
        for field_name, field in class_fields.items():
            if field_name in params:
                param_value = params[field_name]
                # Get the expected type
                expected_type = field.type
                # Check parameter type
                if hasattr(expected_type, "__origin__"):
                    # If it's a parameterized type (like dict[str, int]), only check the base type
                    base_type = expected_type.__origin__
                    if not isinstance(param_value, base_type):
                        error_msg = f"Value for '{field_name}' has incorrect type. Expected {base_type.__name__}, got {type(param_value).__name__}"
                        _logger.error(error_msg)
                        raise ConfigError(error_msg)
                else:
                    # For regular types, check directly
                    if not isinstance(param_value, expected_type):
                        error_msg = f"Value for '{field_name}' has incorrect type. Expected {expected_type.__name__}, got {type(param_value).__name__}"
                        _logger.error(error_msg)
                        raise ConfigError(error_msg)

        try:
            return cls(**params)
        except Exception as e:
            error_msg = f"Failed to create {cls.__name__} instance: {str(e)}"
            _logger.error(error_msg)
            raise ConfigError(error_msg) from e
