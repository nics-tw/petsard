from .Missingist_Drop import Missingist_Drop
from .Missingist_Mean import Missingist_Mean
from .Missingist_Median import Missingist_Median
from .Missingist_Simple import Missingist_Simple
import pandas as pd

class MissingistFactory:
    def __init__(self, df_data, **kwargs):

        self.missing_dict = {}
        self.missing_col = kwargs.get('missing_columns_action', None)
        self.df = df_data

        try:
            self.missing_method = kwargs.get('missing_method', None).lower()
        except AttributeError:
            self.missing_method = kwargs.get('missing_method', None)
        except:
            raise ValueError(
                    f"Preprocessor - MissingistFactory: missing_method {self.missing_method} didn't support.")

        if self.missing_col is not None:
            for col in self.missing_col:
                if self.missing_method == 'drop':
                    _Missingist = Missingist_Drop(
                        df_data=df_data[col])
                elif self.missing_method == 'mean':
                    _Missingist = Missingist_Mean(
                        df_data=df_data[col])
                elif self.missing_method == 'median':
                    _Missingist = Missingist_Median(
                        df_data=df_data[col])
                elif isinstance(self.missing_method, float) or isinstance(self.missing_method, int):
                    _Missingist = Missingist_Simple(
                        df_data=df_data[col], missing_method=self.missing_method)
                else:
                    raise ValueError(
                            f"Preprocessor - MissingistFactory: missing_method {self.missing_method} didn't support.")

                self.missing_dict[col] = _Missingist

    def handle(self):  # -> pd.DataFrame
        processed_df = self.df.copy()
        for col in self.missing_col:
            handled_data = self.missing_dict[col].handle()
            processed_df[col] = handled_data.values

        if self.missing_method == 'drop':
            processed_df.dropna(inplace=True)
        return processed_df, self.missing_dict