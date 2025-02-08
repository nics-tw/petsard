import random
import warnings
from typing import Dict

import numpy as np
import pandas as pd
import pytest

from petsard.evaluator.mlutlity import MLUtility


@pytest.fixture
def sample_evaluator_input():
    """Fixture to create sample data for evaluator testing.

    Returns:
        A function that creates sample data with specified parameters.
    """

    def _data_creator(n: int = 100) -> pd.DataFrame:
        """Create a sample DataFrame with numeric features and categorical target.

        Args:
            n: Number of samples to generate

        Returns:
            DataFrame with both features and target columns
        """
        # Create base numeric features
        data = pd.DataFrame(
            data={
                "x_cont_normal": np.random.rand(n),
                "x_cont_uniform": np.random.uniform(size=n),
                "x_num_same": np.ones(n),
                "x_int_low_card": np.random.randint(0, 2, size=n),
                "x_int_high_card": np.random.randint(0, 15, size=n),
            }
        )

        # Add categorical target column
        categories = [f"value{i}" for i in range(3)]
        values = [random.choice(categories) for _ in range(n)]
        data["unmatch_discr"] = pd.Categorical(values, categories=categories)

        return data

    def _sample_evaluator_input(
        case: Dict[str, int] = None,
    ) -> dict:
        """Create evaluation datasets based on test case.

        Args:
            case: Dictionary specifying test case parameters

        Returns:
            Dictionary containing original, synthetic and control datasets
        """
        default_case: Dict[str, int] = {
            "ori": 100,
            "syn": 100,
            "control": 100,
        }
        if case is not None:
            default_case.update(case)
        case = default_case

        # Create base datasets
        data: dict = {}
        for key, n in case.items():
            if key != "testcase":
                data[key] = _data_creator(n).copy()

        # Handle special test cases for classification
        if "testcase" in case:
            if case["testcase"] in [
                "only_1_level_y_in_ori",
                "only_1_level_y_in_syn",
                "only_1_level_y_both_ori_syn",
            ]:
                same: str = "value0"  # Value for constant target
                categories = [f"value{i}" for i in range(3)]
                non_same_values = [random.choice(categories) for _ in range(100)]

                def make_cat_series(values, is_single=False):
                    """Create a categorical series with proper categories"""
                    if is_single:
                        categories = [same]
                    else:
                        categories = [f"value{i}" for i in range(3)]
                    return pd.Categorical(values, categories=categories)

                # Control group always uses multiple values
                data["control"]["unmatch_discr"] = make_cat_series(non_same_values)

                # Set target values based on test case
                if case["testcase"] == "only_1_level_y_in_ori":
                    data["ori"]["unmatch_discr"] = make_cat_series([same] * 100, True)
                    data["syn"]["unmatch_discr"] = make_cat_series(non_same_values)
                elif case["testcase"] == "only_1_level_y_in_syn":
                    data["ori"]["unmatch_discr"] = make_cat_series(non_same_values)
                    data["syn"]["unmatch_discr"] = make_cat_series([same] * 100, True)
                elif case["testcase"] == "only_1_level_y_both_ori_syn":
                    data["ori"]["unmatch_discr"] = make_cat_series([same] * 100, True)
                    data["syn"]["unmatch_discr"] = make_cat_series([same] * 100, True)

        return data

    return _sample_evaluator_input


class Test_MLUtility:
    """Test suite for MLUtility class"""

    def test_classification_of_single_value(self, sample_evaluator_input):
        """Test classification behavior with single-value targets.

        Test cases:
        1. Only original data has single level target
        2. Only synthetic data has single level target
        3. Both original and synthetic data have single level target

        Expected behavior:
        - Warning about constant target should be issued
        - Scores should be NaN for datasets with constant target
        - Valid scores for datasets with multiple classes
        """
        warnings.simplefilter("ignore", UserWarning)

        for testcase in [
            "only_1_level_y_in_ori",
            "only_1_level_y_in_syn",
            "only_1_level_y_both_ori_syn",
        ]:
            eval = MLUtility(
                config={
                    "method": "mlutility-classification",
                    "target": "unmatch_discr",
                }
            )
            eval.create(data=sample_evaluator_input(case={"testcase": testcase}))
            eval.eval()
            result = eval.get_global()

            # Validate results based on test case
            if testcase in ["only_1_level_y_in_ori", "only_1_level_y_both_ori_syn"]:
                assert pd.isna(result.loc[0, "ori_mean"])
                assert pd.isna(result.loc[0, "ori_std"])
            else:
                assert result.loc[0, "ori_mean"] >= 0.0
                assert result.loc[0, "ori_std"] >= 0.0

            if testcase in ["only_1_level_y_in_syn", "only_1_level_y_both_ori_syn"]:
                assert pd.isna(result.loc[0, "syn_mean"])
                assert pd.isna(result.loc[0, "syn_std"])
            else:
                assert result.loc[0, "syn_mean"] >= 0.0
                assert result.loc[0, "syn_std"] >= 0.0

            if testcase == "only_1_level_y_both_ori_syn":
                assert pd.isna(result.loc[0, "diff"])

    def test_classification_normal_case(self, sample_evaluator_input):
        """Test classification with normal multi-class data.

        Expected behavior:
        - All scores should be valid (non-NaN)
        - Scores should be in valid range [0, 1]
        """
        eval = MLUtility(
            config={
                "method": "mlutility-classification",
                "target": "unmatch_discr",
            }
        )
        eval.create(data=sample_evaluator_input())
        eval.eval()
        result = eval.get_global()

        # Verify all metrics are valid
        assert result.loc[0, "ori_mean"] >= 0.0
        assert result.loc[0, "ori_std"] >= 0.0
        assert result.loc[0, "syn_mean"] >= 0.0
        assert result.loc[0, "syn_std"] >= 0.0
        assert not pd.isna(result.loc[0, "diff"])

    def test_classification_empty_data(self, sample_evaluator_input):
        """Test classification with empty data after preprocessing.

        Expected behavior:
        - All metrics should be NaN
        - Warning about empty data should be issued
        """
        data = sample_evaluator_input()

        # Set NaN values respecting column dtypes
        for col in data["ori"].columns:
            if pd.api.types.is_numeric_dtype(data["ori"][col].dtype):
                data["ori"][col] = pd.Series([np.nan] * len(data["ori"]), dtype=float)
            else:
                data["ori"][col] = pd.Series([None] * len(data["ori"]), dtype=object)

        eval = MLUtility(
            config={
                "method": "mlutility-classification",
                "target": "unmatch_discr",
            }
        )
        eval.create(data=data)
        eval.eval()
        result = eval.get_global()

        # Check if all metrics are NaN
        assert pd.isna(result.loc[0, "ori_mean"])
        assert pd.isna(result.loc[0, "ori_std"])
        assert pd.isna(result.loc[0, "syn_mean"])
        assert pd.isna(result.loc[0, "syn_std"])
        assert pd.isna(result.loc[0, "diff"])
