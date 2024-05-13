import re
from typing import Union

import pandas as pd
from sdmetrics.reports.single_table import (
    DiagnosticReport,
    QualityReport
)
from sdv.metadata import SingleTableMetadata

from PETsARD.evaluator.evaluator_base import EvaluatorBase
from PETsARD.error import (
    ConfigError,
    UnfittedError,
    UnsupportedMethodError
)
from PETsARD.util import safe_round


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
            raise UnsupportedMethodError


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
            raise UnsupportedMethodError

        self.metadata: dict = None

    def _create(self, data: dict):
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
        if not set(data.keys()) == set(['ori', 'syn', 'control']):
            raise ConfigError
        if 'control' in data:
            data.pop('control')
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

        result['score'] = safe_round(self.evaluator.get_score())

        # Tranfer pandas to desired dict format:
        #     {'properties name': {'Score': ...},
        #      'properties name': {'Score': ...}
        #     }
        properties = self.evaluator.get_properties()
        properties['Score'] = safe_round(properties['Score'])

        result['properties'] = \
            properties.set_index('Property').rename_axis(None).to_dict('index')

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

    def _transform_details(self, property: str) -> pd.DataFrame:
        """
        Transforms the details of a specific property in the result dictionary.

        Args:
            property (str): The name of the property.

        Returns:
            (pd.DataFrame) The transformed details dataframe.
        """
        data: pd.DataFrame = self.result['details'][property].copy()

        # set column as index, and remove index name
        if 'Column' in data.columns:
            data.set_index('Column', inplace=True)
            data.index.name = None
        else:
            # set pairwise columns as one column
            data.set_index(['Column 1', 'Column 2'], inplace=True)
            data.index.names = [None, None]

        # set Property
        data['Property'] = property

        # sort columns
        return data[
            ['Property', 'Metric']+
            [col for col in data.columns if col not in ['Property', 'Metric']]
        ]

    def get_global(self) -> Union[pd.DataFrame, None]:
        """
        Returns the global result from the SDMetrics.

        Returns:
            pd.DataFrame: A DataFrame with the global evaluation result.
                One row only for representing the whole data result.
        """
        # get_score
        data = {'Score': self.result['score']}
        # get_properties
        data.update(
            {key: value['Score']
             for key, value in self.result['properties'].items()}
        )
        return pd.DataFrame.from_dict(
            data={'result': data},
            orient='columns'
        ).T

    def get_columnwise(self) -> Union[pd.DataFrame, None]:
        """
        Retrieves the column-wise result from the SDMetrics.

        Returns:
            pd.DataFrame: A DataFrame with the column-wise evaluation result.
                One row represent one column data result.
        """
        if self.config['method_code'] == SDMetricsMap.DIAGNOSTICREPORT:
            property = 'Data Validity'
        elif self.config['method_code'] == SDMetricsMap.QUALITYREPORT:
            property = 'Column Shapes'
        else:
            raise UnsupportedMethodError

        return self._transform_details(property=property)

    def get_pairwise(self) -> Union[pd.DataFrame, None]:
        """
        Retrieves the pairwise result from the SDMetrics.

        Returns:
            pd.DataFrame: A DataFrame with the column-wise evaluation result.
                One row represent one "column x column" data result.
        """
        if self.config['method_code'] == SDMetricsMap.DIAGNOSTICREPORT:
            return None
        elif self.config['method_code'] == SDMetricsMap.QUALITYREPORT:
            property = 'Column Pair Trends'
            return self._transform_details(property=property)
        else:
            raise UnsupportedMethodError
