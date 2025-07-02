import hashlib
import os
import shutil
import tempfile
from unittest.mock import MagicMock, mock_open, patch

import pytest

from petsard.exceptions import BenchmarkDatasetsError
from petsard.loader.benchmarker import BaseBenchmarker, BenchmarkerRequests


# Helper function, not a test class to avoid pytest warnings
# 輔助函數，不是測試類，避免 pytest 警告
def create_test_benchmarker_impl(config):
    """Create a test implementation of BaseBenchmarker
    創建 BaseBenchmarker 的測試實現
    """

    class _TestBenchmarkerImpl(BaseBenchmarker):
        """Implementation of BaseBenchmarker for testing
        用於測試的 BaseBenchmarker 實現類
        """

        def download(self):
            """Implementation of abstract method
            抽象方法的實現
            """
            if self.config["benchmark_already_exist"]:
                self.logger.info(f"Using local file: {self.config['filepath']}")
            else:
                # Simulate download
                # 模擬下載
                with open(self.config["filepath"], "w") as f:
                    f.write("test content")
                self.logger.info(f"Download completed: {self.config['filepath']}")
                # Verify the downloaded file
                # 驗證下載的檔案
                self._verify_file(already_exist=False)

    return _TestBenchmarkerImpl(config)


class TestBenchmarker:
    """Test cases for benchmarker functionality
    測試 benchmarker 功能的測試案例
    """

    @pytest.fixture
    def sample_config(self):
        """Fixture providing sample configuration for tests
        為測試提供樣本配置的 fixture
        """
        return {
            "filepath": "benchmark/test.csv",
            "benchmark_bucket_name": "petsard-benchmark",
            "benchmark_filename": "test.csv",
            "benchmark_sha256": "fake_sha256",
        }

    @pytest.fixture
    def temp_dir(self):
        """Fixture providing a temporary directory for file operations
        為檔案操作提供臨時目錄的 fixture
        """
        temp_dir = tempfile.mkdtemp(prefix="benchmark_test_")
        benchmark_dir = os.path.join(temp_dir, "benchmark")
        os.makedirs(benchmark_dir, exist_ok=True)
        yield temp_dir, benchmark_dir
        # Cleanup after test
        # 測試後清理
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_basebenchmarker_init(self, sample_config):
        """Test initialization of BaseBenchmarker
        測試 BaseBenchmarker 的初始化
        """
        with pytest.raises(TypeError):
            BaseBenchmarker()  # Should be abstract / 應該是抽象類

    def test_benchmarker_requests_init(self, sample_config):
        """Test initialization of BenchmarkerRequests
        測試 BenchmarkerRequests 的初始化
        """
        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = False
            with patch("os.makedirs", side_effect=None) as mock_makedirs:
                benchmarker = BenchmarkerRequests(sample_config)
                assert not benchmarker.config["benchmark_already_exist"]
                mock_makedirs.assert_called_once_with("benchmark", exist_ok=True)

    @patch("requests.get")
    def test_download_success(self, mock_get, sample_config):
        """Test successful download of benchmark data
        測試成功下載基準數據
        """
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
        """Test verification of file with mismatched SHA256
        測試 SHA256 不匹配的檔案驗證
        """
        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = True
            with patch("builtins.open", mock_open(read_data=b"test data")):
                with patch("petsard.loader.benchmarker.digest_sha256") as mock_sha:
                    mock_sha.return_value = "wrong_sha256"
                    with pytest.raises(BenchmarkDatasetsError):
                        BenchmarkerRequests(sample_config)

    def test_download_request_fails(self, sample_config):
        """Test download when request fails
        測試請求失敗時的下載情況
        """
        mock_response = MagicMock()
        mock_response.status_code = 404

        with patch("requests.get") as mock_get:
            mock_get.return_value.__enter__.return_value = mock_response
            benchmarker = BenchmarkerRequests(sample_config)
            benchmarker.logger = MagicMock()

            with pytest.raises(BenchmarkDatasetsError) as exc_info:
                benchmarker.download()

            assert "Download failed" in str(exc_info.value)
            assert "404" in str(exc_info.value)

    def test_file_already_exists_hash_match(self, temp_dir, sample_config):
        """Test with existing file and matching hash
        測試已存在檔案且哈希值匹配的情況
        """
        temp_dir, benchmark_dir = temp_dir
        filepath = os.path.join(benchmark_dir, "test.csv")

        # Create test file
        # 創建測試檔案
        with open(filepath, "w") as f:
            f.write("test content")

        # Calculate actual hash
        # 計算實際哈希值
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            sha256_hash.update(f.read())
        file_hash = sha256_hash.hexdigest()

        # Update config with actual filepath and hash
        # 使用實際檔案路徑和哈希值更新配置
        config = sample_config.copy()
        config["filepath"] = filepath
        config["benchmark_sha256"] = file_hash

        # Create benchmarker with mocked logger
        # 創建帶有模擬 logger 的 benchmarker
        with patch("petsard.loader.benchmarker.digest_sha256") as mock_digest:
            mock_digest.return_value = file_hash
            benchmarker = create_test_benchmarker_impl(config)
            benchmarker.logger = MagicMock()

            # Override benchmark_already_exist to test download skip
            # 覆蓋 benchmark_already_exist 以測試跳過下載
            benchmarker.config["benchmark_already_exist"] = True
            benchmarker.download()

            # Check log message
            # 檢查日誌訊息
            benchmarker.logger.info.assert_called_with(f"Using local file: {filepath}")

    def test_verify_file_remove_fails(self, sample_config):
        """Test when removing file fails during verification
        測試驗證過程中刪除檔案失敗的情況
        """

        # Mock implementation of _verify_file to directly test the removal failure
        # 模擬 _verify_file 的實現，直接測試移除失敗的情況
        class MockBenchmarker(BenchmarkerRequests):
            def _verify_file(self, already_exist=True):
                if not already_exist:
                    try:
                        os.remove(self.config["filepath"])
                    except OSError:
                        self.logger.error(
                            f"Failed to remove file: {self.config['filepath']}"
                        )
                        raise OSError(
                            f"Failed to remove file: {self.config['filepath']}"
                        )

        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = False

            with patch("os.makedirs"):
                # Create the benchmarker
                # 創建 benchmarker
                benchmarker = MockBenchmarker(sample_config)
                benchmarker.logger = MagicMock()

                # Setup the remove to fail
                # 設置移除操作失敗
                with patch("os.remove") as mock_remove:
                    mock_remove.side_effect = OSError("Permission denied")

                    # Now test
                    # 現在測試
                    with pytest.raises(OSError) as exc_info:
                        benchmarker._verify_file(already_exist=False)

                    assert "Failed to remove file" in str(exc_info.value)

    def test_init_file_exists_hash_match(self, temp_dir, sample_config):
        """Test initialization when file exists and hash matches
        測試檔案存在且哈希值匹配時的初始化
        """
        temp_dir, benchmark_dir = temp_dir
        filepath = os.path.join(benchmark_dir, "test.csv")

        # Create test file
        # 創建測試檔案
        with open(filepath, "w") as f:
            f.write("test content")

        # Calculate actual hash
        # 計算實際哈希值
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            sha256_hash.update(f.read())
        file_hash = sha256_hash.hexdigest()

        # Update config with actual filepath and hash
        # 使用實際檔案路徑和哈希值更新配置
        config = sample_config.copy()
        config["filepath"] = filepath
        config["benchmark_sha256"] = file_hash

        # Create benchmarker with real file and hash
        # 使用真實檔案和哈希值創建 benchmarker
        with patch("petsard.loader.benchmarker.digest_sha256") as mock_digest:
            mock_digest.return_value = file_hash
            benchmarker = create_test_benchmarker_impl(config)
            assert benchmarker.config["benchmark_already_exist"]

    def test_file_content_change(self, temp_dir, sample_config):
        """Test hash verification after file content changes
        測試檔案內容變更後的哈希驗證
        """
        temp_dir, benchmark_dir = temp_dir
        filepath = os.path.join(benchmark_dir, "changing_file.csv")

        # Create initial file
        # 創建初始檔案
        with open(filepath, "w") as f:
            f.write("original content")

        # Calculate initial hash
        # 計算初始哈希值
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            sha256_hash.update(f.read())
        original_hash = sha256_hash.hexdigest()

        # Update config with actual filepath and hash
        # 使用實際檔案路徑和哈希值更新配置
        config = sample_config.copy()
        config["filepath"] = filepath
        config["benchmark_sha256"] = original_hash

        # Initially should match
        # 初始應該匹配
        with patch("petsard.loader.benchmarker.digest_sha256") as mock_digest:
            mock_digest.return_value = original_hash
            benchmarker = create_test_benchmarker_impl(config)
            assert benchmarker.config["benchmark_already_exist"]

            # Now modify the file
            # 現在修改檔案
            with open(filepath, "w") as f:
                f.write("modified content")

            # Calculate new hash
            # 計算新哈希值
            sha256_hash = hashlib.sha256()
            with open(filepath, "rb") as f:
                sha256_hash.update(f.read())
            new_hash = sha256_hash.hexdigest()

            # Verify should fail now
            # 現在驗證應該失敗
            mock_digest.return_value = new_hash
            with pytest.raises(BenchmarkDatasetsError):
                benchmarker._verify_file(already_exist=True)
