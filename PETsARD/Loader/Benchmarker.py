from abc import ABC, abstractmethod
import hashlib
import os

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import requests


class BenchmarkerBase(ABC):
    """
    BenchmarkerBase
        Base class for all "Benchmarker".

        The "Benchmarker" class defines the common API
        that all the "Loader" need to implement, as well as common functionality.

    """

    def __init__(self, para_Loader: dict):
        self.para_Loader = para_Loader
        self.para_Loader['benchmark_already_exist'] = False
        if os.path.exists(self.para_Loader['filepath']):
            # if same name data already exist, check the sha256hash,
            #     if match, ignore download and continue,
            #     if NOT match, raise Error
            # TODO ValueError
            exist_sha256hash = \
                self._calculate_sha256(self.para_Loader['filepath'])
            if exist_sha256hash == self.para_Loader['benchmark_sha256']:
                self.para_Loader['benchmark_already_exist'] = True
            else:
                raise ValueError(
                    f"Loader - Benchmarker: file {self.para_Loader['filepath']}"
                    f" already exist but their SHA-256 is NOT match.\n"
                    f"                      "
                    f"Please confirm your dataset version is correct."
                )
        else:
            # if same name data didn't exist,
            #     confirm "./benchmark/" folder is exist (create it if not)
            if not os.path.exists("benchmark"):
                os.makedirs("benchmark")

    @abstractmethod
    def download(self):
        """
        Download the data
        """
        raise NotImplementedError()

    @staticmethod
    def _calculate_sha256(filepath):
        """
        Calculate SHA-256 value of file.
        ...
        Args:
            filepath (str)
                Openable file full path.
        ...
        return:
            (str)
                SHA-256 value of file.
        """
        sha256hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256hash.update(byte_block)
        return sha256hash.hexdigest()

    def _verify_download(self, link: str = ''):
        """
        Verifing the download file SHA-256 value is matched as expected.
        ...
        Arg:
            link (str)
                The download link for error message.
        """
        download_sha256hash = \
            self._calculate_sha256(self.para_Loader['filepath'])
        if not download_sha256hash == self.para_Loader['benchmark_sha256']:
            try:
                os.remove(self.para_Loader['filepath'])
            except OSError as ex:
                raise OSError(
                    f"Loader - Benchmarker: Failed to remove "
                    f"the downloaded file {self.para_Loader['filepath']}. "
                    f"Please delete it manually."
                )
            raise ValueError(
                f"Loader - Benchmarker: The SHA-256 of file "
                f"{self.para_Loader['benchmark_filename']} "
                f"download from link/S3 bucket {link} "
                f"didn't match library record.\n"
                f"                      "
                f"Download data been remove, "
                f"please download benchmark dataset manually."
            )


class BenchmarkerRequests(BenchmarkerBase):
    """
    BenchmarkerRequests
        Download benchmark dataset via requests.
        Expect for public bucket.

    """

    def __init__(self, para_Loader: dict):
        super().__init__(para_Loader)

    def download(self) -> None:
        """
        Use requests.get() to download data,
            than confirm its SHA-256 is matched.

        """
        if self.para_Loader['benchmark_already_exist']:
            print(
                f"Loader - Benchmarker: file {self.para_Loader['filepath']}"
                f" already exist and match SHA-256.\n"
                f"                      "
                f"PETsARD will ignore download and use local data directly."
            )
        else:
            url = (
                f"https://"
                f"{self.para_Loader['benchmark_bucket_name']}"
                f".s3.amazonaws.com/"
                f"{self.para_Loader['benchmark_filename']}"
            )
            with requests.get(url, stream=True) as response:
                if response.status_code == 200:
                    with open(self.para_Loader['filepath'], 'wb') as f:
                        # load 8KB at one time
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(
                        f"Loader - Benchmarker : "
                        f"Success download the benchmark dataset in {url}."
                    )
                else:
                    print(
                        f"Loader - Benchmarker : "
                        f"{response.status_code} error. "
                        f"Failed to download the benchmark dataset in {url}."
                    )
            self._verify_download(link=url)


class BenchmarkerBoto3(BenchmarkerBase):
    """
    BenchmarkerBoto3
        Download benchmark dataset via boto3.
        Expect for private bucket.
    ...
    Users should apply permission from development team,
        and setting AWS configure by your own.

    """

    def __init__(self, para_Loader: dict):
        super().__init__(para_Loader)

    def download(self) -> None:
        """
        Use boto3.resource() to download data,
            than confirm its SHA-256 is matched.

        """
        if self.para_Loader['benchmark_already_exist']:
            print(
                f"Loader - Benchmarker: file {self.para_Loader['filepath']} "
                f"already exist and match SHA-256.\n"
                f"                      "
                f"PETsARD will ignore download and use local data directly."
            )
        else:
            try:
                bucket_name = self.para_Loader['benchmark_bucket_name']
                bucket_key = self.para_Loader['benchmark_filename']
                s3_resource = boto3.resource('s3')
                s3_object = s3_resource.Object(
                    bucket_name=bucket_name,
                    key=bucket_key
                )
                s3_object.download_file(
                    Filename=self.para_Loader['filepath']
                )
                self._verify_download(link=bucket_name + bucket_key)
            except NoCredentialsError:
                print(
                    f"Loader - Benchmarker: "
                    f"Credentials not available for AWS S3 "
                    f"in {self.para_Loader['benchmark_bucket_name']}."
                )
            except ClientError as ex:
                if ex.response['Error']['Code'] == '403':
                    print(
                        f"Loader - Benchmarker: "
                        f"Bucket {self.para_Loader['benchmark_bucket_name']} "
                        f"Access denied to the S3 bucket."
                    )
                elif ex.response['Error']['Code'] == '404':
                    print(
                        f"Loader - Benchmarker: "
                        f"The file {self.para_Loader['benchmark_filename']} "
                        f"does not exist in the S3 bucket."
                    )
                else:
                    print(
                        f"Loader - Benchmarker: "
                        f"An ClientError occurred: {ex}"
                    )
            except Exception as ex:
                print(
                    f"Loader - Benchmarker: "
                    f"An unexpected error occurred: {ex}"
                )
