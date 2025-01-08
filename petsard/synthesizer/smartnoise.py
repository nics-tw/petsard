import pandas as pd
from snsynth import Synthesizer as SNSyn
from snsynth.transform import MinMaxTransformer, TableTransformer

from petsard import Metadata
from petsard.error import UnsupportedMethodError
from petsard.synthesizer.synthesizer_base import SynthesizerBase


class SmartNoise(SynthesizerBase):
    """
    Base class for all "SmartNoise".

    The "SmartNoise" class defines the common API
    that all the "SmartNoise" need to implement,
    as well as common functionality.
    """

    CUBE = ["aim", "mwem", "mst", "pacsynth"]
    GAN = ["dpctgan", "patectgan"]

    def __init__(self, data: pd.DataFrame, metadata: Metadata = None, **kwargs) -> None:
        """
        Args:
            data (pd.DataFrame): The data to be synthesized.
            metadata (Metadata, default=None): The metadata of the data.
            **kwargs: The other parameters.

        Attr.:
            syn_module (str): The name of the synthesizer module.
        """
        super().__init__(data, metadata, **kwargs)
        self.syn_module: str = "SmartNoise"

    def _fit(self) -> None:
        """
        Fit the synthesizer.

        Attr:
            data (pd.DataFrame): The data to be synthesized.
            syn_method (str): The synthesizing method to be applied.
            constant_data (dict): The dict of constant columns.
            _synthesizer (SyntheszierBase): The synthesizer object.
        """
        if self.syn_method in self.CUBE:
            self._synthesizer.fit(self.data, categorical_columns=self.data.columns)
        else:
            data_to_syn: pd.DataFrame = self.data.copy()

            for idx, col in enumerate(self.data.columns):
                if self.data[col].nunique() == 1:
                    # If the column has only one unique value,
                    # it is a constant column.
                    self.constant_data[col] = (self.data[col].unique()[0], idx)
                    data_to_syn.drop(col, axis=1, inplace=True)

            tt = TableTransformer(
                [
                    MinMaxTransformer(
                        lower=data_to_syn[col].min(),
                        upper=data_to_syn[col].max(),
                        negative=False,
                    )
                    for col in data_to_syn.columns
                ]
            )
            self._synthesizer.fit(data_to_syn, transformer=tt)

    def _sample(self) -> pd.DataFrame:
        """
        Sample from the fitted synthesizer.

        Attr:
            sample_num_rows (int): The number of rows to be sampled.
            constant_data (dict): The dict of constant columns.

        Return:
            data_syn (pd.DataFrame): The synthesized data.
        """
        data_syn: pd.DataFrame = self._synthesizer.sample(self.sample_num_rows)

        if self.constant_data:
            for col, (val, idx) in self.constant_data.items():
                data_syn.insert(idx, col, val)

        return data_syn


class SmartNoiseFactory:
    """
    Base class for all "SmartNoise".

    Manage the SmartNoise synthesizers.
    It allocates the task to the right SmartNoise synthesizer
    based on the parameters.
    """

    def __init__(self, data: pd.DataFrame, **kwargs) -> None:
        """
        Args:
            data (pd.DataFrame): The data to be synthesized.
            **kwargs: The other parameters.
        """
        method: str = kwargs.get("method", None)
        epsilon: float = kwargs.get("epsilon", 5.0)
        batch_size: int = kwargs.get("batch_size", 500)  # for all gan
        epochs: int = kwargs.get("epochs", 300)  # for all gan
        sigma: float = kwargs.get("sigma", 5.0)  # for dpctgan
        disabled_dp: bool = kwargs.get("disabled_dp", False)  # for dpctgan
        metadata = kwargs.get("metadata", None)

        if method.startswith("smartnoise-"):
            self.synthesizer = SmartNoiseCreator(
                data,
                metadata=metadata,
                method=method.split("-")[1],
                epsilon=epsilon,
                batch_size=batch_size,
                epochs=epochs,
                sigma=sigma,
                disabled_dp=disabled_dp,
            )
        else:
            raise UnsupportedMethodError

    def create(self):
        """
        Create synthesizer instance.
        Return:
            self.synthesizer (synthesizer): The synthesizer instance.
        """
        return self.synthesizer


class SmartNoiseCreator(SmartNoise):
    """
    Implement synthesize methods from SmartNoise library.
    """

    def __init__(
        self,
        data: pd.DataFrame,
        method: str,
        epsilon: float,
        batch_size: int,
        epochs: int,
        sigma: float,
        disabled_dp: bool,
        metadata: Metadata = None,
        **kwargs,
    ):
        """
        Args:
            data (pd.DataFrame): The data to be synthesized.
            method (str): The synthesizing method to be applied.
            epsilon (float, default = 5.0): The privacy budget.
            metadata (Metadata, default=None): The metadata of the data.
            **kwargs: The other parameters.
        """
        super().__init__(data, metadata, **kwargs)
        self.syn_method: str = method

        if method == "dpctgan":
            self._synthesizer = SNSyn.create(
                method,
                epsilon=epsilon,
                batch_size=batch_size,
                epochs=epochs,
                sigma=sigma,
                disabled_dp=disabled_dp,
            )
        elif method == "patectgan":
            self._synthesizer = SNSyn.create(
                method, epsilon=epsilon, batch_size=batch_size, epochs=epochs
            )
        else:
            self._synthesizer = SNSyn.create(method, epsilon=epsilon)
