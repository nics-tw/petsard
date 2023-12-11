from .Missingist import Missingist

class Missingist_drop(Missingist):
    def __init__(self, df_data, missing_columns, **kwargs):
        super().__init__(df_data, missing_columns, **kwargs) 

    def handle(self):
        """
        Drop all missing value in DataFrame.

        ...
        Method:
            Missingist_drop(pandas.DataFrame)
            Returns:
                pandas.DataFrame: A pandas DataFrame
                    containing drop missing value data, and already re-indexing.
        ...

        Args:

            df_data (pandas.DataFrame):
                The pandas DataFrame which might included missing value.

            cols_check_missing (list ,optional):
            Specifies the columns for check missing value.
            Default is None, it means check all of columns.

        ...
        Raises:
            ValueError: If 'dict_missing' contains both 'miss' and 'keep'.
                It will be conflict, consider to set {colnames: 'miss'} if you already focus on some columns
        """

        _row_before  = self.df_data.shape[0]
        self.df_data = self.df_data.dropna(subset = self.cols_check_missing)\
                                   .reset_index(drop=True)
        _row_drop    = _row_before - self.df_data.shape[0]

        if _row_drop == 0:
            print(f'Missingist Drop: No rows have been dropped.')
        else:
            print(f'Missingist Drop: Dropped {_row_drop} rows.')

        return self.df_data