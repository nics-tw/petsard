from .Missingist import Missingist


class Missingist_Median(Missingist):
    def __init__(self, df_data, **kwargs):
        super().__init__(df_data, **kwargs)

    def handle(self):
        """
        Missing - Fill median method.
        Fill the missing values with the median in DataFrame.

        ...
        Method:
            Missingist_Mean(pandas.DataFrame)
            Returns:
                pandas.DataFrame: A pandas DataFrame
                    containing the table with filled missing value, and already re-indexing.
        ...

        Args:

            df_data (pandas.DataFrame):
                The pandas DataFrame which might included missing value.

            self.missing_columns_action (list ,optional):
                Specifies the columns for check missing value.
        """

        _row_before = self.df_data.isna().sum()
        processed = self.df_data.fillna(value=self.df_data.median()).reset_index(drop=True)
        _row_filled = _row_before - processed.isna().sum()

        if _row_filled == 0:
            print(f'Preprocessor - Missingist (Median): No rows have been filled.')
        else:
            print(
                f'Preprocessor - Missingist (Median): Filled {_row_filled} rows.')

        return processed
