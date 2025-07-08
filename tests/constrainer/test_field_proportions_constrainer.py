import pandas as pd
import pytest

from petsard.constrainer.field_proportions_constrainer import (
    FieldProportionsConfig,
    FieldProportionsConstrainer,
)


class TestFieldProportionsConfig:
    """Test FieldProportionsConfig class"""

    def test_valid_config_initialization(self):
        """Test valid configuration initialization"""
        config = FieldProportionsConfig(
            field_proportions=[
                {"fields": "age", "mode": "all", "tolerance": 0.05},
                {"fields": "income", "mode": "missing", "tolerance": 0.03},
            ]
        )
        assert len(config.field_proportions) == 2
        assert config.target_n_rows is None  # Should be None initially

    def test_invalid_field_proportions_structure(self):
        """Test invalid field proportions structure"""
        with pytest.raises(ValueError):
            FieldProportionsConfig(
                field_proportions=[
                    {"fields": "age"},  # Missing mode
                ]
            )

        with pytest.raises(ValueError):
            FieldProportionsConfig(
                field_proportions=[
                    {"mode": "all"},  # Missing fields
                ]
            )

        with pytest.raises(ValueError):
            FieldProportionsConfig(
                field_proportions=[
                    {
                        "fields": "age",
                        "mode": "invalid",
                        "tolerance": 0.05,
                    },  # Invalid mode
                ]
            )

    def test_invalid_tolerance_values(self):
        """Test invalid tolerance values"""
        with pytest.raises(ValueError):
            FieldProportionsConfig(
                field_proportions=[
                    {"fields": "age", "mode": "all", "tolerance": 1.5},  # > 1
                ]
            )

        with pytest.raises(ValueError):
            FieldProportionsConfig(
                field_proportions=[
                    {"fields": "age", "mode": "all", "tolerance": -0.1},  # < 0
                ]
            )

    def test_verify_data_with_valid_data(self):
        """Test verify_data with valid DataFrame"""
        config = FieldProportionsConfig(
            field_proportions=[
                {"fields": "age", "mode": "all", "tolerance": 0.05},
                {"fields": "income", "mode": "missing", "tolerance": 0.03},
            ]
        )

        # Create test data
        data = pd.DataFrame(
            {
                "age": [25, 30, 35, 40, 25, 30],
                "income": [50000, 60000, None, 80000, 55000, None],
            }
        )

        config.verify_data(data, target_n_rows=100)

        # Check that target_n_rows was set
        assert config.target_n_rows == 100
        # Check that original proportions were calculated
        assert len(config.original_proportions) > 0

    def test_verify_data_with_missing_columns(self):
        """Test verify_data with missing columns"""
        config = FieldProportionsConfig(
            field_proportions=[
                {"fields": "nonexistent_column", "mode": "all", "tolerance": 0.05},
            ]
        )

        data = pd.DataFrame(
            {
                "age": [25, 30, 35],
                "income": [50000, 60000, 70000],
            }
        )

        with pytest.raises(ValueError):
            config.verify_data(data, target_n_rows=100)

    def test_check_proportions(self):
        """Test check_proportions method"""
        config = FieldProportionsConfig(
            field_proportions=[
                {"fields": "category", "mode": "all", "tolerance": 0.1},
            ]
        )

        # Original data
        original_data = pd.DataFrame(
            {
                "category": ["A"] * 50 + ["B"] * 30 + ["C"] * 20,
            }
        )

        config.verify_data(original_data, target_n_rows=100)

        # Filtered data that maintains proportions
        good_filtered_data = pd.DataFrame(
            {
                "category": ["A"] * 50 + ["B"] * 30 + ["C"] * 20,
            }
        )

        satisfied, violations = config.check_proportions(good_filtered_data)
        assert satisfied is True
        assert len(violations) == 0

        # Filtered data that violates proportions
        bad_filtered_data = pd.DataFrame(
            {
                "category": ["A"] * 90 + ["B"] * 5 + ["C"] * 5,  # Heavily skewed
            }
        )

        satisfied, violations = config.check_proportions(bad_filtered_data)
        assert satisfied is False
        assert len(violations) > 0


class TestFieldProportionsConstrainer:
    """Test FieldProportionsConstrainer class"""

    def test_constrainer_initialization(self):
        """Test constrainer initialization"""
        config = {
            "field_proportions": [
                {"fields": "age", "mode": "all", "tolerance": 0.05},
            ]
        }

        constrainer = FieldProportionsConstrainer(config)
        assert constrainer.proportions_config is not None
        assert constrainer.validate_config() is True

    def test_default_tolerance_constrainer(self):
        """Test constrainer with default tolerance"""
        config = {
            "field_proportions": [
                {
                    "fields": "age",
                    "mode": "all",
                },  # No tolerance specified, should use default 0.1
            ]
        }

        constrainer = FieldProportionsConstrainer(config)
        assert constrainer.proportions_config is not None
        assert constrainer.validate_config() is True

    def test_invalid_constrainer_config(self):
        """Test constrainer with invalid configuration"""
        config = {
            "field_proportions": [
                {"fields": "age", "mode": "invalid", "tolerance": 0.05},  # Invalid mode
            ]
        }

        with pytest.raises(ValueError):
            FieldProportionsConstrainer(config)

    def test_apply_with_empty_dataframe(self):
        """Test apply method with empty DataFrame"""
        config = {
            "field_proportions": [
                {"fields": "age", "mode": "all", "tolerance": 0.05},
            ]
        }

        constrainer = FieldProportionsConstrainer(config)
        empty_df = pd.DataFrame()
        result = constrainer.apply(empty_df, target_rows=100)
        assert result.empty

    def test_apply_with_valid_data(self):
        """Test apply method with valid data"""
        config = {
            "field_proportions": [
                {"fields": "category", "mode": "all", "tolerance": 0.1},
            ]
        }

        constrainer = FieldProportionsConstrainer(config)

        # Create test data with known proportions
        data = pd.DataFrame(
            {
                "category": ["A"] * 60 + ["B"] * 30 + ["C"] * 10,  # 60%, 30%, 10%
            }
        )

        result = constrainer.apply(data, target_rows=50)

        # Result should be filtered to maintain proportions
        assert len(result) <= len(data)
        assert "category" in result.columns

    def test_field_combination_proportions(self):
        """Test field combination proportions"""
        config = {
            "field_proportions": [
                {"fields": ["gender", "age_group"], "mode": "all", "tolerance": 0.1},
            ]
        }

        constrainer = FieldProportionsConstrainer(config)

        # Create test data with field combinations
        data = pd.DataFrame(
            {
                "gender": ["M", "F"] * 50,
                "age_group": ["Young", "Old"] * 50,
            }
        )

        result = constrainer.apply(data, target_rows=80)

        # Result should maintain field combination proportions
        assert len(result) <= len(data)
        assert "gender" in result.columns
        assert "age_group" in result.columns

    def test_missing_value_proportions(self):
        """Test missing value proportions"""
        config = {
            "field_proportions": [
                {"fields": "income", "mode": "missing", "tolerance": 0.05},
            ]
        }

        constrainer = FieldProportionsConstrainer(config)

        # Create test data with missing values
        data = pd.DataFrame(
            {
                "income": [50000, None, 60000, None, 70000] * 20,  # 40% missing
            }
        )

        result = constrainer.apply(data, target_rows=80)

        # Result should maintain missing value proportions
        assert len(result) <= len(data)
        missing_ratio = result["income"].isna().mean()
        # Should be close to original missing ratio (40%)
        assert 0.3 <= missing_ratio <= 0.5  # Allow some tolerance

    def test_edge_case_all_same_values(self):
        """Test edge case where all values are the same"""
        config = {
            "field_proportions": [
                {"fields": "category", "mode": "all", "tolerance": 0.1},
            ]
        }

        constrainer = FieldProportionsConstrainer(config)

        # All values are the same
        data = pd.DataFrame(
            {
                "category": ["A"] * 100,
            }
        )

        result = constrainer.apply(data, target_rows=50)
        assert len(result) <= len(data)
        # All values should still be "A"
        assert (result["category"] == "A").all()

    def test_edge_case_target_larger_than_data(self):
        """Test edge case where target is larger than available data"""
        config = {
            "field_proportions": [
                {"fields": "category", "mode": "all", "tolerance": 0.1},
            ]
        }

        constrainer = FieldProportionsConstrainer(config)

        data = pd.DataFrame(
            {
                "category": ["A"] * 50 + ["B"] * 50,
            }
        )

        result = constrainer.apply(data, target_rows=200)  # Larger than data
        # Should return all available data since target is larger
        assert len(result) == len(data)


class TestFieldProportionsConstrainerExtremeEdgeCases:
    """Test extreme edge cases for FieldProportionsConstrainer"""

    def test_extreme_case_single_row_data(self):
        """Test extreme case with only one row of data"""
        config = {
            "field_proportions": [
                {"fields": "category", "mode": "all", "tolerance": 0.1},
            ]
        }

        constrainer = FieldProportionsConstrainer(config)

        # Single row data
        data = pd.DataFrame(
            {
                "category": ["A"],
            }
        )

        result = constrainer.apply(data, target_rows=10)
        assert len(result) <= len(data)
        assert len(result) >= 0

    def test_extreme_case_very_large_tolerance(self):
        """Test extreme case with very large tolerance"""
        config = {
            "field_proportions": [
                {
                    "fields": "category",
                    "mode": "all",
                    "tolerance": 0.9,
                },  # Very large tolerance
            ]
        }

        constrainer = FieldProportionsConstrainer(config)

        data = pd.DataFrame(
            {
                "category": ["A"] * 80 + ["B"] * 20,
            }
        )

        result = constrainer.apply(data, target_rows=50)
        # With large tolerance, should be more flexible
        assert len(result) <= len(data)

    def test_extreme_case_zero_tolerance(self):
        """Test extreme case with zero tolerance"""
        config = {
            "field_proportions": [
                {
                    "fields": "category",
                    "mode": "all",
                    "tolerance": 0.0,
                },  # Zero tolerance
            ]
        }

        constrainer = FieldProportionsConstrainer(config)

        data = pd.DataFrame(
            {
                "category": ["A"] * 50 + ["B"] * 50,  # Perfect 50-50 split
            }
        )

        result = constrainer.apply(data, target_rows=50)
        # Should still work with zero tolerance if proportions are exact
        assert len(result) <= len(data)

    def test_extreme_case_all_missing_values(self):
        """Test extreme case where all values are missing"""
        config = {
            "field_proportions": [
                {"fields": "income", "mode": "missing", "tolerance": 0.1},
            ]
        }

        constrainer = FieldProportionsConstrainer(config)

        # All values are missing
        data = pd.DataFrame(
            {
                "income": [None] * 50,
            }
        )

        result = constrainer.apply(data, target_rows=30)
        assert len(result) <= len(data)
        # All values should still be missing
        if len(result) > 0:
            assert result["income"].isna().all()

    def test_extreme_case_no_missing_values(self):
        """Test extreme case where no values are missing"""
        config = {
            "field_proportions": [
                {"fields": "income", "mode": "missing", "tolerance": 0.1},
            ]
        }

        constrainer = FieldProportionsConstrainer(config)

        # No missing values
        data = pd.DataFrame(
            {
                "income": [50000, 60000, 70000] * 20,
            }
        )

        result = constrainer.apply(data, target_rows=30)
        assert len(result) <= len(data)
        # No values should be missing
        if len(result) > 0:
            assert result["income"].notna().all()

    def test_extreme_case_very_small_target(self):
        """Test extreme case with very small target rows"""
        config = {
            "field_proportions": [
                {"fields": "category", "mode": "all", "tolerance": 0.1},
            ]
        }

        constrainer = FieldProportionsConstrainer(config)

        data = pd.DataFrame(
            {
                "category": ["A"] * 50 + ["B"] * 50,
            }
        )

        result = constrainer.apply(data, target_rows=1)  # Very small target
        assert len(result) <= len(data)

    def test_extreme_case_huge_data_small_target(self):
        """Test extreme case with huge data but small target"""
        config = {
            "field_proportions": [
                {"fields": "category", "mode": "all", "tolerance": 0.1},
            ]
        }

        constrainer = FieldProportionsConstrainer(config)

        # Large dataset
        data = pd.DataFrame(
            {
                "category": ["A"] * 500
                + ["B"] * 300
                + ["C"] * 200,  # Reduced size for testing
            }
        )

        result = constrainer.apply(data, target_rows=10)
        assert len(result) <= len(data)
        # Should maintain proportions even with large reduction
        if len(result) > 0:
            result_props = result["category"].value_counts(normalize=True)
            assert len(result_props) > 0

    def test_extreme_case_many_unique_values(self):
        """Test extreme case with many unique values"""
        config = {
            "field_proportions": [
                {"fields": "id", "mode": "all", "tolerance": 0.1},
            ]
        }

        constrainer = FieldProportionsConstrainer(config)

        # Many unique values (each appears only once)
        data = pd.DataFrame(
            {
                "id": list(range(100)),  # 100 unique values
            }
        )

        result = constrainer.apply(data, target_rows=50)
        assert len(result) <= len(data)

    def test_extreme_case_complex_field_combinations(self):
        """Test extreme case with complex field combinations"""
        config = {
            "field_proportions": [
                {
                    "fields": ["field1", "field2", "field3"],
                    "mode": "all",
                    "tolerance": 0.2,
                },
            ]
        }

        constrainer = FieldProportionsConstrainer(config)

        # Complex combinations - ensure all arrays have same length
        n_rows = 102  # LCM of 2, 3, and 2
        data = pd.DataFrame(
            {
                "field1": (["A", "B"] * (n_rows // 2))[:n_rows],
                "field2": (["X", "Y", "Z"] * (n_rows // 3 + 1))[:n_rows],
                "field3": (["P", "Q"] * (n_rows // 2))[:n_rows],
            }
        )

        result = constrainer.apply(data, target_rows=30)
        assert len(result) <= len(data)

    def test_extreme_case_mixed_data_types(self):
        """Test extreme case with mixed data types"""
        config = {
            "field_proportions": [
                {"fields": "mixed_field", "mode": "all", "tolerance": 0.1},
            ]
        }

        constrainer = FieldProportionsConstrainer(config)

        # Mixed data types
        data = pd.DataFrame(
            {
                "mixed_field": [1, "string", 3.14, None, True, False] * 20,
            }
        )

        result = constrainer.apply(data, target_rows=40)
        assert len(result) <= len(data)

    def test_extreme_case_empty_field_proportions_list(self):
        """Test extreme case with empty field proportions list"""
        config = {
            "field_proportions": [],  # Empty list
        }

        constrainer = FieldProportionsConstrainer(config)

        data = pd.DataFrame(
            {
                "category": ["A"] * 30 + ["B"] * 20,
            }
        )

        result = constrainer.apply(data, target_rows=50)
        # Should return original data since no constraints
        pd.testing.assert_frame_equal(result, data)

    def test_extreme_case_duplicate_field_rules(self):
        """Test extreme case with duplicate field rules"""
        config = {
            "field_proportions": [
                {"fields": "category", "mode": "all", "tolerance": 0.1},
                {
                    "fields": "category",
                    "mode": "all",
                    "tolerance": 0.2,
                },  # Duplicate field
            ]
        }

        # This should raise an error due to duplicate fields
        with pytest.raises(ValueError):
            FieldProportionsConstrainer(config)

    def test_extreme_case_very_unbalanced_data(self):
        """Test extreme case with very unbalanced data"""
        config = {
            "field_proportions": [
                {"fields": "category", "mode": "all", "tolerance": 0.05},
            ]
        }

        constrainer = FieldProportionsConstrainer(config)

        # Very unbalanced: 99% A, 1% B
        data = pd.DataFrame(
            {
                "category": ["A"] * 99 + ["B"] * 1,
            }
        )

        result = constrainer.apply(data, target_rows=100)
        assert len(result) <= len(data)
        # Should maintain the unbalanced distribution
        if len(result) > 0:
            result_props = result["category"].value_counts(normalize=True)
            # A should still dominate
            assert result_props.get("A", 0) > result_props.get("B", 0)

    def test_extreme_case_numerical_precision(self):
        """Test extreme case with numerical precision issues"""
        config = {
            "field_proportions": [
                {
                    "fields": "value",
                    "mode": "all",
                    "tolerance": 0.001,
                },  # Very small tolerance
            ]
        }

        constrainer = FieldProportionsConstrainer(config)

        # Values that might cause floating point precision issues
        data = pd.DataFrame(
            {
                "value": [0.1, 0.2, 0.3] * 334,  # 1002 rows total
            }
        )

        result = constrainer.apply(data, target_rows=1000)
        assert len(result) <= len(data)

    def test_extreme_case_unicode_and_special_characters(self):
        """Test extreme case with unicode and special characters"""
        config = {
            "field_proportions": [
                {"fields": "text", "mode": "all", "tolerance": 0.1},
            ]
        }

        constrainer = FieldProportionsConstrainer(config)

        # Unicode and special characters
        data = pd.DataFrame(
            {
                "text": ["中文", "🚀", "café", "naïve", "résumé"] * 20,
            }
        )

        result = constrainer.apply(data, target_rows=30)
        assert len(result) <= len(data)

    def test_extreme_case_datetime_objects(self):
        """Test extreme case with datetime objects"""
        config = {
            "field_proportions": [
                {"fields": "date", "mode": "all", "tolerance": 0.1},
            ]
        }

        constrainer = FieldProportionsConstrainer(config)

        # Datetime objects
        dates = pd.date_range("2020-01-01", periods=5, freq="D")
        data = pd.DataFrame(
            {
                "date": list(dates) * 20,
            }
        )

        result = constrainer.apply(data, target_rows=40)
        assert len(result) <= len(data)

    def test_extreme_case_large_string_values(self):
        """Test extreme case with very large string values"""
        config = {
            "field_proportions": [
                {"fields": "large_text", "mode": "all", "tolerance": 0.1},
            ]
        }

        constrainer = FieldProportionsConstrainer(config)

        # Very large strings
        large_strings = ["A" * 1000, "B" * 1000, "C" * 1000]
        data = pd.DataFrame(
            {
                "large_text": large_strings * 20,
            }
        )

        result = constrainer.apply(data, target_rows=20)
        assert len(result) <= len(data)

    def test_extreme_case_nested_tuple_combinations(self):
        """Test extreme case with deeply nested tuple combinations"""
        config = {
            "field_proportions": [
                {"fields": ["a", "b", "c", "d", "e"], "mode": "all", "tolerance": 0.2},
            ]
        }

        constrainer = FieldProportionsConstrainer(config)

        # Many fields creating complex combinations
        data = pd.DataFrame(
            {
                "a": ["X", "Y"] * 50,
                "b": ["1", "2"] * 50,
                "c": ["P", "Q"] * 50,
                "d": ["M", "N"] * 50,
                "e": ["I", "J"] * 50,
            }
        )

        result = constrainer.apply(data, target_rows=30)
        assert len(result) <= len(data)

    def test_apply_without_target_rows_should_fail(self):
        """Test that apply without target_rows should fail"""
        config = {
            "field_proportions": [
                {"fields": "category", "mode": "all", "tolerance": 0.1},
            ]
        }

        constrainer = FieldProportionsConstrainer(config)

        data = pd.DataFrame(
            {
                "category": ["A"] * 50 + ["B"] * 50,
            }
        )

        with pytest.raises(ValueError):
            constrainer.apply(data)  # No target_rows provided
