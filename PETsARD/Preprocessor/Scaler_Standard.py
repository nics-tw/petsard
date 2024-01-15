from pandas.api.types import is_numeric_dtype
from sklearn.preprocessing import StandardScaler

from PETsARD.Preprocessor.Scaler import Scaler


class Scaler_Standard(Scaler):
    def __init__(self, df_data, **kwargs):
        super().__init__(df_data, **kwargs)

    def handle(self):
        """
        Scaler - Standardization.
        Scaling data in DataFrame via Standardization,
        means removing the mean and scaling to unit variance.
        Use sklearn.preprocessing.StandardScaler.

        ...
        Method:
            Scaler_Standard(pandas.DataFrame)
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
                self.dict_scaler[col_name] = StandardScaler()
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
