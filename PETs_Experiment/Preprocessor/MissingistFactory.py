class MissingistFactory:
    def __init__(self
                ,df_data
                ,**kwargs):
        missing_method = kwargs.get('missing_method' ,None).lower()
        if missing_method == 'drop':
            from .Missingist_Drop import Missingist_Drop
            _Missingist = Missingist_Drop(df_data = df_data
                                         ,missing_columns_action = kwargs.get('missing_columns_action', None))
        else:
            raise ValueError(f"Preprocessor - MissingistFactory: missing_method {missing_method} didn't support.")
        
        self.Missingist = _Missingist

    def handle(self): # -> pd.DataFrame
        return self.Missingist.handle()