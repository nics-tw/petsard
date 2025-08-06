import logging
import re
import warnings
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

import pandas as pd
from sdmetrics.reports.base_report import BaseReport
from sdmetrics.reports.single_table import DiagnosticReport, QualityReport
from sdv.metadata import Metadata as SDV_Metadata

from petsard.config_base import BaseConfig
from petsard.evaluator.evaluator_base import BaseEvaluator
from petsard.exceptions import UnsupportedMethodError
from petsard.metadater import safe_round


class SDMetricsSingleTableMap(Enum):
    """
    Mapping of SDMetrics.
    """

    DIAGNOSTICREPORT: int = auto()
    QUALITYREPORT: int = auto()

    @classmethod
    def map(cls, method: str) -> int:
        """
        Get suffixes mapping int value
            Accept both of "sdmetrics-" or "sdmetrics-single_table-" prefix

        Args:
            method (str): evaluating method

        Return:
            (int): The method code.
        """
        return cls.__dict__[
            re.sub(r"^(sdmetrics-single_table-|sdmetrics-)", "", method).upper()
        ]


@dataclass
class SDMetricsSingleTableConfig(BaseConfig):
    """
    Configuration for the sdmetrics single-table evaluator.

    Attributes:
        _logger (logging.Logger): The logger object.
        ori (pd.DataFrame): The original data.
        syn (pd.DataFrame): The synthetic data.
        metadata (dict): The metadata of the data.
    """

    ori: pd.DataFrame
    syn: pd.DataFrame
    metadata: dict = None

    def __post_init__(self):
        super().__post_init__()

        if not all(isinstance(attr, pd.DataFrame) for attr in [self.ori, self.syn]):
            error_msg: str = "The 'ori' and 'syn' attributes must be DataFrames."
            self._logger.error(error_msg)
            raise TypeError(error_msg)

    def create_metadata(self) -> None:
        """
        Create metadata from the original data.
        """
        self._logger.debug("Creating SDV metadata")
        sdv_metadata_result: SDV_Metadata = SDV_Metadata().detect_from_dataframe(
            self.ori
        )
        self.metadata = sdv_metadata_result._convert_to_single_table().to_dict()

    def get_sdmetrics_params(self) -> dict:
        """
        Get parameters in the format required by SDMetrics.

        Returns:
            dict: Parameters with 'real_data' and 'synthetic_data' keys
        """
        return {
            "real_data": self.ori,
            "synthetic_data": self.syn,
            "metadata": self.metadata,
        }


class SDMetricsSingleTable(BaseEvaluator):
    """
    Factory for SDMetrics Evaluator.
    """

    REQUIRED_INPUT_KEYS: list[str] = ["ori", "syn"]
    SDMETRICS_SINGLETABLE_CLASS_MAP: dict[int, BaseReport] = {
        SDMetricsSingleTableMap.DIAGNOSTICREPORT: DiagnosticReport,
        SDMetricsSingleTableMap.QUALITYREPORT: QualityReport,
    }
    REQUIRED_SDMETRICS_SINGLETABLE_KEYS: list[str] = [
        "real_data",
        "synthetic_data",
        "metadata",
    ]
    AVAILABLE_SCORES_GRANULARITY: list[str] = [
        "global",
        "columnwise",
        "pairwise",
    ]
    SDMETRICS_SCORES_GRANULARITY_PROPERTIES_MAP: dict[tuple[str, int], str] = {
        ("columnwise", SDMetricsSingleTableMap.DIAGNOSTICREPORT): "Data Validity",
        ("columnwise", SDMetricsSingleTableMap.QUALITYREPORT): "Column Shapes",
        ("pairwise", SDMetricsSingleTableMap.QUALITYREPORT): "Column Pair Trends",
    }

    def __init__(self, config: dict):
        """
        Args:
            config (dict): A dictionary containing the configuration settings.
                - eval_method (str): The method of how you evaluating data.

        Attributes:
            REQUIRED_INPUT_KEYS (list[str]): The required input keys.
            SDMETRICS_SINGLETABLE_CLASS_MAP (dict[int, BaseReport]): The mapping of the SDMetrics classes.
            REQUIRED_SDMETRICS_SINGLETABLE_KEYS (list[str]): The required SDMetrics keys.
            AVAILABLE_SCORES_GRANULARITY (list[str]): The available scores granularity.
            SDMETRICS_SCORES_GRANULARITY_PROPERTIES_MAP (dict[tuple[str, int], str]): The mapping of the scores granularity properties.
            _logger (logging.Logger): The logger object.
            config (dict): A dictionary containing the configuration settings.
            _impl (Any): The evaluator object.
        """
        super().__init__(config=config)
        self._logger: logging.Logger = logging.getLogger(
            f"PETsARD.{self.__class__.__name__}"
        )

        self._logger.debug(
            f"Initializing synthesizer with method: {self.config['eval_method']}"
        )
        try:
            method_code: int = SDMetricsSingleTableMap.map(self.config["eval_method"])
            self._logger.debug(f"Mapped method code: {method_code}")
            evaluator_class: Any = self.SDMETRICS_SINGLETABLE_CLASS_MAP[method_code]
        except KeyError as e:
            error_msg: str = (
                f"Unsupported evaluator method: {self.config['eval_method']}"
            )
            self._logger.error(error_msg)
            raise UnsupportedMethodError(error_msg) from e

        self._impl: BaseReport = evaluator_class()

    def _extract_scores(self) -> dict[str, pd.DataFrame]:
        """
        _extract_result of SDMetrics.
            Uses .get_score()/.get_properties()/.get_details() method in SDMetrics
            to extract result from self._impl into the designated dictionary.

        Return
            (dict[str, pd.DataFrame]) Result as following key-value pairs:
                - score
                - properties
                - details
        """

        sdmetrics_scores: dict[str, pd.DataFrame] = {}

        self._logger.debug("Extract scores level from SDMetrics")
        sdmetrics_scores["score"] = safe_round(self._impl.get_score())

        # Tranfer pandas to desired dict format:
        #     {'properties name': {'Score': ...}, ...}
        properties = self._impl.get_properties()
        properties["Score"] = properties["Score"].apply(safe_round)

        self._logger.debug("Extracting properties level from SDMetrics")
        sdmetrics_scores["properties"] = (
            properties.set_index("Property").rename_axis(None).to_dict("index")
        )

        self._logger.debug("Extracting details level from SDMetrics")
        sdmetrics_scores["details"] = {}
        for property in sdmetrics_scores["properties"].keys():
            sdmetrics_scores["details"][property] = self._impl.get_details(
                property_name=property
            )

        return sdmetrics_scores

    def _get_global(
        self, sdmetrics_scores: dict[str, pd.DataFrame]
    ) -> pd.DataFrame | None:
        """
        Returns the global result from the SDMetrics.

        Args:
            sdmetrics_scores (dict[str, pd.DataFrame]): The SDMetrics scores.
            property (str): The name of the property.

        Returns:
            (pd.DataFrame): A DataFrame with the global evaluation result.
                One row only for representing the whole data result.
        """
        # get_score
        data = {"Score": sdmetrics_scores["score"]}
        # get_properties
        data.update(
            {
                key: value["Score"]
                for key, value in sdmetrics_scores["properties"].items()
            }
        )
        return pd.DataFrame.from_dict(data={"result": data}, orient="columns").T

    def _transform_details(
        self,
        sdmetrics_scores: dict[str, pd.DataFrame],
        property: str,
    ) -> pd.DataFrame:
        """
        Transforms the details of a specific property in the result dictionary.

        Args:
            sdmetrics_scores (dict[str, pd.DataFrame]): The SDMetrics scores.
            property (str): The name of the property.

        Returns:
            (pd.DataFrame) The transformed details dataframe.
        """
        data: pd.DataFrame = sdmetrics_scores["details"][property].copy()

        # set column as index, and remove index name
        if "Column" in data.columns:
            data.set_index("Column", inplace=True)
            data.index.name = None
        elif "Column 1" in data.columns and "Column 2" in data.columns:
            # set pairwise columns as one column
            data.set_index(["Column 1", "Column 2"], inplace=True)
            data.index.names = [None, None]
        # If neither single Column nor pairwise columns exist, keep as is

        # set Property
        data["Property"] = property

        # sort columns
        return data[
            ["Property", "Metric"]
            + [col for col in data.columns if col not in ["Property", "Metric"]]
        ]

    def _eval(self, data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        """
        Evaluating the evaluator.
            _impl should be initialized in this method.

        Args:
            data (dict[str, pd.DataFrame]): The data to be evaluated.

        Return:
            (dict[str, pd.DataFrame]): The evaluation result
        """
        self._logger.info("Evaluating with data")

        self._logger.debug("Initializing SDMetricsSingleTableConfig")

        sdmetrics_singletable_config: SDMetricsSingleTableConfig = (
            SDMetricsSingleTableConfig.from_dict(data)
        )
        sdmetrics_singletable_config.create_metadata()

        self._logger.debug("Initializing evaluator in _eval method")

        # catch warnings during synthesizer initialization:
        # "We strongly recommend saving the metadata using 'save_to_json' for replicability in future SDV versions."
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            params = sdmetrics_singletable_config.get_sdmetrics_params()
            self._impl.generate(**params)

            for warning in w:
                self._logger.debug(f"Warning during _eval: {warning.message}")

        self._logger.info("Successfully evaluating from data")

        sdmetrics_scores: dict[str, pd.DataFrame] = self._extract_scores()
        self._logger.debug(f"Extracted scores: {list(sdmetrics_scores.keys())}")

        scores: dict[str, pd.DataFrame] = {}
        for granularity in self.AVAILABLE_SCORES_GRANULARITY:
            self._logger.debug(f"Extracting {granularity} level as PETsARD format")

            method_code: int = SDMetricsSingleTableMap.map(self.config["eval_method"])

            # Check if we have a specific property mapping for this granularity
            if (
                granularity,
                method_code,
            ) in self.SDMETRICS_SCORES_GRANULARITY_PROPERTIES_MAP:
                property = self.SDMETRICS_SCORES_GRANULARITY_PROPERTIES_MAP[
                    (
                        granularity,
                        method_code,
                    )
                ]
                self._logger.debug(
                    f"Found property '{property}' for {granularity} level"
                )
                scores[granularity] = self._transform_details(
                    sdmetrics_scores, property=property
                )
            elif granularity == "global":
                # Fallback to general global scores if no specific mapping
                self._logger.debug(
                    f"Using general global scores for {granularity} level"
                )
                scores[granularity] = self._get_global(
                    sdmetrics_scores=sdmetrics_scores,
                )
            else:
                self._logger.debug(
                    f"Property not found for {granularity} level. Skipping."
                )
                scores[granularity] = None
        self._logger.info("Successfully extracting scores")

        return scores
