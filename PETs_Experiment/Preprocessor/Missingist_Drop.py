from .Missingist import Missingist


class Missingist_Drop(Missingist):
    def __init__(self, df_data, **kwargs):
        super().__init__(df_data, **kwargs)

    def handle(self):
        """
        Missing - Drop method.
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

            self.missing_columns_action (list ,optional):
                Specifies the columns for check missing value.
        """

        _row_before = self.df_data.shape[0]
        self.df_data = self.df_data.dropna(subset=self.missing_columns_action)\
                                   .reset_index(drop=True)
        _row_drop = _row_before - self.df_data.shape[0]

        if _row_drop == 0:
            print(f'Preprocessor - Missingist (Drop): No rows have been dropped.')
        else:
            print(
                f'Preprocessor - Missingist (Drop): Dropped {_row_drop} rows.')

        return self.df_data
