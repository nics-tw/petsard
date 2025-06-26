import os
import tempfile
from unittest.mock import Mock, patch

import pytest
import yaml

from petsard.exceptions import ConfigError
from petsard.executor import Executor, ExecutorConfig


class TestExecutorConfig:
    """測試 ExecutorConfig 類別"""

    def test_default_config(self):
        """測試預設配置"""
        config = ExecutorConfig()

        assert config.log_output_type == "file"
        assert config.log_level == "INFO"
        assert config.log_dir == "."
        assert config.log_filename == "PETsARD_{timestamp}.log"

    def test_custom_config(self):
        """測試自定義配置"""
        config = ExecutorConfig(
            log_output_type="both",
            log_level="DEBUG",
            log_dir="./logs",
            log_filename="custom_{timestamp}.log",
        )

        assert config.log_output_type == "both"
        assert config.log_level == "DEBUG"
        assert config.log_dir == "./logs"
        assert config.log_filename == "custom_{timestamp}.log"

    def test_invalid_log_output_type(self):
        """測試無效的日誌輸出類型"""
        with pytest.raises(ConfigError):
            ExecutorConfig(log_output_type="invalid")

    def test_invalid_log_level(self):
        """測試無效的日誌等級"""
        with pytest.raises(ConfigError):
            ExecutorConfig(log_level="INVALID")

    def test_valid_log_levels(self):
        """測試所有有效的日誌等級"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        for level in valid_levels:
            config = ExecutorConfig(log_level=level)
            assert config.log_level == level

    def test_valid_log_output_types(self):
        """測試所有有效的日誌輸出類型"""
        valid_types = ["stdout", "file", "both"]

        for output_type in valid_types:
            config = ExecutorConfig(log_output_type=output_type)
            assert config.log_output_type == output_type


class TestExecutor:
    """測試 Executor 類別"""

    def setup_method(self):
        """設定測試環境"""
        self.test_config = {
            "Loader": {"load_data": {"method": "csv", "path": "test_data.csv"}},
            "Synthesizer": {"synthesize": {"method": "sdv", "model": "GaussianCopula"}},
        }

    def create_temp_config_file(self, config_dict):
        """建立臨時配置檔案"""
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
        yaml.dump(config_dict, temp_file)
        temp_file.close()
        return temp_file.name

    def test_init_with_valid_config(self):
        """測試使用有效配置初始化"""
        config_file = self.create_temp_config_file(self.test_config)

        try:
            with patch("petsard.executor.Config") as mock_config_class, patch(
                "petsard.status.Status"
            ) as mock_status_class:
                # 設定模擬物件
                mock_config = Mock()
                mock_config.sequence = ["Loader", "Synthesizer"]
                mock_config_class.return_value = mock_config

                mock_status = Mock()
                mock_status_class.return_value = mock_status

                executor = Executor(config_file)

                # 檢查基本屬性
                assert isinstance(executor.executor_config, ExecutorConfig)
                assert executor.sequence is not None
                assert executor.result == {}

                # 檢查 Config 是否被正確建立
                mock_config_class.assert_called_once()
                # Status 是在 executor.__init__ 中直接創建的，所以我們檢查它是否存在
                assert executor.status is not None

        finally:
            os.unlink(config_file)

    def test_init_with_nonexistent_file(self):
        """測試使用不存在的配置檔案"""
        with pytest.raises(ConfigError):
            Executor("nonexistent_config.yaml")

    def test_get_config_with_executor_settings(self):
        """測試載入包含執行器設定的配置"""
        config_with_executor = {
            "Executor": {
                "log_output_type": "both",
                "log_level": "DEBUG",
                "log_dir": "./test_logs",
            },
            **self.test_config,
        }

        config_file = self.create_temp_config_file(config_with_executor)

        try:
            with patch("petsard.executor.Config") as mock_config_class, patch(
                "petsard.status.Status"
            ) as mock_status_class:
                executor = Executor(config_file)

                # 檢查執行器配置是否被正確更新
                assert executor.executor_config.log_output_type == "both"
                assert executor.executor_config.log_level == "DEBUG"
                assert executor.executor_config.log_dir == "./test_logs"

        finally:
            os.unlink(config_file)

    @patch("petsard.executor.logging.getLogger")
    def test_setup_logger_file_output(self, mock_get_logger):
        """測試檔案輸出日誌設定"""
        config_file = self.create_temp_config_file(self.test_config)
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        try:
            with patch("petsard.executor.Config"), patch(
                "petsard.status.Status"
            ), patch("os.makedirs"), patch("logging.FileHandler") as mock_file_handler:
                executor = Executor(config_file)
                executor.executor_config.log_output_type = "file"
                executor._setup_logger()

                # 檢查是否建立了檔案處理器
                mock_file_handler.assert_called()

        finally:
            os.unlink(config_file)

    @patch("petsard.executor.logging.getLogger")
    def test_setup_logger_stdout_output(self, mock_get_logger):
        """測試標準輸出日誌設定"""
        config_file = self.create_temp_config_file(self.test_config)
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        try:
            with patch("petsard.executor.Config") as mock_config_class, patch(
                "petsard.status.Status"
            ) as mock_status_class, patch(
                "logging.StreamHandler"
            ) as mock_stream_handler, patch("logging.FileHandler"):
                # 設定模擬物件
                mock_config = Mock()
                mock_config.sequence = ["Loader"]
                mock_status = Mock()
                mock_config_class.return_value = mock_config
                mock_status_class.return_value = mock_status

                # 設定 StreamHandler mock
                mock_handler = Mock()
                mock_stream_handler.return_value = mock_handler

                executor = Executor(config_file)
                executor.executor_config.log_output_type = "stdout"
                executor._setup_logger()

                # 檢查是否建立了串流處理器
                mock_stream_handler.assert_called()

        finally:
            os.unlink(config_file)

    def test_run_workflow(self):
        """測試工作流程執行"""
        config_file = self.create_temp_config_file(self.test_config)

        try:
            with patch("petsard.executor.Config") as mock_config_class, patch(
                "petsard.status.Status"
            ) as mock_status_class:
                # 設定模擬物件
                mock_config = Mock()
                mock_config.sequence = ["Loader", "Synthesizer"]  # 設定 sequence 屬性
                mock_status = Mock()
                mock_config_class.return_value = mock_config
                mock_status_class.return_value = mock_status

                # 設定 status mock 的方法
                mock_status.get_full_expt.return_value = {
                    "Loader": "load_data",
                    "Synthesizer": "synthesize",
                }
                mock_status.get_result.return_value = "test_result"

                # 設定佇列模擬
                mock_operator1 = Mock()
                mock_operator2 = Mock()
                mock_config.config.qsize.side_effect = [2, 1, 0]  # 模擬佇列大小變化
                mock_config.config.get.side_effect = [mock_operator1, mock_operator2]
                mock_config.module_flow.get.side_effect = ["Loader", "Synthesizer"]
                mock_config.expt_flow.get.side_effect = ["load_data", "synthesize"]

                executor = Executor(config_file)
                # 替換 executor 的 status 屬性為我們的 mock
                executor.status = mock_status
                executor.sequence = ["Loader", "Synthesizer"]
                executor.run()

                # 檢查操作器是否被正確執行
                mock_operator1.run.assert_called_once()
                mock_operator2.run.assert_called_once()

                # 檢查狀態是否被正確更新
                assert mock_status.put.call_count == 2

        finally:
            os.unlink(config_file)

    def test_set_result_final_module(self):
        """測試最終模組結果設定"""
        config_file = self.create_temp_config_file(self.test_config)

        try:
            with patch("petsard.executor.Config") as mock_config_class, patch(
                "petsard.status.Status"
            ) as mock_status_class:
                # 設定模擬物件
                mock_config = Mock()
                mock_config.sequence = ["Loader", "Synthesizer"]
                mock_config_class.return_value = mock_config

                mock_status = Mock()
                mock_status_class.return_value = mock_status
                mock_status.get_full_expt.return_value = {
                    "Loader": "load_data",
                    "Synthesizer": "synthesize",
                }
                mock_status.get_result.return_value = "final_result"

                executor = Executor(config_file)
                # 替換 executor 的 status 屬性為我們的 mock
                executor.status = mock_status
                executor.sequence = ["Loader", "Synthesizer"]
                executor._set_result("Synthesizer")  # 最終模組

                # 檢查結果是否被正確設定
                expected_key = "Loader[load_data]_Synthesizer[synthesize]"
                assert expected_key in executor.result
                assert executor.result[expected_key] == "final_result"

        finally:
            os.unlink(config_file)

    def test_set_result_non_final_module(self):
        """測試非最終模組結果設定"""
        config_file = self.create_temp_config_file(self.test_config)

        try:
            with patch("petsard.executor.Config"), patch("petsard.status.Status"):
                executor = Executor(config_file)
                executor.sequence = ["Loader", "Synthesizer"]
                executor._set_result("Loader")  # 非最終模組

                # 檢查結果字典應該保持空白
                assert len(executor.result) == 0

        finally:
            os.unlink(config_file)

    def test_get_result(self):
        """測試結果取得"""
        config_file = self.create_temp_config_file(self.test_config)

        try:
            with patch("petsard.executor.Config"), patch("petsard.status.Status"):
                executor = Executor(config_file)
                executor.result = {"test_experiment": "test_result"}

                result = executor.get_result()
                assert result == {"test_experiment": "test_result"}

        finally:
            os.unlink(config_file)

    def test_get_timing(self):
        """測試執行時間記錄取得"""
        config_file = self.create_temp_config_file(self.test_config)

        try:
            with patch("petsard.executor.Config") as mock_config_class, patch(
                "petsard.status.Status"
            ) as mock_status_class:
                import pandas as pd

                # 建立模擬的時間記錄 DataFrame
                mock_timing_data = pd.DataFrame(
                    {
                        "record_id": ["timing_001", "timing_002"],
                        "module_name": ["Loader", "Synthesizer"],
                        "experiment_name": ["load_data", "synthesize"],
                        "step_name": ["run", "run"],
                        "start_time": ["2024-01-01T10:00:00", "2024-01-01T10:01:00"],
                        "end_time": ["2024-01-01T10:00:30", "2024-01-01T10:02:00"],
                        "duration_seconds": [30.00, 60.00],  # 使用 2 位小數精度
                        "duration_precision": [2, 2],  # 新增 duration_precision 欄位
                    }
                )

                # 設定模擬物件
                mock_config = Mock()
                mock_config.sequence = ["Loader", "Synthesizer"]  # 設定 sequence 屬性
                mock_status = Mock()
                mock_config_class.return_value = mock_config
                mock_status_class.return_value = mock_status
                mock_status.get_timing_report_data.return_value = mock_timing_data

                executor = Executor(config_file)

                # 替換 executor 的 status 屬性為我們的 mock
                executor.status = mock_status

                timing_result = executor.get_timing()

                # 檢查是否正確呼叫了 status 的方法
                mock_status.get_timing_report_data.assert_called_once()

                # 檢查回傳的結果
                assert timing_result.equals(mock_timing_data)

        finally:
            os.unlink(config_file)


class TestExecutorIntegration:
    """整合測試"""

    def test_complete_workflow_with_logging(self):
        """測試包含日誌的完整工作流程"""
        config_dict = {
            "Executor": {"log_output_type": "stdout", "log_level": "INFO"},
            "Loader": {"load_test": {"method": "csv", "path": "test.csv"}},
        }

        config_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        )
        yaml.dump(config_dict, config_file)
        config_file.close()

        try:
            with patch("petsard.executor.Config") as mock_config_class, patch(
                "petsard.status.Status"
            ) as mock_status_class, patch(
                "logging.StreamHandler"
            ) as mock_stream_handler, patch("logging.FileHandler"), patch(
                "logging.getLogger"
            ) as mock_get_logger:
                # 設定模擬物件
                mock_config = Mock()
                mock_config.sequence = ["Loader"]  # 設定 sequence 屬性
                mock_status = Mock()
                mock_config_class.return_value = mock_config
                mock_status_class.return_value = mock_status

                # 設定 StreamHandler mock
                mock_handler = Mock()
                mock_handler.level = 20  # INFO level
                mock_stream_handler.return_value = mock_handler

                # 設定 logger mock
                mock_logger = Mock()
                mock_get_logger.return_value = mock_logger

                # 設定空佇列（不執行任何操作器）
                mock_config.config.qsize.return_value = 0

                executor = Executor(config_file.name)

                # 檢查執行器配置是否被正確設定
                assert executor.executor_config.log_output_type == "stdout"
                assert executor.executor_config.log_level == "INFO"

        finally:
            os.unlink(config_file.name)

    def test_error_handling_invalid_yaml(self):
        """測試無效 YAML 檔案的錯誤處理"""
        # 建立無效的 YAML 檔案
        invalid_yaml = "invalid: yaml: content: ["

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as temp_file:
            temp_file.write(invalid_yaml)
            temp_file_path = temp_file.name

        try:
            with pytest.raises(Exception):  # YAML 解析錯誤
                Executor(temp_file_path)
        finally:
            os.unlink(temp_file_path)

    @patch("petsard.executor.time.time")
    def test_execution_timing(self, mock_time):
        """測試執行時間計算"""
        config_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        )
        yaml.dump({"Loader": {"test": {"method": "csv"}}}, config_file)
        config_file.close()

        # 模擬時間
        mock_time.side_effect = [1000.0, 1010.5]  # 開始和結束時間

        try:
            with patch("petsard.executor.Config") as mock_config_class, patch(
                "petsard.status.Status"
            ) as mock_status_class, patch("logging.getLogger") as mock_get_logger:
                mock_logger = Mock()
                mock_get_logger.return_value = mock_logger

                # 設定模擬物件
                mock_config = Mock()
                mock_config.sequence = ["Loader"]  # 設定 sequence 屬性
                mock_status = Mock()
                mock_config_class.return_value = mock_config
                mock_status_class.return_value = mock_status
                mock_config.config.qsize.return_value = 0  # 空佇列

                executor = Executor(config_file.name)
                executor.run()

                # 檢查是否記錄了執行時間
                mock_logger.info.assert_any_call("Starting PETsARD execution workflow")
                # 檢查完成訊息包含執行時間
                completion_calls = [
                    call
                    for call in mock_logger.info.call_args_list
                    if "Completed PETsARD execution workflow" in str(call)
                ]
                assert len(completion_calls) > 0

        finally:
            os.unlink(config_file.name)


if __name__ == "__main__":
    pytest.main([__file__])
