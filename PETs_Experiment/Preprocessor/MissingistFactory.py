class MissingistFactory:
    def __init__(self
                ,df_data      # : pd.DataFrame
                ,missing_method  : str
                ,missing_columns : list = None
                ,**kwargs):
        if missing_method == 'drop':
            from .Missingist_drop import Missingist_drop
            _Missingist = Missingist_drop(df_data         = df_data
                                         ,missing_columns = missing_columns)
        else:
            raise ValueError(f"MissingistFactory: missing_method {missing_method} didn't support.")
        
        self.df_data    = df_data
        self.Missingist = _Missingist
        # self.missing_columns    = _Missingist.missing_columns
        # self.cols_check_missing = _Missingist.cols_check_missing

    def handle(self): # -> pd.DataFrame
        return self.Missingist.handle()