import pandas as pd

from .Outlierist_IQR import Outlierist_IQR
from .Outlierist_Zscore import Outlierist_Zscore
from .Outlierist_IsolationForest import Outlierist_IsolationForest
from .Outlierist_LOF import Outlierist_LOF


class OutlieristFactory:
    def __init__(self, df_data, **kwargs):
        outlier_method = kwargs.get('outlier_method', None).lower()
        if outlier_method == 'iqr':
            self.Outlierist = Outlierist_IQR(
                df_data=df_data,
                outlier_columns_action=kwargs.get(
                    'outlier_columns_action', None)
            )
        elif outlier_method == 'zscore':
            self.Outlierist = Outlierist_Zscore(
                df_data=df_data,
                outlier_columns_action=kwargs.get(
                    'outlier_columns_action', None)
            )
        elif outlier_method == 'isof':
            self.Outlierist = Outlierist_IsolationForest(
                df_data=df_data,
                outlier_columns_action=kwargs.get(
                    'outlier_columns_action', None)
            )
        elif outlier_method == 'lof':
            self.Outlierist = Outlierist_LOF(
                df_data=df_data,
                outlier_columns_action=kwargs.get(
                    'outlier_columns_action', None)
            )
        else:
            raise ValueError(
                f"Preprocessor - OutlieristFactory: "
                f"outlier_method {outlier_method} didn't support."
            )

    def handle(self) -> pd.DataFrame:

        return self.Outlierist.handle()
