import numpy as np
from pandas.api.types import CategoricalDtype
import pandas as pd

from .Encoder import Encoder
from .UniformEncoder import UniformEncoder


class Encoder_Uniform(Encoder):
    def __init__(self, df_data, **kwargs):
        super().__init__(df_data, **kwargs)

    def handle(self):
        """
        Encoder - Uniform Encoder.
        Map the categories to an uniform distribution.

        For example, a column with two categories (e.g., 'Male', 'Female')
            can be mapped to [0.0, 0.5) and [0.5, 1], respectively.

        ...
        Method:
            Encoder_Uniform(pandas.DataFrame)
            Returns:
                pandas.DataFrame: A pandas DataFrame
                    containing labelized data.
        ...

        Args:

            df_data (pandas.DataFrame):
                The pandas DataFrame which might included missing value.

            encoder_columns_action (list ,optional):
                Specifies the columns for convert by encoder.
        """
        self.dict_encoder = {}
        for col_name in self.encoding_columns_action:
            col_data = self.df_data[col_name]
            if isinstance(col_data.dtype, CategoricalDtype):
                self.dict_encoder[col_name] = UniformEncoder()
                self.dict_encoder[col_name].fit(col_data)
                self.df_data[col_name] = \
                    self.dict_encoder[col_name].transform(col_data)

        return self.df_data, self.dict_encoder