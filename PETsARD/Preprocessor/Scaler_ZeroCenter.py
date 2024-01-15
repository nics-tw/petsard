from pandas.api.types import is_numeric_dtype
from sklearn.preprocessing import StandardScaler

from PETsARD.Preprocessor.Scaler import Scaler


class Scaler_ZeroCenter(Scaler):
    def __init__(self, df_data, **kwargs):
        super().__init__(df_data, **kwargs)

    def handle(self):
        """
        Scaler - Zero-Center Scaling.
        Scaling data in DataFrame via Zero-Center Scaling,
        the mean of the transformed data will be zero
            while the variance will be the same.
        Use sklearn.preprocessing.StandardScaler.

        ...
        Method:
            Scaler_ZeroCenter(pandas.DataFrame)
            Returns:
                pandas.DataFrame: A pandas DataFrame
                    containing scaling data.
        ...

        Args:

            df_data (pandas.DataFrame):
                The pandas DataFrame which might included missing value.

            encoder_columns_action (list ,optional):
                Specifies the columns for convert by encoder.
        """

        self.dict_scaler = {}
        digits_longest_colname = len(
            max(self.scaling_columns_action, key=len)
        )
        for col_name in self.scaling_columns_action:
            col_data = self.df_data[col_name]
            if is_numeric_dtype(col_data):
                self.dict_scaler[col_name] = StandardScaler(with_std=False)
                self.df_data[col_name] = \
                    self.dict_scaler[col_name].fit_transform(
                        col_data.values.reshape(-1, 1)
                )

                print(
                    f"Preprocessor - Scaler (Standard): "
                    f"Column {col_name:<{digits_longest_colname}} "
                    f"been standardized."
                )

        return self.df_data, self.dict_scaler
