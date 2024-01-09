import numpy as np

class Missingist:
    def __init__(self, df_data, **kwargs):
        self.df_data = df_data
        self.missing_columns_action = kwargs.get(
            'missing_columns_action', None)
        self.na_percentage = self.df_data.isna().sum()/self.df_data.shape[0]
        self.rng = np.random.default_rng()

    def handle(self, **kwargs):
        raise NotImplementedError(
            "This method should be implemented by subclasses.")
    
    def inverse_transform(self, col_data):
        _na_mask = self.rng.random(len(col_data))
        _na_mask = _na_mask < self.na_percentage
        _col_data = col_data.copy()
        try:
            _col_data[_na_mask] = np.nan
        except ValueError:
            _col_data = _col_data.astype(float)
            _col_data[_na_mask] = np.nan
        return _col_data

