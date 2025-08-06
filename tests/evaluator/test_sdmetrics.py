import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from petsard.evaluator.sdmetrics import SDMetricsSingleTable
from petsard.exceptions import UnsupportedMethodError


class TestSDMetricsSingleTable(unittest.TestCase):
    """Test for SDMetrics Evaluator."""

    def setUp(self):
        """Set up test fixtures."""
        # Test configuration
        self.config = {"eval_method": "sdmetrics-qualityreport"}

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
        evaluator = SDMetricsSingleTable(config=self.config)
        self.assertEqual(evaluator.config, self.config)
        # Verify evaluator is properly initialized
        self.assertIsNotNone(evaluator._impl)

    @patch("sdmetrics.reports.single_table.QualityReport")
    def test_eval_quality_report(self, mock_report):
        """Test eval method with QualityReport."""
        # Setup mock returns
        mock_instance = MagicMock()
        mock_instance.get_score.return_value = 0.8

        properties_df = pd.DataFrame(
            {
                "Property": ["Score", "Column Shapes", "Column Pair Trends"],
                "Score": [0.8, 0.75, 0.85],
            }
        )
        mock_instance.get_properties.return_value = properties_df

        column_shapes_df = pd.DataFrame(
            {
                "Column": ["col1", "col2", "col3"],
                "Metric": ["KSTest", "TVComplement", "KSTest"],
                "Score": [0.7, 0.8, 0.75],
            }
        )

        column_pair_df = pd.DataFrame(
            {
                "Column 1": ["col1", "col1", "col2"],
                "Column 2": ["col2", "col3", "col3"],
                "Metric": ["CorrSimilarity", "CorrSimilarity", "CorrSimilarity"],
                "Score": [0.9, 0.85, 0.8],
            }
        )

        # Mock get_details to return different DataFrames based on property_name
        def mock_get_details(property_name):
            if property_name == "Column Shapes":
                return column_shapes_df
            elif property_name == "Column Pair Trends":
                return column_pair_df
            return pd.DataFrame()

        mock_instance.get_details = mock_get_details
        mock_report.return_value = mock_instance

        # Execute evaluator
        evaluator = SDMetricsSingleTable(config=self.config)
        result = evaluator.eval(self.data)

        # Assert results structure
        self.assertIn("global", result)
        self.assertIn("columnwise", result)
        self.assertIn("pairwise", result)

        # Assert global results content
        global_data = result["global"]
        self.assertIsInstance(global_data, pd.DataFrame)
        # Score improved due to dtype consistency fix
        self.assertAlmostEqual(
            global_data.iloc[0]["Score"], 1.0, places=2
        )  # Check overall score

    @patch("sdmetrics.reports.single_table.DiagnosticReport")
    def test_eval_diagnostic_report(self, mock_report):
        """Test eval method with DiagnosticReport."""
        # Setup config for diagnostic report
        diagnostic_config = {"eval_method": "sdmetrics-diagnosticreport"}

        # Setup mock returns
        mock_instance = MagicMock()
        mock_instance.get_score.return_value = 0.9

        properties_df = pd.DataFrame(
            {
                "Property": ["Score", "Data Validity", "Data Structure"],
                "Score": [0.9, 0.85, 0.95],
            }
        )
        mock_instance.get_properties.return_value = properties_df

        data_validity_df = pd.DataFrame(
            {
                "Column": ["col1", "col2", "col3"],
                "Metric": ["KeyUniqueness", "CategoryAdherence", "BoundaryAdherence"],
                "Score": [1.0, 0.9, 0.95],
            }
        )

        def mock_get_details(property_name):
            if property_name == "Data Validity":
                return data_validity_df
            return pd.DataFrame()

        mock_instance.get_details = mock_get_details
        mock_report.return_value = mock_instance

        # Execute evaluator with diagnostic config
        evaluator = SDMetricsSingleTable(config=diagnostic_config)
        result = evaluator.eval(self.data)

        # Assert structure and content
        self.assertIn("global", result)
        self.assertIsInstance(result["global"], pd.DataFrame)
        self.assertEqual(result["global"].iloc[0]["Score"], 1.0)

    def test_invalid_method(self):
        """Test with invalid evaluation method."""
        with self.assertRaises(UnsupportedMethodError):
            SDMetricsSingleTable(config={"eval_method": "sdmetrics-invalid"})


if __name__ == "__main__":
    unittest.main()
