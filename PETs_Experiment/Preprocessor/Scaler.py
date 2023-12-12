class Scaler:
    def __init__(self
                 ,df_data
                 ,**kwargs
                 ):
        self.df_data = df_data
        self.scaling_columns_action = kwargs.get('scaling_columns_action', None)

    def handle(self, **kwargs):
        raise NotImplementedError(
            "This method should be implemented by subclasses.")