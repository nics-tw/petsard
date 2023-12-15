from .Outlierist import Outlierist

class Outlierist_IQR(Outlierist):
    def __init__(self ,df_data ,**kwargs):
        super().__init__(df_data ,**kwargs) 

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
        from pandas.api.types import is_numeric_dtype ,is_datetime64_any_dtype

        _row_ori        = self.df_data.shape[0]
        _digits_row_ori = len(str(_row_ori))
        _index_final    = set(self.df_data.index)
        _digits_longest_colname = len(max(self.outlier_columns_action, key=len))
        for _col_name in self.outlier_columns_action:
            _col_data = self.df_data[_col_name]
            if is_numeric_dtype(_col_data) or is_datetime64_any_dtype(_col_data):
                if is_datetime64_any_dtype(_col_data):
                    from pandas           import to_datetime
                    from pandas.api.types import is_dtype_equal

                    _col_data_timestamp = to_datetime(_col_data).view(int) / 10**9
                    _index_filter ,_btm ,_upp = self._index_IQR(_col_data_timestamp)
                
                    if is_dtype_equal(_col_data.dtype ,'datetime64[ns]'):
                        _btm = to_datetime(_btm ,unit='s').normalize()
                        _upp = to_datetime(_upp ,unit='s').normalize()
                    else:
                        _btm = to_datetime(_btm, unit='s')
                        _upp = to_datetime(_upp, unit='s')
                else:
                    _index_filter ,_btm ,_upp = self._index_IQR(_col_data)

                _row_drop     = len(_index_filter)
                _index_final -= set(_index_filter)

                if _row_drop == 0:
                    print(f'Preprocessor - Outlierist (IQR): No rows have been dropped on {_col_name}.')
                else:
                    print(f'Preprocessor - Outlierist (IQR): Dropped {_row_drop: >{_digits_row_ori}} rows on {_col_name: <{_digits_longest_colname}}. Kept [{_btm}, {_upp}] only.')

        _row_drop_ttl = _row_ori - len(_index_final)
        if _row_drop_ttl == 0:
            print(f'Preprocessor - Outlierist (IQR): None of rows have been dropped.')
        else:
            print(f'Preprocessor - Outlierist (IQR): Totally Dropped {_row_drop_ttl: >{_digits_row_ori}} in {_row_ori} rows.')

        self.df_data = self.df_data.loc[list(_index_final)]\
                                   .reset_index(drop=True)

        return self.df_data

    def _index_IQR(self ,col_data ,IQR_limit:float=1.5):
        Q1  = col_data.quantile(0.25)
        Q3  = col_data.quantile(0.75)
        IQR = Q3 - Q1
        btm = Q1 - 1.5 * IQR
        upp = Q3 + 1.5 * IQR
        return col_data.index[(  (col_data < btm) \
                               | (col_data > upp)  )
                             ].tolist()\
              ,btm ,upp