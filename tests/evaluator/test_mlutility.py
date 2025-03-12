import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from petsard.evaluator.mlutlity import MLUtility, MLUtilityConfig


class TestMLUtility(unittest.TestCase):
    """Test for MLUtility Evaluator."""

    def setUp(self):
        """Set up test fixtures."""
        # Test configuration for classification
        self.config_classification = {
            "eval_method": "mlutility-classification",
            "target": "target",
        }

        # Test configuration for regression
        self.config_regression = {
            "eval_method": "mlutility-regression",
            "target": "target",
        }

        # Test configuration for clustering
        self.config_cluster = {"eval_method": "mlutility-cluster", "n_clusters": [2, 3]}

        # Create mock data
        np.random.seed(42)  # For reproducibility
        n_samples = 100

        # Features
        X = pd.DataFrame(
            {
                "feature1": np.random.randn(n_samples),
                "feature2": np.random.randn(n_samples),
                "category": np.random.choice(["A", "B", "C"], size=n_samples),
            }
        )

        # Target for classification/regression
        y_class = np.random.choice([0, 1], size=n_samples)
        y_reg = np.random.randn(n_samples)

        # Create dataframes
        self.data_classification = {
            "ori": X.copy().assign(target=y_class),
            "syn": X.copy().assign(target=y_class),
            "control": X.copy().assign(target=y_class),
        }

        self.data_regression = {
            "ori": X.copy().assign(target=y_reg),
            "syn": X.copy().assign(target=y_reg),
            "control": X.copy().assign(target=y_reg),
        }

        self.data_cluster = {"ori": X.copy(), "syn": X.copy(), "control": X.copy()}

    def test_init(self):
        """Test initialization."""
        # Test classification
        evaluator = MLUtility(config=self.config_classification)
        self.assertEqual(evaluator.config, self.config_classification)
        self.assertIsNone(evaluator._impl)
        self.assertIsInstance(evaluator.mlutility_config, MLUtilityConfig)

        # Test regression
        evaluator = MLUtility(config=self.config_regression)
        self.assertEqual(evaluator.config, self.config_regression)

        # Test clustering
        evaluator = MLUtility(config=self.config_cluster)
        self.assertEqual(evaluator.config, self.config_cluster)

    @patch.object(MLUtility, "_classification")
    def test_eval_classification(self, mock_classification):
        """Test eval method with classification."""
        # Setup mock returns
        mock_classification.return_value = {
            "logistic_regression": 0.85,
            "svc": 0.82,
            "random_forest": 0.88,
            "gradient_boosting": 0.87,
        }

        # Execute evaluator
        evaluator = MLUtility(config=self.config_classification)
        result = evaluator.eval(self.data_classification)

        # Assert results structure
        self.assertIn("global", result)
        self.assertIn("details", result)

        # Assert global results content
        global_data = result["global"]
        self.assertIsInstance(global_data, pd.DataFrame)

        # Check expected columns
        expected_cols = ["ori_mean", "ori_std", "syn_mean", "syn_std", "diff"]
        for col in expected_cols:
            self.assertIn(col, global_data.columns)

        # Assert details results content
        details = result["details"]
        self.assertIn("ori", details)
        self.assertIn("syn", details)

    @patch.object(MLUtility, "_regression")
    def test_eval_regression(self, mock_regression):
        """Test eval method with regression."""
        # Setup mock returns
        mock_regression.return_value = {
            "linear_regression": 0.75,
            "random_forest": 0.82,
            "gradient_boosting": 0.80,
        }

        # Execute evaluator
        evaluator = MLUtility(config=self.config_regression)
        result = evaluator.eval(self.data_regression)

        # Assert structure and check similar aspects
        self.assertIn("global", result)
        self.assertIn("details", result)
        self.assertIsInstance(result["global"], pd.DataFrame)

    @patch.object(MLUtility, "_cluster")
    def test_eval_cluster(self, mock_cluster):
        """Test eval method with clustering."""
        # Setup mock returns
        mock_cluster.return_value = {"KMeans_cluster2": 0.65, "KMeans_cluster3": 0.70}

        # Execute evaluator
        evaluator = MLUtility(config=self.config_cluster)
        result = evaluator.eval(self.data_cluster)

        # Assert structure and check similar aspects
        self.assertIn("global", result)
        self.assertIn("details", result)
        self.assertIsInstance(result["global"], pd.DataFrame)

    def test_preprocessing(self):
        """Test the preprocessing functionality."""
        # Simple mock to avoid running actual models but test preprocessing
        with patch.object(MLUtility, "_classification", return_value={}):
            evaluator = MLUtility(config=self.config_classification)

            # We don't need to mock the whole preprocessing, just observe if it runs
            # without errors and returns the expected structure
            result = evaluator.eval(self.data_classification)

            # Basic structure checks
            self.assertIn("global", result)
            self.assertIn("details", result)

    def test_invalid_method(self):
        """Test with invalid evaluation method."""
        with self.assertRaises(Exception):
            MLUtility(config={"eval_method": "mlutility-invalid"})

    def test_missing_target(self):
        """Test regression/classification without target."""
        with self.assertRaises(Exception):
            # Classification requires target
            MLUtility(config={"eval_method": "mlutility-classification"})

        with self.assertRaises(Exception):
            # Regression requires target
            MLUtility(config={"eval_method": "mlutility-regression"})


if __name__ == "__main__":
    unittest.main()
