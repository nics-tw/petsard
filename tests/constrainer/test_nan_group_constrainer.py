import numpy as np
import pandas as pd
import pytest

from petsard.constrainer.nan_group_constrainer import NaNGroupConstrainer
from petsard.error import ConfigError


class TestNaNGroupConstrainer:
    @pytest.fixture
    def sample_df(self):
        """Generate sample data for testing"""
        return pd.DataFrame(
            {
                "id": [1, 2, 3, 4, 5],
                "name": ["John", "Mary", np.nan, "Tom", "Jane"],
                "job": ["Engineer", "Doctor", "Engineer", np.nan, "Teacher"],
                "age": [25, 30, 35, np.nan, 45],
                "salary": [50000, 60000, np.nan, 75000, 80000],
                "bonus": [10000, np.nan, np.nan, 15000, 20000],
            }
        )

    def test_invalid_config_initialization(self):
        """Test initialization with invalid configurations"""
        invalid_configs = [
            None,
            "not_a_dict",
            {"field": "invalid_action"},
            {"field": ("invalid_action", "target")},
            {"field": ("erase", None)},
        ]

        for config in invalid_configs:
            with pytest.raises(ConfigError):
                NaNGroupConstrainer(config)

    def test_valid_config_initialization(self):
        """Test initialization with valid configurations"""
        valid_configs = [
            {"name": ("delete", "salary")},
            {"job": ("erase", ["salary", "bonus"])},
            {"salary": ("copy", "bonus")},
        ]

        for config in valid_configs:
            try:
                _ = NaNGroupConstrainer(config)
            except ConfigError:
                pytest.fail(
                    f"Valid configuration {config} raised unexpected ConfigError"
                )

    def test_validate_config_nonexistent_columns(self, sample_df):
        """Test validation of configurations with non-existent columns"""
        config = {
            "nonexistent_main": ("delete", "salary"),
            "job": ("erase", ["nonexistent_related"]),
        }

        constrainer = NaNGroupConstrainer(config)

        with pytest.warns(UserWarning, match="does not exist in the DataFrame"):
            assert not constrainer.validate_config(sample_df)

    def test_delete_action(self, sample_df):
        """Test delete action on NaN values"""
        config = {"name": ("delete", "salary")}

        constrainer = NaNGroupConstrainer(config)
        result = constrainer.apply(sample_df)

        assert len(result) < len(sample_df)
        assert not result["name"].isna().any()

    def test_erase_action(self, sample_df):
        """Test erase action on NaN values"""
        config = {"job": ("erase", ["salary", "bonus"])}

        constrainer = NaNGroupConstrainer(config)
        result = constrainer.apply(sample_df)

        # Check if related fields are NaN when main field is NaN
        assert result.loc[result["job"].isna(), "salary"].isna().all()
        assert result.loc[result["job"].isna(), "bonus"].isna().all()

    def test_copy_action_compatible_types(self, sample_df):
        """Test copy action with compatible data types"""
        config = {"salary": ("copy", "bonus")}

        constrainer = NaNGroupConstrainer(config)
        result = constrainer.apply(sample_df)

        # Check if values are copied when target is NaN
        mask = result["salary"].notna() & pd.isna(sample_df["bonus"])
        assert (result.loc[mask, "bonus"] == result.loc[mask, "salary"]).all()

    def test_copy_action_incompatible_types(self, sample_df):
        """Test copy action with incompatible data types"""
        config = {"name": ("copy", "age")}  # String to numeric

        constrainer = NaNGroupConstrainer(config)
        with pytest.warns(UserWarning, match="Cannot copy values"):
            result = constrainer.apply(sample_df)
            assert result["age"].equals(sample_df["age"])

    def test_multiple_constraints(self, sample_df):
        """Test applying multiple constraints"""
        config = {"name": ("delete", "salary"), "job": ("erase", "bonus")}

        constrainer = NaNGroupConstrainer(config)
        result = constrainer.apply(sample_df)

        # Verify delete action on name
        assert not result["name"].isna().any()

        # Verify erase action on job
        assert result.loc[result["job"].isna(), "bonus"].isna().all()
