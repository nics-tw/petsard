from unittest.mock import Mock, patch

import pandas as pd
import pytest

from petsard.exceptions import ConfigError
from petsard.metadater import SchemaMetadata
from petsard.operator import (
    BaseOperator,
    ConstrainerOperator,
    EvaluatorOperator,
    LoaderOperator,
    PreprocessorOperator,
    ReporterOperator,
    SplitterOperator,
    SynthesizerOperator,
)


class TestBaseOperator:
    """測試 BaseOperator 基礎類別"""

    def test_init_with_valid_config(self):
        """測試使用有效配置初始化"""
        config = {"method": "test", "param": "value"}

        class TestOperator(BaseOperator):
            def _run(self, input):
                pass

            def set_input(self, status):
                return {}

            def get_result(self):
                return None

            def get_metadata(self):
                return Mock(spec=SchemaMetadata)

        operator = TestOperator(config)

        assert operator.config == config
        assert operator.module_name == "TestOp"
        assert operator.input == {}

    def test_init_with_none_config(self):
        """測試使用 None 配置初始化"""

        class TestOperator(BaseOperator):
            def _run(self, input):
                pass

            def set_input(self, status):
                return {}

            def get_result(self):
                return None

            def get_metadata(self):
                return Mock(spec=SchemaMetadata)

        with pytest.raises(ConfigError):
            TestOperator(None)

    def test_run_template_method(self):
        """測試 run 模板方法"""
        config = {"method": "test"}

        class TestOperator(BaseOperator):
            def __init__(self, config):
                super().__init__(config)
                self.run_called = False

            def _run(self, input):
                self.run_called = True

            def set_input(self, status):
                return {}

            def get_result(self):
                return None

            def get_metadata(self):
                return Mock(spec=SchemaMetadata)

        operator = TestOperator(config)

        with patch("time.time", side_effect=[1000.0, 1001.0]):
            with patch.object(operator, "_logger") as mock_logger:
                operator.run({})

        assert operator.run_called

        # 驗證計時 logging 訊息
        mock_logger.info.assert_any_call("TIMING_START|TestOp|run|1000.0")
        mock_logger.info.assert_any_call("Starting TestOp execution")
        mock_logger.info.assert_any_call("TIMING_END|TestOp|run|1001.0|1.0")

    def test_log_and_raise_config_error_decorator(self):
        """測試配置錯誤裝飾器"""
        config = {"method": "test"}

        class TestOperator(BaseOperator):
            def _run(self, input):
                pass

            def get_result(self):
                return None

            def get_metadata(self):
                return Mock(spec=SchemaMetadata)

            @BaseOperator.log_and_raise_config_error
            def set_input(self, status):
                raise ValueError("Test error")

        operator = TestOperator(config)

        with pytest.raises(ConfigError):
            operator.set_input(Mock())

    def test_not_implemented_methods(self):
        """測試未實作方法的錯誤"""
        config = {"method": "test"}
        operator = BaseOperator(config)

        with pytest.raises(NotImplementedError):
            operator._run({})

        with pytest.raises(NotImplementedError):
            operator.set_input(Mock())

        with pytest.raises(NotImplementedError):
            operator.get_result()

        with pytest.raises(NotImplementedError):
            operator.get_metadata()

    def test_run_with_error_timing(self):
        """測試錯誤情況下的計時記錄"""
        config = {"method": "test"}

        class ErrorOperator(BaseOperator):
            def _run(self, input):
                raise ValueError("Test error")

            def set_input(self, status):
                return {}

            def get_result(self):
                return None

            def get_metadata(self):
                return Mock(spec=SchemaMetadata)

        operator = ErrorOperator(config)

        with patch("time.time", side_effect=[1000.0, 1001.5]):
            with patch.object(operator, "_logger") as mock_logger:
                with pytest.raises(ValueError, match="Test error"):
                    operator.run({})

        # 驗證錯誤計時 logging 訊息
        mock_logger.info.assert_any_call("TIMING_START|ErrorOp|run|1000.0")
        mock_logger.info.assert_any_call("Starting ErrorOp execution")
        mock_logger.info.assert_any_call(
            "TIMING_ERROR|ErrorOp|run|1001.5|1.5|Test error"
        )


class TestLoaderOperator:
    """測試 LoaderOperator"""

    def test_init(self):
        """測試初始化"""
        config = {"method": "csv", "path": "test.csv"}

        with patch("petsard.operator.Loader") as mock_loader_class:
            operator = LoaderOperator(config)

            mock_loader_class.assert_called_once_with(**config)
            assert operator._schema_metadata is None

    def test_run(self):
        """測試執行"""
        config = {"method": "csv", "path": "test.csv"}
        test_data = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        mock_metadata = Mock(spec=SchemaMetadata)

        with patch("petsard.operator.Loader") as mock_loader_class:
            mock_loader = Mock()
            mock_loader.load.return_value = (test_data, mock_metadata)
            mock_loader_class.return_value = mock_loader

            operator = LoaderOperator(config)
            operator._run({})

            assert operator.data.equals(test_data)
            assert operator.metadata == mock_metadata
            assert operator._schema_metadata == mock_metadata

    def test_set_input(self):
        """測試輸入設定"""
        config = {"method": "csv", "path": "test.csv"}

        with patch("petsard.operator.Loader"):
            operator = LoaderOperator(config)
            mock_status = Mock()

            result = operator.set_input(mock_status)
            assert result == operator.input

    def test_get_result(self):
        """測試結果取得"""
        config = {"method": "csv", "path": "test.csv"}
        test_data = pd.DataFrame({"A": [1, 2, 3]})

        with patch("petsard.operator.Loader"):
            operator = LoaderOperator(config)
            operator.data = test_data

            result = operator.get_result()
            assert result.equals(test_data)

    def test_get_metadata(self):
        """測試元資料取得"""
        config = {"method": "csv", "path": "test.csv"}
        mock_metadata = Mock(spec=SchemaMetadata)

        with patch("petsard.operator.Loader"):
            operator = LoaderOperator(config)
            operator.metadata = mock_metadata

            result = operator.get_metadata()
            assert result == mock_metadata


class TestSplitterOperator:
    """測試 SplitterOperator"""

    def test_init(self):
        """測試初始化"""
        config = {"method": "random", "test_size": 0.2}

        with patch("petsard.operator.Splitter") as mock_splitter_class:
            operator = SplitterOperator(config)

            mock_splitter_class.assert_called_once_with(**config)

    def test_run(self):
        """測試執行"""
        config = {"method": "random", "test_size": 0.2}
        input_data = {
            "data": pd.DataFrame({"A": [1, 2, 3]}),
            "metadata": Mock(spec=SchemaMetadata),
            "exist_train_indices": [],
        }

        with patch("petsard.operator.Splitter") as mock_splitter_class:
            mock_splitter = Mock()
            mock_data = {
                1: {
                    "train": pd.DataFrame({"A": [1, 2]}),
                    "validation": pd.DataFrame({"A": [3]}),
                }
            }
            mock_metadata = Mock(spec=SchemaMetadata)
            mock_train_indices = {1: [0, 1]}
            mock_splitter.split.return_value = (
                mock_data,
                mock_metadata,
                mock_train_indices,
            )
            mock_splitter_class.return_value = mock_splitter

            operator = SplitterOperator(config)
            operator._run(input_data)

            # Check that split was called with correct parameters
            # 空的 exist_train_indices 不會被傳遞
            expected_params = {
                "data": input_data["data"],
            }
            mock_splitter.split.assert_called_once_with(**expected_params)

            # Check that results are stored correctly
            assert operator.data == mock_data
            assert operator.metadata == mock_metadata
            assert operator.train_indices == mock_train_indices

    def test_set_input_with_data(self):
        """測試有資料的輸入設定"""
        config = {"test_size": 0.2}  # 沒有 method 參數
        test_data = pd.DataFrame({"A": [1, 2, 3]})
        mock_metadata = Mock(spec=SchemaMetadata)

        with patch("petsard.operator.Splitter"):
            operator = SplitterOperator(config)

            mock_status = Mock()
            mock_status.get_result.return_value = test_data
            mock_status.get_metadata.return_value = mock_metadata
            mock_status.get_exist_train_indices.return_value = []

            result = operator.set_input(mock_status)

            assert result["data"].equals(test_data)
            assert result["metadata"] == mock_metadata
            assert result["exist_train_indices"] == []

    def test_set_input_custom_method(self):
        """測試自定義方法的輸入設定"""
        config = {"method": "custom_data"}

        with patch("petsard.operator.Splitter"):
            operator = SplitterOperator(config)

            mock_status = Mock()
            mock_status.get_exist_train_indices.return_value = []

            result = operator.set_input(mock_status)

            assert result["data"] is None
            assert result["exist_train_indices"] == []

    def test_get_result(self):
        """測試結果取得"""
        config = {"method": "random"}
        test_result = {
            "train": pd.DataFrame({"A": [1, 2]}),
            "validation": pd.DataFrame({"A": [3]}),
        }

        with patch("petsard.operator.Splitter") as mock_splitter_class:
            mock_splitter_class.return_value = Mock()

            operator = SplitterOperator(config)
            operator.data = {1: test_result}  # 直接設定在 operator 上
            result = operator.get_result()

            assert "train" in result
            assert "validation" in result

    def test_get_metadata(self):
        """測試元資料取得"""
        config = {"method": "random"}
        mock_metadata = Mock(spec=SchemaMetadata)

        with patch("petsard.operator.Splitter") as mock_splitter_class:
            mock_splitter = Mock()
            mock_splitter_class.return_value = mock_splitter

            operator = SplitterOperator(config)
            # 設定新的字典格式 metadata
            metadata_dict = {1: {"train": mock_metadata, "validation": mock_metadata}}
            operator.metadata = metadata_dict

            with patch(
                "petsard.operator.deepcopy", return_value=mock_metadata
            ) as mock_deepcopy:
                result = operator.get_metadata()

                mock_deepcopy.assert_called_once_with(mock_metadata)
                assert result == mock_metadata

    def test_get_train_indices(self):
        """測試訓練索引取得"""
        config = {"method": "random"}
        mock_train_indices = {1: [0, 1, 2], 2: [3, 4, 5]}

        with patch("petsard.operator.Splitter") as mock_splitter_class:
            mock_splitter = Mock()
            mock_splitter_class.return_value = mock_splitter

            operator = SplitterOperator(config)
            operator.train_indices = mock_train_indices

            with patch(
                "petsard.operator.deepcopy", return_value=mock_train_indices
            ) as mock_deepcopy:
                result = operator.get_train_indices()

                mock_deepcopy.assert_called_once_with(mock_train_indices)
                assert result == mock_train_indices


class TestPreprocessorOperator:
    """測試 PreprocessorOperator"""

    def test_init_default_method(self):
        """測試預設方法初始化"""
        config = {"method": "default"}

        operator = PreprocessorOperator(config)

        assert operator.processor is None
        assert operator._config == {}
        assert operator._sequence is None

    def test_init_custom_method(self):
        """測試自定義方法初始化"""
        config = {
            "method": "custom",
            "param1": "value1",
            "sequence": ["encoder", "scaler"],
        }

        operator = PreprocessorOperator(config)

        assert operator._sequence == ["encoder", "scaler"]
        assert "sequence" not in operator._config
        assert operator._config["param1"] == "value1"

    def test_run_default_sequence(self):
        """測試預設序列執行"""
        config = {"method": "default"}
        input_data = {
            "data": pd.DataFrame({"A": [1, 2, 3]}),
            "metadata": Mock(spec=SchemaMetadata),
        }

        with patch("petsard.operator.Processor") as mock_processor_class:
            mock_processor = Mock()
            mock_processor.transform.return_value = pd.DataFrame({"A": [1, 2, 3]})
            mock_processor_class.return_value = mock_processor

            operator = PreprocessorOperator(config)
            operator._run(input_data)

            mock_processor.fit.assert_called_once_with(data=input_data["data"])
            mock_processor.transform.assert_called_once_with(data=input_data["data"])

    def test_run_custom_sequence(self):
        """測試自定義序列執行"""
        config = {"method": "custom", "sequence": ["encoder", "scaler"]}
        input_data = {
            "data": pd.DataFrame({"A": [1, 2, 3]}),
            "metadata": Mock(spec=SchemaMetadata),
        }

        with patch("petsard.operator.Processor") as mock_processor_class:
            mock_processor = Mock()
            mock_processor.transform.return_value = pd.DataFrame({"A": [1, 2, 3]})
            mock_processor_class.return_value = mock_processor

            operator = PreprocessorOperator(config)
            operator._run(input_data)

            mock_processor.fit.assert_called_once_with(
                data=input_data["data"], sequence=["encoder", "scaler"]
            )

    def test_set_input_from_splitter(self):
        """測試從 Splitter 設定輸入"""
        config = {"method": "default"}

        operator = PreprocessorOperator(config)

        mock_status = Mock()
        mock_status.get_pre_module.return_value = "Splitter"
        mock_status.get_result.return_value = {
            "train": pd.DataFrame({"A": [1, 2]}),
            "validation": pd.DataFrame({"A": [3]}),
        }
        mock_status.get_metadata.return_value = Mock(spec=SchemaMetadata)

        result = operator.set_input(mock_status)

        assert result["data"].equals(pd.DataFrame({"A": [1, 2]}))

    def test_set_input_from_loader(self):
        """測試從 Loader 設定輸入"""
        config = {"method": "default"}
        test_data = pd.DataFrame({"A": [1, 2, 3]})

        operator = PreprocessorOperator(config)

        mock_status = Mock()
        mock_status.get_pre_module.return_value = "Loader"
        mock_status.get_result.return_value = test_data
        mock_status.get_metadata.return_value = Mock(spec=SchemaMetadata)

        result = operator.set_input(mock_status)

        assert result["data"].equals(test_data)

    def test_get_result(self):
        """測試結果取得"""
        config = {"method": "default"}
        test_data = pd.DataFrame({"A": [1, 2, 3]})

        operator = PreprocessorOperator(config)
        operator.data_preproc = test_data

        with patch("copy.deepcopy", return_value=test_data) as mock_deepcopy:
            result = operator.get_result()

            mock_deepcopy.assert_called_once_with(test_data)
            assert result.equals(test_data)

    def test_get_metadata(self):
        """測試元資料取得"""
        config = {"method": "default"}
        mock_metadata = Mock(spec=SchemaMetadata)

        with patch("petsard.operator.Processor") as mock_processor_class:
            mock_processor = Mock()
            mock_processor._metadata = mock_metadata
            mock_processor._sequence = []
            mock_processor_class.return_value = mock_processor

            operator = PreprocessorOperator(config)
            operator.processor = mock_processor

            with patch("copy.deepcopy", return_value=mock_metadata) as mock_deepcopy:
                result = operator.get_metadata()

                mock_deepcopy.assert_called_once_with(mock_metadata)
                assert result == mock_metadata


class TestSynthesizerOperator:
    """測試 SynthesizerOperator"""

    def test_init(self):
        """測試初始化"""
        config = {"method": "sdv", "model": "GaussianCopula"}

        with patch("petsard.operator.Synthesizer") as mock_synthesizer_class:
            operator = SynthesizerOperator(config)

            mock_synthesizer_class.assert_called_once_with(**config)
            assert operator.data_syn is None

    def test_run(self):
        """測試執行"""
        config = {"method": "sdv", "model": "GaussianCopula"}
        input_data = {
            "data": pd.DataFrame({"A": [1, 2, 3]}),
            "metadata": Mock(spec=SchemaMetadata),
        }
        synthetic_data = pd.DataFrame({"A": [4, 5, 6]})

        with patch("petsard.operator.Synthesizer") as mock_synthesizer_class:
            mock_synthesizer = Mock()
            mock_synthesizer.fit_sample.return_value = synthetic_data
            mock_synthesizer_class.return_value = mock_synthesizer

            operator = SynthesizerOperator(config)
            operator._run(input_data)

            mock_synthesizer.create.assert_called_once_with(
                metadata=input_data["metadata"]
            )
            mock_synthesizer.fit_sample.assert_called_once_with(data=input_data["data"])
            assert operator.data_syn.equals(synthetic_data)

    def test_set_input_with_metadata(self):
        """測試有元資料的輸入設定"""
        config = {"method": "sdv"}
        test_data = pd.DataFrame({"A": [1, 2, 3]})
        mock_metadata = Mock(spec=SchemaMetadata)

        operator = SynthesizerOperator(config)

        mock_status = Mock()
        mock_status.metadata = {"Loader": mock_metadata}
        mock_status.get_pre_module.return_value = "Loader"
        mock_status.get_metadata.return_value = mock_metadata
        mock_status.get_result.return_value = test_data

        result = operator.set_input(mock_status)

        assert result["data"].equals(test_data)
        assert result["metadata"] == mock_metadata

    def test_set_input_without_metadata(self):
        """測試無元資料的輸入設定"""
        config = {"method": "sdv"}
        test_data = pd.DataFrame({"A": [1, 2, 3]})

        operator = SynthesizerOperator(config)

        mock_status = Mock()
        mock_status.metadata = {}
        mock_status.get_pre_module.return_value = "Loader"
        mock_status.get_result.return_value = test_data

        result = operator.set_input(mock_status)

        assert result["data"].equals(test_data)
        assert result["metadata"] is None

    def test_get_result(self):
        """測試結果取得"""
        config = {"method": "sdv"}
        synthetic_data = pd.DataFrame({"A": [1, 2, 3]})

        operator = SynthesizerOperator(config)
        operator.data_syn = synthetic_data

        with patch("copy.deepcopy", return_value=synthetic_data) as mock_deepcopy:
            result = operator.get_result()

            mock_deepcopy.assert_called_once_with(synthetic_data)
            assert result.equals(synthetic_data)


class TestConstrainerOperator:
    """測試 ConstrainerOperator"""

    def test_init_basic(self):
        """測試基本初始化"""
        config = {"field_constraints": {"A": {"min": 0, "max": 10}}}

        with patch("petsard.operator.Constrainer") as mock_constrainer_class:
            operator = ConstrainerOperator(config)

            mock_constrainer_class.assert_called_once()
            assert operator.sample_dict == {}

    def test_init_with_sampling_params(self):
        """測試包含採樣參數的初始化"""
        config = {
            "field_constraints": {"A": {"min": 0, "max": 10}},
            "target_rows": 1000,
            "sampling_ratio": 1.5,
            "max_trials": 100,
            "verbose_step": 10,
        }

        with patch("petsard.operator.Constrainer"):
            operator = ConstrainerOperator(config)

            assert operator.sample_dict["target_rows"] == 1000
            assert operator.sample_dict["sampling_ratio"] == 1.5
            assert operator.sample_dict["max_trials"] == 100
            assert operator.sample_dict["verbose_step"] == 10

    def test_transform_field_combinations(self):
        """測試欄位組合轉換"""
        config = {
            "field_combinations": [
                [{"field": "A", "value": 1}, {"field": "B", "value": 2}],
                [{"field": "C", "value": 3}, {"field": "D", "value": 4}],
            ]
        }

        with patch("petsard.operator.Constrainer"):
            operator = ConstrainerOperator(config)

            # 檢查是否轉換為 tuple
            transformed_config = operator.config
            assert isinstance(transformed_config["field_combinations"][0], tuple)
            assert isinstance(transformed_config["field_combinations"][1], tuple)

    def test_run_simple_apply(self):
        """測試簡單約束應用"""
        config = {"field_constraints": {"A": {"min": 0, "max": 10}}}
        input_data = {"data": pd.DataFrame({"A": [1, 2, 3]})}
        constrained_data = pd.DataFrame({"A": [1, 2, 3]})

        with patch("petsard.operator.Constrainer") as mock_constrainer_class:
            mock_constrainer = Mock()
            mock_constrainer.apply.return_value = constrained_data
            mock_constrainer_class.return_value = mock_constrainer

            operator = ConstrainerOperator(config)
            operator._run(input_data)

            mock_constrainer.apply.assert_called_once_with(input_data["data"])
            assert operator.constrained_data.equals(constrained_data)

    def test_run_resample_until_satisfy(self):
        """測試重採樣直到滿足約束"""
        config = {"field_constraints": {"A": {"min": 0, "max": 10}}, "target_rows": 100}
        input_data = {
            "data": pd.DataFrame({"A": [1, 2, 3]}),
            "synthesizer": Mock(),
            "postprocessor": Mock(),
        }
        constrained_data = pd.DataFrame({"A": [1, 2, 3]})

        with patch("petsard.operator.Constrainer") as mock_constrainer_class:
            mock_constrainer = Mock()
            mock_constrainer.resample_until_satisfy.return_value = constrained_data
            mock_constrainer_class.return_value = mock_constrainer

            operator = ConstrainerOperator(config)
            operator._run(input_data)

            mock_constrainer.resample_until_satisfy.assert_called_once()
            assert operator.constrained_data.equals(constrained_data)


class TestEvaluatorOperator:
    """測試 EvaluatorOperator"""

    def test_init(self):
        """測試初始化"""
        config = {"method": "sdmetrics"}

        with patch("petsard.operator.Evaluator") as mock_evaluator_class:
            operator = EvaluatorOperator(config)

            mock_evaluator_class.assert_called_once_with(**config)
            assert operator.evaluations is None

    def test_run(self):
        """測試執行"""
        config = {"method": "sdmetrics"}
        input_data = {
            "data": {
                "ori": pd.DataFrame({"A": [1, 2, 3]}),
                "syn": pd.DataFrame({"A": [4, 5, 6]}),
                "control": pd.DataFrame({"A": [7, 8, 9]}),
            }
        }
        evaluation_results = {"test_metric": pd.DataFrame({"score": [0.8]})}

        with patch("petsard.operator.Evaluator") as mock_evaluator_class:
            mock_evaluator = Mock()
            mock_evaluator.eval.return_value = evaluation_results
            mock_evaluator_class.return_value = mock_evaluator

            operator = EvaluatorOperator(config)
            operator._run(input_data)

            mock_evaluator.create.assert_called_once()
            mock_evaluator.eval.assert_called_once_with(**input_data)
            assert operator.evaluations == evaluation_results

    def test_set_input_with_splitter(self):
        """測試有 Splitter 的輸入設定"""
        config = {"method": "sdmetrics"}

        operator = EvaluatorOperator(config)

        mock_status = Mock()
        mock_status.status = {"Splitter": Mock()}
        mock_status.get_result.side_effect = lambda module: {
            "Splitter": {
                "train": pd.DataFrame({"A": [1, 2]}),
                "validation": pd.DataFrame({"A": [3]}),
            },
            "Synthesizer": pd.DataFrame({"A": [4, 5]}),
        }[module]
        mock_status.get_pre_module.return_value = "Synthesizer"

        result = operator.set_input(mock_status)

        assert "ori" in result["data"]
        assert "syn" in result["data"]
        assert "control" in result["data"]

    def test_set_input_without_splitter(self):
        """測試無 Splitter 的輸入設定"""
        config = {"method": "sdmetrics"}

        operator = EvaluatorOperator(config)

        mock_status = Mock()
        mock_status.status = {}
        mock_status.get_result.side_effect = lambda module: {
            "Loader": pd.DataFrame({"A": [1, 2, 3]}),
            "Synthesizer": pd.DataFrame({"A": [4, 5, 6]}),
        }[module]
        mock_status.get_pre_module.return_value = "Synthesizer"

        result = operator.set_input(mock_status)

        assert "ori" in result["data"]
        assert "syn" in result["data"]
        assert "control" not in result["data"]


class TestReporterOperator:
    """測試 ReporterOperator"""

    def test_init(self):
        """測試初始化"""
        config = {"method": "save_report"}

        with patch("petsard.operator.Reporter") as mock_reporter_class:
            operator = ReporterOperator(config)

            mock_reporter_class.assert_called_once_with(**config)
            assert operator.report == {}

    def test_run_save_report(self):
        """測試儲存報告執行"""
        config = {"method": "save_report"}
        input_data = {"data": {"test_data": pd.DataFrame({"A": [1, 2, 3]})}}

        with patch("petsard.operator.Reporter") as mock_reporter_class:
            mock_reporter = Mock()
            mock_reporter.result = {
                "Reporter": {
                    "eval_expt_name": "test_experiment",
                    "report": pd.DataFrame({"metric": [0.8, 0.9]}),
                }
            }
            mock_reporter_class.return_value = mock_reporter

            operator = ReporterOperator(config)
            operator._run(input_data)

            mock_reporter.create.assert_called_once_with(data=input_data["data"])
            mock_reporter.report.assert_called_once()
            assert "test_experiment" in operator.report

    def test_run_save_data(self):
        """測試儲存資料執行"""
        config = {"method": "save_data"}
        input_data = {"data": {"test_data": pd.DataFrame({"A": [1, 2, 3]})}}

        with patch("petsard.operator.Reporter") as mock_reporter_class:
            mock_reporter = Mock()
            mock_reporter.result = {"saved_data": "path/to/saved/data"}
            mock_reporter_class.return_value = mock_reporter

            operator = ReporterOperator(config)
            operator._run(input_data)

            assert operator.report == {"saved_data": "path/to/saved/data"}

    def test_set_input(self):
        """測試輸入設定"""
        config = {"method": "save_report"}

        operator = ReporterOperator(config)

        mock_status = Mock()
        mock_status.get_full_expt.return_value = {
            "Loader": "load_data",
            "Synthesizer": "synthesize",
        }
        mock_status.get_result.side_effect = lambda module: {
            "Loader": pd.DataFrame({"A": [1, 2, 3]}),
            "Synthesizer": pd.DataFrame({"A": [4, 5, 6]}),
        }[module]
        mock_status.get_report.return_value = {}

        result = operator.set_input(mock_status)

        assert "data" in result
        assert "exist_report" in result["data"]


if __name__ == "__main__":
    pytest.main([__file__])
