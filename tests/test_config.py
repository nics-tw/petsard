import queue
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from petsard.config import Config, Status
from petsard.exceptions import ConfigError, UnexecutedError
from petsard.metadater import SchemaMetadata
from petsard.operator import BaseOperator


class TestConfig:
    """測試 Config 類別"""

    def test_init_basic_config(self):
        """測試基本配置初始化"""
        config_dict = {
            "Loader": {"load_data": {"method": "csv", "path": "test.csv"}},
            "Synthesizer": {"synth_data": {"method": "sdv", "model": "GaussianCopula"}},
        }

        config = Config(config_dict)

        assert config.yaml == config_dict
        assert config.sequence == ["Loader", "Synthesizer"]
        assert isinstance(config.config, queue.Queue)
        assert isinstance(config.module_flow, queue.Queue)
        assert isinstance(config.expt_flow, queue.Queue)

    def test_config_validation_error(self):
        """測試配置驗證錯誤"""
        # 測試實驗名稱包含 "_[xxx]" 後綴的錯誤
        config_dict = {
            "Loader": {"load_data_[invalid]": {"method": "csv", "path": "test.csv"}}
        }

        with pytest.raises(ConfigError):
            Config(config_dict)

    def test_splitter_handler(self):
        """測試 Splitter 配置處理"""
        config_dict = {
            "Splitter": {
                "split_data": {"method": "random", "test_size": 0.2, "num_samples": 3}
            }
        }

        config = Config(config_dict)

        # 檢查是否正確展開為多個實驗
        splitter_config = config.yaml["Splitter"]
        assert "split_data_[3-1]" in splitter_config
        assert "split_data_[3-2]" in splitter_config
        assert "split_data_[3-3]" in splitter_config

        # 檢查每個實驗的 num_samples 都被設為 1
        for expt_config in splitter_config.values():
            assert expt_config["num_samples"] == 1

    def test_set_flow(self):
        """測試流程設定"""
        config_dict = {
            "Loader": {"load_data": {"method": "csv"}},
            "Synthesizer": {"synth_data": {"method": "sdv"}},
        }

        config = Config(config_dict)

        # 檢查佇列大小
        assert config.config.qsize() == 2
        assert config.module_flow.qsize() == 2
        assert config.expt_flow.qsize() == 2

        # 檢查佇列內容順序
        modules = []
        expts = []
        while not config.module_flow.empty():
            modules.append(config.module_flow.get())
            expts.append(config.expt_flow.get())

        assert modules == ["Loader", "Synthesizer"]
        assert expts == ["load_data", "synth_data"]


class TestStatus:
    """測試 Status 類別"""

    def setup_method(self):
        """設定測試環境"""
        config_dict = {
            "Loader": {"load_data": {"method": "csv"}},
            "Splitter": {"split_data": {"method": "random"}},
            "Reporter": {"report_data": {"method": "save_data"}},
        }
        self.config = Config(config_dict)
        self.status = Status(self.config)

    def test_init(self):
        """測試 Status 初始化"""
        assert self.status.config == self.config
        assert self.status.sequence == ["Loader", "Splitter", "Reporter"]
        assert self.status.status == {}
        assert self.status.metadata == {}
        assert hasattr(self.status, "exist_index")
        assert hasattr(self.status, "report")

    def test_put_and_get_result(self):
        """測試狀態儲存和結果取得"""
        # 建立模擬操作器
        mock_operator = Mock(spec=BaseOperator)
        mock_operator.get_result.return_value = pd.DataFrame({"A": [1, 2, 3]})
        mock_operator.get_metadata.return_value = Mock(spec=SchemaMetadata)

        # 儲存狀態
        self.status.put("Loader", "load_data", mock_operator)

        # 檢查狀態
        assert "Loader" in self.status.status
        assert self.status.status["Loader"]["expt"] == "load_data"
        assert self.status.status["Loader"]["operator"] == mock_operator

        # 檢查結果取得
        result = self.status.get_result("Loader")
        assert isinstance(result, pd.DataFrame)

    def test_metadata_management(self):
        """測試元資料管理"""
        mock_metadata = Mock(spec=SchemaMetadata)

        # 設定元資料
        self.status.set_metadata("Loader", mock_metadata)
        assert self.status.metadata["Loader"] == mock_metadata

        # 取得元資料
        retrieved_metadata = self.status.get_metadata("Loader")
        assert retrieved_metadata == mock_metadata

        # 測試不存在模組的錯誤
        with pytest.raises(UnexecutedError):
            self.status.get_metadata("NonExistent")

    def test_get_pre_module(self):
        """測試取得前一個模組"""
        assert self.status.get_pre_module("Loader") is None
        assert self.status.get_pre_module("Splitter") == "Loader"
        assert self.status.get_pre_module("Reporter") == "Splitter"

    def test_get_full_expt(self):
        """測試取得完整實驗配置"""
        # 建立模擬操作器
        mock_operator1 = Mock(spec=BaseOperator)
        mock_operator2 = Mock(spec=BaseOperator)

        # 儲存狀態
        self.status.put("Loader", "load_data", mock_operator1)
        self.status.put("Splitter", "split_data", mock_operator2)

        # 測試取得所有實驗
        full_expt = self.status.get_full_expt()
        expected = {"Loader": "load_data", "Splitter": "split_data"}
        assert full_expt == expected

        # 測試取得特定模組之前的實驗
        partial_expt = self.status.get_full_expt("Loader")
        expected_partial = {"Loader": "load_data"}
        assert partial_expt == expected_partial

    def test_report_management(self):
        """測試報告管理"""
        # 建立模擬報告操作器
        mock_operator = Mock(spec=BaseOperator)
        mock_report = {"test_report": pd.DataFrame({"metric": [0.8, 0.9]})}
        mock_operator.get_result.return_value = mock_report

        # 儲存報告狀態
        self.status.put("Reporter", "report_data", mock_operator)

        # 檢查報告設定
        self.status.set_report(mock_report)
        retrieved_report = self.status.get_report()
        assert retrieved_report == mock_report

    def test_status_renewal(self):
        """測試狀態更新機制"""
        # 建立模擬操作器
        mock_operator1 = Mock(spec=BaseOperator)
        mock_operator2 = Mock(spec=BaseOperator)
        mock_operator3 = Mock(spec=BaseOperator)

        # 第一輪執行
        self.status.put("Loader", "load_data", mock_operator1)
        self.status.put("Splitter", "split_data", mock_operator2)

        assert len(self.status.status) == 2

        # 第二輪執行 - 從 Loader 重新開始
        self.status.put("Loader", "load_data_2", mock_operator3)

        # 檢查後續模組狀態被清除
        assert len(self.status.status) == 1
        assert "Loader" in self.status.status
        assert "Splitter" not in self.status.status


class TestConfigIntegration:
    """整合測試"""

    def test_complete_workflow_setup(self):
        """測試完整工作流程設定"""
        config_dict = {
            "Loader": {"load_csv": {"method": "csv", "path": "data.csv"}},
            "Preprocessor": {"preprocess": {"method": "default"}},
            "Synthesizer": {"synthesize": {"method": "sdv", "model": "GaussianCopula"}},
            "Evaluator": {"evaluate": {"method": "sdmetrics"}},
            "Reporter": {"report": {"method": "save_report"}},
        }

        config = Config(config_dict)
        status = Status(config)

        # 檢查配置
        assert len(config.sequence) == 5
        assert config.config.qsize() == 5

        # 檢查狀態初始化
        assert status.sequence == config.sequence
        assert len(status.status) == 0
        assert len(status.metadata) == 0

    @patch("petsard.operator.LoaderOperator")
    def test_operator_creation(self, mock_loader_class):
        """測試操作器建立"""
        config_dict = {"Loader": {"load_data": {"method": "csv", "path": "test.csv"}}}

        config = Config(config_dict)

        # 檢查操作器是否被正確建立
        assert config.config.qsize() == 1
        operator = config.config.get()

        # 驗證操作器類型和配置
        mock_loader_class.assert_called_once_with({"method": "csv", "path": "test.csv"})


if __name__ == "__main__":
    pytest.main([__file__])
