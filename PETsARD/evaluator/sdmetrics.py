import re
from typing import (
    Dict
)

import pandas as pd
from sdmetrics.reports.single_table import (
    DiagnosticReport,
    QualityReport
)
from sdv.metadata import SingleTableMetadata

from PETsARD.evaluator.evaluator_base import EvaluatorBase
from PETsARD.error import ConfigError, UnfittedError, UnsupportedEvalMethodError


class SDMetricsMap():
    """
    Mapping of SDMetrics.
    """
    DIAGNOSTICREPORT: int = 1
    QUALITYREPORT: int = 2

    @classmethod
    def map(cls, method: str) -> int:
        """
        Get suffixes mapping int value

        Args:
            method (str): evaluating method

        Return:
            (int): The method code.
        """
        try:
            # accept both of "sdmetrics-" or "sdmetrics-single_table-" prefix
            return cls.__dict__[
                re.sub(
                    r"^(sdmetrics-single_table-|sdmetrics-)",
                    "",
                    method
                ).upper()
            ]
        except KeyError:
            raise UnsupportedEvalMethodError


class SDMetrics(EvaluatorBase):
    """
    Factory for SDMetrics Evaluator, defines which module to use within SDMetrics.

    TODO Consider use nametupled to replace "data" dict for more certain requirement
    """

    def __init__(self, config: dict):
        """
        Args:
            config (dict): A dictionary containing the configuration settings.
                - method (str): The method of how you evaluating data.

        Attributes:
            evaluator (Anonymeter): Anonymeter class for implementing the Anonymeter.
        """
        super().__init__(config=config)

        self.config['method_code'] = SDMetricsMap.map(self.config['method'])

        if self.config['method_code'] == SDMetricsMap.DIAGNOSTICREPORT:
            self.evaluator = DiagnosticReport()
        elif self.config['method_code'] == SDMetricsMap.QUALITYREPORT:
            self.evaluator = QualityReport()
        else:
            raise UnsupportedEvalMethodError

        self.metadata: dict = None

    def create(self, data: dict):
        """
        create() of SDMetrics.
            Defines the sub-evaluator from the SDMetrics library,
            and build the metadata from the original data.

        Args:
            data (dict): The data required for description/evaluation.
                - ori (pd.DataFrame): The original data used for synthesis.
                - syn (pd.DataFrame): The synthetic data generated from 'ori'.

        Attributes:
            metadata (dict):
                A dictionary containing the metadata information as SDV format.

        TODO Consider use nametupled to replace "data" dict for more certain requirement
        """
        if 'ori' not in data or 'syn' not in data:
            raise ConfigError
        self.data = data

        data_ori_metadata = SingleTableMetadata()
        data_ori_metadata.detect_from_dataframe(self.data['ori'])
        self.metadata = data_ori_metadata.to_dict()

    def _extract_result(self) -> dict:
        """
        _extract_result of SDMetrics.
            Uses .get_score()/.get_properties()/.get_details() method in SDMetrics
            to extract result from self.evaluator into the designated dictionary.

        Return
            (dict). Result as following key-value pairs:
            - score (pd.DataFrame):
            - properties (pd.DataFrame):
            - details (pd.DataFrame):
        """
        result = {}

        result['score'] = self.evaluator.get_score()

        # Tranfer pandas to desired dict format:
        #     {'properties name': {'Score': ...},
        #      'properties name': {'Score': ...}
        #     }
        result['properties'] = (
            self.evaluator.get_properties()
                .set_index('Property').rename_axis(None)
                .to_dict('index')
        )

        result['details'] = {}
        for property in result['properties'].keys():
            result['details'][property] =\
                self.evaluator.get_details(property_name=property)

        return result

    def eval(self) -> None:
        """
        Evaluate the SDMetrics process.

        Return
            None. Result contains in self.result as following key-value pairs:
        """
        if not self.evaluator:
            raise UnfittedError

        self.evaluator.generate(
            real_data=self.data['ori'],
            synthetic_data=self.data['syn'],
            metadata=self.metadata
        )
        self.result = self._extract_result()

    def get_global(self) -> pd.DataFrame:
        """
        Returns the global result from the SDMetrics.

        Returns:
            pd.DataFrame: None for SDMetrics didn't have column-wise result.
        """
        return None

    def get_columnwise(self) -> pd.DataFrame:
        """
        Retrieves the column-wise result from the SDMetrics.

        Returns:
            pd.DataFrame: None for SDMetrics didn't have column-wise result.
        """
        return None

    def get_pairwise(self) -> pd.DataFrame:
        """
        Retrieves the pairwise result from the SDMetrics.

        Returns:
            pd.DataFrame: None for SDMetrics didn't have pairwise result.
        """
        return None
