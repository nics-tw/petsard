from dataclasses import dataclass, field
from typing import Any, Dict

import pytest

from petsard.config_base import BaseConfig, ConfigError, ConfigGetParamActionMap


@dataclass
class TestConfig(BaseConfig):
    """Test configuration class for unit tests"""

    # PytestCollectionWarning: cannot collect test class 'TestConfig'
    #   because it has a init constructor (from: tests/test_config_base.py)
    __test__ = False

    a: int
    b: int
    c: Dict[Any, Any] = field(default_factory=dict)
    d: Dict[Any, Any] = field(default_factory=dict)

    def __post_init__(self):
        super().__post_init__()


class TestBaseConfig:
    """Test suite for BaseConfig class"""

    def test_init_and_get(self):
        """Test initialization and get method"""
        # Create a test configuration
        config = TestConfig(a=1, b=2, c={3: "3"}, d={4: "4"})

        # Test the get method
        result = config.get()
        assert "a" in result
        assert "b" in result
        assert "c" in result
        assert "d" in result
        assert result["a"] == 1
        assert result["b"] == 2
        assert result["c"] == {3: "3"}
        assert result["d"] == {4: "4"}
        assert "_logger" in result  # Check that logger is included

    def test_update(self):
        """Test update method"""
        config = TestConfig(a=1, b=2)

        # Update existing attributes
        config.update({"a": 10, "b": 20})
        assert config.a == 10
        assert config.b == 20

        # Test updating non-existent attribute
        with pytest.raises(ConfigError):
            config.update({"nonexistent": 30})

        # Test updating with incorrect type
        with pytest.raises(ConfigError):
            config.update({"a": "string instead of int"})

    def test_get_params_include(self):
        """Test get_params with INCLUDE action"""
        config = TestConfig(a=1, b=2, c={3: "3"}, d={4: "4"})

        # Basic include
        result = config.get_params([{"a": {"action": "INCLUDE"}}])
        assert result == {"a": 1}

        # Include with renaming
        result = config.get_params(
            [{"b": {"action": "INCLUDE", "rename": {"b": "test_b"}}}]
        )
        assert result == {"test_b": 2}

        # Missing matching key in rename dictionary
        with pytest.raises(ConfigError):
            config.get_params(
                [{"b": {"action": "INCLUDE", "rename": {"wrong_key": "test_b"}}}]
            )

    def test_get_params_merge(self):
        """Test get_params with MERGE action"""
        config = TestConfig(a=1, b=2, c={3: "3"}, d={4: "4"})

        # Basic merge
        result = config.get_params([{"c": {"action": "MERGE"}}])
        assert result == {3: "3"}

        # Merge with renaming
        result = config.get_params(
            [{"d": {"action": "MERGE", "rename": {4: "test_d"}}}]
        )
        assert result == {"test_d": "4"}

        # Merge with non-dictionary attribute
        with pytest.raises(ConfigError):
            config.get_params([{"a": {"action": "MERGE"}}])

        # Rename key doesn't exist
        with pytest.raises(ConfigError):
            config.get_params([{"d": {"action": "MERGE", "rename": {5: "test_d"}}}])

    def test_get_params_combined(self):
        """Test get_params with combined actions"""
        config = TestConfig(a=1, b=2, c={3: "3"}, d={4: "4"})

        # Combine different operations
        result = config.get_params(
            [
                {"a": {"action": "INCLUDE"}},
                {"b": {"action": "INCLUDE", "rename": {"b": "test_b"}}},
                {"c": {"action": "MERGE"}},
                {"d": {"action": "MERGE", "rename": {4: "test_d"}}},
            ]
        )

        assert result == {"a": 1, "test_b": 2, 3: "3", "test_d": "4"}

    def test_get_params_validation(self):
        """Test validation in get_params"""
        config = TestConfig(a=1, b=2, c={3: "3", 5: "5"}, d={4: "4"})

        # Non-existent attribute
        with pytest.raises(ConfigError):
            config.get_params([{"nonexistent": {"action": "INCLUDE"}}])

        # Duplicate attribute usage
        with pytest.raises(ConfigError):
            config.get_params(
                [{"a": {"action": "INCLUDE"}}, {"a": {"action": "INCLUDE"}}]
            )

        # Target key conflict
        with pytest.raises(ConfigError):
            config.get_params(
                [
                    {"a": {"action": "INCLUDE"}},
                    {"b": {"action": "INCLUDE", "rename": {"b": "a"}}},
                ]
            )

        # Key conflict when merging
        config.c[6] = "6"
        config.d[6] = "6"
        with pytest.raises(ConfigError):
            config.get_params([{"c": {"action": "MERGE"}}, {"d": {"action": "MERGE"}}])

        # Key conflict after renaming
        with pytest.raises(ConfigError):
            config.get_params(
                [
                    {"c": {"action": "MERGE", "rename": {3: "test_key"}}},
                    {"d": {"action": "MERGE", "rename": {4: "test_key"}}},
                ]
            )

    def test_from_dict(self):
        """Test from_dict class method"""
        # Valid parameters
        config = TestConfig.from_dict({"a": 1, "b": 2})
        assert config.a == 1
        assert config.b == 2

        # Missing required parameter
        with pytest.raises(ConfigError):
            TestConfig.from_dict({"a": 1})  # Missing b

        # Unexpected parameter
        with pytest.raises(ConfigError):
            TestConfig.from_dict({"a": 1, "b": 2, "extra": 3})

        # Incorrect parameter type
        with pytest.raises(ConfigError):
            config = TestConfig.from_dict({"a": "string", "b": 2})


def test_config_get_param_action_map():
    """Test the ConfigGetParamActionMap enum"""
    assert hasattr(ConfigGetParamActionMap, "INCLUDE")
    assert hasattr(ConfigGetParamActionMap, "MERGE")
    assert ConfigGetParamActionMap.INCLUDE != ConfigGetParamActionMap.MERGE
