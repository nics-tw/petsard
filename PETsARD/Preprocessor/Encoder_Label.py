from .Encoder import Encoder
from pandas.api.types import CategoricalDtype
from sklearn.preprocessing import LabelEncoder


class Encoder_Label(Encoder):
    def __init__(self, df_data, **kwargs):
        super().__init__(df_data, **kwargs)

    def handle(self):
        """
        Encoder - Label Encoder.
        Encoding categorical data in DataFrame based on their labels,
        value between 0 to n_classes-1.
        Use sklearn.preprocessing.LabelEncoder.

        ...
        Method:
            Encoder_Label(pandas.DataFrame)
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
        _digits_longest_colname = len(
            max(self.encoding_columns_action, key=len))
        _max_max_code = 0
        _arr_print = []
        for _col_name in self.encoding_columns_action:
            _col_data = self.df_data[_col_name]
            if isinstance(_col_data.dtype, CategoricalDtype):
                self.dict_encoder[_col_name] = LabelEncoder()
                self.df_data[_col_name] = self.dict_encoder[_col_name].fit_transform(
                    _col_data)

                _max_code = len(self.dict_encoder[_col_name].classes_)-1
                _max_max_code = max(_max_max_code, _max_code)

                _arr_print.append(
                    [f'Preprocessor - Encoder (Label): Column {_col_name:<{_digits_longest_colname}} been labelized from 0 to ', _max_code, '.'])

        # Label result with colname and max_label alignment.
        # e.g.
        # Preprocessor - Encoder (Label): Column workclass       been labelized from 0 to  8.
        _arr_print = [
            f"{col1}{col2:>{len(str(_max_max_code))}}{col3}" for col1, col2, col3 in _arr_print]
        print('\n'.join(_arr_print))

        return self.df_data, self.dict_encoder
