import hashlib
import logging
import os
from abc import ABC, abstractmethod

import requests

from petsard.exceptions import BenchmarkDatasetsError


def digest_sha256(filepath):
    """
    Calculate SHA-256 value of file. Load 128KB at one time.
    ...
    Args:
        filepath (str) Openable file full path.
    ...
    return:
        (str) SHA-256 value of file.
    """
    sha256hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(131072), b""):
            sha256hash.update(byte_block)
    return sha256hash.hexdigest()


class BaseBenchmarker(ABC):
    """
    BaseBenchmarker
        Base class for all "Benchmarker".
        The "Benchmarker" class defines the common API
        that all the "Loader" need to implement, as well as common functionality.
    """

    def __init__(self, config: dict):
        """
        Attributes:
            _logger (logging.Logger): The logger object.
            config (dict) The configuration of the benchmarker.
                benchmark_bucket_name (str) The name of the S3 bucket.
                benchmark_filename (str)
                    The name of the benchmark data from benchmark_datasets.yaml.
                benchmark_sha256 (str)
                    The SHA-256 value of the benchmark data from benchmark_datasets.yaml.
                filepath (str) The full path of the benchmark data in local.
                benchmark_already_exist (bool)
                    If the benchmark data already exist. Default is False.
        """
        self._logger: logging.Logger = logging.getLogger(
            f"PETsARD.{self.__class__.__name__}"
        )
        self._logger.info(
            f"Initializing Benchmarker with benchmark_filename: {config['benchmark_filename']}"
        )

        self.config: dict = config
        self.config["benchmark_already_exist"] = False
        if os.path.exists(self.config["filepath"]):
            # if same name data already exist, check the sha256hash,
            #     if match, ignore download and continue,
            #     if NOT match, raise Error
            self._verify_file(already_exist=True)
        else:
            # if same name data didn't exist,
            #     confirm "./benchmark/" folder is exist (create it if not)
            os.makedirs("benchmark", exist_ok=True)

    @abstractmethod
    def download(self):
        """
        Download the data
        """
        raise NotImplementedError()

    def _verify_file(self, already_exist: bool = True):
        """
        Verify the exist file is match to records

        Args:
            already_exist (bool) If the file already exist. Default is True.
              False means verify under download process.
        """
        file_sha256hash = digest_sha256(self.config["filepath"])

        if file_sha256hash == self.config["benchmark_sha256"]:
            self.config["benchmark_already_exist"] = True
        else:
            if already_exist:
                self._logger.error(f"SHA-256 mismatch: {self.config['filepath']}")
                raise BenchmarkDatasetsError(
                    f"SHA-256 mismatch: {self.config['filepath']}. "
                )
            else:
                try:
                    os.remove(self.config["filepath"])
                    self._logger.error(
                        f"Downloaded file SHA-256 mismatch: {self.config['benchmark_filename']} from "
                        f"{self.config['benchmark_bucket_name']}. "
                    )
                    raise BenchmarkDatasetsError(
                        f"Downloaded file SHA-256 mismatch: {self.config['benchmark_filename']} from "
                        f"{self.config['benchmark_bucket_name']}. "
                    )
                except OSError as e:
                    self._logger.error(
                        f"Failed to remove file: {self.config['filepath']}. Please delete it manually."
                    )
                    raise OSError(
                        f"Failed to remove file: {self.config['filepath']}. Please delete it manually."
                    ) from e


class BenchmarkerRequests(BaseBenchmarker):
    """
    BenchmarkerRequests
        Download benchmark dataset via requests.
        Expect for public bucket.

    """

    def __init__(self, config: dict):
        super().__init__(config)

    def download(self) -> None:
        """
        Use requests.get() to download data,
            than confirm its SHA-256 is matched.

        """
        if self.config["benchmark_already_exist"]:
            self._logger.info(f"Using local file: {self.config['filepath']}")
        else:
            url = (
                f"https://"
                f"{self.config['benchmark_bucket_name']}"
                f".s3.amazonaws.com/"
                f"{self.config['benchmark_filename']}"
            )
            self._logger.info(f"Downloading from: {url}")
            with requests.get(url, stream=True) as response:
                if response.status_code == 200:
                    with open(self.config["filepath"], "wb") as f:
                        # load 8KB at one time
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    self._logger.info(
                        f"Download completed: {self.config['benchmark_filename']}"
                    )
                else:
                    self._logger.error(
                        f"Download failed: status={response.status_code}, url={url}"
                    )
                    raise BenchmarkDatasetsError(
                        f"Download failed: status={response.status_code}, url={url}"
                    )
            self._verify_file(already_exist=False)
