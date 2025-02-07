import numpy as np
import pandas as pd
import pytest

from petsard.constrainer.field_combination_constrainer import (
    FieldCombinationConstrainer,
)
from petsard.error import ConfigError


class TestFieldCombinationConstrainer:
    @pytest.fixture
    def sample_df(self):
        """Generate sample data for testing"""
        return pd.DataFrame(
            {
                "job": ["Engineer", "Doctor", "Engineer", np.nan, "Teacher"],
                "level": ["Senior", "Junior", "Senior", "Junior", "Senior"],
                "salary": [50000, 60000, np.nan, 75000, 80000],
                "department": ["IT", "Medical", "IT", "HR", "Education"],
                "grade": ["A", "B", "A", np.nan, "C"],
            }
        )

    def test_validate_config_existing_columns(self, sample_df):
        """Test validate_config method with existing columns"""
        constraints = [
            ({"department": "salary"}, {"HR": 75000}),
            ({("job", "level"): "grade"}, {("Engineer", "Senior"): "A"}),
        ]

        constrainer = FieldCombinationConstrainer(constraints)
        try:
            constrainer.validate_config(sample_df)
        except ConfigError:
            pytest.fail("Valid columns raised unexpected ConfigError")

    def test_validate_config_nonexistent_columns(self, sample_df):
        """Test validate_config method with non-existent columns"""
        constraints = [
            ({"nonexistent_field": "salary"}, {"HR": 75000}),
            ({("job", "nonexistent_level"): "grade"}, {("Engineer", "Senior"): "A"}),
        ]

        constrainer = FieldCombinationConstrainer(constraints)

        with pytest.raises(
            ConfigError, match="Columns .* do not exist in the DataFrame"
        ):
            constrainer.validate_config(sample_df)

    def test_apply_with_nonexistent_columns(self, sample_df):
        """Test apply method with non-existent columns"""
        constraints = [({"nonexistent_field": "salary"}, {"HR": 75000})]

        constrainer = FieldCombinationConstrainer(constraints)

        with pytest.raises(
            ConfigError, match="Columns .* do not exist in the DataFrame"
        ):
            constrainer.apply(sample_df)

    def test_single_field_constraint_with_specific_value(self, sample_df):
        """Test single field constraint with specific value"""
        constraints = [({"department": "salary"}, {"HR": 75000})]

        constrainer = FieldCombinationConstrainer(constraints)
        result = constrainer.apply(sample_df)

        # Verify only HR department with 75000 salary is kept
        assert len(result) == 5  # All rows should be preserved
        assert (result[result["department"] == "HR"]["salary"] == 75000).all()

    def test_valid_single_field_constraint(self):
        """Test valid single field constraint configuration"""
        constraints = [
            ({"department": "salary"}, {"HR": 75000}),
            ({"job": "grade"}, {"Engineer": "A"}),
        ]

        try:
            FieldCombinationConstrainer(constraints)
        except ConfigError:
            pytest.fail("Valid single field constraint raised unexpected ConfigError")

    def test_valid_multi_field_constraint(self):
        """Test valid multi-field constraint configuration"""
        constraints = [
            ({("department", "level"): "salary"}, {("HR", "Junior"): 75000}),
            ({("job", "level"): "grade"}, {("Engineer", "Senior"): "A"}),
        ]

        try:
            FieldCombinationConstrainer(constraints)
        except ConfigError:
            pytest.fail("Valid multi-field constraint raised unexpected ConfigError")

    def test_invalid_constraints_not_list(self):
        """Test that non-list constraints raise ConfigError"""
        with pytest.raises(ConfigError, match="Constraints must be a list"):
            FieldCombinationConstrainer({"department": "salary"})

    def test_invalid_constraint_structure(self):
        """Test invalid constraint tuple structure"""
        with pytest.raises(
            ConfigError, match="Each constraint must be a tuple with two elements"
        ):
            FieldCombinationConstrainer([("invalid",)])

    def test_invalid_field_map(self):
        """Test invalid field map"""
        with pytest.raises(
            ConfigError,
            match="Field map must be a dictionary with exactly one key-value pair",
        ):
            FieldCombinationConstrainer([({}, {"HR": 75000})])
        with pytest.raises(
            ConfigError,
            match="Field map must be a dictionary with exactly one key-value pair",
        ):
            FieldCombinationConstrainer([({1: 2, 3: 4}, {"HR": 75000})])

    def test_invalid_source_fields(self):
        """Test invalid source fields type"""
        with pytest.raises(
            ConfigError, match="Source fields must be a string or tuple of strings"
        ):
            FieldCombinationConstrainer([({1: "salary"}, {"HR": 75000})])
        with pytest.raises(
            ConfigError, match="Source fields must be a string or tuple of strings"
        ):
            FieldCombinationConstrainer(
                [({("department", 1): "salary"}, {("HR", "Junior"): 75000})]
            )

    def test_invalid_target_field(self):
        """Test invalid target field type"""
        with pytest.raises(ConfigError, match="Target field must be a string"):
            FieldCombinationConstrainer(
                [({("department", "level"): 1}, {("HR", "Junior"): 75000})]
            )

    def test_multi_field_source_value_length_mismatch(self):
        """Test mismatch between multi-field source fields and source values"""
        with pytest.raises(ConfigError, match="Source value must be a tuple of length"):
            FieldCombinationConstrainer(
                [({("department", "level"): "salary"}, {("HR",): 75000})]
            )

    def test_unsupported_multi_field_constraint(self):
        """Test that constraints cannot have more than two fields"""
        with pytest.raises(ConfigError):
            FieldCombinationConstrainer(
                [
                    {("department", "job", "level"): "salary"},
                    {("IT", "Engineer", "Senior"): [50000]},
                ]
            )
