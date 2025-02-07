import numpy as np
import pandas as pd
import pytest

from petsard import Constrainer


class MockSynthesizer:
    def sample(self, num_rows: int) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "name": np.random.choice(
                    ["John", "Mary", "Tom", "Jane", None], num_rows
                ),
                "job": np.random.choice(
                    ["Engineer", "Doctor", "Teacher", None], num_rows
                ),
                "salary": np.random.randint(30000, 120000, num_rows),
                "bonus": [
                    None if np.random.random() < 0.3 else x / 10
                    for x in np.random.randint(30000, 120000, num_rows)
                ],
                "age": np.random.randint(20, 70, num_rows),
                "education": np.random.choice(
                    ["High School", "Bachelor", "Master", "PhD"], num_rows
                ),
                "performance": np.random.randint(1, 6, num_rows),
            }
        )


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "name": ["John", None, "Mary", "Tom", "Jane"],
            "job": ["Engineer", "Doctor", None, "Teacher", None],
            "salary": [50000, 80000, None, 60000, 70000],
            "bonus": [5000, None, 8000, None, 7000],
            "age": [25, 35, 45, 55, 65],
            "education": ["High School", "Bachelor", "Master", "PhD", "PhD"],
            "performance": [3, 4, 5, 4, 5],
        }
    )


@pytest.fixture
def config():
    return {
        "nan_groups": {
            "name": {"delete": "salary"},
            "job": {"erase": ["salary", "bonus"]},
            "salary": {"copy": "bonus"},
        },
        "field_constraints": ["age >= 20 & age <= 60", "performance >= 4"],
        "field_combinations": [
            (
                {"education": "performance"},
                {"PhD": [4, 5], "Master": [4, 5], "Bachelor": [3, 4, 5]},
            )
        ],
    }


def test_basic_initialization(config):
    """Test basic constrainer initialization"""
    constrainer = Constrainer(config)
    assert constrainer is not None
    assert constrainer.config == config


def test_nan_groups_constraints(sample_df, config):
    """Test NaN group constraints application"""
    constrainer = Constrainer({"nan_groups": config["nan_groups"]})
    result = constrainer.apply(sample_df)

    # Test 'delete' action
    assert all(pd.notna(result["name"]))

    # Test 'erase' action
    job_null_mask = pd.isna(result["job"])
    assert all(pd.isna(result.loc[job_null_mask, "salary"]))
    assert all(pd.isna(result.loc[job_null_mask, "bonus"]))

    # Test 'copy' action
    salary_mask = pd.notna(result["salary"]) & pd.isna(result["bonus"])
    if not result[salary_mask].empty:
        assert all(
            result.loc[salary_mask, "salary"] == result.loc[salary_mask, "bonus"]
        )


def test_field_constraints(sample_df, config):
    """Test field constraints application"""
    constrainer = Constrainer({"field_constraints": config["field_constraints"]})
    result = constrainer.apply(sample_df)

    # Test age constraint
    assert all(result["age"].between(20, 60))

    # Test performance constraint
    assert all(result["performance"] >= 4)


def test_field_combinations(sample_df, config):
    """Test field combinations constraints"""
    constrainer = Constrainer({"field_combinations": config["field_combinations"]})
    result = constrainer.apply(sample_df)

    # Test education-performance combinations
    phd_mask = result["education"] == "PhD"
    assert all(result.loc[phd_mask, "performance"].isin([4, 5]))

    master_mask = result["education"] == "Master"
    assert all(result.loc[master_mask, "performance"].isin([4, 5]))


def test_all_constraints_together(sample_df, config):
    """Test all constraints working together"""
    constrainer = Constrainer(config)
    result = constrainer.apply(sample_df)

    # Should meet all conditions
    assert all(pd.notna(result["name"]))
    assert all(result["age"].between(20, 60))
    assert all(result["performance"] >= 4)

    phd_mask = result["education"] == "PhD"
    if not result[phd_mask].empty:
        assert all(result.loc[phd_mask, "performance"].isin([4, 5]))


def test_resample_functionality(sample_df, config):
    """Test resample_until_satisfy functionality"""
    constrainer = Constrainer(config)
    synthesizer = MockSynthesizer()

    target_rows = 5
    result = constrainer.resample_until_satisfy(
        data=sample_df,
        target_rows=target_rows,
        synthesizer=synthesizer,
        sampling_ratio=2.0,
        max_trials=10,
    )

    # Check basic requirements
    assert len(result) == target_rows
    assert all(result["age"].between(20, 60))
    assert all(result["performance"] >= 4)


def test_error_handling(sample_df):
    """Test error handling"""
    # Test invalid config format
    with pytest.raises(ValueError):
        Constrainer("not a dict")

    # Test missing columns
    invalid_config = {"field_constraints": ["invalid_column > 0"]}
    constrainer = Constrainer(invalid_config)
    with pytest.raises(Exception):
        constrainer.apply(sample_df)


def test_edge_cases(sample_df, config):
    """Test edge cases"""
    constrainer = Constrainer(config)

    # Test empty DataFrame
    empty_df = pd.DataFrame(columns=sample_df.columns)
    result = constrainer.apply(empty_df)
    assert result.empty

    # Test DataFrame with all NaN
    all_nan_df = pd.DataFrame(
        {
            "name": [None] * 3,
            "job": [None] * 3,
            "salary": [None] * 3,
            "bonus": [None] * 3,
            "age": [None] * 3,
            "education": [None] * 3,
            "performance": [None] * 3,
        }
    )
    result = constrainer.apply(all_nan_df)
    assert result.empty
