import pandas as pd

from .Scaler_Standard import Scaler_Standard
from .Scaler_MinMax import Scaler_MinMax
from .Scaler_ZeroCenter import Scaler_ZeroCenter


class ScalerFactory:
    def __init__(self, df_data, **kwargs):
        scaling_method = kwargs.get('scaling_method', None).lower()
        if scaling_method == 'standard':
            self.Scaler = Scaler_Standard(
                df_data=df_data,
                scaling_columns_action=kwargs.get(
                    'scaling_columns_action', None)
            )
        elif scaling_method == 'minmax':
            self.Scaler = Scaler_MinMax(
                df_data=df_data,
                scaling_columns_action=kwargs.get(
                    'scaling_columns_action', None)
            )
        elif scaling_method == 'zerocenter':
            self.Scaler = Scaler_ZeroCenter(
                df_data=df_data,
                scaling_columns_action=kwargs.get(
                    'scaling_columns_action', None)
            )
        else:
            raise ValueError(
                f"Preprocessor - ScalerFactory: "
                f"scaling_method {scaling_method} didn't support."
            )

    def handle(self) -> pd.DataFrame:
        return self.Scaler.handle()
