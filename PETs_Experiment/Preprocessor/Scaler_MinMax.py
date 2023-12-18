from .Scaler import Scaler
from pandas.api.types import is_numeric_dtype
from sklearn.preprocessing import MinMaxScaler


class Scaler_MinMax(Scaler):
    def __init__(self, df_data, **kwargs):
        super().__init__(df_data, **kwargs)

    def handle(self):
        """
        Scaler - Min-Max Scaling.
        Scaling data in DataFrame via Min-Max Scaling,
        the range of values will be between 0 and 1.
        Use sklearn.preprocessing.MinMaxScaler.

        ...
        Method:
            Scaler_MinMax(pandas.DataFrame)
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
        _digits_longest_colname = len(
            max(self.scaling_columns_action, key=len))
        for _col_name in self.scaling_columns_action:
            _col_data = self.df_data[_col_name]
            if is_numeric_dtype(_col_data):
                self.dict_scaler[_col_name] = MinMaxScaler()
                self.df_data[_col_name] = self.dict_scaler[_col_name].fit_transform(
                    _col_data.values.reshape(-1, 1))

                print(
                    f'Preprocessor - Scaler (Standard): Column {_col_name:<{_digits_longest_colname}} been standardized.')

        return self.df_data, self.dict_scaler
