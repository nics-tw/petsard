import re
import time

from scipy.stats._warnings_errors import FitError
from sdv.metadata import SingleTableMetadata
from sdv.single_table import (
    CopulaGANSynthesizer,
    CTGANSynthesizer,
    GaussianCopulaSynthesizer,
    TVAESynthesizer
)
import pandas as pd

from PETsARD.synthesizer.syntheszier_base import SyntheszierBase
from PETsARD.error import UnsupportedMethodError, UnableToSynthesizeError


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


class SDVSingleTable(SyntheszierBase):
    """
    Base class for all SDV SingleTable classes.
    """

    def __init__(self, data: pd.DataFrame, metadata=None, **kwargs) -> None:
        """
        Args:
            data (pd.DataFrame): The data to be synthesized.
            metadata (dict, default=None): The metadata of the data.
            **kwargs: The other parameters.

        Attr.:
            syn_module (str): The name of the synthesizer module.
            metadata (SingleTableMetadata): The metadata of the data.
        """
        super().__init__(data, **kwargs)
        self.syn_module: str = 'SDV'
        self.metadata: SingleTableMetadata = SingleTableMetadata()

        self._SingleTableMetadata(metadata)

    def _SingleTableMetadata(self, metadata) -> None:
        """
        Create metadata for SDV.
            If metadata is provided, load it.
            Otherwise, detect the metadata from the data.

        Args:
            metadata (dict): The metadata of the data.
        """
        if metadata:
            self.metadata = self.metadata.load_from_dict(metadata)
        else:
            self.metadata.detect_from_dataframe(self.data)

    def _fit(self) -> None:
        """
        Fit the synthesizer.
        """
        try:
            self._synthesizer.fit(self.data)
        except FitError as ex: # See Issue 454
            raise UnableToSynthesizeError(
                f"Synthesizer ({self.syn_module} - {self.syn_method}): "
                f"This datasets couldn't fit in this method. "
                f"If you were in Executor process, "
                f"please remove this experiment and try again. \n"
                f"Following is original error msg: \n"
                f"FitError: {ex}"
            )

    def _sample(self) -> pd.DataFrame:
        """
        Sample from the fitted synthesizer.
            If sample_num_rows more than 100K, batch 100K at once,
                otherwise same as sample_num_rows

        Attr:
            sample_num_rows (int): The number of rows to be sampled.
            reset_sampling (bool):
                Whether the method should reset the randomisation.

        Return:
            data_syn (pd.DataFrame): The synthesized data.
        """

        # batch_size: if sample_num_rows more than 1M,
        #             batch 100K at once,
        #             otherwise same as sample_num_rows
        sample_batch_size: int = (
            100000 if self.sample_num_rows >= 100000
            else self.sample_num_rows
        )

        if self.reset_sampling:
            self._synthesizer.reset_sampling()

        data_syn: pd.DataFrame = self._synthesizer.sample(
            num_rows=self.sample_num_rows,
            batch_size=sample_batch_size,
            output_file_path=None
        )

        return data_syn


class SDVSingleTableCopulaGAN(SDVSingleTable):
    """
    Implement CopulaGAN synthesize method.

    Args:
        data (pd.DataFrame): The data to be synthesized.
        metadata (dict, default=None): The metadata of the data.
        **kwargs: The other parameters.
    """

    def __init__(self, data: pd.DataFrame, metadata=None, **kwargs) -> None:
        super().__init__(data, metadata, **kwargs)
        self.syn_method: str = 'CopulaGAN'

        self._synthesizer = CopulaGANSynthesizer(self.metadata)


class SDVSingleTableCTGAN(SDVSingleTable):
    """
    Implement CTGAN synthesize method.

    Args:
        data (pd.DataFrame): The data to be synthesized.
        metadata (dict, default=None): The metadata of the data.
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
        metadata (dict, default=None): The metadata of the data.
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
        metadata (dict, default=None): The metadata of the data.
        **kwargs: The other parameters.
    """

    def __init__(self, data: pd.DataFrame, metadata=None, **kwargs):
        super().__init__(data, metadata, **kwargs)
        self.syn_method: str = 'TVAE'

        self._synthesizer = TVAESynthesizer(self.metadata)
