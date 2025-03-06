import unittest
from unittest.mock import MagicMock, patch

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

        # Create mock data
        self.data = {
            "ori": pd.DataFrame(
                {
                    "col1": [1, 2, 3, 4, 5],
                    "col2": ["a", "b", "c", "d", "e"],
                    "col3": [1.1, 2.2, 3.3, 4.4, 5.5],
                }
            ),
            "syn": pd.DataFrame(
                {
                    "col1": [1, 2, 3, 4, 5],
                    "col2": ["a", "b", "c", "d", "e"],
                    "col3": [1.1, 2.2, 3.3, 4.4, 5.5],
                }
            ),
            "control": pd.DataFrame(
                {
                    "col1": [6, 7, 8, 9, 10],
                    "col2": ["f", "g", "h", "i", "j"],
                    "col3": [6.6, 7.7, 8.8, 9.9, 10.0],
                }
            ),
        }

    @patch("anonymeter.evaluators.SinglingOutEvaluator")
    def test_init(self, mock_evaluator):
        """Test initialization."""
        evaluator = Anonymeter(config=self.config)
        self.assertEqual(evaluator.config, self.config)
        self.assertIsNone(evaluator._impl)

    @patch("anonymeter.evaluators.SinglingOutEvaluator")
    def test_eval_singlingout(self, mock_singlingout):
        """Test eval method with SinglingOut."""
        # Setup mock returns
        mock_instance = MagicMock()
        mock_instance.risk.return_value.value = 0.5
        mock_instance.risk.return_value.ci = [0.4, 0.6]
        mock_instance.results.return_value.attack_rate.value = 0.3
        mock_instance.results.return_value.attack_rate.error = 0.1
        mock_instance.results.return_value.baseline_rate.value = 0.2
        mock_instance.results.return_value.baseline_rate.error = 0.05
        mock_instance.results.return_value.control_rate.value = 0.1
        mock_instance.results.return_value.control_rate.error = 0.02
        mock_singlingout.return_value = mock_instance

        # Execute evaluator
        evaluator = Anonymeter(config=self.config)
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
        self.assertEqual(result_dict["risk"], 0.5)  # Check specific value

    @patch("anonymeter.evaluators.LinkabilityEvaluator")
    def test_eval_linkability(self, mock_linkability):
        """Test eval method with Linkability."""
        # Setup config for linkability
        linkability_config = {
            "eval_method": "anonymeter-linkability",
            "n_attacks": 100,
            "n_neighbors": 5,
            "aux_cols": [["col1"], ["col3"]],
            "n_jobs": -1,
        }

        # Setup mock returns
        mock_instance = MagicMock()
        mock_instance.risk.return_value.value = 0.4
        mock_instance.risk.return_value.ci = [0.3, 0.5]
        mock_instance.results.return_value.attack_rate.value = 0.25
        mock_instance.results.return_value.attack_rate.error = 0.08
        mock_instance.results.return_value.baseline_rate.value = 0.15
        mock_instance.results.return_value.baseline_rate.error = 0.04
        mock_instance.results.return_value.control_rate.value = 0.1
        mock_instance.results.return_value.control_rate.error = 0.02
        mock_linkability.return_value = mock_instance

        # Execute evaluator
        evaluator = Anonymeter(config=linkability_config)
        result = evaluator.eval(self.data)

        # Assert structure and content
        self.assertIn("global", result)
        self.assertIsInstance(result["global"], pd.DataFrame)
        self.assertEqual(result["global"].iloc[0]["risk"], 0.4)

    def test_invalid_method(self):
        """Test with invalid evaluation method."""
        with self.assertRaises(Exception):
            Anonymeter(config={"eval_method": "anonymeter-invalid"})


if __name__ == "__main__":
    unittest.main()
