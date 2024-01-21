class Postprocessor:
    def __init__(self, data, encoder=None, scaler=None, missingist=None):

        # Assume order here: Encoder than Scaler.
        #     So decode should Scaler than Encoder
        if scaler:
            data = self._decoding(data, scaler, 'Scaler')
        if encoder:
            data = self._decoding(data, encoder, 'Encoder')
        if missingist:
            data = self._decoding(data, missingist, 'Missingist')

        self.data = data

    def _decoding(self, data, Preprocessor, action=''):
        df_result = data.copy()
        for col, preprocessor in Preprocessor.items():
            if action == 'Encoder':
                col_data = data[col].values
            elif action == 'Scaler':
                col_data = data[col].values.reshape(-1, 1)
            elif action == 'Missingist':
                col_data = data[col].values
            else:
                raise ValueError(
                    f"Postprocessor - _decoding: "
                    f"Only Encoder, Scaler, and Missingist "
                    f"is allowed to decoding."
                )

            df_result[col] = preprocessor.inverse_transform(
                col_data).ravel()
            print(
                f"Postprocessor - "
                f"{action} ({str(preprocessor).rstrip('()')}): "
                f"Decoding {col}."
            )

        return df_result
