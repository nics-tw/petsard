import tempfile
from pathlib import Path

import pytest

from petsard.exceptions import ConfigError
from petsard.executor import Executor, ExecutorConfig


class TestExecutorConfig:
    """Test suite for ExecutorConfig functionality."""

    def test_default_values(self):
        """
        Test that default values are set correctly.
        測試預設值是否正確設定
        """
        config = ExecutorConfig()

        assert config.log_output_type == "file"
        assert config.log_level == "INFO"
        assert config.log_dir == "."
        assert config.log_filename == "PETsARD_{timestamp}.log"

    def test_update_config(self):
        """
        Test updating config values via the update method.
        測試透過 update 方法更新配置值
        """
        config = ExecutorConfig()

        # Update with valid values
        config.update(
            {
                "log_output_type": "stdout",
                "log_level": "DEBUG",
                "log_dir": "/tmp/logs",
                "log_filename": "test_{timestamp}.log",
            }
        )

        assert config.log_output_type == "stdout"
        assert config.log_level == "DEBUG"
        assert config.log_dir == "/tmp/logs"
        assert config.log_filename == "test_{timestamp}.log"

    def test_validation_log_output_type(self):
        """
        Test validation of log_output_type.
        測試 log_output_type 的驗證
        """
        # Valid values should not raise exceptions
        ExecutorConfig(log_output_type="stdout")
        ExecutorConfig(log_output_type="file")
        ExecutorConfig(log_output_type="both")

        # Invalid value should raise ConfigError
        with pytest.raises(ConfigError):
            ExecutorConfig(log_output_type="invalid_type")

    def test_validation_log_level(self):
        """
        Test validation of log_level.
        測試 log_level 的驗證
        """
        # Valid values should not raise exceptions
        ExecutorConfig(log_level="DEBUG")
        ExecutorConfig(log_level="INFO")
        ExecutorConfig(log_level="WARNING")
        ExecutorConfig(log_level="ERROR")
        ExecutorConfig(log_level="CRITICAL")

        # Invalid value should raise ConfigError
        with pytest.raises(ConfigError):
            ExecutorConfig(log_level="INVALID_LEVEL")


class TestExecutorInitialization:
    """Test suite for Executor initialization and config loading."""

    def setup_method(self):
        """
        Setup for each test method.
        每個測試方法的設置
        """
        # Create temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def teardown_method(self):
        """
        Teardown after each test method.
        每個測試方法後的清理
        """
        # Clean up temporary directory
        self.temp_dir.cleanup()

    def create_yaml_config(self, content):
        """
        Create a YAML config file with the given content.
        建立具有指定內容的 YAML 配置檔案
        """
        config_path = self.temp_path / "test_config.yaml"
        with open(config_path, "w") as f:
            f.write(content)
        return str(config_path)

    def test_executor_default_config(self):
        """
        Test that Executor uses default ExecutorConfig when not specified in YAML.
        測試當 YAML 未指定時，Executor 使用預設的 ExecutorConfig
        """
        # Create YAML with no Executor section
        yaml_content = """
        Loader:
          sample:
            filepath: data/sample.csv
        """
        config_path = self.create_yaml_config(yaml_content)

        # Initialize Executor
        executor = Executor(config_path)

        # Check default values are used
        assert executor.executor_config.log_output_type == "file"
        assert executor.executor_config.log_level == "INFO"
        assert executor.executor_config.log_dir == "."
        assert "{timestamp}" in executor.executor_config.log_filename

    def test_executor_custom_config(self):
        """
        Test that Executor loads custom config from YAML.
        測試 Executor 從 YAML 載入自定義配置
        """
        # Create YAML with Executor section
        yaml_content = """
        Executor:
          log_output_type: both
          log_level: DEBUG
          log_dir: logs
          log_filename: custom_{timestamp}.log

        Loader:
          sample:
            filepath: data/sample.csv
        """
        config_path = self.create_yaml_config(yaml_content)

        # Initialize Executor
        executor = Executor(config_path)

        # Check custom values are used
        assert executor.executor_config.log_output_type == "both"
        assert executor.executor_config.log_level == "DEBUG"
        assert executor.executor_config.log_dir == "logs"
        assert "custom_{timestamp}.log" == executor.executor_config.log_filename

    def test_logger_setup(self):
        """
        Test that logger is properly set up with correct handlers.
        測試日誌器是否以正確的處理程序設置
        """
        import logging

        # Create YAML with Executor section
        yaml_content = """
        Executor:
          log_output_type: both
          log_level: DEBUG

        Loader:
          sample:
            filepath: data/sample.csv
        """
        config_path = self.create_yaml_config(yaml_content)

        # Initialize Executor
        executor = Executor(config_path)

        # 讓我們新增一些調試信息
        print(f"Executor config log_level: {executor.executor_config.log_level}")
        print(f"DEBUG level: {logging.DEBUG}")

        # Check if root logger has correct setup
        root_logger = logging.getLogger("PETsARD")
        print(f"Root logger level: {root_logger.level}")

        # Verify log level
        assert root_logger.level == logging.DEBUG

        # Verify we have two handlers (file and console)
        assert len(root_logger.handlers) == 2

        # Verify handler types
        handler_types = set(type(handler) for handler in root_logger.handlers)
        assert logging.FileHandler in handler_types
        assert logging.StreamHandler in handler_types
