import time

import pandas as pd
from snsynth.transform import NoTransformer, TableTransformer
from snsynth.transform.identity import IdentityTransformer
from snsynth import Synthesizer as SNSyn

from PETsARD.error import UnsupportSynthesizingMethodError


class SmartNoise:
    """
    Base class for all "SmartNoise".

    The "SmartNoise" class defines the common API
    that all the "SmartNoise" need to implement, 
    as well as common functionality.
    """

    def __init__(self, data: pd.DataFrame, **kwargs) -> None:
        """
        Args:
            data (pd.DataFrame): The data to be synthesized.
            **kwargs: The other parameters.
        """
        self.data: pd.DataFrame = data
        self.syn_method: str = 'Unknown'

    def fit(self) -> None:
        """
        Fit the synthesizer.
        """
        if self._Synthesizer:
            time_start = time.time()

            print(
                f"Synthesizer (SmartNoise): Fitting {self.syn_method}."
            )

            # TODO - for mst and pacsynth,
            # we need to implement other transformer rather than IdentityTransformer
            t = TableTransformer([IdentityTransformer() 
                                  for i in range(self.data.shape[1])])

            # TODO - Only support cube-style synthesizer. 
            # GAN-style synthesizer needed to be implemented.
            self._Synthesizer.fit(self.data, transformer=t)
            print(
                f"Synthesizer (SmartNoise): "
                f"Fitting  {self.syn_method} spent "
                f"{round(time.time()-time_start ,4)} sec."
            )
        else:
            raise ValueError(
                f"Synthesizer (SmartNoise): "
                f".fit() while _Synthesizer didn't ready."
            )

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
        if self._Synthesizer:
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

                data_syn = self._Synthesizer.sample(
                    self.sample_num_rows
                )

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
            
            # TODO - Make Exception more precise
            except Exception as ex:
                raise NotImplementedError(
                    f"Synthesizer (SmartNoise): "
                    f".sample() while _Synthesizer didn't fitted, "
                    f"run .fit() before sampling."
                )
        else:
            raise NotImplementedError(
                f"Synthesizer (SmartNoise): "
                f".sample() while _Synthesizer didn't ready."
            )

    def fit_sample(
            self,
            sample_num_rows:  int = None,
            reset_sampling:   bool = False,
            output_file_path: str = None
    ) -> pd.DataFrame:
        """
        Fit and sample from the synthesizer.
        The combination of the methods `fit()` and `sample()`.
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
        self.fit()
        return self.sample(sample_num_rows, reset_sampling, output_file_path)
    
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

        if method.startswith('smartnoise-'):
            self.Synthesizer = SmartNoiseCreator(
                data,
                method=method.split('-')[1], 
                epsilon=epsilon
            )
        else:
            raise UnsupportSynthesizingMethodError

    def create_synthesizer(self):
        """
        Create synthesizer instance.
        Return:
            self.Synthesizer (synthesizer): The synthesizer instance.
        """
        return self.Synthesizer


class SmartNoiseCreator(SmartNoise):
    """
    Implement synthesize methods from SmartNoise library.
    """

    def __init__(self, data: pd.DataFrame, 
                 method: str, epsilon: float = 5.0, **kwargs):
        """
        Args:
            data (pd.DataFrame): The data to be synthesized.
            method (str): The synthesizing method to be applied.
            epsilon (float, default = 5.0): The privacy budget.
            **kwargs: The other parameters.
        """
        super().__init__(data, **kwargs)
        self.syn_method: str = method

        self._Synthesizer = SNSyn.\
                create(method, epsilon=epsilon)