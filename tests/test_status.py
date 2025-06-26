"""
測試新的 Status 快照功能
"""

from unittest.mock import Mock

import pandas as pd

from petsard.config import Config
from petsard.metadater import SchemaMetadata
from petsard.operator import BaseOperator
from petsard.status import Status


class TestStatusSnapshots:
    """測試 Status 快照功能"""

    def setup_method(self):
        """設定測試環境"""
        config_dict = {
            "Loader": {"data": {"filepath": "benchmark://adult-income"}},
            "Splitter": {"split_data": {"train_split_ratio": 0.8}},
        }
        self.config = Config(config_dict)
        self.status = Status(self.config)

    def test_snapshot_creation(self):
        """測試快照建立"""
        # 建立模擬操作器
        mock_operator = Mock(spec=BaseOperator)
        mock_operator.get_result.return_value = pd.DataFrame({"A": [1, 2, 3]})

        # 建立模擬 SchemaMetadata
        mock_metadata = Mock(spec=SchemaMetadata)
        mock_metadata.schema_id = "test_schema"
        mock_operator.get_metadata.return_value = mock_metadata

        # 執行操作，應該會建立快照
        self.status.put("Loader", "data", mock_operator)

        # 檢查快照是否建立
        snapshots = self.status.get_snapshots()
        assert len(snapshots) == 1

        snapshot = snapshots[0]
        assert snapshot.module_name == "Loader"
        assert snapshot.experiment_name == "data"
        assert snapshot.metadata_after == mock_metadata

    def test_change_tracking(self):
        """測試變更追蹤"""
        # 建立模擬操作器
        mock_operator = Mock(spec=BaseOperator)
        mock_operator.get_result.return_value = pd.DataFrame({"A": [1, 2, 3]})

        # 建立模擬 SchemaMetadata
        mock_metadata = Mock(spec=SchemaMetadata)
        mock_metadata.schema_id = "test_schema"
        mock_operator.get_metadata.return_value = mock_metadata

        # 執行操作
        self.status.put("Loader", "data", mock_operator)

        # 檢查變更歷史
        changes = self.status.get_change_history()
        assert len(changes) == 1

        change = changes[0]
        assert change.change_type == "create"
        assert change.target_type == "schema"
        assert change.target_id == "test_schema"

    def test_metadata_evolution(self):
        """測試元資料演進追蹤"""
        # 建立第一個操作器
        mock_operator1 = Mock(spec=BaseOperator)
        mock_metadata1 = Mock(spec=SchemaMetadata)
        mock_metadata1.schema_id = "schema_v1"
        mock_operator1.get_metadata.return_value = mock_metadata1

        # 建立第二個操作器
        mock_operator2 = Mock(spec=BaseOperator)
        mock_metadata2 = Mock(spec=SchemaMetadata)
        mock_metadata2.schema_id = "schema_v2"
        mock_operator2.get_metadata.return_value = mock_metadata2

        # 執行兩次操作
        self.status.put("Loader", "data", mock_operator1)
        self.status.put("Preprocessor", "preprocess", mock_operator2)

        # 檢查元資料演進
        loader_evolution = self.status.get_metadata_evolution("Loader")
        preprocessor_evolution = self.status.get_metadata_evolution("Preprocessor")

        assert len(loader_evolution) == 1
        assert len(preprocessor_evolution) == 1

    def test_status_summary(self):
        """測試狀態摘要"""
        # 建立模擬操作器
        mock_operator = Mock(spec=BaseOperator)
        mock_metadata = Mock(spec=SchemaMetadata)
        mock_metadata.schema_id = "test_schema"
        mock_operator.get_metadata.return_value = mock_metadata

        # 執行操作
        self.status.put("Loader", "data", mock_operator)

        # 取得狀態摘要
        summary = self.status.get_status_summary()

        assert "sequence" in summary
        assert "active_modules" in summary
        assert "metadata_modules" in summary
        assert "total_snapshots" in summary
        assert "total_changes" in summary

        assert summary["total_snapshots"] == 1
        assert summary["total_changes"] == 1
        assert "Loader" in summary["active_modules"]
        assert "Loader" in summary["metadata_modules"]

    def test_snapshot_retrieval(self):
        """測試快照檢索"""
        # 建立模擬操作器
        mock_operator = Mock(spec=BaseOperator)
        mock_metadata = Mock(spec=SchemaMetadata)
        mock_metadata.schema_id = "test_schema"
        mock_operator.get_metadata.return_value = mock_metadata

        # 執行操作
        self.status.put("Loader", "data", mock_operator)

        # 取得快照
        snapshots = self.status.get_snapshots()
        snapshot_id = snapshots[0].snapshot_id

        # 根據 ID 檢索快照
        retrieved_snapshot = self.status.get_snapshot_by_id(snapshot_id)
        assert retrieved_snapshot is not None
        assert retrieved_snapshot.snapshot_id == snapshot_id

        # 根據模組檢索快照
        loader_snapshots = self.status.get_snapshots("Loader")
        assert len(loader_snapshots) == 1
        assert loader_snapshots[0].module_name == "Loader"


class TestStatusTiming:
    """測試 Status 統一計時系統"""

    def setup_method(self):
        """設定測試環境"""
        config_dict = {
            "Loader": {"data": {"filepath": "benchmark://adult-income"}},
            "Synthesizer": {"method": "sdv"},
        }
        self.config = Config(config_dict)
        self.status = Status(self.config)

    def test_timing_log_handler_setup(self):
        """測試 TimingLogHandler 設置"""
        import logging

        # 檢查 handler 是否正確設置
        assert self.status._timing_handler is not None
        assert isinstance(self.status._timing_handler, logging.Handler)

        # 檢查是否添加到 PETsARD logger
        petsard_logger = logging.getLogger("PETsARD")
        assert self.status._timing_handler in petsard_logger.handlers

    def test_timing_message_parsing(self):
        """測試時間訊息解析"""
        import logging

        # 建立測試 log record
        logger = logging.getLogger("PETsARD.test")

        # 設置實驗名稱映射
        self.status._current_experiments["TestOp"] = "test_exp"

        # 模擬開始計時訊息
        start_time = 1000.0
        logger.info(f"TIMING_START|TestOp|run|{start_time}")

        # 檢查是否有活躍的計時記錄
        timing_key = "TestOp_test_exp_run"
        assert timing_key in self.status._active_timings

        # 模擬結束計時訊息
        end_time = 1001.5
        duration = 1.5
        logger.info(f"TIMING_END|TestOp|run|{end_time}|{duration}")

        # 檢查計時記錄是否完成
        assert timing_key not in self.status._active_timings
        timing_records = self.status.get_timing_records()
        assert len(timing_records) == 1

        record = timing_records[0]
        assert record.module_name == "TestOp"
        assert record.experiment_name == "test_exp"
        assert record.step_name == "run"
        assert record.duration_seconds == duration
        assert record.context["status"] == "completed"

    def test_timing_error_handling(self):
        """測試錯誤情況下的計時記錄"""
        import logging

        logger = logging.getLogger("PETsARD.test")
        self.status._current_experiments["ErrorOp"] = "error_exp"

        # 模擬錯誤計時訊息
        start_time = 1000.0
        end_time = 1001.0
        duration = 1.0
        error_msg = "Test error"

        logger.info(f"TIMING_START|ErrorOp|run|{start_time}")
        logger.info(f"TIMING_ERROR|ErrorOp|run|{end_time}|{duration}|{error_msg}")

        # 檢查錯誤記錄
        timing_records = self.status.get_timing_records()
        assert len(timing_records) == 1

        record = timing_records[0]
        assert record.context["status"] == "error"
        assert record.context["error"] == error_msg
        assert record.duration_seconds == duration

    def test_get_timing_records_filtering(self):
        """測試時間記錄過濾"""
        import logging

        logger = logging.getLogger("PETsARD.test")

        # 設置多個模組的實驗名稱
        self.status._current_experiments.update(
            {"LoaderOp": "load_exp", "SynthesizerOp": "synth_exp"}
        )

        # 模擬多個模組的計時
        modules = [
            ("LoaderOp", "load_exp", 1.0),
            ("SynthesizerOp", "synth_exp", 2.0),
            ("LoaderOp", "load_exp", 1.5),  # 同一模組的另一次執行
        ]

        start_time = 1000.0
        for i, (module, exp, duration) in enumerate(modules):
            current_start = start_time + i * 10
            current_end = current_start + duration

            logger.info(f"TIMING_START|{module}|run|{current_start}")
            logger.info(f"TIMING_END|{module}|run|{current_end}|{duration}")

        # 測試所有記錄
        all_records = self.status.get_timing_records()
        assert len(all_records) == 3

        # 測試特定模組過濾
        loader_records = self.status.get_timing_records("LoaderOp")
        assert len(loader_records) == 2
        assert all(r.module_name == "LoaderOp" for r in loader_records)

        synth_records = self.status.get_timing_records("SynthesizerOp")
        assert len(synth_records) == 1
        assert synth_records[0].module_name == "SynthesizerOp"

    def test_get_timing_report_data(self):
        """測試時間報告資料格式"""
        import logging

        import pandas as pd

        logger = logging.getLogger("PETsARD.test")
        self.status._current_experiments["TestOp"] = "test_exp"

        # 模擬計時記錄
        logger.info("TIMING_START|TestOp|run|1000.0")
        logger.info("TIMING_END|TestOp|run|1001.5|1.5")

        # 取得 DataFrame 格式
        timing_df = self.status.get_timing_report_data()

        assert isinstance(timing_df, pd.DataFrame)
        assert len(timing_df) == 1

        # 檢查必要欄位
        expected_columns = [
            "record_id",
            "module_name",
            "experiment_name",
            "step_name",
            "start_time",
            "end_time",
            "duration_seconds",
            "source",
            "status",
        ]
        for col in expected_columns:
            assert col in timing_df.columns

        # 檢查資料內容
        row = timing_df.iloc[0]
        assert row["module_name"] == "TestOp"
        assert row["experiment_name"] == "test_exp"
        assert row["step_name"] == "run"
        assert row["duration_seconds"] == 1.5
        assert row["source"] == "logging"
        assert row["status"] == "completed"

    def test_empty_timing_data(self):
        """測試空的時間資料"""
        # 沒有任何計時記錄時
        timing_records = self.status.get_timing_records()
        assert len(timing_records) == 0

        timing_df = self.status.get_timing_report_data()
        assert isinstance(timing_df, pd.DataFrame)
        assert len(timing_df) == 0

        # 過濾不存在的模組
        nonexistent_records = self.status.get_timing_records("NonExistentModule")
        assert len(nonexistent_records) == 0
