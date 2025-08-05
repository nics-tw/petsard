import re
from copy import deepcopy

import pandas as pd

from petsard.exceptions import ConfigError, UnexecutedError
from petsard.reporter.base_reporter import (
    BaseReporter,
    DataFrameConstants,
    RegexPatterns,
    ReportGranularity,
    convert_full_expt_tuple_to_name,
)


def convert_eval_expt_name_to_tuple(expt_name: str) -> tuple:
    """
    Converts an Evaluator/Describer experiment name to a tuple.

    Args:
        expt_name (str):
            A string representation of the evaluation experiment configuration,
            formatted as f"{eval_name}_[{granularity}]". e.g.
            - 'sdmetrics-qual_[global]'

    Returns:
        (tuple): A tuple representing a evaluation experiment configuation.
            formatted as ({eval_name}, {granularity}). e.g.
            - ('sdmetrics-qual', 'global')

    Raises:
        ConfigError: If the experiment name does not match the expected pattern.
    """
    match = RegexPatterns.EVAL_EXPT_NAME.match(expt_name)
    if match:
        return match.groups()
    else:
        raise ConfigError(
            f"Invalid experiment name format: '{expt_name}'. Expected format: 'eval_name_[granularity]'"
        )


def full_expt_tuple_filter(
    full_expt_tuple: tuple,
    method: str,
    target: str | list[str],
) -> tuple:
    """
    Filters a tuple based on the given method and target.

    Args:
        full_expt_tuple (tuple): The tuple to be filtered.
        method (str): The filtering method. Must be either 'include' or 'exclude'.
        target (str | List[str]): The target value(s) to include or exclude.

    Returns:
        (tuple): The filtered tuple.

    Raises:
        ConfigError: If the method is not 'include' or 'exclude'.
    """
    method = method.lower()
    if method not in ["include", "exclude"]:
        raise ConfigError
    if isinstance(target, str):
        target = [target]

    result: list = []
    action_next: bool = False

    if method == "include":
        for item in full_expt_tuple:
            if action_next:
                action_next = False
                result.append(item)
                continue
            if item in target:
                result.append(item)
                action_next = True
    else:  # 'exclude'
        for item in full_expt_tuple:
            if action_next:
                action_next = False
                continue
            if item in target:
                action_next = True
                continue
            result.append(item)

    return tuple(result)


class ReporterSaveReportMap:
    """
    Mapping of ReportSaveReport.

    Note: This class is deprecated. Use ReportGranularity enum and get_granularity_method() instead.
    """

    GLOBAL: int = ReportGranularity.GLOBAL
    COLUMNWISE: int = ReportGranularity.COLUMNWISE
    PAIRWISE: int = ReportGranularity.PAIRWISE

    @classmethod
    def map(cls, granularity: str) -> int:
        """
        Get suffixes mapping int value

        Args:
            granularity (str): reporting granularity
        """
        return ReportGranularity.map(granularity)


class ReporterSaveReport(BaseReporter):
    """
    Save evaluating/describing data to file.
    """

    SAVE_REPORT_KEY: str = DataFrameConstants.FULL_EXPT_NAME

    def __init__(self, config: dict):
        """
        Args:
            config (dict): The configuration dictionary.
                - method (str): The method used for reporting.
                - output (str, optional): The output filename prefix for the report.
                    Default is 'petsard'.
                - granularity (str): The granularity of reporting.
                    It should be one of 'global', 'columnwise', or 'pairwise'.
                    Case-insensitive.
                - eval (str): The evaluation experiment name for export reporting.
                    Case-sensitive.

        Raises:
            ConfigError: If the 'source' key is missing in the config
                or if the value of 'source' is not a string or a list of strings.
        """
        super().__init__(config)

        # granularity should be whether global/columnwise/pairwise
        if "granularity" not in self.config:
            raise ConfigError
        if not isinstance(self.config["granularity"], str):
            raise ConfigError
        self.config["granularity"] = self.config["granularity"].lower()
        granularity_code = ReportGranularity.map(self.config["granularity"])
        if granularity_code not in [
            ReportGranularity.GLOBAL,
            ReportGranularity.COLUMNWISE,
            ReportGranularity.PAIRWISE,
        ]:
            raise ConfigError
        self.config["granularity_code"] = granularity_code

        # set eval to None if not exist,
        #   otherwise verify it should be str or List[str]
        eval = self.config.get("eval")
        if isinstance(eval, str):
            eval = [eval]
        if not isinstance(eval, list) or not all(
            isinstance(item, str) for item in eval
        ):
            if eval is not None:
                raise ConfigError
        self.config["eval"] = eval

    def create(self, data: dict = None) -> None:
        """
        Creating the report data by checking is experiment name of Evaluator exist.

        Args:
            data (dict): The data used for creating the report.
                See BaseReporter._verify_create_input() for format requirement.
                - exist_report (dict, optional): The existing report data.
                    - The key is the full evaluation experiment name:
                        "{eval}_[{granularity}]"
                    - The value is the data of the report, pd.DataFrame.

        Attributes:
            - result (dict): Data for the report.
                - Reporter (dict): The report data for the reporter.
                    - full_expt_name (str): The full experiment name.
                    - expt_name (str): The experiment name.
                    - granularity (str): The granularity of the report.
                    - report (pd.DataFrame): The report data.
        """
        # verify input data
        self._verify_create_input(data)

        # Setup evaluation parameters
        eval_pattern, output_eval_name = self._setup_evaluation_parameters()

        # Extract existing report data
        exist_report = data.pop("exist_report", None)

        # Process all experiment data
        final_report_data = self._process_all_experiments(
            data, eval_pattern, output_eval_name, exist_report
        )

        # Store final result
        self._store_final_result(final_report_data, output_eval_name)

    def _setup_evaluation_parameters(self) -> tuple[str, str]:
        """
        Setup evaluation pattern and output name based on configuration.

        Returns:
            tuple[str, str]: (eval_pattern, output_eval_name)
        """
        eval_config = self.config["eval"]
        granularity = self.config["granularity"]

        if eval_config is None:
            eval_pattern = re.escape(f"_[{granularity}]") + "$"
            output_eval_name = f"[{granularity}]"
        else:
            eval_pattern = (
                "^("
                + "|".join([re.escape(eval_item) for eval_item in eval_config])
                + ")"
                + re.escape(f"_[{granularity}]")
                + "$"
            )
            output_eval_name = "-".join(eval_config) + f"_[{granularity}]"

        return eval_pattern, output_eval_name

    def _process_all_experiments(
        self, data: dict, eval_pattern: str, output_eval_name: str, exist_report: dict
    ) -> pd.DataFrame:
        """
        Process all experiment data and merge them into final report.

        Args:
            data (dict): Experiment data dictionary
            eval_pattern (str): Pattern to match evaluation experiments
            output_eval_name (str): Output evaluation name
            exist_report (dict): Existing report data

        Returns:
            pd.DataFrame: Final merged report data, or None if no data
        """
        final_report_data = None
        exist_report_merged = False

        for full_expt_tuple, rpt_data in data.items():
            # Process single experiment data
            skip_flag, processed_data = self._process_report_data(
                report=rpt_data,
                full_expt_tuple=full_expt_tuple,
                eval_pattern=eval_pattern,
                granularity=self.config["granularity"],
                output_eval_name=output_eval_name,
            )

            if skip_flag:
                continue

            # Merge with existing report (only once)
            if (
                not exist_report_merged
                and exist_report
                and output_eval_name in exist_report
            ):
                processed_data = self._safe_merge(
                    df1=exist_report[output_eval_name],
                    df2=processed_data,
                    name1=("exist_report",),
                    name2=full_expt_tuple,
                )
                exist_report_merged = True

            # Merge with accumulated data
            final_report_data = self._merge_with_accumulated_data(
                final_report_data, processed_data, full_expt_tuple
            )

        return final_report_data

    def _merge_with_accumulated_data(
        self,
        accumulated_data: pd.DataFrame,
        new_data: pd.DataFrame,
        full_expt_tuple: tuple,
    ) -> pd.DataFrame:
        """
        Merge new data with accumulated report data.

        Args:
            accumulated_data (pd.DataFrame): Previously accumulated data
            new_data (pd.DataFrame): New data to merge
            full_expt_tuple (tuple): Full experiment tuple for naming

        Returns:
            pd.DataFrame: Merged data
        """
        if accumulated_data is None:
            return new_data.copy()
        else:
            return self._safe_merge(
                df1=accumulated_data,
                df2=new_data,
                name1=("Append report"),
                name2=full_expt_tuple,
            )

    def _store_final_result(
        self, final_report_data: pd.DataFrame, output_eval_name: str
    ) -> None:
        """
        Store the final result in the result dictionary.

        Args:
            final_report_data (pd.DataFrame): Final report data
            output_eval_name (str): Output evaluation name
        """
        granularity = self.config["granularity"]

        if final_report_data is not None:
            self.result["Reporter"] = {
                "eval_expt_name": output_eval_name,
                "granularity": granularity,
                "report": deepcopy(final_report_data),
            }
        else:
            self.result["Reporter"] = {
                "eval_expt_name": output_eval_name,
                "granularity": granularity,
                "report": None,
                "warnings": (
                    f"There is no report data to save under {granularity} granularity."
                ),
            }

    @classmethod
    def _process_report_data(
        cls,
        report: pd.DataFrame,
        full_expt_tuple: tuple[str],
        eval_pattern: str,
        granularity: str,
        output_eval_name: str,
    ) -> tuple[bool, pd.DataFrame]:
        """
        Process the report data by performing validation and transformation steps.

        Args:
            report (pd.DataFrame): The report data to be processed.
            full_expt_tuple (tuple): The tuple containing module names and expt names.
            eval_pattern (str): The pattern to match the evaluation experiment name.
            granularity (str): The granularity of the report.
            output_eval_name (str): The output evaluation experiment name.

        Returns:
            tuple[bool, pd.DataFrame]: (skip_flag, processed_report_data)
        """
        # Step 1-3: Validate input and check if processing should be skipped
        should_skip, validated_report = cls._validate_report_input(
            report, full_expt_tuple, eval_pattern, granularity
        )
        if should_skip:
            return True, None

        # Step 4: Rename columns with eval name prefix
        report_with_renamed_columns = cls._rename_report_columns(
            validated_report, full_expt_tuple
        )

        # Step 5: Reset index based on granularity
        report_with_reset_index = cls._reset_report_index(
            report_with_renamed_columns, granularity
        )

        # Step 6-7: Insert module names and add full experiment name
        final_report = cls._add_experiment_metadata(
            report_with_reset_index, full_expt_tuple, output_eval_name
        )

        return False, final_report

    @classmethod
    def _validate_report_input(
        cls,
        report: pd.DataFrame,
        full_expt_tuple: tuple[str],
        eval_pattern: str,
        granularity: str,
    ) -> tuple[bool, pd.DataFrame]:
        """
        Validate report input and check if processing should be skipped.

        Returns:
            tuple[bool, pd.DataFrame]: (should_skip, validated_report)
        """
        # 1. Check if final module is Evaluator/Describer
        if full_expt_tuple[-2] not in cls.SAVE_REPORT_AVAILABLE_MODULE:
            return True, None

        # 2. Check if eval_expt_name matches granularity pattern
        if not re.search(eval_pattern, full_expt_tuple[-1]):
            return True, None

        # 3. Check if report data exists
        if report is None:
            cls._log_missing_report_warning(full_expt_tuple, granularity)
            return True, None

        return False, report.copy()

    @classmethod
    def _log_missing_report_warning(
        cls, full_expt_tuple: tuple[str], granularity: str
    ) -> None:
        """Log warning when report data is missing."""
        import logging

        logger = logging.getLogger(f"PETsARD.{__name__}")
        eval_name = convert_eval_expt_name_to_tuple(full_expt_tuple[-1])[0]
        logger.warning(
            f"No {granularity} granularity report found "
            f"in {full_expt_tuple[-2]} {eval_name}. "
            f"Skipping data collection."
        )

    @classmethod
    def _rename_report_columns(
        cls, report: pd.DataFrame, full_expt_tuple: tuple[str]
    ) -> pd.DataFrame:
        """
        Rename columns with eval name prefix.

        Args:
            report (pd.DataFrame): The report data.
            full_expt_tuple (tuple[str]): The full experiment tuple.

        Returns:
            pd.DataFrame: Report with renamed columns.
        """
        eval_expt_tuple = convert_eval_expt_name_to_tuple(full_expt_tuple[-1])
        eval_name = eval_expt_tuple[0]

        column_mapping = {col: f"{eval_name}_{col}" for col in report.columns}
        return report.rename(columns=column_mapping)

    @classmethod
    def _reset_report_index(
        cls, report: pd.DataFrame, granularity: str
    ) -> pd.DataFrame:
        """
        Reset index based on granularity type.

        Args:
            report (pd.DataFrame): The report data.
            granularity (str): The granularity type.

        Returns:
            pd.DataFrame: Report with reset index.
        """
        granularity_code = ReportGranularity.map(granularity)

        if granularity_code == ReportGranularity.COLUMNWISE:
            return cls._reset_columnwise_index(report)
        elif granularity_code == ReportGranularity.PAIRWISE:
            return cls._reset_pairwise_index(report)

        return report

    @classmethod
    def _reset_columnwise_index(cls, report: pd.DataFrame) -> pd.DataFrame:
        """Reset index for columnwise granularity."""
        report = report.reset_index(drop=False)
        return report.rename(columns={"index": DataFrameConstants.COLUMN})

    @classmethod
    def _reset_pairwise_index(cls, report: pd.DataFrame) -> pd.DataFrame:
        """Reset index for pairwise granularity."""
        report = report.reset_index(drop=False)
        report = report.rename(
            columns={
                "level_0": DataFrameConstants.COLUMN1,
                "level_1": DataFrameConstants.COLUMN2,
            }
        )
        if "index" in report.columns:
            report = report.drop(columns=["index"])
        return report

    @classmethod
    def _add_experiment_metadata(
        cls,
        report: pd.DataFrame,
        full_expt_tuple: tuple[str],
        output_eval_name: str,
    ) -> pd.DataFrame:
        """
        Add experiment metadata columns to the report.

        Args:
            report (pd.DataFrame): The report data.
            full_expt_tuple (tuple[str]): The full experiment tuple.
            output_eval_name (str): The output evaluation experiment name.

        Returns:
            pd.DataFrame: Report with added metadata.
        """
        # Insert module names as columns
        report_with_modules, postfix = cls._insert_module_columns(
            report, full_expt_tuple, output_eval_name
        )

        # Add full experiment name as first column
        report_with_full_name = cls._insert_full_experiment_name(
            report_with_modules, full_expt_tuple, postfix
        )

        return report_with_full_name

    @classmethod
    def _insert_module_columns(
        cls,
        report: pd.DataFrame,
        full_expt_tuple: tuple[str],
        output_eval_name: str,
    ) -> tuple[pd.DataFrame, str]:
        """
        Insert module names as columns in the report.

        Args:
            report (pd.DataFrame): The report data.
            full_expt_tuple (tuple[str]): The full experiment tuple.
            output_eval_name (str): The output evaluation experiment name.

        Returns:
            tuple[pd.DataFrame, str]: (report_with_modules, postfix_for_full_name)
        """
        full_expt_name_postfix = ""

        for i in range(len(full_expt_tuple) - 2, -1, -2):
            module_name = full_expt_tuple[i]
            experiment_name = full_expt_tuple[i + 1]

            if module_name in cls.SAVE_REPORT_AVAILABLE_MODULE:
                report.insert(0, module_name, output_eval_name)
                full_expt_name_postfix += module_name + output_eval_name
            else:
                report.insert(0, module_name, experiment_name)

        return report, full_expt_name_postfix

    @classmethod
    def _insert_full_experiment_name(
        cls,
        report: pd.DataFrame,
        full_expt_tuple: tuple[str],
        postfix: str,
    ) -> pd.DataFrame:
        """
        Insert the full experiment name as the first column.

        Args:
            report (pd.DataFrame): The report data.
            full_expt_tuple (tuple[str]): The full experiment tuple.
            postfix (str): The postfix for the full experiment name.

        Returns:
            pd.DataFrame: Report with full experiment name column.
        """
        full_expt_name = cls._generate_full_experiment_name(full_expt_tuple, postfix)
        report.insert(0, DataFrameConstants.FULL_EXPT_NAME, full_expt_name)
        return report

    @classmethod
    def _generate_full_experiment_name(
        cls, full_expt_tuple: tuple[str], postfix: str
    ) -> str:
        """
        Generate the full experiment name.

        Args:
            full_expt_tuple (tuple[str]): The full experiment tuple.
            postfix (str): The postfix to append.

        Returns:
            str: The generated full experiment name.
        """
        filtered_tuple = full_expt_tuple_filter(
            full_expt_tuple=full_expt_tuple,
            method="exclude",
            target=cls.SAVE_REPORT_AVAILABLE_MODULE,
        )
        base_name = convert_full_expt_tuple_to_name(filtered_tuple)

        return "_".join(
            component for component in [base_name, postfix] if component != ""
        )

    @classmethod
    def _safe_merge(
        cls,
        df1: pd.DataFrame,
        df2: pd.DataFrame,
        name1: str,
        name2: str,
    ) -> pd.DataFrame:
        """
        Safely merge two DataFrames with full outer join.

        Args:
            df1 (pd.DataFrame): The first DataFrame.
            df2 (pd.DataFrame): The second DataFrame.
            name1 (str): The name of the first DataFrame.
            name2 (str): The name of the second DataFrame.

        Returns:
            pd.DataFrame: The merged DataFrame.
        """
        # Step 1: Identify and validate common columns
        common_columns = cls._identify_common_columns(df1, df2)

        # Step 2: Harmonize data types for common columns
        cls._harmonize_column_dtypes(df1, df2, common_columns, name1, name2)

        # Step 3: Perform the merge operation
        merged_df = cls._perform_dataframe_merge(df1, df2, common_columns)

        # Step 4: Clean up merged DataFrame
        cleaned_df = cls._cleanup_merged_dataframe(merged_df, df1, common_columns)

        return cleaned_df

    @classmethod
    def _identify_common_columns(
        cls, df1: pd.DataFrame, df2: pd.DataFrame
    ) -> list[str]:
        """
        Identify common columns that are allowed for merging.

        Args:
            df1 (pd.DataFrame): The first DataFrame.
            df2 (pd.DataFrame): The second DataFrame.

        Returns:
            list[str]: List of common columns allowed for merging.
        """
        allowed_columns = cls.ALLOWED_IDX_MODULE + DataFrameConstants.MERGE_COLUMNS

        common_columns = [col for col in df1.columns if col in df2.columns]
        return [col for col in common_columns if col in allowed_columns]

    @classmethod
    def _harmonize_column_dtypes(
        cls,
        df1: pd.DataFrame,
        df2: pd.DataFrame,
        common_columns: list[str],
        name1: str,
        name2: str,
    ) -> None:
        """
        Ensure common columns have the same data types across DataFrames.

        Args:
            df1 (pd.DataFrame): The first DataFrame.
            df2 (pd.DataFrame): The second DataFrame.
            common_columns (list[str]): List of common columns.
            name1 (str): Name of the first DataFrame for logging.
            name2 (str): Name of the second DataFrame for logging.
        """
        for col in common_columns:
            if df1[col].dtype != df2[col].dtype:
                cls._log_dtype_mismatch_warning(
                    col, df1[col].dtype, df2[col].dtype, name1, name2
                )
                df1[col] = df1[col].astype("object")
                df2[col] = df2[col].astype("object")

    @classmethod
    def _log_dtype_mismatch_warning(
        cls, column: str, dtype1, dtype2, name1: str, name2: str
    ) -> None:
        """Log warning for data type mismatches."""
        import logging

        logger = logging.getLogger(f"PETsARD.{__name__}")
        logger.warning(
            f"Column '{column}' has different dtypes in "
            f"'{name1}' ({dtype1}) and '{name2}' ({dtype2}). "
            f"Converting to object dtype."
        )

    @classmethod
    def _perform_dataframe_merge(
        cls, df1: pd.DataFrame, df2: pd.DataFrame, common_columns: list[str]
    ) -> pd.DataFrame:
        """
        Perform the actual DataFrame merge operation.

        Args:
            df1 (pd.DataFrame): The first DataFrame.
            df2 (pd.DataFrame): The second DataFrame.
            common_columns (list[str]): List of common columns for merging.

        Returns:
            pd.DataFrame: The merged DataFrame.
        """
        colname_replace = DataFrameConstants.REPLACE_TAG
        colname_suffix = DataFrameConstants.RIGHT_SUFFIX

        # Add replace tag to df2
        df2[colname_replace] = colname_replace

        if common_columns:
            return pd.merge(
                df1,
                df2,
                on=common_columns,
                how="outer",
                suffixes=("", colname_suffix),
            ).reset_index(drop=True)
        else:
            return cls._concatenate_dataframes_vertically(df1, df2)

    @classmethod
    def _concatenate_dataframes_vertically(
        cls, df1: pd.DataFrame, df2: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Concatenate DataFrames vertically when no common columns exist.

        Args:
            df1 (pd.DataFrame): The first DataFrame.
            df2 (pd.DataFrame): The second DataFrame.

        Returns:
            pd.DataFrame: The concatenated DataFrame.
        """
        # Align columns
        all_columns = list(df1.columns) + [
            col for col in df2.columns if col not in df1.columns
        ]
        df1_aligned = df1.reindex(columns=all_columns)
        df2_aligned = df2.reindex(columns=all_columns)

        # Concatenate with df2 first, then df1 to match expected order
        return pd.concat([df2_aligned, df1_aligned], ignore_index=True)

    @classmethod
    def _cleanup_merged_dataframe(
        cls,
        merged_df: pd.DataFrame,
        original_df1: pd.DataFrame,
        common_columns: list[str],
    ) -> pd.DataFrame:
        """
        Clean up the merged DataFrame by handling suffixed columns and replace tags.

        Args:
            merged_df (pd.DataFrame): The merged DataFrame.
            original_df1 (pd.DataFrame): The original first DataFrame.
            common_columns (list[str]): List of common columns.

        Returns:
            pd.DataFrame: The cleaned DataFrame.
        """
        colname_replace = DataFrameConstants.REPLACE_TAG
        colname_suffix = DataFrameConstants.RIGHT_SUFFIX
        allowed_columns = cls.ALLOWED_IDX_MODULE + DataFrameConstants.MERGE_COLUMNS

        if common_columns:
            # Replace df1 columns with df2 columns where replace tag is present
            for col in original_df1.columns:
                if col in allowed_columns:  # Skip common columns
                    continue

                right_col = col + colname_suffix
                if right_col in merged_df.columns:
                    mask = merged_df[colname_replace] == colname_replace
                    merged_df.loc[mask, col] = merged_df.loc[mask, right_col]
                    merged_df.drop(columns=[right_col], inplace=True)

        # Remove replace tag column
        if colname_replace in merged_df.columns:
            merged_df.drop(columns=[colname_replace], inplace=True)

        return merged_df

    def report(self) -> None:
        """
        Generates a report based on the provided report data.
            The report is saved to the specified output location.
        """
        if "Reporter" not in self.result:
            raise UnexecutedError
        reporter: dict = self.result["Reporter"]

        if "warnings" in reporter:
            import logging

            logger = logging.getLogger(f"PETsARD.{__name__}")
            logger.warning(
                "No CSV file will be saved. "
                "This warning can be ignored "
                "if running with different granularity config."
            )
            return

        if not all(key in reporter for key in ["eval_expt_name", "report"]):
            raise ConfigError
        eval_expt_name: str = reporter["eval_expt_name"]
        # petsard[Report]_{eval_expt_name}
        full_output: str = f"{self.config['output']}[Report]_{eval_expt_name}"

        report: pd.DataFrame = reporter["report"]
        if report is None:
            # the unexpected report is None without warnings
            raise UnexecutedError

        self._save(data=report, full_output=full_output)
