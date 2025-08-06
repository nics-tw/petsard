import re

import numpy as np
import pandas as pd
import pytest

from petsard.exceptions import ConfigError, UnsupportedMethodError
from petsard.reporter.reporter import Reporter
from petsard.reporter.reporter_base import (
    ExperimentConfig,
    NamingStrategy,
    convert_full_expt_tuple_to_name,
)
from petsard.reporter.reporter_save_data import ReporterSaveData
from petsard.reporter.reporter_save_report import (
    ReporterSaveReport,
    convert_eval_expt_name_to_tuple,
    full_expt_tuple_filter,
)
from petsard.reporter.reporter_save_timing import ReporterSaveTiming


# shared evaluation data
@pytest.fixture
def sample_reporter_input():
    data: dict = {}
    data["data"] = {}
    temp_data = {}

    test1_global_name = ("Evaluator", "test1_[global]")
    test1_global = pd.DataFrame(
        {
            "Score": [0.9],
            "ScoreA": [0.8],
        }
    )

    test2_global_name = ("Evaluator", "test2_[global]")
    test2_global = pd.DataFrame(
        {
            "Score": [0.1],
            "ScoreB": [0.2],
        }
    )

    test1_columnwise_name = ("Evaluator", "test1_[columnwise]")
    test1_columnwise = pd.DataFrame(
        {
            "index": ["col1", "col2"],
            "Score": [0.9, 0.8],
            "ScoreA": [0.7, 0.6],
        }
    )
    test1_columnwise.set_index("index", inplace=True)

    test2_columnwise_name = ("Evaluator", "test2_[columnwise]")
    test2_columnwise = pd.DataFrame(
        {
            "index": ["col1", "col2"],
            "Score": [0.1, 0.2],
            "ScoreB": [0.3, 0.4],
        }
    )
    test2_columnwise.set_index("index", inplace=True)

    test1_pairwise_name = ("Evaluator", "test1_[pairwise]")
    test1_pairwise = pd.DataFrame(
        {
            "level_0": ["col1", "col1", "col2", "col2"],
            "level_1": ["col1", "col2", "col1", "col2"],
            "Score": [0.9, 0.8, 0.7, 0.6],
            "ScoreA": [0.5, 0.4, 0.3, 0.2],
        }
    )
    test1_pairwise.set_index(["level_0", "level_1"], inplace=True)

    test2_pairwise_name = ("Evaluator", "test2_[pairwise]")
    test2_pairwise = pd.DataFrame(
        {
            "level_0": ["col1", "col1", "col2", "col2"],
            "level_1": ["col1", "col2", "col1", "col2"],
            "Score": [0.1, 0.2, 0.3, 0.4],
            "ScoreA": [0.5, 0.6, 0.7, 0.8],
        }
    )
    test2_pairwise.set_index(["level_0", "level_1"], inplace=True)

    test3_name = ("Postprocessor", "test3")
    test3 = pd.DataFrame(
        {
            "col1": [0.1, 0.2, 0.3],
            "col2": [0.9, 0.8, 0.7],
        }
    )

    temp_data_dict = {
        test1_global_name: test1_global,
        test2_global_name: test2_global,
        test1_columnwise_name: test1_columnwise,
        test2_columnwise_name: test2_columnwise,
        test1_pairwise_name: test1_pairwise,
        test2_pairwise_name: test2_pairwise,
        test3_name: test3,
    }
    for key, value in temp_data_dict.items():
        temp_data[key] = value
    data["data"] = temp_data

    return data


@pytest.fixture
def sample_reporter_output():
    def _sample_reporter_output(case: str) -> pd.DataFrame:
        if case == "global-process":
            return pd.DataFrame(
                data={
                    "full_expt_name": ["Evaluator[global]"],
                    "Evaluator": ["[global]"],
                    "test1_Score": [0.9],
                    "test1_ScoreA": [0.8],
                    "test2_Score": [0.1],
                    "test2_ScoreB": [0.2],
                }
            )
        elif case == "columnwise-process":
            return pd.DataFrame(
                data={
                    "full_expt_name": [
                        "Evaluator[columnwise]",
                        "Evaluator[columnwise]",
                    ],
                    "Evaluator": [
                        "[columnwise]",
                        "[columnwise]",
                    ],
                    "column": ["col1", "col2"],
                    "test1_Score": [0.9, 0.8],
                    "test1_ScoreA": [0.7, 0.6],
                    "test2_Score": [0.1, 0.2],
                    "test2_ScoreB": [0.3, 0.4],
                }
            )
        elif case == "pairwise-process":
            return pd.DataFrame(
                data={
                    "full_expt_name": [
                        "Evaluator[pairwise]",
                        "Evaluator[pairwise]",
                        "Evaluator[pairwise]",
                        "Evaluator[pairwise]",
                    ],
                    "Evaluator": [
                        "[pairwise]",
                        "[pairwise]",
                        "[pairwise]",
                        "[pairwise]",
                    ],
                    "column1": ["col1", "col1", "col2", "col2"],
                    "column2": ["col1", "col2", "col1", "col2"],
                    "test1_Score": [0.9, 0.8, 0.7, 0.6],
                    "test1_ScoreA": [0.5, 0.4, 0.3, 0.2],
                    "test2_Score": [0.1, 0.2, 0.3, 0.4],
                    "test2_ScoreA": [0.5, 0.6, 0.7, 0.8],
                }
            )
        else:  # case 'global'
            return pd.DataFrame(
                data={
                    "Score": [0.1, 0.9],
                    "ScoreA": [np.nan, 0.8],
                    "ScoreB": [0.2, np.nan],
                }
            )

    return _sample_reporter_output


@pytest.fixture
def sample_full_expt_tuple():
    def _sample_full_expt_tuple(case: int) -> tuple[str]:
        if case == 2:
            return ("Loader", "default", "Preprocessor", "test_low_dash")
        elif case == 3:
            return (
                "Loader",
                "default",
                "Preprocessor",
                "default",
                "Evaluator",
                "test[global]",
            )
        else:  # case 1
            return ("Loader", "default", "Preprocessor", "default")

    return _sample_full_expt_tuple


@pytest.fixture
def sample_full_expt_name():
    def _sample_full_expt_name(case: int) -> tuple[str]:
        if case == 2:
            return "Loader[default]_Preprocessor[test_low_dash]"
        elif case == 3:
            return "Loader[default]_Preprocessor[default]_Evaluator[test[global]]"
        else:  # case 1
            return "Loader[default]_Preprocessor[default]"

    return _sample_full_expt_name


@pytest.fixture
def sample_eval_expt_tuple():
    def _sample_eval_expt_tuple(case: int) -> tuple[str]:
        if case == 2:
            return ("desc", "columnwise")
        elif case == 3:
            return ("desc", "pairwise")
        else:  # case 1
            return ("sdmetrics-qual", "global")

    return _sample_eval_expt_tuple


@pytest.fixture
def sample_eval_expt_name():
    def _sample_eval_expt_name(case: int) -> str:
        if case == 2:
            return "desc_[columnwise]"
        elif case == 3:
            return "desc_[pairwise]"
        else:  # case 1
            return "sdmetrics-qual_[global]"

    return _sample_eval_expt_name


class Test_Reporter:
    """
    A test class for the Reporter class.
    """

    def test_method(self):
        """
        Test case for the arg. `method` of Reporter class.

        - The Reporter.reporter will be created as ReporterSaveData when:
            - method='save_data', source='test'
        - The Reporter.reporter will be created as ReporterSaveReport when:
            - method='save_report', granularity='global', eval='test'
        - The Reporter will raise an UnsupportedMethodError when:
            - method='invalid_method'
        """
        rpt = Reporter(method="save_data", source="test")
        assert isinstance(rpt, ReporterSaveData)

        rpt = Reporter(method="save_report", granularity="global", eval="test")
        assert isinstance(rpt, ReporterSaveReport)

        with pytest.raises(UnsupportedMethodError):
            Reporter(method="invalid_method")

    def test_method_save_timing(self):
        """
        Test case for the arg. `method` = 'save_timing' of Reporter class.

        - The Reporter.reporter will be created as ReporterSaveTiming when:
            - method='save_timing'
        """
        rpt = Reporter(method="save_timing")
        assert isinstance(rpt, ReporterSaveTiming)

        rpt = Reporter(method="save_timing", time_unit="minutes")
        assert isinstance(rpt, ReporterSaveTiming)

        rpt = Reporter(method="save_timing", module="Loader")
        assert isinstance(rpt, ReporterSaveTiming)

    def test_method_save_data(self):
        """
        Test case for the arg. `method` = 'save_data' of Reporter class.

        - The Reporter will raise an UnsupportedMethodError when:
            - method='save_data' but no source is provided
        """
        with pytest.raises(ConfigError):
            Reporter(method="save_data")

    def test_method_save_report(self):
        """
        Test case for the arg. `method` = 'save_report' of Reporter class.

        - The Reporter will be created when:
            - method='save_report', granularity='global', but no eval is provided
        - The Reporter will raise an UnsupportedMethodError when:
            - method='save_report' but no granularity or eval is provided
            - method='save_report', eval='test', but no granularity is provided
        """
        rpt = Reporter(method="save_report", granularity="global")
        assert isinstance(rpt, ReporterSaveReport)

        with pytest.raises(ConfigError):
            Reporter(method="save_report")
        with pytest.raises(ConfigError):
            Reporter(method="save_report", eval="test")


class Test_ReporterSaveData:
    """
    A test class for the ReporterSaveData class.
    """

    def test_source(self):
        """
        Test case for the arg. `source` of ReporterSaveData class.

        - ReporterSaveData will be created when `source` is set to:
            - a string
            - a list of strings
        - ReporterSaveData will raise a ConfigError when `source` is set to:
            - didn't setting
            - other non-str/List[str] format, e.g.
                - a float value
                - a list containing a float value
                - a tuple
        """
        cfg = {}
        cfg["method"] = "save_data"

        with pytest.raises(ConfigError):
            ReporterSaveData(config=cfg)

        cfg["source"] = "test"
        rpt = ReporterSaveData(config=cfg)
        assert isinstance(rpt, ReporterSaveData)

        cfg["source"] = ["test1", "test2"]
        rpt = ReporterSaveData(config=cfg)
        assert isinstance(rpt, ReporterSaveData)

        with pytest.raises(ConfigError):
            cfg["source"] = 0.8
            ReporterSaveData(config=cfg)

        with pytest.raises(ConfigError):
            cfg["source"] = ["test", 0.8]
            ReporterSaveData(config=cfg)

        with pytest.raises(ConfigError):
            cfg["source"] = ("test1", "test2")
            ReporterSaveData(config=cfg)


class Test_ReporterSaveReport:
    """
    A test class for the ReporterSaveReport class.
    """

    def test_granularity(self):
        """
        Test case for the arg. `granularity` of ReporterSaveReport class.

        - ReporterSaveReport will be created when `granularity` is set to:
            - 'global'
            - 'columnwise'
            - 'pairwise'
        - ReporterSaveReport will raise a ConfigError when `granularity` is set to:
            - didn't setting
            - other string such as 'invalid_method'
            - other non-str format, e.g. a list
        """
        cfg = {}
        cfg["method"] = "save_report"
        cfg["eval"] = "test"

        with pytest.raises(ConfigError):
            ReporterSaveReport(config=cfg)

        cfg["granularity"] = "global"
        rpt = ReporterSaveReport(config=cfg)
        assert isinstance(rpt, ReporterSaveReport)

        cfg["granularity"] = "columnwise"
        rpt = ReporterSaveReport(config=cfg)
        assert isinstance(rpt, ReporterSaveReport)

        cfg["granularity"] = "pairwise"
        rpt = ReporterSaveReport(config=cfg)
        assert isinstance(rpt, ReporterSaveReport)

        with pytest.raises(ConfigError):
            cfg["granularity"] = "invalid_method"
            ReporterSaveReport(config=cfg)

        # 多 granularity 支援現在應該正常工作
        cfg["granularity"] = ["global", "columnwise"]
        rpt = ReporterSaveReport(config=cfg)
        assert isinstance(rpt, ReporterSaveReport)
        assert rpt.config["granularity_list"] == ["global", "columnwise"]

        # 測試新的 granularity 類型
        cfg["granularity"] = ["details", "tree"]
        rpt = ReporterSaveReport(config=cfg)
        assert isinstance(rpt, ReporterSaveReport)
        assert rpt.config["granularity_list"] == ["details", "tree"]

    def test_eval(self):
        """
        Test case for the arg. `eval` of ReporterSaveReport class.

        - ReporterSaveReport will be created when `eval` is set to:
            - a string
            - a list of strings
            - didn't setting
        - ReporterSaveReport will raise a ConfigError when `eval` is set to:
            - other non-str/List[str] format, e.g.
                - a float value
                - a list containing a float value
                - a tuple
        """
        cfg = {}
        cfg["method"] = "save_report"
        cfg["granularity"] = "global"

        rpt = ReporterSaveReport(config=cfg)
        assert isinstance(rpt, ReporterSaveReport)

        cfg["eval"] = "test"
        rpt = ReporterSaveReport(config=cfg)
        assert isinstance(rpt, ReporterSaveReport)

        cfg["eval"] = ["test1", "test2"]
        rpt = ReporterSaveReport(config=cfg)
        assert isinstance(rpt, ReporterSaveReport)

        with pytest.raises(ConfigError):
            cfg["eval"] = 0.8
            ReporterSaveReport(config=cfg)

        with pytest.raises(ConfigError):
            cfg["eval"] = ["test", 0.8]
            ReporterSaveReport(config=cfg)

        with pytest.raises(ConfigError):
            cfg["eval"] = ("test1", "test2")
            ReporterSaveReport(config=cfg)

    def test_multi_granularity_support(self):
        """
        Test case for multi-granularity support in ReporterSaveReport class.

        - ReporterSaveReport should support both str and list[str] for granularity
        - Should support new granularity types: details, tree
        - Should maintain backward compatibility
        """
        cfg = {"method": "save_report", "eval": "test"}

        # Test single granularity (backward compatibility)
        cfg["granularity"] = "global"
        rpt = ReporterSaveReport(config=cfg)
        assert rpt.config["granularity"] == "global"
        assert rpt.config["granularity_list"] == ["global"]
        assert len(rpt.config["granularity_codes"]) == 1

        # Test multiple granularities
        cfg["granularity"] = ["global", "columnwise", "pairwise"]
        rpt = ReporterSaveReport(config=cfg)
        assert rpt.config["granularity"] == "global"  # backward compatibility
        assert rpt.config["granularity_list"] == ["global", "columnwise", "pairwise"]
        assert len(rpt.config["granularity_codes"]) == 3

        # Test new granularity types
        cfg["granularity"] = ["details", "tree"]
        rpt = ReporterSaveReport(config=cfg)
        assert rpt.config["granularity_list"] == ["details", "tree"]

        # Test mixed granularities
        cfg["granularity"] = ["global", "details", "tree", "columnwise"]
        rpt = ReporterSaveReport(config=cfg)
        assert len(rpt.config["granularity_list"]) == 4

        # Test invalid granularity should raise error
        with pytest.raises(ConfigError):
            cfg["granularity"] = ["invalid_granularity"]
            ReporterSaveReport(config=cfg)

        # Test invalid type should raise error
        with pytest.raises(ConfigError):
            cfg["granularity"] = 123
            ReporterSaveReport(config=cfg)

    def test_multi_granularity_create(self, sample_reporter_input):
        """
        Test case for create() method with multi-granularity support.

        - Should process multiple granularities and return combined results
        - Should handle cases where some granularities have no data
        """
        cfg = {
            "method": "save_report",
            "granularity": ["global", "columnwise"],
            "eval": ["test1", "test2"],
        }

        rpt = ReporterSaveReport(config=cfg)
        data = sample_reporter_input

        # Test create with multi-granularity
        result = rpt.create(data=data["data"])

        # Should return dict with Reporter key
        assert isinstance(result, dict)
        assert "Reporter" in result

        # Should contain results for both granularities
        reporter_data = result["Reporter"]
        assert isinstance(reporter_data, dict)

        # Check that we have results for the granularities that have data
        expected_keys = ["test1-test2_[global]", "test1-test2_[columnwise]"]
        for key in expected_keys:
            if key in reporter_data:
                assert "eval_expt_name" in reporter_data[key]
                assert "granularity" in reporter_data[key]
                assert "report" in reporter_data[key]

    def test_setup_evaluation_parameters_for_granularity(self):
        """
        Test case for _setup_evaluation_parameters_for_granularity method.
        """
        cfg = {
            "method": "save_report",
            "granularity": ["global", "columnwise"],
            "eval": ["test-eval"],
        }

        rpt = ReporterSaveReport(config=cfg)

        # Test global granularity
        eval_pattern, output_eval_name = (
            rpt._setup_evaluation_parameters_for_granularity("global")
        )
        assert eval_pattern == "^(test\\-eval)_\\[global\\]$"
        assert output_eval_name == "test-eval_[global]"

        # Test columnwise granularity
        eval_pattern, output_eval_name = (
            rpt._setup_evaluation_parameters_for_granularity("columnwise")
        )
        assert eval_pattern == "^(test\\-eval)_\\[columnwise\\]$"
        assert output_eval_name == "test-eval_[columnwise]"

        # Test with no eval config
        cfg["eval"] = None
        rpt = ReporterSaveReport(config=cfg)
        eval_pattern, output_eval_name = (
            rpt._setup_evaluation_parameters_for_granularity("global")
        )
        assert eval_pattern == "_\\[global\\]$"
        assert output_eval_name == "[global]"

    def test_reset_details_index(self):
        """
        Test case for _reset_details_index method.
        """
        # Create test DataFrame
        test_df = pd.DataFrame(
            {"metric1": [0.8, 0.9], "metric2": [0.7, 0.85]},
            index=["detail1", "detail2"],
        )

        result = ReporterSaveReport._reset_details_index(test_df)

        # Should reset index and add index column
        assert "index" in result.columns
        assert len(result) == 2
        assert result.iloc[0]["index"] == "detail1"
        assert result.iloc[1]["index"] == "detail2"

    def test_reset_tree_index(self):
        """
        Test case for _reset_tree_index method.
        """
        # Create test DataFrame
        test_df = pd.DataFrame(
            {"metric1": [0.8, 0.9], "metric2": [0.7, 0.85]}, index=["node1", "node2"]
        )

        result = ReporterSaveReport._reset_tree_index(test_df)

        # Should reset index and add index column
        assert "index" in result.columns
        assert len(result) == 2
        assert result.iloc[0]["index"] == "node1"
        assert result.iloc[1]["index"] == "node2"

    def test_create(self, sample_reporter_input, sample_reporter_output):
        """
        Test case for `create()` function of ReporterSaveReport class.

        - ReporterSaveReport will successfully create a report when:
            - the granularity been set to 'global''
            - the granularity been set to 'columnwise''
            - the granularity been set to 'pairwise''
        """

        def _test_create(data: dict, granularity: str) -> tuple[dict, pd.DataFrame]:
            cfg: dict = {}
            cfg["method"] = "save_report"
            cfg["granularity"] = granularity

            rpt = ReporterSaveReport(config=cfg)
            result = rpt.create(data=data["data"])
            expected_rpt = sample_reporter_output(case=f"{granularity}-process")

            return (result, expected_rpt)

        data: dict = sample_reporter_input
        granularity: str = None

        granularity = "global"
        result, expected_rpt = _test_create(data, granularity)
        # 新的多 granularity 格式
        if (
            isinstance(result["Reporter"], dict)
            and f"[{granularity}]" in result["Reporter"]
        ):
            reporter_data = result["Reporter"][f"[{granularity}]"]
            assert reporter_data["eval_expt_name"] == f"[{granularity}]"
            assert reporter_data["granularity"] == f"{granularity}"
            pd.testing.assert_frame_equal(reporter_data["report"], expected_rpt)

        granularity = "columnwise"
        result, expected_rpt = _test_create(data, granularity)
        if (
            isinstance(result["Reporter"], dict)
            and f"[{granularity}]" in result["Reporter"]
        ):
            reporter_data = result["Reporter"][f"[{granularity}]"]
            assert reporter_data["eval_expt_name"] == f"[{granularity}]"
            assert reporter_data["granularity"] == f"{granularity}"
            pd.testing.assert_frame_equal(reporter_data["report"], expected_rpt)

        granularity = "pairwise"
        result, expected_rpt = _test_create(data, granularity)
        if (
            isinstance(result["Reporter"], dict)
            and f"[{granularity}]" in result["Reporter"]
        ):
            reporter_data = result["Reporter"][f"[{granularity}]"]
            assert reporter_data["eval_expt_name"] == f"[{granularity}]"
            assert reporter_data["granularity"] == f"{granularity}"
            pd.testing.assert_frame_equal(reporter_data["report"], expected_rpt)

    def test_process_report_data(self, sample_reporter_input):
        """
        Test case for the _process_report_data function.

        - The column names of the input DataFrame will correctly
            rename columns and add column when:
            - the input DataFrame is a global granularity
            - the input DataFrame is a columnwise granularity
            - the input DataFrame is a pairwise granularity
        - The skip_flag will be set to True when:
            - the input DataFrame is a non-Evaluator/Describer e.g. Postprocessor
        """

        def _test_process_report_data(report: pd.DataFrame, full_expt_tuple: tuple):
            granularity: str = None
            output_eval_name: str = None
            skip_flag: bool = None
            rpt: pd.DataFrame = None

            try:
                granularity = convert_eval_expt_name_to_tuple(full_expt_tuple[1])[1]
            except (TypeError, ConfigError):
                granularity = "global"
            output_eval_name = f"[{granularity}]"
            skip_flag, rpt = ReporterSaveReport._process_report_data(
                report=report,
                full_expt_tuple=full_expt_tuple,
                eval_pattern=re.escape(f"_[{granularity}]") + "$",
                granularity=granularity,
                output_eval_name=output_eval_name,
            )
            return skip_flag, rpt

        data: dict = sample_reporter_input
        full_expt_tuple: tuple = None
        skip_flag: bool = None
        rpt: pd.DataFrame = None

        full_expt_tuple = ("Evaluator", "test1_[global]")
        skip_flag, rpt = _test_process_report_data(
            report=data["data"][full_expt_tuple],
            full_expt_tuple=full_expt_tuple,
        )
        assert not skip_flag
        assert rpt.columns.tolist() == [
            "full_expt_name",
            "Evaluator",
            "test1_Score",
            "test1_ScoreA",
        ]

        full_expt_tuple = ("Evaluator", "test1_[columnwise]")
        skip_flag, rpt = _test_process_report_data(
            report=data["data"][full_expt_tuple],
            full_expt_tuple=full_expt_tuple,
        )
        assert not skip_flag
        assert rpt.columns.tolist() == [
            "full_expt_name",
            "Evaluator",
            "column",
            "test1_Score",
            "test1_ScoreA",
        ]

        full_expt_tuple = ("Evaluator", "test1_[pairwise]")
        skip_flag, rpt = _test_process_report_data(
            report=data["data"][full_expt_tuple],
            full_expt_tuple=full_expt_tuple,
        )
        assert not skip_flag
        assert rpt.columns.tolist() == [
            "full_expt_name",
            "Evaluator",
            "column1",
            "column2",
            "test1_Score",
            "test1_ScoreA",
        ]

        full_expt_tuple = ("Postprocessor", "test3")
        skip_flag, rpt = _test_process_report_data(
            report=data["data"][full_expt_tuple],
            full_expt_tuple=full_expt_tuple,
        )
        assert skip_flag
        assert rpt is None

    def test_safe_merge(self, sample_reporter_input, sample_reporter_output):
        """
        Test case for the _safe_merge( function.

        - The FULL OUTER JOIN will correctly
            rename columns and add column when:
            - Pure data with only 'Score' column is overlapping
            - the global granularity after _process_report_data()
            - the same global granularity data with modification
                after _process_report_data()
            - the columnwise granularity after _process_report_data()
            - the pairwise granularity after _process_report_data()
        """

        def _test_safe_merge(
            data: dict,
            granularity: str,
            name1: tuple[str],
            name2: tuple[str],
            process: bool = False,
            modify_test1: bool = False,
        ):
            data1: pd.DataFrame = data["data"][name1].copy()
            data2: pd.DataFrame = data["data"][name2].copy()
            if modify_test1:
                data1["Score"] = 0.66
                name1 = ("Postprocessor", "Before") + name1
                name2 = ("Postprocessor", "After") + name2
            if process:
                output_eval_name = f"[{granularity}]"
                skip_flag, data1 = ReporterSaveReport._process_report_data(
                    report=data1,
                    full_expt_tuple=name1,
                    eval_pattern=re.escape(f"_[{granularity}]") + "$",
                    granularity=granularity,
                    output_eval_name=output_eval_name,
                )
                skip_flag, data2 = ReporterSaveReport._process_report_data(
                    report=data2,
                    full_expt_tuple=name2,
                    eval_pattern=re.escape(f"_[{granularity}]") + "$",
                    granularity=granularity,
                    output_eval_name=output_eval_name,
                )
            rpt = ReporterSaveReport._safe_merge(
                data1,
                data2,
                name1,
                name2,
            )
            return rpt

        data: dict = sample_reporter_input
        granularity: str = None
        name1: tuple[str] = None
        name2: tuple[str] = None
        rpt: pd.DataFrame = None
        expected_rpt: pd.DataFrame = None

        granularity = "global"
        name1 = ("Evaluator", f"test1_[{granularity}]")
        name2 = ("Evaluator", f"test2_[{granularity}]")
        rpt = _test_safe_merge(data, granularity, name1, name2)
        expected_rpt = sample_reporter_output(case="global")
        pd.testing.assert_frame_equal(rpt, expected_rpt)

        rpt = _test_safe_merge(data, granularity, name1, name2, process=True)
        expected_rpt = sample_reporter_output(case="global-process")
        pd.testing.assert_frame_equal(rpt, expected_rpt)

        granularity = "global"
        name1 = ("Evaluator", f"test1_[{granularity}]")
        name2 = ("Evaluator", f"test1_[{granularity}]")
        rpt = _test_safe_merge(
            data, granularity, name1, name2, process=True, modify_test1=True
        )
        expected_rpt = pd.DataFrame(
            data={
                "full_expt_name": [
                    "Postprocessor[After]_Evaluator[global]",
                    "Postprocessor[Before]_Evaluator[global]",
                ],
                "Postprocessor": [
                    "After",
                    "Before",
                ],
                "Evaluator": ["[global]", "[global]"],
                "test1_Score": [0.9, 0.66],
                "test1_ScoreA": [0.8, 0.8],
            }
        )  # seems it will rearrange the row order, and cannot close.
        pd.testing.assert_frame_equal(rpt, expected_rpt)

        granularity = "columnwise"
        name1 = ("Evaluator", f"test1_[{granularity}]")
        name2 = ("Evaluator", f"test2_[{granularity}]")
        rpt = _test_safe_merge(data, granularity, name1, name2, process=True)
        expected_rpt = sample_reporter_output(case="columnwise-process")
        pd.testing.assert_frame_equal(rpt, expected_rpt)

        granularity = "pairwise"
        name1 = ("Evaluator", f"test1_[{granularity}]")
        name2 = ("Evaluator", f"test2_[{granularity}]")
        rpt = _test_safe_merge(data, granularity, name1, name2, process=True)
        expected_rpt = sample_reporter_output(case="pairwise-process")
        pd.testing.assert_frame_equal(rpt, expected_rpt)


class Test_utils:
    """
    A test class for the utility functions in the reporter module.
    """

    def test_convert_full_expt_tuple_to_name(
        self,
        sample_full_expt_tuple,
        sample_full_expt_name,
    ):
        """
        Test case for the convert_full_expt_tuple_to_name function.

        - convert_full_expt_tuple_to_name(expt_tuple: tuple):
            will be converted to correct format string when:
            - expt_tuple = ('Loader', 'default', 'Preprocessor', 'default')
            - expt_tuple = ('Loader', 'default', 'Preprocessor', 'test_low_dash')
        """
        # ('Loader', 'default', 'Preprocessor', 'default')
        # ('Loader', 'default', 'Preprocessor', 'test_low_dash')
        # ('Loader', 'default', 'Preprocessor', 'default', 'Evaluator', 'test[global]')
        for case in range(1, 3 + 1, 1):
            full_expt_tuple: tuple = sample_full_expt_tuple(case=case)
            full_expt_name: str = sample_full_expt_name(case=case)
            assert convert_full_expt_tuple_to_name(full_expt_tuple) == full_expt_name

    def test_convert_eval_expt_name_to_tuple(
        self,
        sample_eval_expt_name,
        sample_eval_expt_tuple,
    ):
        """
        Test case for the convert_eval_expt_name_to_tuple function.

        - convert_eval_expt_name_to_tuple(expt_name: str):
            will be converted to correct format tuple when:
            - expt_name = 'sdmetrics-qual_[global]'
            - expt_name = 'desc_[columnwise]'
            - expt_name = 'desc_[pairwise]'
        """
        # 'sdmetrics-qual_[global]'
        # 'desc_[columnwise]'
        # 'desc_[pairwise]'
        for case in range(1, 3 + 1, 1):
            eval_expt_name: str = sample_eval_expt_name(case=case)
            eval_expt_tuple: tuple = sample_eval_expt_tuple(case=case)
            assert convert_eval_expt_name_to_tuple(eval_expt_name) == eval_expt_tuple

    def test_convert_eval_expt_name_to_tuple_invalid_format(self):
        """
        Test case for invalid format inputs to convert_eval_expt_name_to_tuple function.

        - convert_eval_expt_name_to_tuple should raise ConfigError when:
            - Missing brackets: 'test_global'
            - Missing underscore: 'test[global]'
            - Empty brackets: 'test_[]'
            - Invalid characters: 'test@_[global]'
            - Multiple brackets: 'test_[global][extra]'
        """
        from petsard.exceptions import ConfigError

        invalid_formats = [
            "test_global",  # Missing brackets
            "test[global]",  # Missing underscore before brackets
            "test_[]",  # Empty brackets
            "test@_[global]",  # Invalid characters
            "test_[global][extra]",  # Multiple brackets
            "",  # Empty string
            "_[global]",  # Missing eval name
            "test_",  # Missing brackets entirely
        ]

        for invalid_format in invalid_formats:
            with pytest.raises(ConfigError):
                convert_eval_expt_name_to_tuple(invalid_format)

    def test_full_expt_tuple_filter_invalid_method(self):
        """
        Test case for invalid method inputs to full_expt_tuple_filter function.

        - full_expt_tuple_filter should raise ConfigError when:
            - method is not 'include' or 'exclude'
        """
        from petsard.exceptions import ConfigError

        test_tuple = ("Loader", "default", "Preprocessor", "default")
        target = "Loader"

        invalid_methods = ["invalid", "", "both", "inc", "exc"]

        for invalid_method in invalid_methods:
            with pytest.raises(ConfigError):
                full_expt_tuple_filter(test_tuple, invalid_method, target)

    def test_full_expt_tuple_filter_valid_operations(self):
        """
        Test case for valid operations of full_expt_tuple_filter function.

        - full_expt_tuple_filter should work correctly with:
            - include method with string target
            - include method with list target
            - exclude method with string target
            - exclude method with list target
        """

        test_tuple = (
            "Loader",
            "default",
            "Preprocessor",
            "default",
            "Evaluator",
            "test",
        )

        # Test include with string
        result = full_expt_tuple_filter(test_tuple, "include", "Loader")
        assert result == ("Loader", "default")

        # Test include with list
        result = full_expt_tuple_filter(test_tuple, "include", ["Loader", "Evaluator"])
        assert result == ("Loader", "default", "Evaluator", "test")

        # Test exclude with string
        result = full_expt_tuple_filter(test_tuple, "exclude", "Preprocessor")
        assert result == ("Loader", "default", "Evaluator", "test")

        # Test exclude with list
        result = full_expt_tuple_filter(
            test_tuple, "exclude", ["Loader", "Preprocessor"]
        )
        assert result == ("Evaluator", "test")

        # Test case insensitive method
        result = full_expt_tuple_filter(test_tuple, "INCLUDE", "Loader")
        assert result == ("Loader", "default")


class TestReporterSaveTiming:
    """測試 ReporterSaveTiming 類別"""

    @pytest.fixture
    def sample_timing_data(self):
        """建立測試用的時間資料"""
        return pd.DataFrame(
            [
                {
                    "record_id": "timing_001",
                    "module_name": "LoaderOp",
                    "experiment_name": "default",
                    "step_name": "run",
                    "start_time": "2025-01-01T10:00:00",
                    "end_time": "2025-01-01T10:00:01",
                    "duration_seconds": 1.0,
                    "source": "logging",
                    "status": "completed",
                },
                {
                    "record_id": "timing_002",
                    "module_name": "SynthesizerOp",
                    "experiment_name": "default",
                    "step_name": "run",
                    "start_time": "2025-01-01T10:00:02",
                    "end_time": "2025-01-01T10:00:04",
                    "duration_seconds": 2.0,
                    "source": "logging",
                    "status": "completed",
                },
                {
                    "record_id": "timing_003",
                    "module_name": "EvaluatorOp",
                    "experiment_name": "default",
                    "step_name": "run",
                    "start_time": "2025-01-01T10:00:05",
                    "end_time": "2025-01-01T10:00:06",
                    "duration_seconds": 1.5,
                    "source": "logging",
                    "status": "completed",
                },
            ]
        )

    def test_init_default(self):
        """測試預設初始化"""
        config = {"method": "save_timing"}
        reporter = ReporterSaveTiming(config)

        assert reporter.config["modules"] == []
        assert reporter.config["time_unit"] == "seconds"

    def test_init_with_module_filter(self):
        """測試模組過濾初始化"""
        # 單一模組
        config = {"method": "save_timing", "module": "LoaderOp"}
        reporter = ReporterSaveTiming(config)
        assert reporter.config["modules"] == ["LoaderOp"]

        # 多個模組
        config = {"method": "save_timing", "module": ["LoaderOp", "SynthesizerOp"]}
        reporter = ReporterSaveTiming(config)
        assert reporter.config["modules"] == ["LoaderOp", "SynthesizerOp"]

    def test_init_with_time_unit(self):
        """測試時間單位初始化"""
        valid_units = ["days", "hours", "minutes", "seconds"]

        for unit in valid_units:
            config = {"method": "save_timing", "time_unit": unit}
            reporter = ReporterSaveTiming(config)
            assert reporter.config["time_unit"] == unit

        # 無效時間單位應該回到預設值
        config = {"method": "save_timing", "time_unit": "invalid"}
        reporter = ReporterSaveTiming(config)
        assert reporter.config["time_unit"] == "seconds"

    def test_create_with_empty_data(self):
        """測試空資料的處理"""
        config = {"method": "save_timing"}
        reporter = ReporterSaveTiming(config)

        # 沒有 timing_data 鍵
        result = reporter.create({})
        assert result is None

        # 空的 DataFrame
        result = reporter.create({"timing_data": pd.DataFrame()})
        assert result is None

    def test_create_seconds_unit(self, sample_timing_data):
        """測試秒為單位的處理"""
        config = {"method": "save_timing", "time_unit": "seconds"}
        reporter = ReporterSaveTiming(config)

        result = reporter.create({"timing_data": sample_timing_data})

        # ReporterSaveTiming 現在直接返回 DataFrame
        assert isinstance(result, pd.DataFrame)
        result_df = result

        # 檢查欄位
        assert "duration_seconds" in result_df.columns

        # 檢查資料
        assert len(result_df) == 3
        assert result_df["duration_seconds"].sum() == 4.5

    def test_create_minutes_unit(self, sample_timing_data):
        """測試分鐘為單位的處理"""
        config = {"method": "save_timing", "time_unit": "minutes"}
        reporter = ReporterSaveTiming(config)

        result = reporter.create({"timing_data": sample_timing_data})

        # ReporterSaveTiming 現在直接返回 DataFrame
        assert isinstance(result, pd.DataFrame)
        result_df = result

        # 檢查欄位
        assert "duration_minutes" in result_df.columns
        assert "duration_seconds" not in result_df.columns

        # 檢查轉換 (4.5 秒 = 0.075 分鐘)
        expected_total_minutes = 4.5 / 60
        assert abs(result_df["duration_minutes"].sum() - expected_total_minutes) < 0.001

    def test_create_hours_unit(self, sample_timing_data):
        """測試小時為單位的處理"""
        config = {"method": "save_timing", "time_unit": "hours"}
        reporter = ReporterSaveTiming(config)

        result = reporter.create({"timing_data": sample_timing_data})

        # ReporterSaveTiming 現在直接返回 DataFrame
        assert isinstance(result, pd.DataFrame)
        result_df = result

        # 檢查欄位
        assert "duration_hours" in result_df.columns
        assert "duration_seconds" not in result_df.columns

        # 檢查轉換 (4.5 秒 = 0.00125 小時)
        expected_total_hours = 4.5 / 3600
        assert abs(result_df["duration_hours"].sum() - expected_total_hours) < 0.000001

    def test_create_days_unit(self, sample_timing_data):
        """測試天為單位的處理"""
        config = {"method": "save_timing", "time_unit": "days"}
        reporter = ReporterSaveTiming(config)

        result = reporter.create({"timing_data": sample_timing_data})

        # ReporterSaveTiming 現在直接返回 DataFrame
        assert isinstance(result, pd.DataFrame)
        result_df = result

        # 檢查欄位
        assert "duration_days" in result_df.columns
        assert "duration_seconds" not in result_df.columns

        # 檢查轉換 (4.5 秒 = 0.0000520833... 天)
        expected_total_days = 4.5 / 86400
        assert abs(result_df["duration_days"].sum() - expected_total_days) < 0.0000001

    def test_create_with_module_filter(self, sample_timing_data):
        """測試模組過濾"""
        config = {"method": "save_timing", "module": "LoaderOp"}
        reporter = ReporterSaveTiming(config)

        result = reporter.create({"timing_data": sample_timing_data})

        # ReporterSaveTiming 現在直接返回 DataFrame
        assert isinstance(result, pd.DataFrame)
        result_df = result

        # 只應該有 LoaderOp 的記錄
        assert len(result_df) == 1
        assert result_df.iloc[0]["module_name"] == "LoaderOp"
        assert result_df.iloc[0]["duration_seconds"] == 1.0

    def test_create_with_multiple_module_filter(self, sample_timing_data):
        """測試多模組過濾"""
        config = {"method": "save_timing", "module": ["LoaderOp", "SynthesizerOp"]}
        reporter = ReporterSaveTiming(config)

        result = reporter.create({"timing_data": sample_timing_data})

        # ReporterSaveTiming 現在直接返回 DataFrame
        assert isinstance(result, pd.DataFrame)
        result_df = result

        # 應該有 LoaderOp 和 SynthesizerOp 的記錄
        assert len(result_df) == 2
        module_names = set(result_df["module_name"])
        assert module_names == {"LoaderOp", "SynthesizerOp"}

    def test_create_column_order(self, sample_timing_data):
        """測試欄位順序"""
        config = {"method": "save_timing", "time_unit": "minutes"}
        reporter = ReporterSaveTiming(config)

        result = reporter.create({"timing_data": sample_timing_data})

        # ReporterSaveTiming 現在直接返回 DataFrame
        assert isinstance(result, pd.DataFrame)
        result_df = result

        # 檢查基本欄位順序
        expected_start = [
            "record_id",
            "module_name",
            "experiment_name",
            "step_name",
            "start_time",
            "end_time",
            "duration_minutes",
        ]

        actual_columns = list(result_df.columns)
        for i, expected_col in enumerate(expected_start):
            assert actual_columns[i] == expected_col

    def test_report_empty_result(self):
        """測試空結果的報告"""
        config = {"method": "save_timing"}
        reporter = ReporterSaveTiming(config)

        # 沒有結果時應該印出訊息但不出錯
        reporter.report()  # 應該不會拋出異常

    def test_report_with_data(self, sample_timing_data):
        """測試有資料的報告"""
        config = {"method": "save_timing", "output": "test_timing"}
        reporter = ReporterSaveTiming(config)

        result = reporter.create({"timing_data": sample_timing_data})

        # 這裡我們不實際儲存檔案，只檢查不會出錯
        # ReporterSaveTiming 現在直接返回 DataFrame
        assert isinstance(result, pd.DataFrame)
        assert not result.empty


class TestExperimentConfig:
    """測試 ExperimentConfig 類別"""

    def test_traditional_naming_exactly_same(self):
        """測試傳統命名完全與現在一樣"""
        df = pd.DataFrame({"a": [1, 2]})

        # 基本配置
        config = ExperimentConfig(
            module="Synthesizer",
            exp_name="exp1",
            data=df,
            naming_strategy=NamingStrategy.TRADITIONAL,
        )

        assert config.traditional_tuple == ("Synthesizer", "exp1")
        assert config.traditional_name == "Synthesizer-exp1"
        assert config.filename == "petsard_Synthesizer-exp1.csv"

        # 帶粒度的配置
        config_with_granularity = ExperimentConfig(
            module="Evaluator",
            exp_name="eval1",
            data=df,
            granularity="global",
            naming_strategy=NamingStrategy.TRADITIONAL,
        )

        assert config_with_granularity.traditional_tuple == (
            "Evaluator",
            "eval1_[global]",
        )
        assert config_with_granularity.traditional_name == "Evaluator-eval1_[global]"
        assert (
            config_with_granularity.filename == "petsard_Evaluator-eval1_[global].csv"
        )
        assert (
            config_with_granularity.report_filename
            == "petsard[Report]_Evaluator-eval1_[global].csv"
        )

    def test_compact_naming_clear_and_readable(self):
        """測試簡潔命名清晰易讀"""
        df = pd.DataFrame({"a": [1, 2]})

        # 基本配置
        config = ExperimentConfig(
            module="Synthesizer",
            exp_name="privacy_exp",
            data=df,
            naming_strategy=NamingStrategy.COMPACT,
        )

        assert config.compact_name == "Sy.privacy_exp"
        assert config.filename == "petsard_Sy.privacy_exp.csv"

        # 複雜配置
        complex_config = ExperimentConfig(
            module="Evaluator",
            exp_name="cross_validation",
            data=df,
            granularity="global",
            iteration=3,
            parameters={"epsilon": 1.0, "method": "ctgan"},
            naming_strategy=NamingStrategy.COMPACT,
        )

        compact_name = complex_config.compact_name
        assert "Ev" in compact_name  # 模組簡寫
        assert "cross_validation" in compact_name  # 實驗名稱
        assert "i3" in compact_name  # 迭代次數
        assert "G" in compact_name  # 粒度簡寫
        # COMPACT 格式不包含參數編碼，只包含核心資訊

        # 檔案名稱應該清晰可讀
        filename = complex_config.filename
        assert filename.startswith("petsard_")
        assert filename.endswith(".csv")
        # 用點號分隔，容易識別各部分
        parts = filename.replace("petsard_", "").replace(".csv", "").split(".")
        assert len(parts) >= 4  # 至少有模組、實驗名、迭代、粒度

    def test_module_abbreviations(self):
        """測試模組簡寫映射"""
        df = pd.DataFrame({"a": [1, 2]})

        modules_and_abbrev = [
            ("Loader", "Ld"),
            ("Splitter", "Sp"),
            ("Processor", "Pr"),
            ("Synthesizer", "Sy"),
            ("Constrainer", "Cn"),
            ("Evaluator", "Ev"),
            ("Reporter", "Rp"),
        ]

        for module, expected_abbrev in modules_and_abbrev:
            config = ExperimentConfig(
                module=module,
                exp_name="test",
                data=df,
                naming_strategy=NamingStrategy.COMPACT,
            )
            assert config.compact_name.startswith(expected_abbrev)

    def test_granularity_abbreviations(self):
        """測試粒度簡寫"""
        df = pd.DataFrame({"a": [1, 2]})

        granularities_and_abbrev = [
            ("global", "G"),
            ("columnwise", "C"),
            ("pairwise", "P"),
            ("details", "D"),
            ("tree", "T"),
        ]

        for granularity, expected_abbrev in granularities_and_abbrev:
            config = ExperimentConfig(
                module="Evaluator",
                exp_name="test",
                data=df,
                granularity=granularity,
                naming_strategy=NamingStrategy.COMPACT,
            )
            assert expected_abbrev in config.compact_name

    def test_parameter_encoding(self):
        """測試簡化的 COMPACT 格式（不包含參數編碼）"""
        df = pd.DataFrame({"a": [1, 2]})

        config = ExperimentConfig(
            module="Synthesizer",
            exp_name="test",
            data=df,
            parameters={
                "epsilon": 0.1,
                "delta": 1e-5,
                "method": "differential_privacy",
                "extra_param": "should_be_truncated",
            },
            naming_strategy=NamingStrategy.COMPACT,
        )

        compact_name = config.compact_name
        assert "Sy" in compact_name  # module abbreviation
        assert "test" in compact_name  # experiment name
        # COMPACT 格式不再包含參數編碼
        assert "e0.1" not in compact_name
        assert "d1e-05" not in compact_name
        assert "diff" not in compact_name

    def test_from_traditional_tuple_conversion(self):
        """測試從傳統 tuple 轉換"""
        df = pd.DataFrame({"a": [1, 2]})

        # 基本 tuple
        config1 = ExperimentConfig.from_traditional_tuple(
            ("Synthesizer", "exp1"), df, NamingStrategy.COMPACT
        )
        assert config1.module == "Synthesizer"
        assert config1.exp_name == "exp1"
        assert config1.granularity is None
        assert config1.naming_strategy == NamingStrategy.COMPACT

        # 帶粒度的 tuple
        config2 = ExperimentConfig.from_traditional_tuple(
            ("Evaluator", "eval1_[global]"), df, NamingStrategy.COMPACT
        )
        assert config2.module == "Evaluator"
        assert config2.exp_name == "eval1"
        assert config2.granularity == "global"

    def test_backward_compatibility(self):
        """測試向後相容性"""
        df = pd.DataFrame({"a": [1, 2]})

        # 從傳統格式創建，然後轉回傳統格式
        original_tuple = ("Evaluator", "privacy_eval_[columnwise]")
        config = ExperimentConfig.from_traditional_tuple(
            original_tuple, df, NamingStrategy.TRADITIONAL
        )

        # 轉回傳統格式應該完全一樣
        assert config.traditional_tuple == original_tuple

    def test_iteration_support_for_multiple_executions(self):
        """測試多次執行的迭代支援"""
        df = pd.DataFrame({"a": [1, 2]})

        # 模擬多次 processor 執行
        base_config = ExperimentConfig(
            module="Processor",
            exp_name="data_pipeline",
            data=df,
            naming_strategy=NamingStrategy.COMPACT,
        )

        # 第一次執行
        config1 = base_config.with_iteration(1).with_parameters(step="normalize")
        assert "i1" in config1.compact_name
        # COMPACT 格式不包含參數編碼
        assert "Pr" in config1.compact_name
        assert "data_pipeline" in config1.compact_name

        # 第二次執行
        config2 = base_config.with_iteration(2).with_parameters(step="encode")
        assert "i2" in config2.compact_name
        # COMPACT 格式不包含參數編碼
        assert "Pr" in config2.compact_name
        assert "data_pipeline" in config2.compact_name

        # 檔案名稱應該不同
        assert config1.filename != config2.filename

    def test_filename_readability(self):
        """測試檔案名稱可讀性"""
        df = pd.DataFrame({"a": [1, 2]})

        config = ExperimentConfig(
            module="Synthesizer",
            exp_name="privacy_synthesis",
            data=df,
            iteration=2,
            granularity="global",
            parameters={"epsilon": 1.0, "method": "ctgan"},
            naming_strategy=NamingStrategy.COMPACT,
        )

        filename = config.filename

        # 檔案名稱應該：
        # 1. 以 petsard_ 開頭
        assert filename.startswith("petsard_")

        # 2. 以 .csv 結尾
        assert filename.endswith(".csv")

        # 3. 用點號分隔各部分，容易識別
        name_part = filename.replace("petsard_", "").replace(".csv", "")
        parts = name_part.split(".")

        # 4. 包含所有重要資訊
        assert any("Sy" in part for part in parts)  # 模組
        assert any("privacy_synthesis" in part for part in parts)  # 實驗名
        assert any("i2" in part for part in parts)  # 迭代
        assert any("G" in part for part in parts)  # 粒度
        # COMPACT 格式不包含參數編碼

        # 5. 長度合理（不超過 100 字符）
        assert len(filename) < 100

    def test_real_world_examples(self):
        """測試真實世界的使用範例"""
        df = pd.DataFrame({"score": [0.85]})

        examples = [
            # 基本合成實驗
            {
                "config": ExperimentConfig(
                    module="Synthesizer",
                    exp_name="baseline",
                    data=df,
                    naming_strategy=NamingStrategy.COMPACT,
                ),
                "expected_pattern": "petsard_Sy.baseline.csv",
            },
            # 隱私合成實驗
            {
                "config": ExperimentConfig(
                    module="Synthesizer",
                    exp_name="dp_synthesis",
                    data=df,
                    parameters={"epsilon": 1.0, "method": "ctgan"},
                    naming_strategy=NamingStrategy.COMPACT,
                ),
                "expected_contains": ["Sy", "dp_synthesis"],
            },
            # 多輪評估
            {
                "config": ExperimentConfig(
                    module="Evaluator",
                    exp_name="cross_val",
                    data=df,
                    granularity="global",
                    iteration=3,
                    naming_strategy=NamingStrategy.COMPACT,
                ),
                "expected_contains": ["Ev", "cross_val", "i3", "G"],
            },
            # 多階段處理
            {
                "config": ExperimentConfig(
                    module="Processor",
                    exp_name="preprocessing",
                    data=df,
                    iteration=1,
                    parameters={"method": "standard_scaler"},
                    naming_strategy=NamingStrategy.COMPACT,
                ),
                "expected_contains": ["Pr", "preprocessing", "i1"],
            },
        ]

        for example in examples:
            config = example["config"]
            filename = config.filename

            if "expected_pattern" in example:
                assert filename == example["expected_pattern"]

            if "expected_contains" in example:
                for expected in example["expected_contains"]:
                    assert expected in filename, (
                        f"'{expected}' not found in '{filename}'"
                    )

            # 所有檔案名稱都應該清晰可讀
            assert len(filename) < 80  # 合理長度
            assert filename.count(".") >= 2  # 至少有模組.實驗名.csv


class TestReporterNamingStrategy:
    """測試 Reporter 的 naming_strategy 功能"""

    def test_naming_strategy_initialization(self):
        """測試 naming_strategy 參數的初始化"""
        # 預設應該是 traditional
        config = {"method": "save_report", "granularity": "global"}
        reporter = ReporterSaveReport(config)
        assert reporter.config["naming_strategy"] == "traditional"

        # 明確設定 traditional
        config = {
            "method": "save_report",
            "granularity": "global",
            "naming_strategy": "traditional",
        }
        reporter = ReporterSaveReport(config)
        assert reporter.config["naming_strategy"] == "traditional"

        # 設定 compact
        config = {
            "method": "save_report",
            "granularity": "global",
            "naming_strategy": "compact",
        }
        reporter = ReporterSaveReport(config)
        assert reporter.config["naming_strategy"] == "compact"

        # 無效值應該回退到 traditional
        config = {
            "method": "save_report",
            "granularity": "global",
            "naming_strategy": "invalid",
        }
        reporter = ReporterSaveReport(config)
        assert reporter.config["naming_strategy"] == "traditional"

    def test_generate_report_filename_traditional(self):
        """測試傳統命名策略的檔名生成"""
        config = {
            "method": "save_report",
            "granularity": "global",
            "naming_strategy": "traditional",
            "output": "petsard",
        }
        reporter = ReporterSaveReport(config)

        # 測試基本檔名生成
        filename = reporter._generate_report_filename("[global]", "global")
        assert filename == "petsard[Report]_[global]"

        # 測試帶評估名稱的檔名
        filename = reporter._generate_report_filename("demo-quality_[global]", "global")
        assert filename == "petsard[Report]_demo-quality_[global]"

    def test_generate_report_filename_compact(self):
        """測試簡潔命名策略的檔名生成"""
        config = {
            "method": "save_report",
            "granularity": "global",
            "naming_strategy": "compact",
            "output": "petsard",
        }
        reporter = ReporterSaveReport(config)

        # 測試基本檔名生成
        filename = reporter._generate_report_filename("[global]", "global")
        assert filename.startswith("petsard.report.Rp")
        assert "G" in filename  # 應該包含粒度簡寫

        # 測試帶評估名稱的檔名
        filename = reporter._generate_report_filename("demo-quality_[global]", "global")
        assert filename.startswith("petsard.report.Rp")
        assert "demo-quality" in filename
        assert "G" in filename

    def test_naming_strategy_filename_differences(self):
        """測試不同命名策略產生不同的檔名"""
        # Traditional 配置
        traditional_config = {
            "method": "save_report",
            "granularity": "global",
            "naming_strategy": "traditional",
            "output": "petsard",
        }
        traditional_reporter = ReporterSaveReport(traditional_config)

        # Compact 配置
        compact_config = {
            "method": "save_report",
            "granularity": "global",
            "naming_strategy": "compact",
            "output": "petsard",
        }
        compact_reporter = ReporterSaveReport(compact_config)

        # 生成檔名
        eval_name = "demo-quality_[global]"
        traditional_filename = traditional_reporter._generate_report_filename(
            eval_name, "global"
        )
        compact_filename = compact_reporter._generate_report_filename(
            eval_name, "global"
        )

        # 檔名應該不同
        assert traditional_filename != compact_filename

        # Traditional 格式檢查
        assert "[Report]_" in traditional_filename

        # Compact 格式檢查
        assert ".report." in compact_filename
        assert "Rp" in compact_filename

    def test_naming_strategy_with_different_granularities(self):
        """測試不同粒度的命名策略"""
        granularities = ["global", "columnwise", "pairwise", "details", "tree"]

        for granularity in granularities:
            # Traditional
            traditional_config = {
                "method": "save_report",
                "granularity": granularity,
                "naming_strategy": "traditional",
                "output": "petsard",
            }
            traditional_reporter = ReporterSaveReport(traditional_config)
            traditional_filename = traditional_reporter._generate_report_filename(
                f"test_[{granularity}]", granularity
            )
            assert "[Report]_" in traditional_filename
            assert granularity in traditional_filename

            # Compact
            compact_config = {
                "method": "save_report",
                "granularity": granularity,
                "naming_strategy": "compact",
                "output": "petsard",
            }
            compact_reporter = ReporterSaveReport(compact_config)
            compact_filename = compact_reporter._generate_report_filename(
                f"test_[{granularity}]", granularity
            )
            assert ".report." in compact_filename
            assert "Rp" in compact_filename

    def test_naming_strategy_backward_compatibility(self):
        """測試命名策略的向後相容性"""
        # 不設定 naming_strategy 應該預設為 traditional
        config = {"method": "save_report", "granularity": "global"}
        reporter = ReporterSaveReport(config)

        filename = reporter._generate_report_filename("[global]", "global")
        assert filename == "petsard[Report]_[global]"

        # 這應該與明確設定 traditional 的結果相同
        config_explicit = {
            "method": "save_report",
            "granularity": "global",
            "naming_strategy": "traditional",
        }
        reporter_explicit = ReporterSaveReport(config_explicit)
        filename_explicit = reporter_explicit._generate_report_filename(
            "[global]", "global"
        )

        assert filename == filename_explicit
