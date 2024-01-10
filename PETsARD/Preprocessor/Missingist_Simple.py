from PETsARD.Preprocessor.Missingist import Missingist


class Missingist_Simple(Missingist):
    def __init__(self, df_data, **kwargs):
        super().__init__(df_data, **kwargs)
        self.value = kwargs.get('missing_method', None)

    def handle(self):
        """
        Missing - Simple fill method.
        Fill the missing values with a predetermined number.

        ...
        Method:
            Missingist_Mean(pandas.DataFrame)
            Returns:
                pandas.DataFrame: A pandas DataFrame
                    containing the table with filled missing value,
                    and already re-indexing.
        ...

        Args:

            df_data (pandas.DataFrame):
                The pandas DataFrame which might included missing value.

            self.missing_columns_action (list ,optional):
                Specifies the columns for check missing value.
        """

        row_before = self.df_data.isna().sum()
        processed = self.df_data\
            .fillna(value=self.value).reset_index(drop=True)
        row_filled = row_before - processed.isna().sum()

        if row_filled == 0:
            print(
                f"Preprocessor - Missingist (Simple): "
                f"No rows have been filled."
            )
        else:
            print(
                f"Preprocessor - Missingist (Simple): "
                f"Filled {row_filled} rows."
            )

        return processed
