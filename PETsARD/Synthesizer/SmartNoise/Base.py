import time

import pandas as pd
from sdv.metadata import SingleTableMetadata

from PETsARD.Synthesizer.SmartNoise import SmartNoise


class SDV_SingleTable(SmartNoise):
    """
    Base class for all SDV SingleTable classes.

    Args:
        data (pd.DataFrame): The data to be synthesized.
        **kwargs: The other parameters.

    Return:
        None
    TODO - Put all SDV related class together
    TODO - Nice to have - Simplify the code (Factory part)
    """

    def __init__(self, data: pd.DataFrame, **kwargs) -> None:
        super().__init__(data, **kwargs)

        self._SingleTableMetadata()

    def _SingleTableMetadata(self) -> None:
        """
        Create metadata for SDV.
        Args:
            None
        Return:
            None
        """
        time_start = time.time()

        self.metadata = SingleTableMetadata()
        self.metadata.detect_from_dataframe(self.data)
        print(
            f"Synthesizer (SDV - SingleTable): "
            f"Metafile loading time: "
            f"{round(time.time()-time_start ,4)} sec."
        )

    def fit(self) -> None:
        """
        Fit the synthesizer.
        Args:
            None
        Return:
            None
        """
        if self._Synthesizer:
            time_start = time.time()

            print(
                f"Synthesizer (SDV - SingleTable): Fitting {self.syn_method}."
            )
            self._Synthesizer.fit(self.data)
            print(
                f"Synthesizer (SDV - SingleTable): "
                f"Fitting  {self.syn_method} spent "
                f"{round(time.time()-time_start ,4)} sec."
            )
        else:
            raise ValueError(
                f"Synthesizer (SDV - SingleTable): "
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
                Whether the method should reset the randomisation.
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

                # batch_size: if sample_num_rows more than 1M,
                #             batch 100K at once,
                #             otherwise same as sample_num_rows
                self.sample_batch_size = (
                    100000 if self.sample_num_rows >= 1000000
                    else self.sample_num_rows
                )

                if reset_sampling:
                    self._Synthesizer.reset_sampling()

                data_syn = self._Synthesizer.sample(
                    num_rows=self.sample_num_rows,
                    batch_size=self.sample_batch_size,
                    output_file_path=output_file_path
                )

                str_sample_num_rows_as_raw = (
                    ' (same as raw)' if self.sample_num_rows_as_raw
                    else ''
                )
                print(
                    f"Synthesizer (SDV - SingleTable): "
                    f"Sampling {self.syn_method} "
                    f"# {self.sample_num_rows} rows"
                    f"{str_sample_num_rows_as_raw} "
                    f"in {round(time.time()-time_start ,4)} sec."
                )
                return data_syn
            except Exception as ex:
                raise NotImplementedError(
                    f"Synthesizer (SDV - SingleTable): "
                    f".sample() while _Synthesizer didn't fitted, "
                    f"run .fit() before sampling."
                )
        else:
            raise NotImplementedError(
                f"Synthesizer (SDV - SingleTable): "
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
                Whether the method should reset the randomisation.
            output_file_path (str, default=None):
                The location of the output file.
        Return:
            data_syn (pd.DataFrame): The synthesized data.
        """
        self.fit()
        return self.sample(sample_num_rows, reset_sampling, output_file_path)
