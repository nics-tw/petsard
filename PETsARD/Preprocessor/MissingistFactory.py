import pandas as pd

from PETsARD.Preprocessor.Missingist_Drop import Missingist_Drop
from PETsARD.Preprocessor.Missingist_Mean import Missingist_Mean
from PETsARD.Preprocessor.Missingist_Median import Missingist_Median
from PETsARD.Preprocessor.Missingist_Simple import Missingist_Simple


class MissingistFactory:
    def __init__(self, df_data, **kwargs):

        self.missing_dict = {}
        self.missing_col = kwargs.get('missing_columns_action', None)
        self.df = df_data

        # TODO Not assign value via Error
        try:
            self.missing_method = kwargs.get('missing_method', None).lower()
        except AttributeError:
            self.missing_method = kwargs.get('missing_method', None)
        except:
            raise ValueError(
                f"Preprocessor - MissingistFactory: "
                f"missing_method {self.missing_method} didn't support."
            )

        if self.missing_col is not None:
            for col in self.missing_col:
                if self.missing_method == 'drop':
                    self.missing_dict[col] = Missingist_Drop(
                        df_data=df_data[col]
                    )
                elif self.missing_method == 'mean':
                    self.missing_dict[col] = Missingist_Mean(
                        df_data=df_data[col]
                    )
                elif self.missing_method == 'median':
                    self.missing_dict[col] = Missingist_Median(
                        df_data=df_data[col]
                    )
                elif isinstance(self.missing_method, float) or\
                        isinstance(self.missing_method, int):
                    self.missing_dict[col] = Missingist_Simple(
                        df_data=df_data[col],
                        missing_method=self.missing_method
                    )
                else:
                    raise ValueError(
                        f"Preprocessor - MissingistFactory: "
                        f"missing_method {self.missing_method} didn't support."
                    )

    def handle(self) -> pd.DataFrame:
        processed_df = self.df.copy()
        for col in self.missing_col:
            handled_data = self.missing_dict[col].handle()
            processed_df[col] = handled_data.values

        if self.missing_method == 'drop':
            processed_df.dropna(inplace=True)

        return processed_df, self.missing_dict
