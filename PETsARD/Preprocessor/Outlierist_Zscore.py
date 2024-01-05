from pandas import to_datetime
from pandas.api.types import (
    is_dtype_equal,
    is_numeric_dtype,
    is_datetime64_any_dtype
)

from .Outlierist import Outlierist


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

        row_ori = self.df_data.shape[0]
        digits_row_ori = len(str(row_ori))
        index_final = set(self.df_data.index)
        digits_longest_colname = \
            len(max(self.outlier_columns_action, key=len))
        for col_name in self.outlier_columns_action:
            col_data = self.df_data[col_name]
            if is_numeric_dtype(col_data) or \
                    is_datetime64_any_dtype(col_data):
                if is_datetime64_any_dtype(col_data):

                    col_data_timestamp = \
                        to_datetime(col_data).view(int) / 10**9
                    index_filter, mean, scale = \
                        self._index_Zscore(col_data_timestamp)

                    if is_dtype_equal(col_data.dtype, 'datetime64[ns]'):
                        mean = to_datetime(mean, unit='s').normalize()
                        scale = to_datetime(scale, unit='s').normalize()
                    else:
                        mean = to_datetime(mean, unit='s')
                        scale = to_datetime(scale, unit='s')
                else:
                    index_filter, mean, scale = \
                        self._index_Zscore(col_data)

                row_drop = len(index_filter)
                index_final -= set(index_filter)

                if row_drop == 0:
                    print(
                        f"Preprocessor - Outlierist (Z-score): "
                        f"No rows have been dropped on {col_name}."
                    )
                else:
                    print(
                        f"Preprocessor - Outlierist (Z-score): "
                        f"Dropped {row_drop: >{digits_row_ori}} rows "
                        f"on {col_name: <{digits_longest_colname}}. "
                        f"Kept [{mean}, {scale}] only."
                    )

        row_drop_ttl = row_ori - len(index_final)
        if row_drop_ttl == 0:
            print(
                f"Preprocessor - Outlierist (Z-score): "
                f"None of rows have been dropped."
            )
        else:
            print(
                f"Preprocessor - Outlierist (Z-score): "
                f"Totally Dropped {row_drop_ttl: >{digits_row_ori}} "
                f"in {row_ori} rows."
            )

        self.df_data = self.df_data\
            .loc[list(index_final)].reset_index(drop=True)

        return self.df_data

    def _index_Zscore(self, col_data, Z_limit: float = 3.0):
        m = col_data.mean()
        s = col_data.std()
        col_fit = (col_data - m)/s
        return col_data.index[
            ((col_fit < -Z_limit) | (col_fit > Z_limit))
        ].tolist(), m, s
