import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from petsard.evaluator.customer_evaluator import CustomEvaluator


class TestCustomEvaluator(unittest.TestCase):
    """Test for Custom Evaluator."""

    def setUp(self):
        """Set up test fixtures."""
        # Test configuration
        self.config = {
            "eval_method": "custom_method",
            "module_path": "/path/to/custom_module.py",
            "class_name": "MyCustomEvaluator",
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

    @patch("petsard.util.load_external_module")
    def test_init(self, mock_load_module):
        """Test initialization."""
        # Create mock custom evaluator class
        mock_evaluator_class = MagicMock()
        mock_evaluator_class.REQUIRED_INPUT_KEYS = ["ori", "syn"]
        mock_evaluator_class.AVAILABLE_SCORES_GRANULARITY = ["global"]

        # Setup mock return for the load_external_module
        mock_load_module.return_value = (None, mock_evaluator_class)

        # Initialize the CustomEvaluator
        evaluator = CustomEvaluator(config=self.config)

        # Verify load_external_module was called with correct arguments
        mock_load_module.assert_called_once_with(
            module_path="/path/to/custom_module.py",
            class_name="MyCustomEvaluator",
            logger=evaluator._logger,
            required_methods=CustomEvaluator.REQUIRED_METHODS,
        )

        # Verify properties were set correctly
        self.assertEqual(evaluator.config, self.config)
        self.assertEqual(evaluator.REQUIRED_INPUT_KEYS, ["ori", "syn"])
        self.assertEqual(evaluator.AVAILABLE_SCORES_GRANULARITY, ["global"])

        # Verify the mock custom evaluator class was instantiated
        mock_evaluator_class.assert_called_once_with(config=self.config)

    @patch("petsard.util.load_external_module")
    def test_eval(self, mock_load_module):
        """Test eval method."""
        # Create mock custom evaluator instance
        mock_evaluator_instance = MagicMock()
        expected_result = {
            "global": pd.DataFrame({"score": [0.85]}),
            "details": {"metric1": 0.8, "metric2": 0.9},
        }
        mock_evaluator_instance.eval.return_value = expected_result

        # Create mock custom evaluator class
        mock_evaluator_class = MagicMock(return_value=mock_evaluator_instance)
        mock_evaluator_class.REQUIRED_INPUT_KEYS = ["ori", "syn"]
        mock_evaluator_class.AVAILABLE_SCORES_GRANULARITY = ["global", "details"]

        # Setup mock return
        mock_load_module.return_value = (None, mock_evaluator_class)

        # Initialize and evaluate
        evaluator = CustomEvaluator(config=self.config)
        result = evaluator._eval(self.data)

        # Verify the eval method was called on the custom evaluator
        mock_evaluator_instance.eval.assert_called_once_with(data=self.data)

        # Verify the results match
        self.assertEqual(result, expected_result)

    def test_missing_module_path(self):
        """Test initialization with missing module_path."""
        invalid_config = self
