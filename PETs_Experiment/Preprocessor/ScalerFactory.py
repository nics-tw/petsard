class ScalerFactory:
    def __init__(self
                ,df_data
                ,**kwargs):
        scaling_method = kwargs.get('scaling_method' ,None).lower()
        if scaling_method == 'standard':
            from .Scaler_Standard import Scaler_Standard
            _Scaler = Scaler_Standard(df_data = df_data
                                     ,scaling_columns_action = kwargs.get('scaling_columns_action', None))
        else:
            raise ValueError(f"Preprocessor - ScalerFactory: scaling_method {scaling_method} didn't support.")
        
        self.Scaler = _Scaler

    def handle(self): # -> pd.DataFrame
        return self.Scaler.handle()