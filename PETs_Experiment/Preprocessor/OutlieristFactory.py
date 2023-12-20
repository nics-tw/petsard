from .Outlierist_IQR import Outlierist_IQR

class OutlieristFactory:
    def __init__(self, df_data, **kwargs):
        outlier_method = kwargs.get('outlier_method', None).lower()
        if outlier_method == 'iqr':
            _Outlierist = Outlierist_IQR(df_data=df_data, outlier_columns_action=kwargs.get(
                'outlier_columns_action', None))
        else:
            raise ValueError(
                f"Preprocessor - OutlieristFactory: outlier_method {outlier_method} didn't support.")

        self.Outlierist = _Outlierist

    def handle(self):  # -> pd.DataFrame
        return self.Outlierist.handle()
