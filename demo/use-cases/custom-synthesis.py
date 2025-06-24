import numpy as np
import pandas as pd

from petsard.metadater import Metadata


class MySynthesizer_Shuffle:
    """
    A simple synthesizer that shuffles each column independently.

    This synthesizer preserves the distribution of each column while breaking
    the relationships between columns. It can be useful for simple anonymization
    or as a baseline synthetic data generation method.
    """

    def __init__(self, config: dict, metadata: Metadata):
        """
        Initialize the synthesizer.

        In this demo we don't use metadata, but please keep it in the signature,
        and feel free to prepare your synthesizer to use it.

        Args:
            metadata (Metadata): The metadata object.
        """
        self.config: dict = config
        self.result: pd.DataFrame = None

        if "random_seed" in self.config:
            np.random.seed(self.config["random_seed"])

    def fit(self, data: pd.DataFrame) -> None:
        """
        Shuffle Algorithm
        """
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Data must be a pandas DataFrame")

        if data.empty:
            raise ValueError("Cannot fit on empty data")

        columns: list[str] = data.columns.tolist()
        synthetic_data: pd.DataFrame = pd.DataFrame()

        values: np.ndarray = None
        for col in columns:
            # Get the column data and handle different types appropriately
            original_series: pd.Series = data[col]

            if pd.api.types.is_categorical_dtype(original_series):
                # For categorical data, convert to codes, shuffle, then map back
                codes = original_series.cat.codes.values.copy()
                np.random.shuffle(codes)
                # Convert shuffled codes back to categorical values
                synthetic_data[col] = pd.Categorical.from_codes(
                    codes,
                    categories=original_series.cat.categories,
                    ordered=original_series.cat.ordered,
                )
            else:
                # For non-categorical data, create a copy of values and shuffle
                values = original_series.values.copy()
                np.random.shuffle(values)
                synthetic_data[col] = values

        self.result = synthetic_data

    def sample(self) -> pd.DataFrame:
        return self.result
