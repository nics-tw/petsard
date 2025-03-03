import numpy as np
import pandas as pd
import pytest

from petsard.constrainer.nan_group_constrainer import NaNGroupConstrainer
from petsard.exceptions import ConfigError


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
                "performance": [4, 5, np.nan, 3, 4],
            }
        )

    def test_invalid_config_initialization(self):
        """Test initialization with invalid configurations"""
        invalid_configs = [
            None,
            "not_a_dict",
            {"field": 123},  # Not a dict
            {"field": {"invalid_action": "target"}},  # Invalid action
            {"field": {"erase": None}},  # None target
            # Delete cannot coexist with other actions
            {"job": {"delete": "salary", "erase": ["bonus"]}},
            {"name": {"delete": "age", "copy": "id"}},
        ]

        for config in invalid_configs:
            with pytest.raises(ConfigError):
                NaNGroupConstrainer(config)

    def test_valid_config_initialization(self):
        """Test initialization with valid configurations"""
        valid_configs = [
            {"name": {"delete": "salary"}},  # Delete is standalone
            {"job": {"erase": ["salary", "bonus"]}},  # Multiple targets for erase
            {"salary": {"copy": "bonus"}},  # Single target for copy
            {"name": {"delete": "age"}},  # Delete with unused target
            {"job": {"erase": "bonus"}},  # Single target for erase
        ]

        for config in valid_configs:
            try:
                _ = NaNGroupConstrainer(config)
            except ConfigError:
                pytest.fail(
                    f"Valid configuration {config} raised unexpected ConfigError"
                )

    def test_multiple_actions_same_field(self, sample_df):
        """Test multiple actions on the same field"""
        # No more testing delete with other actions
        config = {"job": {"erase": ["bonus", "performance"]}}

        constrainer = NaNGroupConstrainer(config)
        result = constrainer.apply(sample_df)

        # Check if erase actions are applied correctly
        job_null_mask = result["job"].isna()
        assert result.loc[job_null_mask, "bonus"].isna().all()
        assert result.loc[job_null_mask, "performance"].isna().all()

    def test_delete_action(self, sample_df):
        """Test delete action on NaN values"""
        config = {"name": {"delete": "salary"}}

        constrainer = NaNGroupConstrainer(config)
        result = constrainer.apply(sample_df)

        assert len(result) < len(sample_df)
        assert not result["name"].isna().any()

    def test_erase_action(self, sample_df):
        """Test erase action on NaN values"""
        config = {"job": {"erase": ["salary", "bonus"]}}

        constrainer = NaNGroupConstrainer(config)
        result = constrainer.apply(sample_df)

        # Check if related fields are NaN when main field is NaN
        assert result.loc[result["job"].isna(), "salary"].isna().all()
        assert result.loc[result["job"].isna(), "bonus"].isna().all()

    def test_copy_action_compatible_types(self, sample_df):
        """Test copy action with compatible data types"""
        config = {"salary": {"copy": "bonus"}}

        constrainer = NaNGroupConstrainer(config)
        result = constrainer.apply(sample_df)

        # Check if values are copied when target is NaN
        mask = result["salary"].notna() & pd.isna(sample_df["bonus"])
        assert (result.loc[mask, "bonus"] == result.loc[mask, "salary"]).all()

    def test_copy_action_incompatible_types(self, sample_df):
        """Test copy action with incompatible data types"""
        config = {
            "name": {"copy": "age"}  # String to numeric
        }

        constrainer = NaNGroupConstrainer(config)
        with pytest.warns(UserWarning, match="Cannot copy values"):
            result = constrainer.apply(sample_df)
            assert result["age"].equals(sample_df["age"])

    def test_multiple_constraints(self, sample_df):
        """Test applying multiple constraints"""
        # Separate delete and other actions into different fields
        config = {
            "name": {"delete": "salary"},  # Delete action alone
            "job": {"erase": "bonus"},  # Erase action alone
        }

        constrainer = NaNGroupConstrainer(config)
        result = constrainer.apply(sample_df)

        # Verify delete action on name
        assert not result["name"].isna().any()

        # Verify erase action on job
        job_null_rows = result[result["job"].isna()]
        assert job_null_rows["bonus"].isna().all()
