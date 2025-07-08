import pandas as pd
import pytest

from petsard.constrainer.field_constrainer import FieldConstrainer
from petsard.exceptions import ConfigError


class TestFieldConstrainerValidation:
    @pytest.fixture
    def sample_df(self):
        """Generate sample DataFrame for testing purposes"""
        return pd.DataFrame(
            {"id": [1, 2, 3], "age": [25, 30, 35], "salary": [50000, 60000, 70000]}
        )

    def test_invalid_config_structure(self):
        """
        Test configuration structure validation.
        Verifies that invalid configurations raise appropriate errors.
        """
        invalid_configs = [
            (None, "Configuration must be a list"),
            ("not_a_list", "Configuration must be a list"),
            ({"key": "value"}, "Configuration must be a list"),
            ([1, 2, 3], "All configuration items must be strings"),
            ([None], "All configuration items must be strings"),
            ([""], "Empty constraint at index 0"),
            (["age > 30", ""], "Empty constraint at index 1"),
        ]

        for config, expected_error in invalid_configs:
            with pytest.raises(ConfigError, match=expected_error):
                FieldConstrainer(config)

    def test_invalid_constraint_syntax(self):
        """
        Test constraint syntax validation.
        Verifies that invalid syntax in constraints raises appropriate errors.
        """
        invalid_constraints = [
            (["age > 30)"], "Unmatched parentheses"),
            (["age salary"], "No valid operator found"),
            (["age >>= 30"], "Invalid operator in constraint"),
        ]

        for config, expected_error in invalid_constraints:
            with pytest.raises(ConfigError, match=expected_error):
                FieldConstrainer(config)

    def test_nonexistent_columns(self, sample_df):
        """
        Test validation of column existence.
        Verifies that constraints referencing non-existent columns raise errors.
        """
        constrainer = FieldConstrainer(["nonexistent > 30"])
        with pytest.raises(ConfigError, match="Column 'nonexistent' .* does not exist"):
            constrainer.validate_config(sample_df)

    def test_apply_with_nonexistent_columns(self, sample_df):
        """
        Test apply method with non-existent columns
        Verifies that applying constraints with non-existent columns raises ConfigError
        """
        constrainer = FieldConstrainer(["nonexistent > 30"])

        with pytest.raises(
            ConfigError, match="Column 'nonexistent' .* does not exist in DataFrame"
        ):
            constrainer.apply(sample_df)

    def test_valid_config(self, sample_df):
        """
        Test valid configuration scenarios.
        Verifies that valid constraints pass validation.
        """
        valid_configs = [
            ["age > 30"],
            ["salary >= 50000", "age <= 40"],
            ["(age > 25) & (salary < 80000)"],
            ["age IS NOT pd.NA"],
            ["salary + id < 100000"],
        ]

        for config in valid_configs:
            constrainer = FieldConstrainer(config)
            assert constrainer.validate_config(sample_df) is True

    def test_complex_expression_validation(self, sample_df):
        """
        Test validation of complex constraint expressions.
        Verifies that complex combinations of operators and fields are handled correctly.
        """
        constrainer = FieldConstrainer(
            ["((age > 30) & (salary > 60000)) | (id IS pd.NA)"]
        )
        assert constrainer.validate_config(sample_df) is True

    def test_field_extraction(self):
        """
        Test the extraction of field names from various constraint patterns.
        Verifies correct handling of complex expressions including:
        - Field addition operations
        - Parenthesized expressions
        - NULL checks
        - Date operations
        """
        test_cases = [
            ("salary + id < 100000", ["salary", "id"]),
            (
                "((age > 30) & (salary > 60000)) | (id IS pd.NA)",
                ["age", "salary", "id"],
            ),
            ("date + days >= DATE(2023-01-02)", ["date", "days"]),
            ("(bonus IS pd.NA) & (age > 25)", ["bonus", "age"]),
        ]

        constrainer = FieldConstrainer([])
        for constraint, expected_fields in test_cases:
            fields = constrainer._extract_fields(constraint)
            assert sorted(fields) == sorted(expected_fields), (
                f"Field extraction failed for '{constraint}'. Expected: {expected_fields}, Got: {fields}"
            )

    def test_apply_with_empty_dataframe(self):
        """Test applying constraints to empty DataFrame"""
        constrainer = FieldConstrainer(["age > 30"])
        empty_df = pd.DataFrame(columns=["age", "name"])
        result = constrainer.apply(empty_df)
        assert result.empty
        assert list(result.columns) == ["age", "name"]

    def test_apply_with_all_rows_filtered(self, sample_df):
        """Test when all rows are filtered out by constraints"""
        constrainer = FieldConstrainer(["age > 100"])  # Impossible constraint
        result = constrainer.apply(sample_df)
        assert result.empty
        assert list(result.columns) == list(sample_df.columns)

    def test_complex_boolean_operations(self, sample_df):
        """Test complex boolean operations in constraints"""
        constrainer = FieldConstrainer(["((age > 20) & (salary < 80000)) | (id == 1)"])
        result = constrainer.apply(sample_df)

        # Should keep rows that meet the complex condition
        for _, row in result.iterrows():
            condition_met = ((row["age"] > 20) and (row["salary"] < 80000)) or (
                row["id"] == 1
            )
            assert condition_met

    def test_null_handling_in_constraints(self):
        """Test handling of null values in constraints"""
        df_with_nulls = pd.DataFrame(
            {
                "id": [1, 2, 3, 4],
                "age": [25, None, 35, 40],
                "salary": [50000, 60000, None, 70000],
            }
        )

        constrainer = FieldConstrainer(["age IS NOT pd.NA"])
        result = constrainer.apply(df_with_nulls)

        # Should only keep rows where age is not null
        assert all(pd.notna(result["age"]))
        assert len(result) == 3  # Should have 3 non-null age rows

    def test_multiple_constraints_interaction(self, sample_df):
        """Test multiple constraints working together"""
        constrainer = FieldConstrainer(["age >= 25", "salary >= 50000", "id <= 3"])
        result = constrainer.apply(sample_df)

        # All constraints should be satisfied
        assert all(result["age"] >= 25)
        assert all(result["salary"] >= 50000)
        assert all(result["id"] <= 3)
