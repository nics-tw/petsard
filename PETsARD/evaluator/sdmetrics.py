import re
import time
from typing import (
    Dict
)

import pandas as pd
from sdmetrics.reports.single_table import (
    DiagnosticReport,
    QualityReport
)
from sdv.metadata import SingleTableMetadata


class SDMetricsMethodMap():
    """
    Mapping of SDMetrics.
    """
    DIAGNOSTICREPORT: int = 1
    QUALITYREPORT: int = 2

    @classmethod
    def getext(cls, method: str) -> int:
        """
        Get suffixes mapping int value
        ...
        Args:
            method (str):
                evaluating method
        """
        try:
            # accept both of "sdmetrics-single_table-" or "sdmetrics-" prefix
            return cls.__dict__[
                re.sub(
                    r"^(sdmetrics-single_table-|sdmetrics-)",
                    "",
                    method
                ).upper()
            ]
        except KeyError as ex:
            print(
                f"Evaluator (SDMetrics): Method "
                f"{method} not recognized.\n"
                f"{ex}"
            )


class SDMetrics:
    """
    Factory for "SDMetrics" Evaluator.

    SDMetricsFactory defines which module to use within SDMetrics.

    """

    def __init__(
        self,
        data: Dict[str, pd.DataFrame],
        method: str = None,
        **kwargs
    ):
        # Factory method for implementing the specified Loader class
        if SDMetricsMethodMap.getext(method) == SDMetricsMethodMap.DIAGNOSTICREPORT:
            self.Evaluator = SDMetricsDiagnosticReport(
                method=method,
                data=data
            )
        elif SDMetricsMethodMap.getext(method) == SDMetricsMethodMap.QUALITYREPORT:
            self.Evaluator = SDMetricsQualityReport(
                method=method,
                data=data
            )
        else:
            raise ValueError(
                f"Evaluator (SDMetrics): "
                f"method {method} didn't support."
            )

    def create_evaluator(self):
        """
        create_evaluator()
            return the Evaluator which selected by Factory.
        """
        return self.Evaluator


class SDMetricsBase():
    """
    Base class for all "SDMetrics".

    ...

    Args:
        data (dict)
            Following data logic defined in Evaluator.

    ...
    Returns:
        None

    ...
    TODO Consider use nametupled to replace "data" dict for more certain requirement

    """

    def __init__(
        self,
        data: Dict[str, pd.DataFrame],
        method: str = None,
        **kwargs
    ):
        self.data_ori = data['ori']
        self.data_syn = data['syn']
        self.eval_method = 'Unknown'

        data_ori_metadata = SingleTableMetadata()
        data_ori_metadata.detect_from_dataframe(self.data_ori)
        self.data_ori_metadata = data_ori_metadata.to_dict()

    def eval(self):
        """
        eval() of SDMetrics.
            Defines the sub-evaluator from the SDMetrics library

        """
        if self._Evaluator:
            time_start = time.time()
            print(
                f"Evaluator (SDMetrics): Evaluating {self.eval_method}."
            )

            self._Evaluator.generate(
                real_data=self.data_ori,
                synthetic_data=self.data_syn,
                metadata=self.data_ori_metadata
            )

            print(
                f"Evaluator (SDMetrics): "
                f"Evaluating {self.eval_method} spent "
                f"{round(time.time()-time_start ,4)} sec."
            )
            self.evaluation = self._extract_result()
        else:
            raise ValueError(
                f"Evaluator (SDMetrics): .eval() "
                f"while _Evaluator didn't ready."
            )

    def _extract_result(self) -> dict:
        """
        _extract_result of SDMetrics.

        ...
        Return
            (dict)
                Contains the following key-value pairs

        ...

        TODO  Consider using alternative methods to extract results
                and evaluate migrating this functionality to the Reporter.

        """
        dict_result = {}

        dict_result['score'] = self._Evaluator.get_score()

        # Tranfer pandas to desired dict format:
        #     {'properties name': {'Score': ...},
        #      'properties name': {'Score': ...}
        #     }
        dict_result['properties'] = (
            self._Evaluator.get_properties()
                .set_index('Property').rename_axis(None)
                .to_dict('index')
        )

        dict_result['details'] = {}
        for property in dict_result['properties'].keys():
            dict_result['details'][property] =\
                self._Evaluator.get_details(property_name=property)

        return dict_result


class SDMetricsDiagnosticReport(SDMetricsBase):
    """
    Estimation of the DiagnosticReport in the SDMetrics library.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.eval_method: str = 'DiagnosticReport'
        self._Evaluator = DiagnosticReport()


class SDMetricsQualityReport(SDMetricsBase):
    """
    Estimation of the QualityReport in the SDMetrics library.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.eval_method: str = 'QualityReport'
        self._Evaluator = QualityReport()
