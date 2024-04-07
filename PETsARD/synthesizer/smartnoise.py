import time

import pandas as pd
from snsynth.transform import TableTransformer, MinMaxTransformer
from snsynth import Synthesizer as SNSyn

from PETsARD.synthesizer.syntheszier_base import SyntheszierBase
from PETsARD.error import UnfittedError, UnsupportedMethodError


class SmartNoise(SyntheszierBase):
    """
    Base class for all "SmartNoise".

    The "SmartNoise" class defines the common API
    that all the "SmartNoise" need to implement,
    as well as common functionality.
    """

    CUBE = ['aim', 'mwem', 'mst', 'pacsynth']
    GAN = ['dpctgan', 'patectgan']

    def __init__(self, data: pd.DataFrame, **kwargs) -> None:
        """
        Args:
            data (pd.DataFrame): The data to be synthesized.
            **kwargs: The other parameters.

        Attr.:
            syn_module (str): The name of the synthesizer module.
        """
        super().__init__(data, **kwargs)
        self.syn_module: str = 'SmartNoise'

    def fit(self) -> None:
        """
        Fit the synthesizer.
        """
        if self._synthesizer:
            time_start = time.time()

            print(
                f"Synthesizer (SmartNoise): Fitting {self.syn_method}."
            )

            if self.syn_method in self.CUBE:
                self._synthesizer.fit(
                    self.data,
                    categorical_columns=self.data.columns
                )
            else:
                data_to_syn: pd.DataFrame = self.data.copy()

                for idx, col in enumerate(self.data.columns):
                    if self.data[col].nunique() == 1:
                        # If the column has only one unique value,
                        # it is a constant column.
                        self.constant_data[col] = (self.data[col].unique()[0],
                                                   idx)
                        data_to_syn.drop(col, axis=1, inplace=True)

                tt = TableTransformer([
                    MinMaxTransformer(lower=data_to_syn[col].min(),
                                      upper=data_to_syn[col].max(),
                                      negative=False)
                    for col in data_to_syn.columns
                ])

                self._synthesizer.fit(data_to_syn, transformer=tt)
            print(
                f"Synthesizer (SmartNoise): "
                f"Fitting  {self.syn_method} spent "
                f"{round(time.time()-time_start ,4)} sec."
            )
        else:
            raise UnfittedError

    def sample(self,
               sample_num_rows:  int = None,
               reset_sampling:   bool = False,
               output_file_path: str = None
               ) -> pd.DataFrame:
        """
        Sample from the fitted synthesizer.
        Args:
            sample_num_rows (int, default=None):
                Number of synthesized data will be sampled.
            reset_sampling (bool, default=False):
                Redundant variable.
            output_file_path (str, default=None):
                The location of the output file.
        Return:
            data_syn (pd.DataFrame): The synthesized data.
        """
        if self._synthesizer:
            try:
                time_start = time.time()

                # sample_num_rows: if didn't set sample_num_rows,
                #                  default is same as train data rows.
                self.sample_num_rows_as_raw = (
                    True if sample_num_rows is None
                    else False
                )
                self.sample_num_rows = (
                    self.data.shape[0] if self.sample_num_rows_as_raw
                    else sample_num_rows
                )

                data_syn = self._synthesizer.sample(
                    self.sample_num_rows
                )

                if self.constant_data:
                    for col, (val, idx) in self.constant_data.items():
                        data_syn.insert(idx, col, val)

                data_syn.to_csv(output_file_path, index=False)

                str_sample_num_rows_as_raw = (
                    ' (same as raw)' if self.sample_num_rows_as_raw
                    else ''
                )
                print(
                    f"Synthesizer (SmartNoise): "
                    f"Sampling {self.syn_method} "
                    f"# {self.sample_num_rows} rows"
                    f"{str_sample_num_rows_as_raw} "
                    f"in {round(time.time()-time_start ,4)} sec."
                )
                return data_syn
            except Exception as ex:
                raise UnfittedError
        else:
            raise UnfittedError


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
        method: str = kwargs.get('method', None)
        epsilon: float = kwargs.get('epsilon', 5.0)
        batch_size: int = kwargs.get('batch_size', 500)  # for all gan
        epochs: int = kwargs.get('epochs', 300)  # for all gan
        sigma: float = kwargs.get('sigma', 5.0)  # for dpctgan
        disabled_dp: bool = kwargs.get('disabled_dp', False)  # for dpctgan

        if method.startswith('smartnoise-'):
            self.synthesizer = SmartNoiseCreator(
                data,
                method=method.split('-')[1],
                epsilon=epsilon,
                batch_size=batch_size,
                epochs=epochs,
                sigma=sigma,
                disabled_dp=disabled_dp
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

    def __init__(self, data: pd.DataFrame,
                 method: str, epsilon: float, batch_size: int,
                 epochs: int, sigma: float, disabled_dp: bool, **kwargs):
        """
        Args:
            data (pd.DataFrame): The data to be synthesized.
            method (str): The synthesizing method to be applied.
            epsilon (float, default = 5.0): The privacy budget.
            **kwargs: The other parameters.
        """
        super().__init__(data, **kwargs)
        self.syn_method: str = method


        if method == 'dpctgan':
            self._synthesizer = SNSyn.create(method, epsilon=epsilon,
                                             batch_size=batch_size,
                                             epochs=epochs,
                                             sigma=sigma,
                                             disabled_dp=disabled_dp)
        elif method == 'patectgan':
            self._synthesizer = SNSyn.create(method, epsilon=epsilon,
                                             batch_size=batch_size,
                                             epochs=epochs)
        else:
            self._synthesizer = SNSyn.create(method, epsilon=epsilon)