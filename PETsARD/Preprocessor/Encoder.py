class Encoder:
    def __init__(
            self,
            df_data,
            **kwargs
    ):
        self.df_data = df_data
        self.encoding_columns_action = \
            kwargs.get('encoding_columns_action', None)

    def handle(self, **kwargs):
        raise NotImplementedError(
            f"Preprocessor - Encoder: "
            f"This method should be implemented by subclasses."
        )
