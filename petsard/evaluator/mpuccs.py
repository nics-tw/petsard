from collections import Counter
from typing import Any, Optional

import numpy as np
import pandas as pd
from tqdm import tqdm

from petsard.evaluator.evaluator_base import BaseEvaluator


class MPUCCs(BaseEvaluator):
    """
    Maximal Partial Unique Column Combinations (mpUCCs) Evaluator

    This evaluator implements an advanced singling-out risk assessment algorithm
    based on the theory of maximal partial unique column combinations (mpUCCs).
    It identifies field combinations that can uniquely identify records in both
    synthetic and original datasets, providing a more accurate privacy risk assessment.

    Theoretical Foundation:
    - mpUCCs = QIDs (Quasi-identifiers)
    - Singling-out attacks essentially find unique field combinations in synthetic data
      that also correspond to unique records in original data
    - This is equivalent to finding partial UCCs (pUCCs) and checking for collisions

    Key Improvements over traditional approaches:
    1. Avoids overestimation by focusing on maximal combinations only
    2. Uses progressive tree-based search with entropy-based pruning
    3. Supports precision handling for numeric and datetime fields
    4. Provides comprehensive progress tracking
    """

    REQUIRED_INPUT_KEYS: list[str] = ["ori", "syn"]
    AVAILABLE_SCORES_GRANULARITY: list[str] = [
        "global",
        "details",
        "tree",
    ]

    # 數值常數
    ENTROPY_EPSILON = 1e-10  # 避免 log 計算中的零值
    MIN_COMBO_SIZE = 1  # 最小組合大小（也是單一組合的大小）
    UNIQUE_COUNT_THRESHOLD = 1  # 判定為唯一值的出現次數閾值
    DEFAULT_MIN_ENTROPY_DELTA = 0.0  # 預設最小熵增益閾值
    DEFAULT_RENYI_ALPHA = 2.0  # Rényi 熵參數 α=2 (Collision Entropy)
    DEFAULT_FIELD_DECAY_FACTOR = 0.5  # 預設欄位衰減因子

    def __init__(self, config: dict):
        """
        Initialize MPUCCs Evaluator

        Args:
            config (dict): Configuration dictionary containing:
                - eval_method (str): Evaluation method identifier
                - n_cols (int|list|None): Target combination sizes to evaluate
                - min_entropy_delta (float): Minimum entropy gain threshold for pruning
                - field_decay_factor (float): Decay factor for field combination weighting
                - renyi_alpha (float): Alpha parameter for Rényi entropy calculation
                - numeric_precision (int|None): Precision for numeric field comparison
                - datetime_precision (str|None): Precision for datetime field comparison
        """
        super().__init__(config)

        # Set default configuration values
        self.config.setdefault("n_cols", None)
        self.config.setdefault("min_entropy_delta", self.DEFAULT_MIN_ENTROPY_DELTA)
        self.config.setdefault("field_decay_factor", self.DEFAULT_FIELD_DECAY_FACTOR)
        self.config.setdefault("renyi_alpha", self.DEFAULT_RENYI_ALPHA)
        self.config.setdefault("numeric_precision", None)
        self.config.setdefault("datetime_precision", None)

    def _detect_numeric_precision(self, data: pd.DataFrame) -> int:
        """
        Detect the minimum precision of numeric fields

        Args:
            data: DataFrame to analyze

        Returns:
            int: Minimum precision as negative log value (e.g., 0.01 precision returns 2)
        """
        min_precision = 0

        for col in data.columns:
            if pd.api.types.is_numeric_dtype(
                data[col]
            ) and not pd.api.types.is_datetime64_any_dtype(data[col]):
                # Filter out NaN values
                non_null_values = data[col].dropna()
                if len(non_null_values) == 0:
                    continue

                # Check if integer type
                if pd.api.types.is_integer_dtype(data[col]):
                    continue

                # For floating point numbers, check decimal places
                for value in non_null_values:
                    if pd.isna(value):
                        continue
                    # Convert to string and check decimal places
                    str_value = f"{value:.10f}".rstrip("0").rstrip(".")
                    if "." in str_value:
                        decimal_places = len(str_value.split(".")[1])
                        min_precision = max(min_precision, decimal_places)

                self._logger.info(
                    f"Field {col} detected numeric precision: 10^-{min_precision}"
                )

        return min_precision

    def _detect_datetime_precision(self, data: pd.DataFrame) -> str:
        """
        Detect the minimum precision of datetime fields

        Args:
            data: DataFrame to analyze

        Returns:
            str: Time precision ('D', 'H', 'T', 's', 'ms', 'us', 'ns')
        """
        min_precision = "D"  # Default to day
        precision_order = [
            "D",
            "H",
            "T",
            "s",
            "ms",
            "us",
            "ns",
        ]  # Day, hour, minute, second, millisecond, microsecond, nanosecond

        for col in data.columns:
            if pd.api.types.is_datetime64_any_dtype(data[col]):
                non_null_values = data[col].dropna()
                if len(non_null_values) == 0:
                    continue

                # Check time precision
                for value in non_null_values.head(
                    100
                ):  # Only check first 100 values for efficiency
                    if pd.isna(value):
                        continue

                    # Check for nanoseconds
                    if value.nanosecond != 0:
                        min_precision = "ns"
                        break
                    # Check for microseconds
                    elif value.microsecond != 0:
                        if precision_order.index("us") > precision_order.index(
                            min_precision
                        ):
                            min_precision = "us"
                    # Check for milliseconds
                    elif value.microsecond // 1000 != 0:
                        if precision_order.index("ms") > precision_order.index(
                            min_precision
                        ):
                            min_precision = "ms"
                    # Check for seconds
                    elif value.second != 0:
                        if precision_order.index("s") > precision_order.index(
                            min_precision
                        ):
                            min_precision = "s"
                    # Check for minutes
                    elif value.minute != 0:
                        if precision_order.index("T") > precision_order.index(
                            min_precision
                        ):
                            min_precision = "T"
                    # Check for hours
                    elif value.hour != 0:
                        if precision_order.index("H") > precision_order.index(
                            min_precision
                        ):
                            min_precision = "H"

                self._logger.info(
                    f"Field {col} detected datetime precision: {min_precision}"
                )

        return min_precision

    def _apply_numeric_precision(
        self, data: pd.DataFrame, precision: int
    ) -> pd.DataFrame:
        """
        Apply precision rounding to numeric fields

        Args:
            data: DataFrame to process
            precision: Precision (decimal places)

        Returns:
            Processed DataFrame
        """
        data_copy = data.copy()

        for col in data_copy.columns:
            if pd.api.types.is_numeric_dtype(
                data_copy[col]
            ) and not pd.api.types.is_datetime64_any_dtype(data_copy[col]):
                if not pd.api.types.is_integer_dtype(data_copy[col]):
                    data_copy[col] = data_copy[col].round(precision)

        return data_copy

    def _normalize_datetime_precision(self, precision: str) -> str:
        """
        Normalize datetime precision format with case-insensitive support

        Args:
            precision: Original precision string

        Returns:
            Normalized precision string
        """
        # Build case mapping table
        precision_mapping = {
            "D": "D",
            "d": "D",
            "H": "H",
            "h": "H",
            "T": "T",
            "t": "T",
            "min": "T",
            "MIN": "T",
            "S": "s",
            "s": "s",
            "sec": "s",
            "SEC": "s",
            "L": "ms",
            "l": "ms",
            "ms": "ms",
            "MS": "ms",
            "U": "us",
            "u": "us",
            "us": "us",
            "US": "us",
            "micro": "us",
            "MICRO": "us",
            "N": "ns",
            "n": "ns",
            "ns": "ns",
            "NS": "ns",
            "nano": "ns",
            "NANO": "ns",
        }

        return precision_mapping.get(precision, precision.lower())

    def _apply_datetime_precision(
        self, data: pd.DataFrame, precision: str
    ) -> pd.DataFrame:
        """
        Apply precision rounding to datetime fields

        Args:
            data: DataFrame to process
            precision: Time precision (supports case-insensitive)

        Returns:
            Processed DataFrame
        """
        data_copy = data.copy()
        normalized_precision = self._normalize_datetime_precision(precision)

        for col in data_copy.columns:
            if pd.api.types.is_datetime64_any_dtype(data_copy[col]):
                data_copy[col] = data_copy[col].dt.floor(normalized_precision)

        return data_copy

    def _get_sorted_columns_by_cardinality(self, data: pd.DataFrame) -> list[str]:
        """Get columns sorted by cardinality in descending order"""
        column_cardinalities = []

        for col in data.columns:
            cardinality = data[col].nunique()
            column_cardinalities.append((col, cardinality))

        # Sort by cardinality in descending order
        column_cardinalities.sort(key=lambda x: x[1], reverse=True)
        return [col for col, _ in column_cardinalities]

    def _find_valid_base_combo(
        self, combo: tuple[str, ...], target_sizes: set[int], sorted_columns: list[str]
    ) -> Optional[tuple[str, ...]]:
        """
        Find valid base combination based on field priority

        Args:
            combo: Current combination
            target_sizes: Target size set
            sorted_columns: Fields sorted by priority

        Returns:
            Found base combination, or None if not found
        """
        if len(combo) <= 1:
            return None

        # Sort current combination fields by priority
        combo_fields_by_priority = [field for field in sorted_columns if field in combo]

        # Find target sizes smaller than current combination size, sorted in descending order
        valid_target_sizes = [
            size for size in sorted(target_sizes, reverse=True) if size < len(combo)
        ]

        # Start from the largest valid target size, find the first matching subset
        for target_size in valid_target_sizes:
            # Take the highest priority target_size fields as base combination
            base_combo = tuple(combo_fields_by_priority[:target_size])

            if len(base_combo) == target_size:
                return base_combo

        return None

    def _dedup_data(self, data: pd.DataFrame) -> tuple[pd.DataFrame, int]:
        """Deduplication processing"""
        original_cnt = len(data)
        deduplicated_data = data.drop_duplicates().reset_index(drop=True)
        deduplicated_cnt = len(deduplicated_data)

        self._logger.info(
            f"Deduplication: {original_cnt} -> {deduplicated_cnt} "
            f"(removed {original_cnt - deduplicated_cnt} records)"
        )

        return deduplicated_data, deduplicated_cnt

    def _calculate_entropy_for_combo(
        self, combo: tuple[str, ...], syn_data: pd.DataFrame, all_combinations: dict
    ) -> float:
        """Calculate normalized Rényi entropy (α=2, Collision Entropy) with caching"""
        if combo in all_combinations:
            return all_combinations[combo]

        combo_values = [tuple(row) for row in syn_data[list(combo)].values]
        counter = Counter(combo_values)
        total_cnt = len(syn_data)
        n_unique_combinations = len(counter)

        # If only one combination, entropy is 0
        if n_unique_combinations <= 1:
            normalized_entropy = 0.0
        else:
            # Calculate actual probability distribution
            probs = np.array([count / total_cnt for count in counter.values()])

            # Calculate collision entropy (Rényi α=2)
            # H₂(X) = -log₂(∑ pᵢ²)
            collision_prob = np.sum(probs ** self.config.get("renyi_alpha", 2.0))
            raw_renyi_entropy = -np.log2(collision_prob + self.ENTROPY_EPSILON)

            # Maximum Rényi entropy: when all p_i = 1/n
            # H_2_max = -log(n * (1/n)^2) = -log(1/n) = log(n)
            max_renyi_entropy = np.log2(n_unique_combinations)

            # Normalize entropy to [0, 1] range
            normalized_entropy = (
                raw_renyi_entropy / max_renyi_entropy if max_renyi_entropy > 0 else 0.0
            )

        # Cache result
        all_combinations[combo] = normalized_entropy
        return normalized_entropy

    def _detect_unique_combinations_with_cnter(
        self, data: pd.DataFrame, field_combo: tuple[str, ...]
    ) -> dict[tuple, int]:
        """Counter-optimized uniqueness detection"""
        combo_values = [tuple(row) for row in data[list(field_combo)].values]
        counter = Counter(combo_values)

        unique_combinations = {}
        for i, combo_value in enumerate(combo_values):
            if counter[combo_value] == self.UNIQUE_COUNT_THRESHOLD:
                unique_combinations[combo_value] = i

        return unique_combinations

    def _calculate_conditional_entropy_gain(
        self,
        new_combo: tuple[str, ...],
        base_combo: tuple[str, ...],
        syn_data: pd.DataFrame,
        identified_indices: set[int],
        all_combinations: dict,
    ) -> float:
        """
        Calculate conditional entropy gain of new combination relative to base combination

        Args:
            new_combo: New field combination (e.g., k1+k2)
            base_combo: Base combination (e.g., k1)
            syn_data: Synthetic data
            identified_indices: Already identified indices
            all_combinations: Dictionary of all combination entropy values

        Returns:
            float: Entropy gain value, > 0 indicates improvement
        """
        if not base_combo:
            # If no base combination, return entropy of new combination
            return self._calculate_entropy_for_combo(
                new_combo, syn_data, all_combinations
            )

        # Use cache to calculate base and new combination entropy
        base_entropy = self._calculate_entropy_for_combo(
            base_combo, syn_data, all_combinations
        )
        new_entropy = self._calculate_entropy_for_combo(
            new_combo, syn_data, all_combinations
        )

        # Entropy gain = new entropy - base entropy
        entropy_gain = new_entropy - base_entropy

        return entropy_gain

    def _find_unique_match(
        self, data: pd.DataFrame, fields: tuple[str, ...], values: tuple[Any]
    ) -> Optional[int]:
        """Find unique match in dataset"""
        if not isinstance(values, tuple):
            values = (values,)

        if len(fields) != len(values):
            return None

        mask = np.ones(len(data), dtype=bool)

        for field, value in zip(fields, values):
            if pd.isna(value):
                current_mask = data[field].isna().values
            else:
                current_mask = data[field].values == value

            mask &= current_mask

            if not mask.any():
                return None

        matching_indices = np.where(mask)[0]
        return (
            matching_indices[0]
            if len(matching_indices) == self.UNIQUE_COUNT_THRESHOLD
            else None
        )

    def _progressive_field_search(
        self,
        sorted_columns: list[str],
        syn_data: pd.DataFrame,
        ori_data: pd.DataFrame,
    ) -> tuple[list[dict], set[int], int, list[dict]]:
        """
        Progressive field search - Core algorithm (mpUCCs version)

        Returns:
            tuple: (detailed results, identified indices, iteration count, tree results)
        """
        details_results = []
        identified_indices = set()  # Already identified record indices
        maximal_combinations = {}  # Record minimum identifying combination for each index {syn_idx: combo}
        tree_results = []  # Tree results

        # Valid combination set - only contains target size combinations
        valid_combinations = set()
        # All combination set - contains all generated combinations and corresponding entropy values
        all_combinations = {}  # {combo: entropy_value}
        # Pruned combination set - pruned combinations will not be considered again
        pruned_combinations = set()

        columns_num = len(sorted_columns)
        n_cols = self.config.get("n_cols", None)

        # Determine combination sizes to process
        if n_cols is None:
            target_sizes = set(range(self.MIN_COMBO_SIZE, columns_num + 1))
        elif isinstance(n_cols, int):
            target_sizes = {n_cols} if n_cols <= columns_num else set()
        elif isinstance(n_cols, list):
            target_sizes = {size for size in n_cols if size <= columns_num}
        else:
            raise ValueError(
                f"Invalid n_cols configuration: {n_cols}. Should be None, int or list[int]."
            )

        # max_target_size should be the maximum value in target_sizes
        max_target_size = max(target_sizes) if target_sizes else columns_num
        # Find minimum target size to ensure algorithm can start
        min_target_size = min(target_sizes) if target_sizes else self.MIN_COMBO_SIZE

        # Pre-calculate all combinations to process for unified progress bar
        all_step_combos = []

        # Progressive field addition
        for field_idx, current_field in enumerate(sorted_columns):
            self._logger.info(f"Processing field {field_idx + 1}: {current_field}")

            # Current step combinations to evaluate
            current_step_combos = []

            # 1. Single current field (always generated, but only processed if in target sizes)
            single_combo = (current_field,)
            if self.MIN_COMBO_SIZE in target_sizes:
                # Single field has no base combination
                current_step_combos.append(
                    (single_combo, None)
                )  # (combination, base combination)

            # Always add single field to all_combinations as base and calculate its entropy
            single_entropy = self._calculate_entropy_for_combo(
                single_combo, syn_data, all_combinations
            )
            all_combinations[single_combo] = single_entropy

            # 2. Current field combined with all previous combinations
            for existing_combo in list(all_combinations.keys()):
                # Check if current field is already in existing combination
                if current_field in existing_combo:
                    continue

                new_combo = tuple(
                    sorted(
                        existing_combo + (current_field,),
                        key=lambda x: sorted_columns.index(x),
                    )
                )

                # Always add new combination to all_combinations (for future expansion)
                if len(new_combo) <= max_target_size:
                    new_entropy = self._calculate_entropy_for_combo(
                        new_combo, syn_data, all_combinations
                    )
                    all_combinations[new_combo] = new_entropy

                # Only add combinations that match target sizes to current step processing
                if len(new_combo) in target_sizes and len(new_combo) <= max_target_size:
                    # Use new logic to find valid base combination
                    valid_base_combo = self._find_valid_base_combo(
                        new_combo, target_sizes, sorted_columns
                    )
                    current_step_combos.append((new_combo, valid_base_combo))

            # Add current step combinations to total list with field marking
            for combo, base_combo in current_step_combos:
                all_step_combos.append((combo, base_combo, current_field))

        # Use unified progress bar to process all combinations
        progress_bar = tqdm(
            all_step_combos, desc="Processing field combinations", unit="combo"
        )

        # Build field index mapping table
        field_to_index = {field: idx for idx, field in enumerate(sorted_columns)}

        for combo, base_combo, current_field in progress_bar:
            # Calculate current field progress
            current_field_idx = field_to_index[current_field]
            field_progress = f"Field {current_field_idx + 1}/{len(sorted_columns)}"

            # Update progress bar description to show field progress and current processing field
            progress_bar.set_description(
                f"{field_progress} - Processing {current_field} combinations"
            )

            # Check if base_combo is in target sizes and actually processed
            base_combo_valid = base_combo and len(base_combo) in target_sizes

            # Check if base_combo has been pruned
            base_is_pruned = (
                base_combo in pruned_combinations if base_combo_valid else None
            )

            # If base combination is pruned, directly prune this combination
            if base_is_pruned:
                combo_size = len(combo)
                # Correct field_weighted calculation: combo_size = 1 is 1.0, then decay sequentially
                if combo_size == 1:
                    field_weighted = 1.0
                else:
                    field_weighted = self.config.get(
                        "field_decay_factor", self.DEFAULT_FIELD_DECAY_FACTOR
                    ) ** (combo_size - 1)

                tree_record = {
                    "check_order": len(tree_results) + 1,  # Which check number
                    "combo_size": combo_size,  # How many fields used
                    "field_combo": str(combo),  # Field combination
                    "base_combo": str(base_combo),  # Base field combination
                    "base_is_pruned": True,  # Base combination is pruned
                    "combo_entropy": None,  # Don't calculate combination entropy
                    "base_entropy": None,  # Don't show base entropy
                    "entropy_gain": None,  # Don't calculate entropy gain
                    "is_pruned": True,  # Is pruned
                    "mpuccs_cnt": 0,  # Number of mpUCCs in syn
                    "mpuccs_collision_cnt": 0,  # How many mpUCCs collisions found
                    "field_weighted": field_weighted,  # Field weighting
                    "total_weighted": field_weighted,  # Total weighting = field_weighted
                    "weighted_mpuccs_collision_cnt": 0.0,  # Weighted mpUCCs collision
                }
                pruned_combinations.add(combo)
                tree_results.append(tree_record)
                continue

            # Normal case: calculate required entropy values
            combo_entropy = all_combinations.get(combo, 0.0)
            combo_size = len(combo)

            # Calculate weighting values
            # Correct field_weighted calculation: combo_size = 1 is 1.0, then decay sequentially
            if combo_size == 1:
                field_weighted = 1.0
            else:
                field_weighted = self.config.get(
                    "field_decay_factor", self.DEFAULT_FIELD_DECAY_FACTOR
                ) ** (combo_size - 1)

            # total_weighted now only equals field_weighted
            total_weighted = field_weighted

            tree_record = {
                "check_order": len(tree_results) + 1,  # Which check number
                "combo_size": combo_size,  # How many fields used
                "field_combo": str(combo),  # Field combination
                "base_combo": str(base_combo)
                if base_combo_valid
                else None,  # Base field combination
                "base_is_pruned": base_is_pruned,  # Whether base combination is pruned
                "combo_entropy": combo_entropy,  # Field combination entropy
                "base_entropy": all_combinations.get(base_combo, 0.0)
                if base_combo_valid
                else None,  # Base field combination entropy
                "entropy_gain": None,  # Entropy gain (calculated later)
                "is_pruned": None
                if not base_combo_valid
                else False,  # Whether pruned (not applicable when no base_combo)
                "mpuccs_cnt": 0,  # Number of mpUCCs in syn (calculated later)
                "mpuccs_collision_cnt": 0,  # How many mpUCCs collisions found
                "field_weighted": field_weighted,  # Field weighting
                "total_weighted": total_weighted,  # Total weighting = field_weighted
                "weighted_mpuccs_collision_cnt": 0.0,  # Weighted mpUCCs collision (calculated later)
            }

            # Conditional entropy check (only when there's valid and unpruned base combination)
            should_check_entropy = len(combo) in target_sizes and (
                (base_combo_valid and not base_is_pruned)
                or len(combo) == min_target_size
            )

            if should_check_entropy and base_combo_valid and not base_is_pruned:
                entropy_gain = self._calculate_conditional_entropy_gain(
                    combo,
                    base_combo,
                    syn_data,
                    identified_indices,
                    all_combinations,
                )
                tree_record["entropy_gain"] = entropy_gain

                # If no entropy gain, prune this combination and all its supersets
                if entropy_gain <= self.config.get(
                    "min_entropy_delta", self.DEFAULT_MIN_ENTROPY_DELTA
                ):
                    self._logger.debug(
                        f"Pruning combination {combo} (entropy gain: {entropy_gain:.6f})"
                    )
                    pruned_combinations.add(combo)
                    tree_record["is_pruned"] = True
                    tree_results.append(tree_record)
                    continue
            elif should_check_entropy and (not base_combo_valid or base_is_pruned):
                # When no valid base combination or base combination is pruned, don't check entropy gain
                tree_record["entropy_gain"] = None
                tree_record["is_pruned"] = None

            # Detect unique combinations
            unique_combinations = self._detect_unique_combinations_with_cnter(
                syn_data, combo
            )

            # Set number of mpUCCs in syn
            tree_record["mpuccs_cnt"] = len(unique_combinations)

            # Check if there are unique combinations to process
            if not unique_combinations:
                tree_record["mpuccs_collision_cnt"] = 0
                tree_results.append(tree_record)
                continue

            # Process each unique combination (mpUCCs logic)
            unique_match_count = 0
            for value_combo, syn_idx in unique_combinations.items():
                # Check if a smaller combination has already identified this record (mpUCCs logic)
                if syn_idx in maximal_combinations:
                    existing_combo = maximal_combinations[syn_idx]
                    if len(existing_combo) <= len(combo):
                        # Already have same or smaller combination, skip current combination
                        continue

                # Find match in original data
                ori_idx = self._find_unique_match(ori_data, combo, value_combo)

                if ori_idx is not None:
                    # Record or update minimum identifying combination
                    if syn_idx not in maximal_combinations or len(combo) < len(
                        maximal_combinations[syn_idx]
                    ):
                        maximal_combinations[syn_idx] = combo

                        details_results.append(
                            {
                                "combo_size": len(combo),
                                "syn_idx": syn_idx,
                                "field_combo": str(combo),
                                "value_combo": str(
                                    value_combo
                                    if isinstance(value_combo, tuple)
                                    else (value_combo,)
                                ),
                                "ori_idx": ori_idx,
                            }
                        )

                        identified_indices.add(syn_idx)
                        unique_match_count += 1

            # Record found mpuccs_collision_cnt count and weighted values
            tree_record["mpuccs_collision_cnt"] = unique_match_count
            tree_record["weighted_mpuccs_collision_cnt"] = (
                unique_match_count * tree_record["total_weighted"]
            )
            tree_results.append(tree_record)

            # Only add combinations in target sizes to valid set
            if len(combo) in target_sizes:
                valid_combinations.add(combo)

        return details_results, identified_indices, 0, tree_results

    def _eval(self, data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        """
        Main evaluation method - Progressive tree-based search

        Args:
            data: Dictionary containing 'ori' and 'syn' DataFrames

        Returns:
            Dictionary containing evaluation results with keys:
            - 'global': Global statistics
            - 'details': Detailed collision results
            - 'tree': Tree search results
        """
        # Data preprocessing
        ori_data = data["ori"].copy()
        syn_data = data["syn"].copy()

        # Precision handling
        if self.config.get("numeric_precision") is None:
            # Auto-detect numeric precision
            detected_precision = self._detect_numeric_precision(ori_data)
            if detected_precision > 0:
                self.config["numeric_precision"] = detected_precision
                self._logger.info(
                    f"Auto-detected numeric precision: {detected_precision} decimal places"
                )

                # Apply numeric precision
                ori_data = self._apply_numeric_precision(ori_data, detected_precision)
                syn_data = self._apply_numeric_precision(syn_data, detected_precision)
                self._logger.info("Applied numeric precision rounding")
        else:
            # Use specified numeric precision
            precision = self.config["numeric_precision"]
            ori_data = self._apply_numeric_precision(ori_data, precision)
            syn_data = self._apply_numeric_precision(syn_data, precision)
            self._logger.info(
                f"Applied specified numeric precision: {precision} decimal places"
            )

        if self.config.get("datetime_precision") is None:
            # Auto-detect datetime precision
            detected_dt_precision = self._detect_datetime_precision(ori_data)
            if detected_dt_precision != "D":  # If not default day precision
                self.config["datetime_precision"] = detected_dt_precision
                self._logger.info(
                    f"Auto-detected datetime precision: {detected_dt_precision}"
                )

                # Apply datetime precision
                ori_data = self._apply_datetime_precision(
                    ori_data, detected_dt_precision
                )
                syn_data = self._apply_datetime_precision(
                    syn_data, detected_dt_precision
                )
                self._logger.info("Applied datetime precision rounding")
        else:
            # Use specified datetime precision
            precision = self.config["datetime_precision"]
            ori_data = self._apply_datetime_precision(ori_data, precision)
            syn_data = self._apply_datetime_precision(syn_data, precision)
            self._logger.info(f"Applied specified datetime precision: {precision}")

        # Deduplication
        ori_data, ori_cnt = self._dedup_data(ori_data)
        syn_data, syn_cnt = self._dedup_data(syn_data)

        # Get columns sorted by cardinality
        sorted_columns = self._get_sorted_columns_by_cardinality(syn_data)
        self._logger.info(f"Field processing order (by cardinality): {sorted_columns}")

        # Progressive field search
        details_results, identified_indices, iteration_count, tree_results = (
            self._progressive_field_search(sorted_columns, syn_data, ori_data)
        )

        # Calculate global statistics
        total_syn_records = len(syn_data)
        total_identified = len(identified_indices)
        identification_rate = (
            total_identified / total_syn_records if total_syn_records > 0 else 0.0
        )

        # Calculate weighted identification rate
        total_weighted_identified = sum(
            result["weighted_mpuccs_collision_cnt"] for result in tree_results
        )
        weighted_identification_rate = (
            total_weighted_identified / total_syn_records
            if total_syn_records > 0
            else 0.0
        )

        # Global results
        global_results = pd.DataFrame(
            [
                {
                    "total_syn_records": total_syn_records,
                    "total_ori_records": len(ori_data),
                    "total_identified": total_identified,
                    "identification_rate": identification_rate,
                    "weighted_identification_rate": weighted_identification_rate,
                    "total_combinations_checked": len(tree_results),
                    "total_combinations_pruned": sum(
                        1 for r in tree_results if r.get("is_pruned", False)
                    ),
                    "config_n_cols": str(self.config.get("n_cols", "None")),
                    "config_min_entropy_delta": self.config.get(
                        "min_entropy_delta", self.DEFAULT_MIN_ENTROPY_DELTA
                    ),
                    "config_field_decay_factor": self.config.get(
                        "field_decay_factor", self.DEFAULT_FIELD_DECAY_FACTOR
                    ),
                    "config_renyi_alpha": self.config.get(
                        "renyi_alpha", self.DEFAULT_RENYI_ALPHA
                    ),
                    "config_numeric_precision": self.config.get(
                        "numeric_precision", "None"
                    ),
                    "config_datetime_precision": self.config.get(
                        "datetime_precision", "None"
                    ),
                }
            ]
        )

        # Details results
        details_df = (
            pd.DataFrame(details_results) if details_results else pd.DataFrame()
        )

        # Tree results
        tree_df = pd.DataFrame(tree_results) if tree_results else pd.DataFrame()

        return {
            "global": global_results,
            "details": details_df,
            "tree": tree_df,
        }
