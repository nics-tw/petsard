import numpy as np
import pandas as pd
import pytest

from petsard.constrainer import Constrainer


class MockSynthesizer:
    def __init__(self):
        self.config = {}

    def sample(self, num_rows: int = None) -> pd.DataFrame:
        # Use num_rows from config if not provided as parameter
        if num_rows is None:
            num_rows = self.config.get("sample_num_rows", 10)

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


def test_empty_config():
    """Test constrainer with empty config"""
    constrainer = Constrainer({})
    sample_data = pd.DataFrame({"name": ["Alice", "Bob"], "age": [25, 30]})
    result = constrainer.apply(sample_data)
    pd.testing.assert_frame_equal(result, sample_data)


def test_unknown_constraint_type_warning():
    """Test warning for unknown constraint types"""
    config = {"unknown_constraint": {"some": "config"}}

    with pytest.warns(
        UserWarning, match="Unknown constraint type 'unknown_constraint'"
    ):
        constrainer = Constrainer(config)

    # Should still work, just ignore unknown constraint
    sample_data = pd.DataFrame({"age": [25, 30]})
    result = constrainer.apply(sample_data)
    pd.testing.assert_frame_equal(result, sample_data)


def test_resample_trails_attribute(sample_df, config):
    """Test that resample_trails attribute is properly set"""
    constrainer = Constrainer(config)
    synthesizer = MockSynthesizer()

    # Initially should be None
    assert constrainer.resample_trails is None

    constrainer.resample_until_satisfy(
        data=sample_df, target_rows=3, synthesizer=synthesizer, max_trials=2
    )

    # Should be set after resampling
    assert constrainer.resample_trails is not None
    assert isinstance(constrainer.resample_trails, int)
    assert constrainer.resample_trails >= 0


def test_register_custom_constraint(sample_df):
    """Test registering custom constraint type"""
    from petsard.constrainer.constrainer_base import BaseConstrainer

    class CustomConstrainer(BaseConstrainer):
        def __init__(self, config):
            self.config = config

        def apply(self, df):
            # Simple custom constraint: remove rows where name starts with 'J'
            return df[~df["name"].str.startswith("J", na=False)]

        def validate_config(self, df):
            return True

    # Register the custom constraint
    Constrainer.register("custom_filter", CustomConstrainer)

    config = {"custom_filter": {"remove_j_names": True}}
    constrainer = Constrainer(config)
    result = constrainer.apply(sample_df)

    # Should not have any names starting with 'J'
    assert not any(result["name"].str.startswith("J", na=False))


def test_register_invalid_constraint_class():
    """Test error when registering invalid constraint class"""

    class InvalidConstrainer:
        pass

    with pytest.raises(ValueError, match="Must inherit from BaseConstrainer"):
        Constrainer.register("invalid", InvalidConstrainer)


def test_field_proportions_integration(sample_df):
    """Test field proportions constrainer integration with new architecture"""
    # Create test data with known proportions
    data = pd.DataFrame(
        {
            "category": ["A"] * 60 + ["B"] * 30 + ["C"] * 10,
            "income": [50000, None, 60000, None, 70000] * 20,
            "age_group": ["Young", "Old"] * 50,
        }
    )

    # Test 1: Single field proportions (updated architecture)
    config1 = {
        "field_proportions": [{"fields": "category", "mode": "all", "tolerance": 0.1}]
    }

    constrainer1 = Constrainer(config1)
    result1 = constrainer1.apply(data, target_rows=50)

    # Check that proportions are maintained within tolerance
    original_props = data["category"].value_counts(normalize=True)
    result_props = result1["category"].value_counts(normalize=True)

    for category in original_props.index:
        if category in result_props.index:
            prop_diff = abs(original_props[category] - result_props[category])
            assert prop_diff <= 0.15  # Allow some flexibility due to filtering

    # Test 2: Missing value proportions (updated architecture)
    config2 = {
        "field_proportions": [
            {"fields": "income", "mode": "missing", "tolerance": 0.05}
        ]
    }

    constrainer2 = Constrainer(config2)
    result2 = constrainer2.apply(data, target_rows=80)

    # Check missing value proportions
    original_missing = data["income"].isna().mean()
    result_missing = result2["income"].isna().mean()
    assert abs(original_missing - result_missing) <= 0.1  # Allow some tolerance

    # Test 3: Field combination proportions (updated architecture)
    config3 = {
        "field_proportions": [
            {"fields": ["category", "age_group"], "mode": "all", "tolerance": 0.15}
        ]
    }

    constrainer3 = Constrainer(config3)
    result3 = constrainer3.apply(data, target_rows=60)

    # Check that field combinations are maintained
    original_combos = data.groupby(["category", "age_group"]).size()
    result_combos = result3.groupby(["category", "age_group"]).size()

    # Should have similar distribution patterns
    assert len(result_combos) > 0
    assert len(result3) <= len(data)


def test_field_proportions_with_other_constraints(sample_df):
    """Test field proportions working with other constraint types"""
    # Create test data
    data = pd.DataFrame(
        {
            "name": ["John", "Mary", "Tom", "Jane", "Bob"] * 20,
            "category": ["A"] * 60 + ["B"] * 30 + ["C"] * 10,
            "age": np.random.randint(15, 70, 100),
            "performance": np.random.randint(1, 6, 100),
        }
    )

    # Combine field proportions with field constraints (updated architecture)
    config = {
        "field_proportions": [{"fields": "category", "mode": "all", "tolerance": 0.1}],
        "field_constraints": ["age >= 20 & age <= 60", "performance >= 3"],
    }

    constrainer = Constrainer(config)
    result = constrainer.apply(data, target_rows=50)

    # Should satisfy both field constraints and proportions
    assert all(result["age"].between(20, 60))
    assert all(result["performance"] >= 3)
    assert len(result) <= len(data)

    # Check proportions are reasonably maintained
    if len(result) > 0:
        result_props = result["category"].value_counts(normalize=True)
        assert len(result_props) > 0


def test_field_proportions_comprehensive_integration():
    """Test comprehensive field proportions integration (based on user's final test)"""
    # 建立測試資料 - 基於用戶提供的最終測試
    data = pd.DataFrame(
        {
            "education": ["Bachelor"] * 40 + ["Master"] * 35 + ["PhD"] * 25,
            "income": [">50K", "<=50K"] * 50,
            "workclass": ["Private"] * 80 + [None] * 20,
        }
    )

    print(f"原始資料形狀: {data.shape}")
    original_education_props = data["education"].value_counts(normalize=True)
    original_workclass_missing = data["workclass"].isna().mean()

    # 使用更新後的配置（移除 target_n_rows 和 date_name_map）
    config = {
        "field_proportions": [
            {"fields": "education", "mode": "all", "tolerance": 0.1},
            {"fields": "workclass", "mode": "missing", "tolerance": 0.05},
            {"fields": ["education", "income"], "mode": "all", "tolerance": 0.15},
        ]
    }

    constrainer = Constrainer(config)

    # 測試新的架構
    result = constrainer.apply(data, target_rows=60)

    # 驗證結果
    assert len(result) <= len(data)
    assert len(result) > 0

    # 檢查 education 分布是否維持
    result_education_props = result["education"].value_counts(normalize=True)
    for edu in original_education_props.index:
        if edu in result_education_props.index:
            prop_diff = abs(original_education_props[edu] - result_education_props[edu])
            assert prop_diff <= 0.2  # 允許一定的容差

    # 檢查 workclass 缺失率是否維持
    result_workclass_missing = result["workclass"].isna().mean()
    missing_diff = abs(original_workclass_missing - result_workclass_missing)
    assert missing_diff <= 0.1  # 允許一定的容差

    # 檢查欄位組合是否存在
    result_combos = result.groupby(["education", "income"]).size()
    assert len(result_combos) > 0


def test_field_proportions_multiple_modes():
    """Test field proportions with multiple constraint modes"""
    # 測試多種模式的組合
    data = pd.DataFrame(
        {
            "category": ["A"] * 50 + ["B"] * 30 + ["C"] * 20,
            "status": (["Active", None, "Inactive"] * 34)[:100],  # 確保長度為100
            "region": (["North", "South", "East", "West"] * 25)[:100],  # 確保長度為100
        }
    )

    config = {
        "field_proportions": [
            {"fields": "category", "mode": "all", "tolerance": 0.1},
            {"fields": "status", "mode": "missing", "tolerance": 0.05},
            {"fields": "region", "mode": "all", "tolerance": 0.15},
        ]
    }

    constrainer = Constrainer(config)
    result = constrainer.apply(data, target_rows=80)

    # 基本驗證
    assert len(result) <= len(data)
    assert len(result) > 0

    # 檢查各種模式都有效果
    if len(result) > 0:
        # Category proportions
        original_cat_props = data["category"].value_counts(normalize=True)
        result_cat_props = result["category"].value_counts(normalize=True)
        assert len(result_cat_props) > 0

        # Missing value proportions
        original_missing = data["status"].isna().mean()
        result_missing = result["status"].isna().mean()
        # 允許一定範圍的差異
        assert abs(original_missing - result_missing) <= 0.15

        # Region proportions
        result_region_props = result["region"].value_counts(normalize=True)
        assert len(result_region_props) > 0


def test_field_proportions_edge_cases_integration():
    """Test field proportions edge cases integration"""
    # 測試極端情況

    # Test 1: 非常小的資料集
    small_data = pd.DataFrame({"type": ["X", "Y", "X", "Y", "X"]})

    config_small = {
        "field_proportions": [{"fields": "type", "mode": "all", "tolerance": 0.2}]
    }

    constrainer_small = Constrainer(config_small)
    result_small = constrainer_small.apply(small_data, target_rows=3)
    assert len(result_small) <= len(small_data)

    # Test 2: 目標行數大於原始資料
    config_large = {
        "field_proportions": [{"fields": "type", "mode": "all", "tolerance": 0.1}]
    }

    constrainer_large = Constrainer(config_large)
    result_large = constrainer_large.apply(small_data, target_rows=100)
    # 應該返回所有可用資料
    assert len(result_large) == len(small_data)

    # Test 3: 空的 field_proportions 列表
    config_empty = {"field_proportions": []}

    constrainer_empty = Constrainer(config_empty)
    result_empty = constrainer_empty.apply(small_data, target_rows=3)
    # 應該返回原始資料（無約束）
    pd.testing.assert_frame_equal(result_empty, small_data)
