import os
from abc import ABC, abstractmethod

import requests

from petsard.loader.util import DigestSha256


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

        TODO ValueError
        """
        file_sha256hash = DigestSha256(self.config["filepath"])

        if file_sha256hash == self.config["benchmark_sha256"]:
            self.config["benchmark_already_exist"] = True

        if not self.config["benchmark_already_exist"]:
            if already_exist:
                raise ValueError(
                    f"Loader - Benchmarker: file {self.config['filepath']} "
                    f"already exist but their SHA-256 is NOT match. "
                    f"Please confirm your dataset version is correct."
                )
            else:
                try:
                    os.remove(self.config["filepath"])
                    raise ValueError(
                        f"Loader - Benchmarker: The SHA-256 of file "
                        f"{self.config['benchmark_filename']} "
                        f"download from link/S3 bucket "
                        f"{self.config['benchmark_bucket_name']} "
                        f"didn't match library record. "
                        f"Download data been remove, "
                        f"please download benchmark dataset manually."
                    )
                except OSError:
                    raise OSError(
                        f"Loader - Benchmarker: Failed to remove the downloaded file "
                        f"{self.config['filepath']}. Please delete it manually."
                    )


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
            print(
                f"Loader - Benchmarker: file {self.config['filepath']}"
                f" already exist and match SHA-256.\n"
                f"                      "
                f"petsard will ignore download and use local data directly."
            )
        else:
            url = (
                f"https://"
                f"{self.config['benchmark_bucket_name']}"
                f".s3.amazonaws.com/"
                f"{self.config['benchmark_filename']}"
            )
            with requests.get(url, stream=True) as response:
                if response.status_code == 200:
                    with open(self.config["filepath"], "wb") as f:
                        # load 8KB at one time
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(
                        f"Loader - Benchmarker : "
                        f"Success download the benchmark dataset from {url}."
                    )
                else:
                    print(
                        f"Loader - Benchmarker : "
                        f"{response.status_code} error. "
                        f"Failed to download the benchmark dataset from {url}."
                    )
            self._verify_file(already_exist=False)
