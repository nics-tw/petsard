from copy import deepcopy

import pandas as pd

from petsard.exceptions import UnexecutedError
from petsard.reporter.base_reporter import BaseReporter


class ReporterSaveTiming(BaseReporter):
    """
    Save timing data to file.
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

        Raises:
            ConfigError: If the 'source' key is missing in the config
                or if the value of 'source' is not a string or a list of strings.
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

    def create(self, data: dict = None) -> None:
        """
        Creating the timing data by collecting timing information from experiments.

        Args:
            data (dict): The data used for creating the timing report.
                - timing_data (pd.DataFrame): The timing data DataFrame.

        Attributes:
            - result (dict): Data for the timing report.
                - timing_report (pd.DataFrame): The timing data.
        """
        if data is None:
            data = {}

        timing_data = data.get("timing_data")

        # Handle empty or missing timing data
        if timing_data is None or (
            isinstance(timing_data, pd.DataFrame) and timing_data.empty
        ):
            self.result = {}
            return

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
                timing_data = timing_data.copy()
                timing_data[duration_col] = timing_data["duration_seconds"] / 60
            elif time_unit == "hours":
                timing_data = timing_data.copy()
                timing_data[duration_col] = timing_data["duration_seconds"] / 3600
            elif time_unit == "days":
                timing_data = timing_data.copy()
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

        # Collect result
        self.result["timing_report"] = deepcopy(timing_data)

    def report(self) -> None:
        """
        Generates a timing report based on the collected timing data.
            The report is saved to the specified output location.
        """
        if not self.result:
            import logging

            logger = logging.getLogger(f"PETsARD.{__name__}")
            logger.warning("No timing data found. No CSV file will be saved.")
            return

        if "timing_report" not in self.result:
            raise UnexecutedError

        timing_data: pd.DataFrame = self.result["timing_report"]

        if timing_data.empty:
            import logging

            logger = logging.getLogger(f"PETsARD.{__name__}")
            logger.warning("No timing data found. No CSV file will be saved.")
            return

        # petsard[Timing]
        full_output: str = f"{self.config['output']}[Timing]"

        self._save(data=timing_data, full_output=full_output)
