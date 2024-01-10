import pandas as pd

from .Encoder_Label import Encoder_Label
from .Encoder_Uniform import Encoder_Uniform


class EncoderFactory:
    def __init__(self, df_data, **kwargs):
        encoding_method = kwargs.get('encoding_method', None).lower()
        if encoding_method == 'label':
            self.Encoder = Encoder_Label(
                df_data=df_data,
                encoding_columns_action=kwargs.get(
                    'encoding_columns_action', None)
            )
        elif encoding_method == 'uniform':
            self.Encoder = Encoder_Uniform(
                df_data=df_data,
                encoding_columns_action=kwargs.get(
                    'encoding_columns_action', None)
            )
        else:
            raise ValueError(
                f"Preprocessor - EncoderFactory: "
                f"encoding_method {encoding_method} didn't support."
            )

    def handle(self) -> pd.DataFrame:
        return self.Encoder.handle()
