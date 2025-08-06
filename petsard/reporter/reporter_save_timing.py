"""
純函式化的 ReporterSaveTiming
完全無狀態設計，專注於業務邏輯
"""

import pandas as pd

from petsard.reporter.reporter_base import BaseReporter


class ReporterSaveTiming(BaseReporter):
    """
    純函式化的時間報告器
    完全無狀態，專注於業務邏輯
    """

    def __init__(self, config: dict):
        """
        Args:
            config (dict): The configuration dictionary.
                - method (str): The method used for reporting.
                - output (str, optional): The output filename prefix for the report.
                    Default is 'petsard'.
                - module (str or list, optional): Module name(s) to filter timing data.
                - time_unit (str, optional): Time unit for reporting ('seconds', 'minutes', 'hours', 'days').
                    Default is 'seconds'.
        """
        super().__init__(config)

        # Handle module filtering
        module = self.config.get("module", [])
        if isinstance(module, str):
            module = [module]
        elif module is None:
            module = []
        self.config["modules"] = module

        # Handle time unit
        time_unit = self.config.get("time_unit", "seconds")
        valid_units = ["days", "hours", "minutes", "seconds"]
        if time_unit not in valid_units:
            time_unit = "seconds"
        self.config["time_unit"] = time_unit

    def create(self, data: dict = None) -> pd.DataFrame | None:
        """
        純函式：處理時間資料並返回結果

        Args:
            data (dict): The data used for creating the timing report.
                - timing_data (pd.DataFrame): The timing data DataFrame.

        Returns:
            pd.DataFrame | None: 處理後的時間資料，如果沒有資料則返回 None
        """
        if data is None:
            data = {}

        timing_data = data.get("timing_data")

        # Handle empty or missing timing data
        if timing_data is None or (
            isinstance(timing_data, pd.DataFrame) and timing_data.empty
        ):
            return None

        return self._process_timing_data(timing_data)

    def report(self, processed_data: pd.DataFrame | None = None) -> pd.DataFrame | None:
        """
        純函式：生成並保存報告

        Args:
            processed_data (pd.DataFrame | None): 處理後的時間資料

        Returns:
            pd.DataFrame | None: 生成的報告資料
        """
        # 處理空資料情況
        if processed_data is None:
            import logging

            logger = logging.getLogger(f"PETsARD.{__name__}")
            logger.warning("No timing data found. No CSV file will be saved.")
            return None

        if processed_data.empty:
            import logging

            logger = logging.getLogger(f"PETsARD.{__name__}")
            logger.warning("No timing data found. No CSV file will be saved.")
            return None

        # 保存報告
        full_output: str = f"{self.config['output']}[Timing]"
        self._save(data=processed_data, full_output=full_output)

        return processed_data

    def _process_timing_data(self, timing_data: pd.DataFrame) -> pd.DataFrame:
        """
        處理時間資料的核心邏輯

        Args:
            timing_data (pd.DataFrame): 原始時間資料

        Returns:
            pd.DataFrame: 處理後的時間資料
        """
        # 複製資料以避免修改原始資料
        timing_data = timing_data.copy()

        # Filter by modules if specified
        if self.config["modules"]:
            timing_data = timing_data[
                timing_data["module_name"].isin(self.config["modules"])
            ]

        # Handle time unit conversion
        time_unit = self.config["time_unit"]
        if time_unit != "seconds":
            # Create new column with converted time
            duration_col = f"duration_{time_unit}"
            if time_unit == "minutes":
                timing_data[duration_col] = timing_data["duration_seconds"] / 60
            elif time_unit == "hours":
                timing_data[duration_col] = timing_data["duration_seconds"] / 3600
            elif time_unit == "days":
                timing_data[duration_col] = timing_data["duration_seconds"] / 86400

            # Remove the original duration_seconds column
            timing_data = timing_data.drop(columns=["duration_seconds"])

            # Reorder columns to put the new duration column in the right place
            cols = list(timing_data.columns)
            if duration_col in cols:
                cols.remove(duration_col)
                # Insert after 'end_time' if it exists
                if "end_time" in cols:
                    insert_idx = cols.index("end_time") + 1
                    cols.insert(insert_idx, duration_col)
                else:
                    cols.append(duration_col)
                timing_data = timing_data[cols]

        return timing_data
