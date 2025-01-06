from abc import ABC, abstractmethod
import time
import warnings

import pandas as pd

from petsard import Metadata
from petsard.error import UnfittedError


class SynthesizerBase(ABC):

    def __init__(
        self,
        data: pd.DataFrame,
        metadata: Metadata = None,
        **kwargs
    ) -> None:
        """
        Args:
            data (pd.DataFrame): The data to be synthesized.
            metadata (Metadata, default=None): The metadata class of the data.
            **kwargs: The other parameters.

        Attr.:
            data (pd.DataFrame): The data to be synthesized.
            syn_module (str): The name of the synthesizer module.
            syn_method (str): The name of the synthesizer method.
            constant_data (dict): The dict of constant columns.
            sample_num_rows_as (str): The source of the sample number of rows.
            sample_num_rows (int): The number of rows to be sampled.
            reset_sampling (bool): Whether the method should reset the randomisation.
            output_file_path (str): The location of the output file.
            _synthesizer (SyntheszierBase): The synthesizer object.
        """
        self.data: pd.DataFrame = data
        self.syn_module: str = 'Unknown'
        self.syn_method: str = 'Unknown'
        self.constant_data: dict = {}
        self.sample_num_rows_as: str = None
        self.sample_num_rows: int = None
        self.reset_sampling: bool = None
        self.output_file_path: str = None

        if metadata is not None:
            if hasattr(metadata, 'metadata') and 'global' in metadata.metadata:
                # 1. if Splitter information exist, use rnum after split
                if 'row_num_after_split' in metadata.metadata['global'] and \
                        'train' in metadata.metadata['global']['row_num_after_split']:
                    self.sample_num_rows_as = 'Splitter data'
                    self.sample_num_rows = \
                        metadata.metadata['global']['row_num_after_split']['train']
                # 2. if Loader only, assume data didn't been split
                elif 'row_num' in metadata.metadata['global']:
                    self.sample_num_rows_as = 'Loader data'
                    self.sample_num_rows = metadata.metadata['global']['row_num']
            else:
                warnings.warn(
                    "There's no global information in the metadata." +
                    "No rows number information will be used."
                )
        if self.sample_num_rows is None:
            self.sample_num_rows_as = 'input data'
            self.sample_num_rows = self.data.shape[0]

        self._synthesizer: SynthesizerBase = None

    @abstractmethod
    def _fit(self) -> None:
        """
        Fit the synthesizer.
        """
        raise NotImplementedError

    def fit(self) -> None:
        time_start = time.time()

        print(
            f"Synthesizer ({self.syn_module}): "
            f"Fitting {self.syn_method}."
        )
        self._fit()
        print(
            f"Synthesizer ({self.syn_module}): "
            f"Fitting {self.syn_method} spent "
            f"{round(time.time()-time_start ,4)} sec."
        )

    @abstractmethod
    def _sample(self) -> pd.DataFrame:
        """
        Sample from the fitted synthesizer.

        Return:
            data_syn (pd.DataFrame): The synthesized data.
        """
        raise NotImplementedError

    def sample(
        self,
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

        Attr:
            sample_num_rows_as (str): The source of the sample number of rows.
            sample_num_rows (int): The number of rows to be sampled.
            reset_sampling (bool):
                Whether the method should reset the randomisation.
            output_file_path (str): The location of the output file.

        Return:
            data_syn (pd.DataFrame): The synthesized data.
        """
        if sample_num_rows is not None:
            self.sample_num_rows_as = 'manual input'
            self.sample_num_rows = sample_num_rows
        self.reset_sampling = reset_sampling
        self.output_file_path = output_file_path

        data_syn: pd.DataFrame = None

        if self._synthesizer is None:
            raise UnfittedError

        try:
            time_start = time.time()

            data_syn = self._sample()

            if output_file_path is not None:
                data_syn.to_csv(output_file_path, index=False)

            str_sample_num_rows_as = (
                f' (same as {self.sample_num_rows_as})'
                if self.sample_num_rows_as
                else ''
            )
            print(
                f"Synthesizer ({self.syn_module}): "
                f"Sampling {self.syn_method} "
                f"# {self.sample_num_rows} rows"
                f"{str_sample_num_rows_as} "
                f"in {round(time.time()-time_start ,4)} sec."
            )
            return data_syn
        except Exception:
            raise UnfittedError

    def fit_sample(
        self,
        sample_num_rows:  int = None,
        reset_sampling:   bool = False,
        output_file_path: str = None
    ) -> pd.DataFrame:
        """
        Fit and sample from the synthesizer
            The combination of the methods `fit()` and `sample()`.

        Args:
            sample_num_rows (int, default=None): Number of synthesized data will be sampled.
            reset_sampling (bool, default=False): Whether the method should reset the randomisation.
            output_file_path (str, default=None): The location of the output file.

        Return:
            data_syn (pd.DataFrame): The synthesized data.
        """
        self.fit()
        return self.sample(sample_num_rows, reset_sampling, output_file_path)
