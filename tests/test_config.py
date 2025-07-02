import queue
from dataclasses import dataclass, field
from typing import Any, Dict
from unittest.mock import Mock

import pandas as pd
import pytest

from petsard.config import Config
from petsard.config_base import BaseConfig, ConfigGetParamActionMap
from petsard.exceptions import ConfigError, UnexecutedError
from petsard.metadater import SchemaMetadata
from petsard.operator import BaseOperator
from petsard.status import Status


@dataclass
class TestConfigClass(BaseConfig):
    """Test configuration class for unit tests"""

    # PytestCollectionWarning: cannot collect test class 'TestConfig'
    #   because it has a init constructor (from: tests/test_config_base.py)
    __test__ = False

    a: int
    b: int
    c: Dict[Any, Any] = field(default_factory=dict)
    d: Dict[Any, Any] = field(default_factory=dict)

    def __post_init__(self):
        super().__post_init__()


class TestConfig:
    """測試 Config 類別"""

    def test_init_basic_config(self):
        """測試基本配置初始化"""
        config_dict = {
            "Loader": {"load_data": {"filepath": "test.csv"}},
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
        config_dict = {"Loader": {"load_data_[invalid]": {"filepath": "test.csv"}}}

        with pytest.raises(ConfigError):
            Config(config_dict)

    def test_splitter_handler(self):
        """測試 Splitter 配置處理"""
        config_dict = {
            "Splitter": {"split_data": {"train_split_ratio": 0.8, "num_samples": 3}}
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
            "Loader": {"load_data": {"method": "default"}},
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
            "Loader": {"data": {"filepath": "benchmark://adult-income"}},
            "Splitter": {"split_data": {"train_split_ratio": 0.8}},
            "Reporter": {"output": {"method": "save_data", "source": "Loader"}},
        }
        self.config = Config(config_dict)
        self.status = Status(self.config)

    def test_init(self):
        """測試 Status 初始化"""
        assert self.status.config == self.config
        assert self.status.sequence == ["Loader", "Splitter", "Reporter"]
        assert self.status.status == {}
        assert self.status.metadata == {}
        assert hasattr(self.status, "exist_train_indices")
        assert hasattr(self.status, "report")

    def test_put_and_get_result(self):
        """測試狀態儲存和結果取得"""
        # 建立模擬操作器
        mock_operator = Mock(spec=BaseOperator)
        mock_operator.get_result.return_value = pd.DataFrame({"A": [1, 2, 3]})

        # 建立模擬 SchemaMetadata
        mock_metadata = Mock(spec=SchemaMetadata)
        mock_metadata.schema_id = "test_schema"
        mock_operator.get_metadata.return_value = mock_metadata

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

        # 檢查報告內容
        assert "test_report" in retrieved_report
        pd.testing.assert_frame_equal(
            retrieved_report["test_report"], mock_report["test_report"]
        )

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
            "Loader": {"load_csv": {"filepath": "data.csv"}},
            "Preprocessor": {"preprocess": {"method": "default"}},
            "Synthesizer": {"synthesize": {"method": "sdv", "model": "GaussianCopula"}},
            "Evaluator": {"evaluate": {"method": "sdmetrics"}},
            "Reporter": {"report": {"method": "save_report", "granularity": "global"}},
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

    def test_operator_creation(self):
        """測試操作器建立"""
        config_dict = {"Loader": {"load_data": {"filepath": "test.csv"}}}

        config = Config(config_dict)

        # 檢查操作器是否被正確建立
        assert config.config.qsize() == 1
        operator = config.config.get()

        # 驗證操作器類型
        from petsard.operator import LoaderOperator

        assert isinstance(operator, LoaderOperator)


class TestBaseConfig:
    """Test suite for BaseConfig class"""

    def test_init_and_get(self):
        """Test initialization and get method"""
        # Create a test configuration
        config = TestConfigClass(a=1, b=2, c={3: "3"}, d={4: "4"})

        # Test the get method
        result = config.get()
        assert "a" in result
        assert "b" in result
        assert "c" in result
        assert "d" in result
        assert result["a"] == 1
        assert result["b"] == 2
        assert result["c"] == {3: "3"}
        assert result["d"] == {4: "4"}
        assert "_logger" in result  # Check that logger is included

    def test_update(self):
        """Test update method"""
        config = TestConfigClass(a=1, b=2)

        # Update existing attributes
        config.update({"a": 10, "b": 20})
        assert config.a == 10
        assert config.b == 20

        # Test updating non-existent attribute
        with pytest.raises(ConfigError):
            config.update({"nonexistent": 30})

        # Test updating with incorrect type
        with pytest.raises(ConfigError):
            config.update({"a": "string instead of int"})

    def test_get_params_include(self):
        """Test get_params with INCLUDE action"""
        config = TestConfigClass(a=1, b=2, c={3: "3"}, d={4: "4"})

        # Basic include
        result = config.get_params([{"a": {"action": "INCLUDE"}}])
        assert result == {"a": 1}

        # Include with renaming
        result = config.get_params(
            [{"b": {"action": "INCLUDE", "rename": {"b": "test_b"}}}]
        )
        assert result == {"test_b": 2}

        # Missing matching key in rename dictionary
        with pytest.raises(ConfigError):
            config.get_params(
                [{"b": {"action": "INCLUDE", "rename": {"wrong_key": "test_b"}}}]
            )

    def test_get_params_merge(self):
        """Test get_params with MERGE action"""
        config = TestConfigClass(a=1, b=2, c={3: "3"}, d={4: "4"})

        # Basic merge
        result = config.get_params([{"c": {"action": "MERGE"}}])
        assert result == {3: "3"}

        # Merge with renaming
        result = config.get_params(
            [{"d": {"action": "MERGE", "rename": {4: "test_d"}}}]
        )
        assert result == {"test_d": "4"}

        # Merge with non-dictionary attribute
        with pytest.raises(ConfigError):
            config.get_params([{"a": {"action": "MERGE"}}])

        # Rename key doesn't exist
        with pytest.raises(ConfigError):
            config.get_params([{"d": {"action": "MERGE", "rename": {5: "test_d"}}}])

    def test_get_params_combined(self):
        """Test get_params with combined actions"""
        config = TestConfigClass(a=1, b=2, c={3: "3"}, d={4: "4"})

        # Combine different operations
        result = config.get_params(
            [
                {"a": {"action": "INCLUDE"}},
                {"b": {"action": "INCLUDE", "rename": {"b": "test_b"}}},
                {"c": {"action": "MERGE"}},
                {"d": {"action": "MERGE", "rename": {4: "test_d"}}},
            ]
        )

        assert result == {"a": 1, "test_b": 2, 3: "3", "test_d": "4"}

    def test_get_params_validation(self):
        """Test validation in get_params"""
        config = TestConfigClass(a=1, b=2, c={3: "3", 5: "5"}, d={4: "4"})

        # Non-existent attribute
        with pytest.raises(ConfigError):
            config.get_params([{"nonexistent": {"action": "INCLUDE"}}])

        # Duplicate attribute usage
        with pytest.raises(ConfigError):
            config.get_params(
                [{"a": {"action": "INCLUDE"}}, {"a": {"action": "INCLUDE"}}]
            )

        # Target key conflict
        with pytest.raises(ConfigError):
            config.get_params(
                [
                    {"a": {"action": "INCLUDE"}},
                    {"b": {"action": "INCLUDE", "rename": {"b": "a"}}},
                ]
            )

        # Key conflict when merging
        config.c[6] = "6"
        config.d[6] = "6"
        with pytest.raises(ConfigError):
            config.get_params([{"c": {"action": "MERGE"}}, {"d": {"action": "MERGE"}}])

        # Key conflict after renaming
        with pytest.raises(ConfigError):
            config.get_params(
                [
                    {"c": {"action": "MERGE", "rename": {3: "test_key"}}},
                    {"d": {"action": "MERGE", "rename": {4: "test_key"}}},
                ]
            )

    def test_from_dict(self):
        """Test from_dict class method"""
        # Valid parameters
        config = TestConfigClass.from_dict({"a": 1, "b": 2})
        assert config.a == 1
        assert config.b == 2

        # Missing required parameter
        with pytest.raises(ConfigError):
            TestConfigClass.from_dict({"a": 1})  # Missing b

        # Unexpected parameter
        with pytest.raises(ConfigError):
            TestConfigClass.from_dict({"a": 1, "b": 2, "extra": 3})

        # Incorrect parameter type
        with pytest.raises(ConfigError):
            config = TestConfigClass.from_dict({"a": "string", "b": 2})


def test_config_get_param_action_map():
    """Test the ConfigGetParamActionMap enum"""
    assert hasattr(ConfigGetParamActionMap, "INCLUDE")
    assert hasattr(ConfigGetParamActionMap, "MERGE")
    assert ConfigGetParamActionMap.INCLUDE != ConfigGetParamActionMap.MERGE


if __name__ == "__main__":
    pytest.main([__file__])
