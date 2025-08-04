import unittest
from unittest.mock import patch

import pandas as pd

from petsard.evaluator.anonymeter import Anonymeter


class TestAnonymeter(unittest.TestCase):
    """Test for Anonymeter Evaluator."""

    def setUp(self):
        """Set up test fixtures."""
        # Test configuration
        self.config = {
            "eval_method": "anonymeter-singlingout",
            "n_attacks": 100,
            "n_cols": 2,
            "max_attempts": 1000,
            "mode": "multivariate",
        }

        # Create mock data with more rows to avoid sampling issues
        import numpy as np

        np.random.seed(42)  # For reproducible results

        n_rows = 200  # Enough rows for sampling
        self.data = {
            "ori": pd.DataFrame(
                {
                    "col1": np.random.randint(1, 100, n_rows),
                    "col2": np.random.choice(["a", "b", "c", "d", "e"], n_rows),
                    "col3": np.random.uniform(1.0, 10.0, n_rows),
                }
            ),
            "syn": pd.DataFrame(
                {
                    "col1": np.random.randint(1, 100, n_rows),
                    "col2": np.random.choice(["a", "b", "c", "d", "e"], n_rows),
                    "col3": np.random.uniform(1.0, 10.0, n_rows),
                }
            ),
            "control": pd.DataFrame(
                {
                    "col1": np.random.randint(100, 200, n_rows),
                    "col2": np.random.choice(["f", "g", "h", "i", "j"], n_rows),
                    "col3": np.random.uniform(10.0, 20.0, n_rows),
                }
            ),
        }

    @patch("anonymeter.evaluators.SinglingOutEvaluator")
    def test_init(self, mock_evaluator):
        """Test initialization."""
        evaluator = Anonymeter(config=self.config)
        self.assertEqual(evaluator.config, self.config)
        self.assertIsNone(evaluator._impl)

    def test_eval_singlingout(self):
        """Test eval method with SinglingOut."""
        # Use a smaller n_attacks to avoid sampling issues
        small_config = self.config.copy()
        small_config["n_attacks"] = 10
        small_config["max_attempts"] = 100

        # Execute evaluator
        evaluator = Anonymeter(config=small_config)
        result = evaluator.eval(self.data)

        # Assert results structure
        self.assertIn("global", result)
        self.assertIn("details", result)

        # Assert global results content
        global_data = result["global"]
        self.assertIsInstance(global_data, pd.DataFrame)
        result_dict = global_data.iloc[0].to_dict()
        self.assertIn("risk", result_dict)
        self.assertIn("risk_CI_btm", result_dict)
        self.assertIn("risk_CI_top", result_dict)
        self.assertIn("attack_rate", result_dict)

        # Check that risk is a valid number (not NaN)
        self.assertIsNotNone(result_dict["risk"])
        self.assertFalse(pd.isna(result_dict["risk"]))

    def test_eval_linkability(self):
        """Test eval method with Linkability."""
        # Setup config for linkability with smaller n_attacks
        linkability_config = {
            "eval_method": "anonymeter-linkability",
            "n_attacks": 10,  # Reduced to avoid sampling issues
            "n_neighbors": 5,
            "aux_cols": [["col1"], ["col3"]],
            "n_jobs": -1,
        }

        # Execute evaluator
        evaluator = Anonymeter(config=linkability_config)
        result = evaluator.eval(self.data)

        # Assert structure and content
        self.assertIn("global", result)
        self.assertIsInstance(result["global"], pd.DataFrame)

        # Check that risk is a valid number (not NaN)
        risk_value = result["global"].iloc[0]["risk"]
        self.assertIsNotNone(risk_value)
        self.assertFalse(pd.isna(risk_value))

    def test_invalid_method(self):
        """Test with invalid evaluation method."""
        with self.assertRaises(Exception):
            Anonymeter(config={"eval_method": "anonymeter-invalid"})


if __name__ == "__main__":
    unittest.main()
