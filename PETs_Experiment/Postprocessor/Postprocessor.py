class Postprocessor:
    def __init__(self, data, encoder=None, scaler=None
                 ):

        # Assume order here: Encoder than Scaler. So decode should Scaler than Encoder
        if scaler:
            data = self._decoding(data, scaler  ,'Scaler' )
        if encoder:
            data = self._decoding(data, encoder ,'Encoder')

        self.data = data

    def _decoding(self ,data, Preprocessor ,action=''):
        _df_result = data.copy()
        for _col, _Preprocessor in Preprocessor.items():
            if action == 'Encoder':
                _col_data = data[_col].values
            elif action == 'Scaler':
                _col_data = data[_col].values.reshape(1,-1)
            else:
                raise ValueError(
                    "Postprocessor - _decoding: Only Encoder/Scaler is allowed to decoding.")
            _df_result[_col] = _Preprocessor.inverse_transform(_col_data).ravel()
            print(f"Postprocessor - {action} ({str(_Preprocessor).rstrip('()')}): Decoding {_col}.")
        return _df_result
