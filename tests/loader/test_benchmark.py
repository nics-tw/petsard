from unittest.mock import MagicMock, mock_open, patch

import pytest

from petsard.loader.benchmark import BaseBenchmarker, BenchmarkerRequests
from petsard.loader.util import DigestSha256


class TestBenchmarker:
    """Test cases for benchmarker functionality"""

    @pytest.fixture
    def sample_config(self):
        """Fixture providing sample configuration for tests"""
        return {
            "filepath": "benchmark/test.csv",
            "benchmark_bucket_name": "petsard-benchmark",
            "benchmark_filename": "test.csv",
            "benchmark_sha256": "fake_sha256",
        }

    def test_basebenchmarker_init(self, sample_config):
        """Test initialization of BaseBenchmarker"""
        with pytest.raises(TypeError):
            BaseBenchmarker()  # Should be abstract

    def test_benchmarker_requests_init(self, sample_config):
        """Test initialization of BenchmarkerRequests"""
        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = False
            with patch("os.makedirs", side_effect=None) as mock_makedirs:
                benchmarker = BenchmarkerRequests(sample_config)
                assert not benchmarker.config["benchmark_already_exist"]
                mock_makedirs.assert_called_once_with("benchmark", exist_ok=True)

    @patch("requests.get")
    def test_download_success(self, mock_get, sample_config):
        """Test successful download of benchmark data"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content.return_value = [b"test_content"]
        mock_get.return_value.__enter__.return_value = mock_response

        with patch("builtins.open", mock_open()) as _:  # mock_file
            with patch.object(BenchmarkerRequests, "_verify_file") as mock_verify:
                benchmarker = BenchmarkerRequests(sample_config)
                with patch("os.makedirs", side_effect=None):
                    benchmarker.download()
                    mock_verify.assert_called_once_with(already_exist=False)

    def test_verify_file_mismatch(self, sample_config):
        """Test verification of file with mismatched SHA256"""
        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = True
            with patch("builtins.open", mock_open(read_data=b"test data")):
                with patch.object(DigestSha256, "__new__") as mock_sha:
                    mock_sha.return_value = "wrong_sha256"
                    with pytest.raises(ValueError):
                        BenchmarkerRequests(sample_config)
