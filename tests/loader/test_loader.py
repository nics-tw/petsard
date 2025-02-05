from unittest.mock import patch

import pandas as pd
import pytest

from petsard.error import NoConfigError, UnsupportedMethodError
from petsard.loader import Loader


class TestLoader:
    """Test cases for main Loader functionality"""

    @pytest.fixture
    def sample_csv_path(self, tmp_path):
        """Create a temporary CSV file for testing"""
        csv_file = tmp_path / "test.csv"
        pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]}).to_csv(
            csv_file, index=False
        )
        return str(csv_file)

    def test_loader_init_no_config(self):
        """Test Loader initialization with no config"""
        with pytest.raises(NoConfigError):
            Loader()

    @pytest.mark.parametrize(
        "filepath,expected_ext",
        [
            ("path/to/file.csv", ".csv"),
            ("path.with.dots/file.csv", ".csv"),
            ("path/to/file.name.with.dots.csv", ".csv"),
            ("./relative/path/file.csv", ".csv"),
            ("../parent/path/file.csv", ".csv"),
            ("/absolute/path/file.csv", ".csv"),
            ("file.CSV", ".csv"),  # 測試大小寫
            ("path/to/file.XLSX", ".xlsx"),
        ],
    )
    def test_handle_filepath_with_complex_name(self, filepath, expected_ext):
        """
        Test handling of complex file paths
        > issue 375
        """
        loader = Loader(filepath=filepath)
        assert loader.config["file_ext"] == expected_ext
        assert loader.config["filepath"] == filepath

    def test_loader_init_with_filepath(self, sample_csv_path):
        """Test Loader initialization with filepath"""
        loader = Loader(filepath=sample_csv_path)
        assert loader.config["filepath"] == sample_csv_path
        assert loader.config["file_ext"] == ".csv"

    def test_loader_init_with_column_types(self, sample_csv_path):
        """Test Loader initialization with column types"""
        column_types = {"category": ["B"]}
        loader = Loader(filepath=sample_csv_path, column_types=column_types)
        assert loader.config["column_types"] == column_types

    def test_benchmark_loader(self):
        """Test loading benchmark dataset"""
        with patch(
            "petsard.loader.benchmark.BenchmarkerRequests"
        ) as _:  # mock_benchmarker:
            loader = Loader(filepath="benchmark://adult-income")
            assert loader.config["benchmark"]
            assert "benchmark_name" in loader.config
            assert loader.config["benchmark_name"] == "adult-income"

    def test_load_csv(self, sample_csv_path):
        """Test loading CSV file"""
        loader = Loader(filepath=sample_csv_path)
        loader.load()
        assert isinstance(loader.data, pd.DataFrame)
        assert loader.metadata is not None

    def test_invalid_file_extension(self):
        """Test handling of invalid file extensions"""
        with pytest.raises(UnsupportedMethodError):
            Loader(filepath="test.invalid")

    def test_custom_na_values(self, sample_csv_path):
        """Test loading with custom NA values"""
        loader = Loader(filepath=sample_csv_path, na_values=["x"])
        loader.load()
        assert loader.data is not None
