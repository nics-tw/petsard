class Outlierist:
    def __init__(self
                 ,df_data
                 ,**kwargs
                 ):
        self.df_data = df_data
        self.outlier_columns_action = kwargs.get('outlier_columns_action', None)

    def handle(self, **kwargs):
        raise NotImplementedError(
            "This method should be implemented by subclasses.")