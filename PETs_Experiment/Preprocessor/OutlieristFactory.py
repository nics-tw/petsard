from PETs_Experiment.Preprocessor import Outlierist_IsolationForest
from .Outlierist_IQR import Outlierist_IQR
from .Outlierist_Zscore import Outlierist_Zscore
from .Outlierist_IsolationForest import Outlierist_IsolationForest
from .Outlierist_LOF import Outlierist_LOF

class OutlieristFactory:
    def __init__(self, df_data, **kwargs):
        outlier_method = kwargs.get('outlier_method', None).lower()
        if outlier_method == 'iqr':
            _Outlierist = Outlierist_IQR(df_data=df_data, outlier_columns_action=kwargs.get(
                'outlier_columns_action', None))
        elif outlier_method == 'zscore':
            _Outlierist = Outlierist_Zscore(df_data=df_data, outlier_columns_action=kwargs.get(
                'outlier_columns_action', None))
        elif outlier_method == 'isof':
            _Outlierist = Outlierist_IsolationForest(df_data=df_data, outlier_columns_action=kwargs.get(
                'outlier_columns_action', None))
        elif outlier_method == 'lof':
            _Outlierist = Outlierist_LOF(df_data=df_data, outlier_columns_action=kwargs.get(
                'outlier_columns_action', None))
        else:
            raise ValueError(
                f"Preprocessor - OutlieristFactory: outlier_method {outlier_method} didn't support.")

        self.Outlierist = _Outlierist

    def handle(self):  # -> pd.DataFrame
        return self.Outlierist.handle()
