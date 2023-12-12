from .Scaler import Scaler

class Scaler_Standard(Scaler):
    def __init__(self ,df_data ,**kwargs):
        super().__init__(df_data ,**kwargs) 

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
        from pandas.api.types      import is_numeric_dtype
        from sklearn.preprocessing import StandardScaler

        self.dict_scaler = {}
        _digits_longest_colname = len(max(self.scaling_columns_action, key=len))
        for _col_name in self.scaling_columns_action:
            _col_data = self.df_data[_col_name]
            if is_numeric_dtype(_col_data):
                self.dict_scaler[_col_name] = StandardScaler()
                self.df_data[_col_name] = self.dict_scaler[_col_name].fit_transform(_col_data.values.reshape(1, -1))[0]

                print(f'Preprocessor - Scaler (Standard): Column {_col_name:<{_digits_longest_colname}} been standardized.')

        return self.df_data ,self.dict_scaler