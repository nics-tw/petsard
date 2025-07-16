import itertools

import numpy as np
import pandas as pd
import pytest

from petsard.constrainer.field_combination_constrainer import (
    FieldCombinationConstrainer,
)
from petsard.exceptions import ConfigError


class TestFieldCombinationConstrainer:
    @pytest.fixture
    def sample_df(self):
        """
        Generate sample data for testing

        Returns:
            pd.DataFrame: DataFrame containing all possible combinations of:
                - Job categories (including NA)
                - Experience levels (including NA)
                - Salary ranges (including NA)
                - Performance grades (including NA)
        """
        jobs = ["Engineer", "Analyst", "Researcher", np.nan]
        levels = ["Junior", "Senior", "Staff", np.nan]
        salaries = [50000, 60000, 70000, np.nan]
        grades = ["A", "B", "C", np.nan]

        data = [
            {
                "job": job,
                "level": level,
                "salary": salary,
                "grade": grade,
            }
            for job, level, salary, grade in itertools.product(
                jobs, levels, salaries, grades
            )
        ]

        return pd.DataFrame(data)

    def test_validate_config_existing_columns(self, sample_df):
        """Test validate_config method with existing columns"""
        constraints = [
            ({"level": "salary"}, {"Senior": 70000}),
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
            ({"nonexistent_field": "salary"}, {"Senior": 70000}),
            ({("job", "nonexistent_level"): "grade"}, {("Engineer", "Senior"): "A"}),
        ]

        constrainer = FieldCombinationConstrainer(constraints)

        with pytest.raises(
            ConfigError, match="Columns .* do not exist in the DataFrame"
        ):
            constrainer.validate_config(sample_df)

    def test_apply_with_nonexistent_columns(self, sample_df):
        """Test apply method with non-existent columns"""
        constraints = [({"nonexistent_field": "salary"}, {"Senior": 70000})]

        constrainer = FieldCombinationConstrainer(constraints)

        with pytest.raises(
            ConfigError, match="Columns .* do not exist in the DataFrame"
        ):
            constrainer.apply(sample_df)

    def test_single_field_constraint_with_specific_value(self, sample_df):
        """Test single field constraint with specific value"""
        constraints = [({"level": "salary"}, {"Senior": 75000})]

        constrainer = FieldCombinationConstrainer(constraints)
        result = constrainer.apply(sample_df)

        # Verify only Senior level with 70000 salary is kept
        assert len(result) == 192  # 4*4*4*4 - 4*4*4
        assert (result[result["level"] == "Senior"]["salary"] == 70000).all()

    def test_valid_single_field_constraint(self):
        """Test valid single field constraint configuration"""
        constraints = [
            ({"level": "salary"}, {"Senior": 70000}),
            ({"job": "grade"}, {"Engineer": "A"}),
        ]

        try:
            FieldCombinationConstrainer(constraints)
        except ConfigError:
            pytest.fail("Valid single field constraint raised unexpected ConfigError")

    def test_valid_multi_field_constraint(self):
        """Test valid multi-field constraint configuration"""
        constraints = [
            ({("job", "level"): "salary"}, {("Engineer", "Junior"): 70000}),
            ({("job", "level"): "grade"}, {("Engineer", "Senior"): "A"}),
            (
                {("grade", "job", "level"): "salary"},
                {("A", "Engineer", "Senior"): [70000]},
            ),
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
        with pytest.raises(ConfigError):
            FieldCombinationConstrainer(
                [
                    {("grade", "job", "level"): "salary"},
                    {("A", "Engineer", "Senior"): [70000]},
                ]
            )

    def test_invalid_field_map(self):
        """Test invalid field map"""
        with pytest.raises(
            ConfigError,
            match="Field map must be a dictionary with exactly one key-value pair",
        ):
            FieldCombinationConstrainer([({}, {"Senior": 70000})])
        with pytest.raises(
            ConfigError,
            match="Field map must be a dictionary with exactly one key-value pair",
        ):
            FieldCombinationConstrainer([({1: 2, 3: 4}, {"Senior": 70000})])

    def test_invalid_source_fields(self):
        """Test invalid source fields type"""
        with pytest.raises(
            ConfigError, match="Source fields must be a string or tuple of strings"
        ):
            FieldCombinationConstrainer([({1: "salary"}, {"Senior": 70000})])
        with pytest.raises(
            ConfigError, match="Source fields must be a string or tuple of strings"
        ):
            FieldCombinationConstrainer(
                [({("job", 1): "salary"}, {("Engineer", "Junior"): 70000})]
            )

    def test_invalid_target_field(self):
        """Test invalid target field type"""
        with pytest.raises(ConfigError, match="Target field must be a string"):
            FieldCombinationConstrainer(
                [({("job", "level"): 1}, {("Engineer", "Junior"): 70000})]
            )

    def test_multi_field_source_value_length_mismatch(self):
        """Test mismatch between multi-field source fields and source values"""
        with pytest.raises(ConfigError, match="Source value must be a tuple of length"):
            FieldCombinationConstrainer(
                [({("job", "level"): "salary"}, {("Engineer",): 75000})]
            )

    def test_apply_with_empty_dataframe(self):
        """Test applying constraints to empty DataFrame"""
        constraints = [({"level": "salary"}, {"Senior": 70000})]
        constrainer = FieldCombinationConstrainer(constraints)

        empty_df = pd.DataFrame(columns=["job", "level", "salary", "grade"])
        result = constrainer.apply(empty_df)

        assert result.empty
        assert list(result.columns) == ["job", "level", "salary", "grade"]

    def test_apply_with_no_matching_combinations(self, sample_df):
        """Test when no rows match the field combinations"""
        constraints = [({"job": "salary"}, {"NonExistentJob": 100000})]
        constrainer = FieldCombinationConstrainer(constraints)

        result = constrainer.apply(sample_df)

        # FieldCombinationConstrainer keeps rows that don't match the constraint
        # It only filters out rows that have the source value but wrong target value
        # Since no job is "NonExistentJob", all rows are kept
        assert len(result) == len(sample_df)
        assert list(result.columns) == list(sample_df.columns)

    def test_multiple_field_combinations_with_overlapping_conditions(self, sample_df):
        """Test multiple field combinations with overlapping conditions"""
        constraints = [
            ({"job": "level"}, {"Engineer": "Senior"}),
            ({"level": "salary"}, {"Senior": 70000}),
        ]
        constrainer = FieldCombinationConstrainer(constraints)
        result = constrainer.apply(sample_df)

        # Should only keep rows that satisfy both conditions
        engineer_senior_mask = (result["job"] == "Engineer") & (
            result["level"] == "Senior"
        )
        if not result[engineer_senior_mask].empty:
            assert all(result.loc[engineer_senior_mask, "salary"] == 70000)

    def test_field_combination_with_nan_values(self):
        """Test field combinations when source fields contain NaN"""
        df_with_nan = pd.DataFrame(
            {
                "job": ["Engineer", np.nan, "Analyst", "Engineer"],
                "level": ["Junior", "Senior", np.nan, "Senior"],
                "salary": [50000, 60000, 70000, 80000],
                "grade": ["A", "B", "C", "A"],
            }
        )

        constraints = [({"job": "grade"}, {"Engineer": "A"})]
        constrainer = FieldCombinationConstrainer(constraints)
        result = constrainer.apply(df_with_nan)

        # Should handle NaN values properly
        engineer_mask = result["job"] == "Engineer"
        if not result[engineer_mask].empty:
            assert all(result.loc[engineer_mask, "grade"] == "A")

    def test_target_field_list_values(self, sample_df):
        """Test when target field has list of allowed values"""
        constraints = [
            ({"job": "grade"}, {"Engineer": ["A", "B"], "Analyst": ["B", "C"]})
        ]
        constrainer = FieldCombinationConstrainer(constraints)
        result = constrainer.apply(sample_df)

        # Check that Engineers only have grades A or B
        engineer_mask = result["job"] == "Engineer"
        if not result[engineer_mask].empty:
            assert all(result.loc[engineer_mask, "grade"].isin(["A", "B"]))

        # Check that Analysts only have grades B or C
        analyst_mask = result["job"] == "Analyst"
        if not result[analyst_mask].empty:
            assert all(result.loc[analyst_mask, "grade"].isin(["B", "C"]))

    def test_complex_multi_field_source_combinations(self):
        """Test complex multi-field source combinations"""
        df = pd.DataFrame(
            {
                "dept": ["IT", "HR", "IT", "Finance", "IT"],
                "level": ["Junior", "Senior", "Senior", "Junior", "Staff"],
                "location": ["NYC", "LA", "NYC", "NYC", "LA"],
                "salary": [60000, 80000, 90000, 55000, 95000],
            }
        )

        constraints = [
            (
                {("dept", "level", "location"): "salary"},
                {("IT", "Senior", "NYC"): 90000, ("HR", "Senior", "LA"): 80000},
            )
        ]

        constrainer = FieldCombinationConstrainer(constraints)
        result = constrainer.apply(df)

        # Check specific combinations
        it_senior_nyc = (
            (result["dept"] == "IT")
            & (result["level"] == "Senior")
            & (result["location"] == "NYC")
        )
        if not result[it_senior_nyc].empty:
            assert all(result.loc[it_senior_nyc, "salary"] == 90000)
