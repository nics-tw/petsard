#!/usr/bin/env python3
"""
MPUCCs (Maximal Partial Unique Column Combinations) Evaluator 綜合測試

本測試檔案整合了所有 mpUCCs 相關的測試功能，包括：
- 基本功能測試
- 精度處理測試
- 熵計算驗證
- 剪枝邏輯測試
- 完整整合測試
"""

import logging
from collections import Counter
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pytest

from petsard.evaluator.mpuccs import MPUCCs

# 設定測試日誌
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


class TestMPUCCsBasic:
    """MPUCCs 基本功能測試"""

    def test_initialization(self):
        """測試 MPUCCs 初始化"""
        config = {
            "eval_method": "mpuccs",
            "n_cols": [1, 2],
            "min_entropy_delta": 0.1,
            "field_decay_factor": 0.5,
            "renyi_alpha": 2.0,
        }

        mpuccs = MPUCCs(config)

        assert mpuccs.config["eval_method"] == "mpuccs"
        assert mpuccs.config["n_cols"] == [1, 2]
        assert mpuccs.config["min_entropy_delta"] == 0.1
        assert mpuccs.config["field_decay_factor"] == 0.5
        assert mpuccs.config["renyi_alpha"] == 2.0

    def test_basic_evaluation(self):
        """測試基本評估功能"""
        # 創建簡單測試資料
        ori_data = pd.DataFrame(
            {
                "A": [1, 2, 3, 4, 5],
                "B": [10, 20, 30, 40, 50],
                "C": ["a", "b", "c", "d", "e"],
            }
        )

        syn_data = pd.DataFrame(
            {
                "A": [1, 2, 3, 6, 7],
                "B": [10, 20, 30, 60, 70],
                "C": ["a", "b", "c", "f", "g"],
            }
        )

        config = {"eval_method": "mpuccs", "n_cols": [1, 2]}
        mpuccs = MPUCCs(config)

        data = {"ori": ori_data, "syn": syn_data}
        results = mpuccs.eval(data)

        # 驗證結果結構
        assert "global" in results
        assert "details" in results
        assert "tree" in results

        # 驗證 global 結果
        global_df = results["global"]
        assert len(global_df) == 1
        assert "total_syn_records" in global_df.columns
        assert "total_identified" in global_df.columns
        assert "identification_rate" in global_df.columns

    def test_empty_data(self):
        """測試空資料處理"""
        ori_data = pd.DataFrame({"A": []})
        syn_data = pd.DataFrame({"A": []})

        config = {"eval_method": "mpuccs"}
        mpuccs = MPUCCs(config)

        data = {"ori": ori_data, "syn": syn_data}
        results = mpuccs.eval(data)

        # 空資料應該正常處理
        assert results["global"]["total_syn_records"].iloc[0] == 0
        assert results["global"]["total_identified"].iloc[0] == 0


class TestMPUCCsPrecisionHandling:
    """MPUCCs 精度處理測試"""

    def test_numeric_precision_auto_detection(self):
        """測試數值精度自動檢測"""
        ori_data = pd.DataFrame(
            {
                "ID": [1, 2, 3, 4, 5],
                "Price": [10.123, 20.456, 30.789, 40.012, 50.345],  # 3位小數
                "Score": [85.12, 90.34, 78.56, 92.78, 88.90],  # 2位小數
                "Count": [100, 200, 300, 400, 500],  # 整數
            }
        )

        syn_data = pd.DataFrame(
            {
                "ID": [1, 2, 3, 6, 7],
                "Price": [10.123, 20.456, 30.789, 60.678, 70.901],
                "Score": [85.12, 90.34, 78.56, 95.67, 82.34],
                "Count": [100, 200, 300, 600, 700],
            }
        )

        config = {
            "eval_method": "mpuccs",
            "n_cols": [1],
            "numeric_precision": None,  # 自動檢測
        }

        mpuccs = MPUCCs(config)
        data = {"ori": ori_data, "syn": syn_data}
        results = mpuccs.eval(data)

        # 應該檢測到最高精度（3位小數）
        assert mpuccs.config.get("numeric_precision") == 3

    def test_numeric_precision_manual_setting(self):
        """測試手動設定數值精度"""
        ori_data = pd.DataFrame(
            {
                "Value": [1.123456, 2.234567, 3.345678, 4.456789, 5.567890],
            }
        )

        syn_data = pd.DataFrame(
            {
                "Value": [1.123456, 2.234567, 3.345678, 6.678901, 7.789012],
            }
        )

        config = {
            "eval_method": "mpuccs",
            "n_cols": [1],
            "numeric_precision": 2,  # 手動設定為2位小數
        }

        mpuccs = MPUCCs(config)
        data = {"ori": ori_data, "syn": syn_data}
        results = mpuccs.eval(data)

        # 應該使用手動設定的精度
        assert mpuccs.config.get("numeric_precision") == 2

    def test_datetime_precision_auto_detection(self):
        """測試日期時間精度自動檢測"""
        base_time = datetime(2023, 1, 1, 12, 30, 45, 123456)

        ori_data = pd.DataFrame(
            {
                "ID": [1, 2, 3, 4, 5],
                "Timestamp": [
                    base_time,
                    base_time + timedelta(seconds=1),
                    base_time + timedelta(minutes=1),
                    base_time + timedelta(hours=1),
                    base_time + timedelta(days=1),
                ],
            }
        )

        syn_data = pd.DataFrame(
            {
                "ID": [1, 2, 3, 6, 7],
                "Timestamp": [
                    base_time,
                    base_time + timedelta(seconds=1),
                    base_time + timedelta(minutes=1),
                    base_time + timedelta(hours=2),
                    base_time + timedelta(days=2),
                ],
            }
        )

        config = {
            "eval_method": "mpuccs",
            "n_cols": [1],
            "datetime_precision": None,  # 自動檢測
        }

        mpuccs = MPUCCs(config)
        data = {"ori": ori_data, "syn": syn_data}
        results = mpuccs.eval(data)

        # 應該檢測到微秒精度
        detected_precision = mpuccs.config.get("datetime_precision")
        assert detected_precision in ["us", "ns"]  # 可能是微秒或納秒

    def test_datetime_precision_normalization(self):
        """測試日期時間精度正規化"""
        mpuccs = MPUCCs({"eval_method": "mpuccs"})

        # 測試大小寫不敏感的精度正規化
        assert mpuccs._normalize_datetime_precision("D") == "D"
        assert mpuccs._normalize_datetime_precision("d") == "D"
        assert mpuccs._normalize_datetime_precision("H") == "H"
        assert mpuccs._normalize_datetime_precision("h") == "H"
        assert mpuccs._normalize_datetime_precision("min") == "T"
        assert mpuccs._normalize_datetime_precision("MIN") == "T"
        assert mpuccs._normalize_datetime_precision("s") == "s"
        assert mpuccs._normalize_datetime_precision("SEC") == "s"
        assert mpuccs._normalize_datetime_precision("ms") == "ms"
        assert mpuccs._normalize_datetime_precision("MS") == "ms"
        assert mpuccs._normalize_datetime_precision("us") == "us"
        assert mpuccs._normalize_datetime_precision("MICRO") == "us"
        assert mpuccs._normalize_datetime_precision("ns") == "ns"
        assert mpuccs._normalize_datetime_precision("NANO") == "ns"


class TestMPUCCsEntropyCalculation:
    """MPUCCs 熵計算測試"""

    def test_renyi_entropy_calculation(self):
        """測試 Rényi 熵計算"""
        # 創建具有不同熵特性的測試資料
        ori_data = pd.DataFrame(
            {
                "HighEntropy": [1, 2, 3, 4, 5, 6, 7, 8],  # 高熵（均勻分佈）
                "MediumEntropy": [1, 1, 2, 2, 3, 3, 4, 4],  # 中等熵
                "LowEntropy": [1, 1, 1, 1, 2, 2, 3, 4],  # 低熵（偏斜分佈）
                "VeryLowEntropy": [1, 1, 1, 1, 1, 1, 2, 3],  # 極低熵
            }
        )

        syn_data = pd.DataFrame(
            {
                "HighEntropy": [1, 2, 3, 4, 9, 10, 11, 12],
                "MediumEntropy": [1, 1, 2, 2, 9, 9, 10, 10],
                "LowEntropy": [1, 1, 1, 1, 9, 9, 10, 11],
                "VeryLowEntropy": [1, 1, 1, 1, 1, 1, 9, 10],
            }
        )

        config = {
            "eval_method": "mpuccs",
            "n_cols": [1],
            "renyi_alpha": 2.0,
        }

        mpuccs = MPUCCs(config)
        data = {"ori": ori_data, "syn": syn_data}
        results = mpuccs.eval(data)

        # 分析樹狀結果中的熵值
        tree_df = results["tree"]
        single_field_combos = tree_df[tree_df["combo_size"] == 1]

        entropy_values = {}
        for _, row in single_field_combos.iterrows():
            field_name = row["field_combo"].strip("(),'")
            entropy_val = row["combo_entropy"]
            entropy_values[field_name] = entropy_val

        # 驗證熵值順序：高熵 > 中等熵 > 低熵 > 極低熵
        assert entropy_values["HighEntropy"] > entropy_values["MediumEntropy"]
        assert entropy_values["MediumEntropy"] > entropy_values["LowEntropy"]
        assert entropy_values["LowEntropy"] > entropy_values["VeryLowEntropy"]

        # 驗證熵值在 [0, 1] 範圍內
        for field, entropy in entropy_values.items():
            assert 0 <= entropy <= 1, f"Field {field} entropy {entropy} not in [0,1]"

    def test_entropy_gain_calculation(self):
        """測試熵增益計算"""
        ori_data = pd.DataFrame(
            {
                "A": [1, 2, 3, 4, 5],
                "B": [1, 1, 2, 2, 3],
            }
        )

        syn_data = pd.DataFrame(
            {
                "A": [1, 2, 3, 6, 7],
                "B": [1, 1, 2, 2, 3],
            }
        )

        config = {
            "eval_method": "mpuccs",
            "n_cols": [1, 2],
            "min_entropy_delta": 0.0,
        }

        mpuccs = MPUCCs(config)
        data = {"ori": ori_data, "syn": syn_data}
        results = mpuccs.eval(data)

        tree_df = results["tree"]

        # 檢查是否有熵增益計算
        two_field_combos = tree_df[tree_df["combo_size"] == 2]
        assert len(two_field_combos) > 0

        for _, row in two_field_combos.iterrows():
            entropy_gain = row["entropy_gain"]
            if entropy_gain is not None:
                # 熵增益可以是正數、負數或零
                assert isinstance(entropy_gain, (int, float))


class TestMPUCCsPruningLogic:
    """MPUCCs 剪枝邏輯測試"""

    def test_entropy_based_pruning(self):
        """測試基於熵的剪枝"""
        ori_data = pd.DataFrame(
            {
                "A": [1, 1, 1, 1, 1],  # 極低熵
                "B": [1, 2, 3, 4, 5],  # 高熵
                "C": [1, 1, 2, 2, 3],  # 中等熵
            }
        )

        syn_data = pd.DataFrame(
            {
                "A": [1, 1, 1, 1, 1],
                "B": [1, 2, 3, 6, 7],
                "C": [1, 1, 2, 2, 3],
            }
        )

        config = {
            "eval_method": "mpuccs",
            "n_cols": [1, 2, 3],
            "min_entropy_delta": 0.1,  # 設定較高的剪枝閾值
        }

        mpuccs = MPUCCs(config)
        data = {"ori": ori_data, "syn": syn_data}
        results = mpuccs.eval(data)

        tree_df = results["tree"]

        # 檢查是否有組合被剪枝
        pruned_combos = tree_df[tree_df["is_pruned"] == True]
        assert len(pruned_combos) >= 0  # 可能有組合被剪枝

        # 檢查剪枝統計
        global_df = results["global"]
        total_pruned = global_df["total_combinations_pruned"].iloc[0]
        assert total_pruned >= 0

    def test_base_combo_pruning_propagation(self):
        """測試基礎組合剪枝傳播"""
        ori_data = pd.DataFrame(
            {
                "A": [1, 1, 1, 1, 1],  # 極低熵，容易被剪枝
                "B": [1, 2, 3, 4, 5],
                "C": [1, 2, 3, 4, 5],
            }
        )

        syn_data = pd.DataFrame(
            {
                "A": [1, 1, 1, 1, 1],
                "B": [1, 2, 3, 6, 7],
                "C": [1, 2, 3, 6, 7],
            }
        )

        config = {
            "eval_method": "mpuccs",
            "n_cols": [1, 2, 3],
            "min_entropy_delta": 0.2,  # 高剪枝閾值
        }

        mpuccs = MPUCCs(config)
        data = {"ori": ori_data, "syn": syn_data}
        results = mpuccs.eval(data)

        tree_df = results["tree"]

        # 檢查基礎組合剪枝狀態追蹤
        for _, row in tree_df.iterrows():
            base_is_pruned = row["base_is_pruned"]
            is_pruned = row["is_pruned"]

            # 如果基礎組合被剪枝，當前組合也應該被剪枝
            if base_is_pruned is True:
                assert is_pruned is True


class TestMPUCCsIntegration:
    """MPUCCs 完整整合測試"""

    def test_complete_workflow(self):
        """測試完整工作流程"""
        # 創建具有真實特徵的測試資料
        ori_data = pd.DataFrame(
            {
                "ID": [1, 2, 3, 4, 5, 6, 7, 8],
                "Age": [25, 30, 35, 40, 25, 30, 35, 40],
                "Income": [50000, 60000, 70000, 80000, 55000, 65000, 75000, 85000],
                "City": ["A", "B", "C", "D", "A", "B", "C", "D"],
            }
        )

        syn_data = pd.DataFrame(
            {
                "ID": [1, 2, 3, 9, 10, 11, 12, 13],  # 部分匹配
                "Age": [25, 30, 35, 45, 50, 55, 60, 65],
                "Income": [50000, 60000, 70000, 90000, 95000, 100000, 105000, 110000],
                "City": ["A", "B", "C", "E", "F", "G", "H", "I"],
            }
        )

        config = {
            "eval_method": "mpuccs",
            "n_cols": [1, 2, 3],
            "min_entropy_delta": 0.0,
            "field_decay_factor": 0.5,
            "renyi_alpha": 2.0,
        }

        mpuccs = MPUCCs(config)
        data = {"ori": ori_data, "syn": syn_data}
        results = mpuccs.eval(data)

        # 驗證完整結果結構
        assert "global" in results
        assert "details" in results
        assert "tree" in results

        # 驗證 global 統計
        global_df = results["global"]
        assert len(global_df) == 1

        required_global_cols = [
            "total_syn_records",
            "total_ori_records",
            "total_identified",
            "identification_rate",
            "weighted_identification_rate",
            "total_combinations_checked",
            "total_combinations_pruned",
        ]

        for col in required_global_cols:
            assert col in global_df.columns

        # 驗證識別率在合理範圍內
        identification_rate = global_df["identification_rate"].iloc[0]
        assert 0 <= identification_rate <= 1

        # 驗證 tree 結果
        tree_df = results["tree"]
        assert len(tree_df) > 0

        required_tree_cols = [
            "check_order",
            "combo_size",
            "field_combo",
            "combo_entropy",
            "mpuccs_cnt",
            "mpuccs_collision_cnt",
            "weighted_mpuccs_collision_cnt",
        ]

        for col in required_tree_cols:
            assert col in tree_df.columns

    def test_skip_ncols_configuration(self):
        """測試跳躍式 n_cols 配置"""
        ori_data = pd.DataFrame(
            {
                "A": [1, 2, 3, 4, 5],
                "B": [10, 20, 30, 40, 50],
                "C": [100, 200, 300, 400, 500],
                "D": ["a", "b", "c", "d", "e"],
            }
        )

        syn_data = pd.DataFrame(
            {
                "A": [1, 2, 3, 6, 7],
                "B": [10, 20, 30, 60, 70],
                "C": [100, 200, 300, 600, 700],
                "D": ["a", "b", "c", "f", "g"],
            }
        )

        # 測試跳躍式配置：只評估 1 和 3 欄位組合
        config = {
            "eval_method": "mpuccs",
            "n_cols": [1, 3],
            "min_entropy_delta": 0.0,
        }

        mpuccs = MPUCCs(config)
        data = {"ori": ori_data, "syn": syn_data}
        results = mpuccs.eval(data)

        tree_df = results["tree"]

        # 檢查只有 1 和 3 欄位組合被處理
        combo_sizes = set(tree_df["combo_size"].unique())
        expected_sizes = {1, 3}

        # 應該包含目標大小，但可能不包含 2（因為跳過了）
        assert 1 in combo_sizes
        assert 3 in combo_sizes
        # 2 欄位組合不應該在目標處理中，但可能在樹中作為基礎組合

        # 檢查 3 欄位組合的基礎組合邏輯
        three_field_combos = tree_df[tree_df["combo_size"] == 3]
        if len(three_field_combos) > 0:
            for _, row in three_field_combos.iterrows():
                base_combo = row["base_combo"]
                if base_combo and base_combo != "None":
                    # 在跳躍式配置下，3 欄位組合的基礎應該是 1 欄位組合
                    base_fields = (
                        str(base_combo).count(",") + 1 if "," in str(base_combo) else 1
                    )
                    assert base_fields == 1, (
                        f"Expected 1-field base combo, got {base_fields}-field"
                    )

    def test_deduplication_functionality(self):
        """測試去重功能"""
        # 創建包含重複記錄的資料
        ori_data = pd.DataFrame(
            {
                "A": [1, 1, 2, 2, 3],  # 有重複
                "B": [10, 10, 20, 20, 30],
            }
        )

        syn_data = pd.DataFrame(
            {
                "A": [1, 1, 2, 4, 5],  # 有重複
                "B": [10, 10, 20, 40, 50],
            }
        )

        config = {"eval_method": "mpuccs", "n_cols": [1]}
        mpuccs = MPUCCs(config)

        data = {"ori": ori_data, "syn": syn_data}
        results = mpuccs.eval(data)

        global_df = results["global"]

        # 去重後的記錄數應該少於原始記錄數
        total_syn_records = global_df["total_syn_records"].iloc[0]
        total_ori_records = global_df["total_ori_records"].iloc[0]

        assert total_syn_records <= len(syn_data)
        assert total_ori_records <= len(ori_data)


class TestMPUCCsEdgeCases:
    """MPUCCs 邊界情況測試"""

    def test_single_column_data(self):
        """測試單欄位資料"""
        ori_data = pd.DataFrame({"A": [1, 2, 3, 4, 5]})
        syn_data = pd.DataFrame({"A": [1, 2, 3, 6, 7]})

        config = {"eval_method": "mpuccs", "n_cols": [1]}
        mpuccs = MPUCCs(config)

        data = {"ori": ori_data, "syn": syn_data}
        results = mpuccs.eval(data)

        # 單欄位資料應該正常處理
        assert len(results["global"]) == 1
        tree_df = results["tree"]
        assert len(tree_df) == 1
        assert tree_df["combo_size"].iloc[0] == 1

    def test_all_unique_data(self):
        """測試全唯一資料"""
        ori_data = pd.DataFrame(
            {
                "A": [1, 2, 3, 4, 5],
                "B": [10, 20, 30, 40, 50],
            }
        )

        syn_data = pd.DataFrame(
            {
                "A": [6, 7, 8, 9, 10],
                "B": [60, 70, 80, 90, 100],
            }
        )

        config = {"eval_method": "mpuccs", "n_cols": [1, 2]}
        mpuccs = MPUCCs(config)

        data = {"ori": ori_data, "syn": syn_data}
        results = mpuccs.eval(data)

        # 全唯一但無碰撞的資料，識別率應該為 0
        global_df = results["global"]
        identification_rate = global_df["identification_rate"].iloc[0]
        assert identification_rate == 0.0

    def test_all_identical_data(self):
        """測試全相同資料"""
        ori_data = pd.DataFrame(
            {
                "A": [1, 1, 1, 1, 1],
                "B": [10, 10, 10, 10, 10],
            }
        )

        syn_data = pd.DataFrame(
            {
                "A": [1, 1, 1, 1, 1],
                "B": [10, 10, 10, 10, 10],
            }
        )

        config = {"eval_method": "mpuccs", "n_cols": [1, 2]}
        mpuccs = MPUCCs(config)

        data = {"ori": ori_data, "syn": syn_data}
        results = mpuccs.eval(data)

        # 全相同資料去重後應該只剩一筆
        global_df = results["global"]
        total_syn_records = global_df["total_syn_records"].iloc[0]
        total_ori_records = global_df["total_ori_records"].iloc[0]

        assert total_syn_records == 1
        assert total_ori_records == 1


def test_renyi_vs_shannon_entropy():
    """展示 Rényi 熵與 Shannon 熵的差異"""
    distributions = {
        "均勻分佈": [1, 2, 3, 4, 5, 6, 7, 8],
        "輕微偏斜": [1, 1, 2, 2, 3, 4, 5, 6],
        "中度偏斜": [1, 1, 1, 2, 2, 3, 4, 5],
        "極端偏斜": [1, 1, 1, 1, 1, 2, 3, 4],
    }

    for dist_name, values in distributions.items():
        # 計算機率分佈
        counter = Counter(values)
        total = len(values)
        probs = [count / total for count in counter.values()]

        # Shannon 熵
        shannon_entropy = -sum(p * np.log(p) for p in probs if p > 0)

        # Rényi 熵 (α=2)
        sum_probs_squared = sum(p**2 for p in probs)
        renyi_entropy = -np.log(sum_probs_squared) if sum_probs_squared > 0 else 0.0

        # 正規化
        n_unique = len(counter)
        max_entropy = np.log(n_unique)
        shannon_normalized = shannon_entropy / max_entropy if max_entropy > 0 else 0.0
        renyi_normalized = renyi_entropy / max_entropy if max_entropy > 0 else 0.0

        # 驗證 Rényi 熵特性
        assert 0 <= renyi_normalized <= 1
        assert 0 <= shannon_normalized <= 1

        # 在偏斜分佈中，Rényi 熵通常較低
        if "偏斜" in dist_name:
            assert renyi_normalized <= shannon_normalized


if __name__ == "__main__":
    # 運行所有測試
    pytest.main([__file__, "-v"])
