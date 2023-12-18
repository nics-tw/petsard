class Missingist:
    def __init__(self, df_data, **kwargs):
        self.df_data = df_data
        self.missing_columns_action = kwargs.get(
            'missing_columns_action', None)

    def handle(self, **kwargs):
        raise NotImplementedError(
            "This method should be implemented by subclasses.")
