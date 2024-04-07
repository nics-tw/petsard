import re
import time

import pandas as pd
from sdv.metadata import SingleTableMetadata
from sdv.single_table import (
    CopulaGANSynthesizer,
    CTGANSynthesizer,
    GaussianCopulaSynthesizer,
    TVAESynthesizer
)

from PETsARD.error import UnfittedError, UnsupportedMethodError


class SDVMap():
    """
    Mapping of SDV.
    """
    COPULAGAN:      int = 1
    CTGAN:          int = 2
    GAUSSIANCOPULA: int = 3
    TVAE:           int = 4

    @classmethod
    def map(cls, method: str) -> int:
        """
        Get suffixes mapping int value

        Args:
            method (str): evaluating method

        Return:
            (int): The method code.
        """
        try:
            # accept both of "sdv-" or "sdv-single_table-" prefix
            return cls.__dict__[
                re.sub(
                    r"^(sdv-single_table-|sdv-)",
                    "",
                    method
                ).upper()
            ]
        except KeyError:
            raise UnsupportedMethodError


class SDVFactory:
    """
    Factory method of the SDV synthesizers.

    Args:
        data (pd.DataFrame): The data to be synthesized from.
        metadata (dict, default=None): The metadata of the data.
        **kwargs: The other parameters.
            method (str): The synthesizer method. Default is None.
    """

    def __init__(self, data: pd.DataFrame, **kwargs) -> None:
        method: str = kwargs.get('method', None)
        method_code = SDVMap.map(method)  # self.config['method']
        metadata = kwargs.get('metadata', None)

        if method_code == SDVMap.COPULAGAN:
            self.synthesizer = SDVSingleTableCopulaGAN(
                data=data, metadata=metadata)
        elif method_code == SDVMap.CTGAN:
            self.synthesizer = SDVSingleTableCTGAN(
                data=data, metadata=metadata)
        elif method_code == SDVMap.GAUSSIANCOPULA:
            self.synthesizer = SDVSingleTableGaussianCopula(
                data=data, metadata=metadata)
        elif method_code == SDVMap.TVAE:
            self.synthesizer = SDVSingleTableTVAE(
                data=data, metadata=metadata)
        else:
            raise UnsupportedMethodError

    def create(self):
        """
        Create synthesizer instance.

        Return:
            self.synthesizer (synthesizer): The synthesizer instance.
        """
        return self.synthesizer


class SDVSingleTable():
    """
    Base class for all SDV SingleTable classes.

    Args:
        data (pd.DataFrame): The data to be synthesized.
        metadata (dict, default=None): The metadata of the data.
        **kwargs: The other parameters.
    """

    def __init__(self, data: pd.DataFrame, metadata=None, **kwargs) -> None:
        super().__init__(data, **kwargs)
        self.data: pd.DataFrame = data
        self.syn_method: str = 'Unknown'

        self._SingleTableMetadata(metadata)

    def _SingleTableMetadata(self, metadata) -> None:
        """
        Create metadata for SDV.
        Args:
            metadata (dict): The metadata of the data.
        Return:
            None
        """
        time_start = time.time()

        self.metadata = SingleTableMetadata()
        if metadata:
            # if a metadata is provided, load it
            self.metadata = self.metadata.load_from_dict(metadata)
        else:
            # otherwise, detect the metadata from the data
            self.metadata.detect_from_dataframe(self.data)
        print(
            f"Synthesizer (SDV - SingleTable): "
            f"Metafile loading time: "
            f"{round(time.time()-time_start ,4)} sec."
        )

    def fit(self) -> None:
        """
        Fit the synthesizer.
        """
        if self._synthesizer:
            time_start = time.time()

            print(
                f"Synthesizer (SDV - SingleTable): Fitting {self.syn_method}."
            )
            self._synthesizer.fit(self.data)
            print(
                f"Synthesizer (SDV - SingleTable): "
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
            sample_num_rows (int, default=None): Number of synthesized data will be sampled.
            reset_sampling (bool, default=False): Whether the method should reset the randomisation.
            output_file_path (str, default=None): The location of the output file.

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

                # batch_size: if sample_num_rows more than 1M,
                #             batch 100K at once,
                #             otherwise same as sample_num_rows
                self.sample_batch_size = (
                    100000 if self.sample_num_rows >= 1000000
                    else self.sample_num_rows
                )

                if reset_sampling:
                    self._synthesizer.reset_sampling()

                data_syn = self._synthesizer.sample(
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
                raise UnfittedError
        else:
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


class SDVSingleTableCopulaGAN(SDVSingleTable):
    """
    Implement CopulaGAN synthesize method.

    Args:
        data (pd.DataFrame): The data to be synthesized.
        **kwargs: The other parameters.
    """

    def __init__(self, data: pd.DataFrame, metadata=None, **kwargs) -> None:
        super().__init__(data, metadata, **kwargs)
        self.syn_method: str = 'CopulaGAN'

        # metadata already create in SDV_SingleTable
        self._synthesizer = CopulaGANSynthesizer(self.metadata)


class SDVSingleTableCTGAN(SDVSingleTable):
    """
    Implement CTGAN synthesize method.

    Args:
        data (pd.DataFrame): The data to be synthesized.
        **kwargs: The other parameters.
    """

    def __init__(self, data: pd.DataFrame, metadata=None, **kwargs):
        super().__init__(data, metadata, **kwargs)

        self.syn_method: str = 'CTGAN'

        self._synthesizer = CTGANSynthesizer(self.metadata)


class SDVSingleTableGaussianCopula(SDVSingleTable):
    """
    Implement Gaussian Copula synthesize method.

    Args:
        data (pd.DataFrame): The data to be synthesized.
        **kwargs: The other parameters.
    """

    def __init__(self, data: pd.DataFrame, metadata=None, **kwargs):
        super().__init__(data, metadata, **kwargs)
        self.syn_method: str = 'GaussianCopula'

        self._synthesizer = GaussianCopulaSynthesizer(self.metadata)


class SDVSingleTableTVAE(SDVSingleTable):
    """
    Implement TVAE synthesize method.

    Args:
        data (pd.DataFrame): The data to be synthesized.
        **kwargs: The other parameters.
    """

    def __init__(self, data: pd.DataFrame, metadata=None, **kwargs):
        super().__init__(data, metadata, **kwargs)
        self.syn_method: str = 'TVAE'

        self._synthesizer = TVAESynthesizer(self.metadata)
