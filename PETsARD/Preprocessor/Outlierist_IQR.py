from pandas import to_datetime
from pandas.api.types import (
    is_dtype_equal,
    is_numeric_dtype,
    is_datetime64_any_dtype
)

from .Outlierist import Outlierist


class Outlierist_IQR(Outlierist):
    def __init__(self, df_data, **kwargs):
        super().__init__(df_data, **kwargs)

    def handle(self):
        """
        Outlier - IQR method. Sometimes call Boxplot Rule.
        Drop all outlier based on 1.5 IQR in DataFrame.

        ...
        Method:
            Outlierist_IQR(pandas.DataFrame)
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
        digits_longest_colname = len(
            max(self.outlier_columns_action, key=len)
        )
        for col_name in self.outlier_columns_action:
            col_data = self.df_data[col_name]
            if is_numeric_dtype(col_data) or is_datetime64_any_dtype(col_data):
                if is_datetime64_any_dtype(col_data):

                    col_data_timestamp = \
                        to_datetime(col_data).view(int) / 10**9
                    index_filter, btm, upp = self._index_IQR(
                        col_data_timestamp
                    )

                    if is_dtype_equal(col_data.dtype, 'datetime64[ns]'):
                        btm = to_datetime(btm, unit='s').normalize()
                        upp = to_datetime(upp, unit='s').normalize()
                    else:
                        btm = to_datetime(btm, unit='s')
                        upp = to_datetime(upp, unit='s')
                else:
                    index_filter, btm, upp = self._index_IQR(col_data)

                row_drop = len(index_filter)
                index_final -= set(index_filter)

                if row_drop == 0:
                    print(
                        f"Preprocessor - Outlierist (IQR): "
                        f"No rows have been dropped on {col_name}."
                    )
                else:
                    print(
                        f"Preprocessor - Outlierist (IQR): "
                        f"Dropped {row_drop: >{digits_row_ori}} rows "
                        f"on {col_name: <{digits_longest_colname}}. "
                        f"Kept [{btm}, {upp}] only."
                    )

        row_drop_ttl = row_ori - len(index_final)
        if row_drop_ttl == 0:
            print(
                f"Preprocessor - Outlierist (IQR): "
                f"None of rows have been dropped."
            )
        else:
            print(
                f"Preprocessor - Outlierist (IQR): "
                f"Totally Dropped {row_drop_ttl: >{digits_row_ori}} "
                f"in {row_ori} rows."
            )

        self.df_data = self.df_data\
            .loc[list(index_final)].reset_index(drop=True)

        return self.df_data

    def _index_IQR(self, col_data, IQR_limit: float = 1.5):
        Q1 = col_data.quantile(0.25)
        Q3 = col_data.quantile(0.75)
        IQR = Q3 - Q1
        btm = Q1 - 1.5 * IQR
        upp = Q3 + 1.5 * IQR
        return col_data.index[
            ((col_data < btm) | (col_data > upp))
        ].tolist(), btm, upp
