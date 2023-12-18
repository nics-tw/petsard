from .Missingist_Drop import Missingist_Drop
from .Missingist_Mean import Missingist_Mean
from .Missingist_Median import Missingist_Median
from .Missingist_Simple import Missingist_Simple

class MissingistFactory:
    def __init__(self, df_data, **kwargs):
        try:
            missing_method = kwargs.get('missing_method', None).lower()
        except AttributeError:
            missing_method = kwargs.get('missing_method', None)
            if isinstance(missing_method, float) or isinstance(missing_method, int):
                _Missingist = Missingist_Simple(
                    df_data=df_data, missing_columns_action=kwargs.get('missing_columns_action', None), missing_method=missing_method)
        else:
            if missing_method == 'drop':
                _Missingist = Missingist_Drop(
                    df_data=df_data, missing_columns_action=kwargs.get('missing_columns_action', None))
            elif missing_method == 'mean':
                _Missingist = Missingist_Mean(
                    df_data=df_data, missing_columns_action=kwargs.get('missing_columns_action', None))
            elif missing_method == 'median':
                _Missingist = Missingist_Median(
                    df_data=df_data, missing_columns_action=kwargs.get('missing_columns_action', None))
            else:
                raise ValueError(
                    f"Preprocessor - MissingistFactory: missing_method {missing_method} didn't support.")

        self.Missingist = _Missingist

    def handle(self):  # -> pd.DataFrame
        return self.Missingist.handle()
