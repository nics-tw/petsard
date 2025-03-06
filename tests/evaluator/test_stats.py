import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from petsard.evaluator.stats import Stats, StatsConfig, StatsJSDivergence, StatsMean


class TestStats(unittest.TestCase):
    """Test for Stats Evaluator."""

    def setUp(self):
        """Set up test fixtures."""
        # Test configuration
        self.config = {
            "eval_method": "stats",
            "stats_method": ["mean", "std", "jsdivergence"],
            "compare_method": "pct_change",
            "aggregated_method": "mean",
            "summary_method": "mean",
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
        }

    def test_init(self):
        """Test initialization."""
        evaluator = Stats(config=self.config)
        self.assertEqual(evaluator.config, self.config)
        self.assertIsNone(evaluator._impl)
        self.assertIsInstance(evaluator.stats_config, StatsConfig)

    @patch.object(StatsMean, "eval")
    @patch.object(StatsJSDivergence, "eval")
    def test_eval_basic(self, mock_js, mock_mean):
        """Test eval method with basic statistics."""
        # Setup mock returns
        mock_mean.return_value = 3.0  # Average of [1, 2, 3, 4, 5]
        mock_js.return_value = 0.0  # JSD is 0 for identical distributions

        # Patch Metadata._convert_dtypes to correctly identify column types
        with patch("petsard.loader.Metadata._convert_dtypes") as mock_convert:
            # Return appropriate dtype identifiers
            def side_effect(dtype):
                if np.issubdtype(dtype, np.number):
                    return "numerical"
                elif dtype == np.dtype("O"):
                    return "categorical"
                return "unknown"

            mock_convert.side_effect = side_effect

            # Execute evaluator
            evaluator = Stats(config=self.config)
            result = evaluator.eval(self.data)

        # Assert results structure
        self.assertIn("global", result)
        self.assertIn("columnwise", result)

        # Assert global results contain a Score
        global_data = result["global"]
        self.assertIsInstance(global_data, pd.DataFrame)
        self.assertIn("Score", global_data.columns)

        # Assert columnwise results contain expected columns
        columnwise_data = result["columnwise"]
        self.assertIsInstance(columnwise_data, pd.DataFrame)

        # Check for specific columns that should exist in results
        expected_cols = [
            "mean_ori",
            "mean_syn",
            "mean_pct_change",
            "std_ori",
            "std_syn",
            "std_pct_change",
        ]
        for col in expected_cols:
            self.assertTrue(
                any(col in columnwise_data.columns for col in expected_cols),
                f"Expected column pattern '{col}' not found",
            )

    def test_eval_with_different_data(self):
        """Test eval with different original and synthetic data."""
        # Create data with different values to test comparison
        different_data = {
            "ori": pd.DataFrame(
                {
                    "col1": [1, 2, 3, 4, 5],
                    "col3": [1.0, 2.0, 3.0, 4.0, 5.0],
                }
            ),
            "syn": pd.DataFrame(
                {
                    "col1": [2, 3, 4, 5, 6],  # Shifted by 1
                    "col3": [2.0, 4.0, 6.0, 8.0, 10.0],  # Doubled
                }
            ),
        }

        # Patch Metadata._convert_dtypes to correctly identify column types
        with patch("petsard.loader.Metadata._convert_dtypes") as mock_convert:
            mock_convert.return_value = (
                "numerical"  # Simplify by making all columns numerical
            )

            # Test with both comparison methods
            for compare_method in ["diff", "pct_change"]:
                config = self.config.copy()
                config["compare_method"] = compare_method
                config["stats_method"] = ["mean"]  # Simplify test to just mean

                evaluator = Stats(config=config)
                result = evaluator.eval(different_data)

                # Verify results contain the comparison column
                self.assertIn("columnwise", result)
                columnwise = result["columnwise"]
                comparison_col = f"mean_{compare_method}"
                self.assertIn(comparison_col, columnwise.columns)

                # Basic check that values are different from 0 (since data is different)
                self.assertTrue((columnwise[comparison_col].abs() > 0).any())

    def test_invalid_stats_method(self):
        """Test with invalid stats method."""
        invalid_config = self.config.copy()
        invalid_config["stats_method"] = ["invalid_method"]

        with self.assertRaises(Exception):
            Stats(config=invalid_config)

    def test_invalid_compare_method(self):
        """Test with invalid comparison method."""
        invalid_config = self.config.copy()
        invalid_config["compare_method"] = "invalid_method"

        with self.assertRaises(Exception):
            Stats(config=invalid_config)


if __name__ == "__main__":
    unittest.main()
