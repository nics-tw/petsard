"""
Functional tests for PETsARD end-to-end workflows.

These tests verify that PETsARD can successfully execute complete workflows
using the same YAML configurations as the demo examples, ensuring that
the overall system functionality works as expected.
"""

import os
import tempfile

import pandas as pd
import pytest

from petsard.executor import Executor


class TestPETsARDFunctionalWorkflows:
    """Test complete PETsARD workflows using demo YAML configurations."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary directory for test outputs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    def _extract_module_data(self, result, module_name):
        """
        Extract data for a specific module from the nested result structure.

        Args:
            result: The executor result dictionary
            module_name: Name of the module to extract (e.g., 'Loader', 'Postprocessor')

        Returns:
            The data for the specified module, or None if not found
        """
        # Look for workflow keys that contain the module name
        for workflow_key, workflow_data in result.items():
            if module_name in workflow_key and isinstance(workflow_data, dict):
                # Look for the actual module data within the workflow
                for data_key, data_value in workflow_data.items():
                    if module_name in data_key:
                        return data_value
        return None

    def test_default_synthesis_workflow(self, temp_output_dir):
        """Test the default synthesis workflow (demo/tutorial/default-synthesis.yaml)."""
        # Create a minimal YAML config for default synthesis
        config_content = f"""---
Loader:
  data:
    filepath: 'benchmark://adult-income'
Preprocessor:
  demo:
    method: 'default'
Synthesizer:
  demo:
    method: 'default'
Postprocessor:
  demo:
    method: 'default'
Reporter:
  output:
    method: 'save_data'
    source: 'Postprocessor'
    output_dir: '{temp_output_dir}'
...
"""

        # Write config to temporary file
        config_path = os.path.join(temp_output_dir, "test_config.yaml")
        with open(config_path, "w") as f:
            f.write(config_content)

        # Execute the workflow
        executor = Executor(config_path)

        # Note: executor.run() returns None in current version
        # In v2.0.0, this will return success/failed status codes
        executor.run()

        # Check execution completion using new method
        assert executor.is_execution_completed(), (
            "Execution should be completed after run()"
        )

        # Get results using the correct API
        result = executor.get_result()

        # Verify execution completed successfully
        assert result is not None

        # Verify synthetic data was generated
        synthetic_data = self._extract_module_data(result, "Postprocessor")
        assert synthetic_data is not None, "Postprocessor data not found in result"
        assert isinstance(synthetic_data, pd.DataFrame)
        assert len(synthetic_data) > 0

        # Verify data has expected structure (adult-income dataset columns)
        expected_columns = [
            "age",
            "workclass",
            "fnlwgt",
            "education",
            "educational-num",
            "marital-status",
            "occupation",
            "relationship",
            "race",
            "gender",
            "capital-gain",
            "capital-loss",
            "hours-per-week",
            "native-country",
            "income",
        ]
        for col in expected_columns:
            assert col in synthetic_data.columns, f"Missing expected column: {col}"

    def test_data_preprocessing_workflow(self, temp_output_dir):
        """Test data preprocessing workflow with missing value handling."""
        config_content = f"""---
Loader:
  data:
    filepath: 'benchmark://adult-income'
    na_values: '?'
Preprocessor:
  missing-only:
    sequence:
      - 'missing'
      - 'encoder'
Synthesizer:
  demo:
    method: 'default'
Postprocessor:
  demo:
    method: 'default'
Reporter:
  output:
    method: 'save_data'
    source: 'Synthesizer'
    output_dir: '{temp_output_dir}'
...
"""

        config_path = os.path.join(temp_output_dir, "test_preprocessing_config.yaml")
        with open(config_path, "w") as f:
            f.write(config_content)

        executor = Executor(config_path)

        # Note: executor.run() returns None in current version
        # In v2.0.0, this will return success/failed status codes
        executor.run()

        # Check execution completion using new method
        assert executor.is_execution_completed(), (
            "Execution should be completed after run()"
        )

        # Get results using the correct API
        result = executor.get_result()

        # Verify execution completed successfully
        assert result is not None

        synthetic_data = self._extract_module_data(result, "Synthesizer")
        assert synthetic_data is not None, "Synthesizer data not found in result"
        assert isinstance(synthetic_data, pd.DataFrame)
        assert len(synthetic_data) > 0

    def test_data_constraining_workflow(self, temp_output_dir):
        """Test data constraining workflow with various constraint types."""
        config_content = f"""---
Loader:
  data:
    filepath: 'benchmark://adult-income'
Preprocessor:
  demo:
    method: 'default'
Synthesizer:
  demo:
    method: 'default'
Postprocessor:
  demo:
    method: 'default'
Constrainer:
  demo:
    field_constraints:
      - "age >= 18 & age <= 65"
      - "hours-per-week >= 20 & hours-per-week <= 60"
    field_proportions:
      - fields: 'education'
        mode: 'all'
        tolerance: 0.1
Reporter:
  output:
    method: 'save_data'
    source: 'Constrainer'
    output_dir: '{temp_output_dir}'
...
"""

        config_path = os.path.join(temp_output_dir, "test_constraining_config.yaml")
        with open(config_path, "w") as f:
            f.write(config_content)

        executor = Executor(config_path)

        # Note: executor.run() returns None in current version
        # In v2.0.0, this will return success/failed status codes
        executor.run()

        # Check execution completion using new method
        assert executor.is_execution_completed(), (
            "Execution should be completed after run()"
        )

        # Get results using the correct API
        result = executor.get_result()

        # Verify execution completed successfully
        assert result is not None

        constrained_data = self._extract_module_data(result, "Constrainer")
        assert constrained_data is not None, "Constrainer data not found in result"
        assert isinstance(constrained_data, pd.DataFrame)
        assert len(constrained_data) > 0

        # Verify constraints were applied
        if "age" in constrained_data.columns:
            age_data = constrained_data["age"].dropna()
            if len(age_data) > 0:
                assert age_data.min() >= 18, (
                    "Age constraint violation: minimum age < 18"
                )
                assert age_data.max() <= 65, (
                    "Age constraint violation: maximum age > 65"
                )

        if "hours-per-week" in constrained_data.columns:
            hours_data = constrained_data["hours-per-week"].dropna()
            if len(hours_data) > 0:
                assert hours_data.min() >= 20, (
                    "Hours constraint violation: minimum hours < 20"
                )
                assert hours_data.max() <= 60, (
                    "Hours constraint violation: maximum hours > 60"
                )

    def test_evaluation_workflow(self, temp_output_dir):
        """Test workflow with evaluation components."""
        config_content = f"""---
Loader:
  data:
    filepath: 'benchmark://adult-income'
Splitter:
  demo:
    num_samples: 1
    train_split_ratio: 0.8
Preprocessor:
  demo:
    method: 'default'
Synthesizer:
  demo:
    method: 'default'
Postprocessor:
  demo:
    method: 'default'
Evaluator:
  demo-quality:
    method: 'sdmetrics-qualityreport'
Reporter:
  save_report_global:
    method: 'save_report'
    granularity: 'global'
    output_dir: '{temp_output_dir}'
...
"""

        config_path = os.path.join(temp_output_dir, "test_evaluation_config.yaml")
        with open(config_path, "w") as f:
            f.write(config_content)

        executor = Executor(config_path)

        # Note: executor.run() returns None in current version
        # In v2.0.0, this will return success/failed status codes
        executor.run()

        # Check execution completion using new method
        assert executor.is_execution_completed(), (
            "Execution should be completed after run()"
        )

        # Get results using the correct API
        result = executor.get_result()

        # Verify execution completed successfully
        assert result is not None

        # Verify evaluation results exist
        timing_result = executor.get_timing()
        assert timing_result is not None
        assert isinstance(timing_result, pd.DataFrame)

    def test_minimal_workflow(self, temp_output_dir):
        """Test minimal workflow with just loader and reporter."""
        config_content = f"""---
Loader:
  data:
    filepath: 'benchmark://adult-income'
Reporter:
  output:
    method: 'save_data'
    source: 'Loader'
    output_dir: '{temp_output_dir}'
...
"""

        config_path = os.path.join(temp_output_dir, "test_minimal_config.yaml")
        with open(config_path, "w") as f:
            f.write(config_content)

        executor = Executor(config_path)

        # Note: executor.run() returns None in current version
        # In v2.0.0, this will return success/failed status codes
        executor.run()

        # Check execution completion using new method
        assert executor.is_execution_completed(), (
            "Execution should be completed after run()"
        )

        # Get results using the correct API
        result = executor.get_result()

        # Verify execution completed successfully
        assert result is not None

        loaded_data = self._extract_module_data(result, "Loader")
        assert loaded_data is not None, "Loader data not found in result"
        assert isinstance(loaded_data, pd.DataFrame)
        assert len(loaded_data) > 0

    def test_custom_sequence_preprocessing(self, temp_output_dir):
        """Test custom preprocessing sequence."""
        config_content = f"""---
Loader:
  data:
    filepath: 'benchmark://adult-income'
Preprocessor:
  custom-sequence:
    sequence:
      - 'missing'
      - 'outlier'
      - 'scaler'
      - 'encoder'
Synthesizer:
  demo:
    method: 'default'
Postprocessor:
  demo:
    method: 'default'
Reporter:
  output:
    method: 'save_data'
    source: 'Postprocessor'
    output_dir: '{temp_output_dir}'
...
"""

        config_path = os.path.join(temp_output_dir, "test_custom_sequence_config.yaml")
        with open(config_path, "w") as f:
            f.write(config_content)

        executor = Executor(config_path)

        # Note: executor.run() returns None in current version
        # In v2.0.0, this will return success/failed status codes
        executor.run()

        # Check execution completion using new method
        assert executor.is_execution_completed(), (
            "Execution should be completed after run()"
        )

        # Get results using the correct API
        result = executor.get_result()

        # Verify execution completed successfully
        assert result is not None

        processed_data = self._extract_module_data(result, "Postprocessor")
        assert processed_data is not None, "Postprocessor data not found in result"
        assert isinstance(processed_data, pd.DataFrame)
        assert len(processed_data) > 0

    @pytest.mark.parametrize(
        "config_name,expected_modules",
        [
            (
                "default-synthesis",
                ["Loader", "Preprocessor", "Synthesizer", "Postprocessor"],
            ),
            ("minimal", ["Loader"]),
            (
                "with-splitter",
                ["Loader", "Splitter", "Preprocessor", "Synthesizer", "Postprocessor"],
            ),
        ],
    )
    def test_workflow_module_execution(
        self, temp_output_dir, config_name, expected_modules
    ):
        """Test that workflows execute expected modules."""
        if config_name == "default-synthesis":
            config_content = f"""---
Loader:
  data:
    filepath: 'benchmark://adult-income'
Preprocessor:
  demo:
    method: 'default'
Synthesizer:
  demo:
    method: 'default'
Postprocessor:
  demo:
    method: 'default'
Reporter:
  output:
    method: 'save_data'
    source: 'Postprocessor'
    output_dir: '{temp_output_dir}'
...
"""
        elif config_name == "minimal":
            config_content = f"""---
Loader:
  data:
    filepath: 'benchmark://adult-income'
Reporter:
  output:
    method: 'save_data'
    source: 'Loader'
    output_dir: '{temp_output_dir}'
...
"""
        elif config_name == "with-splitter":
            config_content = f"""---
Loader:
  data:
    filepath: 'benchmark://adult-income'
Splitter:
  demo:
    num_samples: 1
    train_split_ratio: 0.8
Preprocessor:
  demo:
    method: 'default'
Synthesizer:
  demo:
    method: 'default'
Postprocessor:
  demo:
    method: 'default'
Reporter:
  output:
    method: 'save_data'
    source: 'Postprocessor'
    output_dir: '{temp_output_dir}'
...
"""

        config_path = os.path.join(temp_output_dir, f"test_{config_name}_config.yaml")
        with open(config_path, "w") as f:
            f.write(config_content)

        executor = Executor(config_path)

        # Note: executor.run() returns None in current version
        # In v2.0.0, this will return success/failed status codes
        executor.run()

        # Check execution completion using new method
        assert executor.is_execution_completed(), (
            "Execution should be completed after run()"
        )

        # Get results using the correct API
        result = executor.get_result()

        # Verify execution completed successfully
        assert result is not None

        # Verify expected modules were executed
        for module in expected_modules:
            module_data = self._extract_module_data(result, module)
            assert module_data is not None, (
                f"Expected module {module} not found in results"
            )


class TestPETsARDConfigurationValidation:
    """Test configuration validation and error handling."""

    def test_invalid_yaml_config(self, tmp_path):
        """Test handling of invalid YAML configuration."""
        config_content = """---
Loader:
  data:
    filepath: 'benchmark://adult-income'
InvalidModule:
  invalid_config: true
...
"""

        config_path = tmp_path / "invalid_config.yaml"
        config_path.write_text(config_content)

        # Should handle invalid configuration gracefully
        with pytest.raises((NameError, ValueError, KeyError, AttributeError)):
            executor = Executor(str(config_path))
            # Note: executor.run() returns None in current version
            # In v2.0.0, this will return success/failed status codes
            executor.run()

    def test_missing_required_config(self, tmp_path):
        """Test handling of missing required configuration."""
        config_content = """---
# Empty configuration - should fail
...
"""

        config_path = tmp_path / "missing_config.yaml"
        config_path.write_text(config_content)

        # Should handle missing required configuration
        with pytest.raises((ValueError, KeyError, AttributeError, TypeError)):
            executor = Executor(str(config_path))
            # Note: executor.run() returns None in current version
            # In v2.0.0, this will return success/failed status codes
            executor.run()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
