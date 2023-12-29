from .Outlierist import Outlierist
from pandas import to_datetime
from pandas.api.types import is_dtype_equal
from pandas.api.types import is_numeric_dtype, is_datetime64_any_dtype

class Outlierist_Zscore(Outlierist):
    def __init__(self, df_data, **kwargs):
        super().__init__(df_data, **kwargs)

    def handle(self):
        """
        Outlier - Z-score method.
        Drop the samples with z-score > 3.

        ...
        Method:
            Outlierist_Zscore(pandas.DataFrame)
            Returns:
                pandas.DataFrame: A pandas DataFrame
                    containing drop outlier data, and already re-indexing.
        ...

        Args:

            df_data (pandas.DataFrame):
                The pandas DataFrame which might included missing value.

            outlier_columns_action (list ,optional):
                Specifies the columns for check outlier value.
        """

        _row_ori = self.df_data.shape[0]
        _digits_row_ori = len(str(_row_ori))
        _index_final = set(self.df_data.index)
        _digits_longest_colname = len(
            max(self.outlier_columns_action, key=len))
        for _col_name in self.outlier_columns_action:
            _col_data = self.df_data[_col_name]
            if is_numeric_dtype(_col_data) or is_datetime64_any_dtype(_col_data):
                if is_datetime64_any_dtype(_col_data):

                    _col_data_timestamp = to_datetime(
                        _col_data).view(int) / 10**9
                    _index_filter, _mean, _scale = self._index_Zscore(
                        _col_data_timestamp)

                    if is_dtype_equal(_col_data.dtype, 'datetime64[ns]'):
                        _mean = to_datetime(_mean, unit='s').normalize()
                        _scale = to_datetime(_scale, unit='s').normalize()
                    else:
                        _mean = to_datetime(_mean, unit='s')
                        _scale = to_datetime(_scale, unit='s')
                else:
                    _index_filter, _mean, _scale = self._index_Zscore(_col_data)

                _row_drop = len(_index_filter)
                _index_final -= set(_index_filter)

                if _row_drop == 0:
                    print(
                        f'Preprocessor - Outlierist (Z-score): No rows have been dropped on {_col_name}.')
                else:
                    print(
                        f'Preprocessor - Outlierist (Z-score): Dropped {_row_drop: >{_digits_row_ori}} rows on {_col_name: <{_digits_longest_colname}}. Kept [{_mean}, {_scale}] only.')

        _row_drop_ttl = _row_ori - len(_index_final)
        if _row_drop_ttl == 0:
            print(f'Preprocessor - Outlierist (Z-score): None of rows have been dropped.')
        else:
            print(
                f'Preprocessor - Outlierist (Z-score): Totally Dropped {_row_drop_ttl: >{_digits_row_ori}} in {_row_ori} rows.')

        self.df_data = self.df_data.loc[list(_index_final)]\
                                   .reset_index(drop=True)

        return self.df_data

    def _index_Zscore(self, col_data, Z_limit: float = 3.0):
        m = col_data.mean()
        s = col_data.std()
        col_fit = (col_data - m)/s
        return col_data.index[((col_fit < -Z_limit)
                               | (col_fit > Z_limit))
                              ].tolist(), m, s
