from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from petsard.exceptions import ConfigError, UnsupportedMethodError
from petsard.loader.loader import Loader, LoaderConfig, LoaderFileExt


class TestLoaderConfig:
    """Test cases for LoaderConfig class
    LoaderConfig 類的測試案例
    """

    def test_config_requires_filepath_or_method(self):
        """Test that either filepath or method must be specified
        測試必須指定 filepath 或 method 參數
        """
        with pytest.raises(ConfigError):
            LoaderConfig()

    def test_default_method(self):
        """Test default method configuration
        測試默認方法配置
        """
        with patch.object(LoaderConfig, "_load_benchmark_config") as mock_load_config:
            mock_load_config.return_value = {
                "adult-income": {
                    "filename": "adult-income.csv",
                    "access": "public",
                    "region_name": "us-west-2",
                    "bucket_name": "petsard-benchmark",
                    "sha256": "1f13ee2bf9d7c66098429281ab91fa1b51cbabd3b805cc365b3c6b44491ea2c0",
                }
            }

            config = LoaderConfig(method="default")
            # 檢查初始 filepath 被設置為 benchmark URL
            # Check that initial filepath is set to benchmark URL
            assert config.DEFAULT_METHOD_FILEPATH == "benchmark://adult-income"
            # 檢查 filepath 已被處理為本地路徑
            # Check that filepath has been processed to local path
            assert str(config.filepath).endswith("benchmark/adult-income.csv")
            # 檢查 benchmark 標記已被設置
            # Check that benchmark flag is set
            assert config.benchmark
            assert config.benchmark_name == "adult-income"

    def test_unsupported_method(self):
        """Test unsupported method raises error
        測試不支援的方法會引發錯誤
        """
        with pytest.raises(UnsupportedMethodError):
            LoaderConfig(method="unsupported_method")

    def test_benchmark_path_parsing(self):
        """Test parsing of benchmark path
        測試基準資料集路徑解析
        """
        with patch.object(LoaderConfig, "_load_benchmark_config") as mock_load_config:
            mock_load_config.return_value = {
                "adult-income": {
                    "filename": "adult.csv",
                    "access": "public",
                    "region_name": "us-west-2",
                    "bucket_name": "test-bucket",
                    "sha256": "test-hash",
                }
            }
            config = LoaderConfig(filepath="benchmark://adult-income")
            assert config.benchmark
            assert config.benchmark_name == "adult-income"
            assert config.filepath == Path("benchmark").joinpath("adult.csv")
            assert config.benchmark_filename == "adult.csv"
            assert config.benchmark_access == "public"
            assert config.benchmark_region_name == "us-west-2"
            assert config.benchmark_bucket_name == "test-bucket"
            assert config.benchmark_sha256 == "test-hash"

    def test_unsupported_benchmark(self):
        """Test unsupported benchmark raises error
        測試不支援的基準資料集會引發錯誤
        """
        with patch.object(LoaderConfig, "_load_benchmark_config") as mock_load_config:
            mock_load_config.return_value = {}
            with pytest.raises(UnsupportedMethodError):
                LoaderConfig(filepath="benchmark://nonexistent")

    def test_private_benchmark_unsupported(self):
        """Test private benchmark access raises error
        測試私有基準資料集存取會引發錯誤
        """
        with patch.object(LoaderConfig, "_load_benchmark_config") as mock_load_config:
            mock_load_config.return_value = {
                "private-data": {
                    "filename": "private.csv",
                    "access": "private",
                    "region_name": "us-west-2",
                    "bucket_name": "private-bucket",
                    "sha256": "test-hash",
                }
            }
            with pytest.raises(UnsupportedMethodError):
                LoaderConfig(filepath="benchmark://private-data")

    @pytest.mark.parametrize(
        "filepath,expected_ext,expected_code",
        [
            ("path/to/file.csv", ".csv", LoaderFileExt.CSVTYPE),
            ("path/to/file.xlsx", ".xlsx", LoaderFileExt.EXCELTYPE),
            ("path/to/file.xls", ".xls", LoaderFileExt.EXCELTYPE),
            ("path/to/file.CSV", ".csv", LoaderFileExt.CSVTYPE),
            ("path/to/file.XLSX", ".xlsx", LoaderFileExt.EXCELTYPE),
        ],
    )
    def test_file_extension_handling(self, filepath, expected_ext, expected_code):
        """Test file extension parsing and mapping
        測試檔案副檔名解析和映射
        """
        config = LoaderConfig(filepath=filepath)
        assert config.file_ext == expected_ext
        assert config.file_ext_code == expected_code

    def test_invalid_file_extension(self):
        """Test handling of invalid file extensions
        測試處理無效的檔案副檔名
        """
        with pytest.raises(UnsupportedMethodError):
            LoaderConfig(filepath="path/to/file.invalid")

    def test_unsupported_column_type(self):
        """Test handling of unsupported column types
        測試處理不支援的欄位類型
        """
        with pytest.raises(UnsupportedMethodError):
            LoaderConfig(
                filepath="path/to/file.csv", column_types={"unsupported_type": ["col1"]}
            )

    def test_get_method(self):
        """Test get() method returns config dictionary
        測試 get() 方法返回配置字典
        """
        config = LoaderConfig(filepath="path/to/file.csv")
        config_dict = config.get()
        assert isinstance(config_dict, dict)
        assert config_dict["filepath"] == "path/to/file.csv"
        assert config_dict["file_ext"] == ".csv"


class TestLoader:
    """Test cases for main Loader functionality
    主要 Loader 功能的測試案例
    """

    @pytest.fixture
    def sample_csv_path(self, tmp_path):
        """Create a temporary CSV file for testing
        創建臨時 CSV 檔案用於測試
        """
        csv_file = tmp_path / "test.csv"
        pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]}).to_csv(
            csv_file, index=False
        )
        return str(csv_file)

    def test_loader_init_no_config(self):
        """Test Loader initialization with no config
        測試沒有配置的 Loader 初始化
        """
        with pytest.raises(ConfigError):
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
            ("file.CSV", ".csv"),  # 測試大小寫 / Test case sensitivity
            ("path/to/file.XLSX", ".xlsx"),
        ],
    )
    def test_handle_filepath_with_complex_name(self, filepath, expected_ext):
        """Test handling of complex file paths
        測試處理複雜的檔案路徑
        > issue 375
        """
        loader = Loader(filepath=filepath)
        assert loader.config.file_ext == expected_ext
        assert loader.config.filepath == filepath

    def test_loader_init_with_filepath(self, sample_csv_path):
        """Test Loader initialization with filepath
        測試使用檔案路徑初始化 Loader
        """
        loader = Loader(filepath=sample_csv_path)
        assert loader.config.filepath == sample_csv_path
        assert loader.config.file_ext == ".csv"

    def test_loader_init_with_column_types(self, sample_csv_path):
        """Test Loader initialization with column types
        測試使用欄位類型初始化 Loader
        """
        column_types = {"category": ["B"]}
        loader = Loader(filepath=sample_csv_path, column_types=column_types)
        assert loader.config.column_types == column_types

    def test_benchmark_loader(self):
        """Test loading benchmark dataset
        測試載入基準資料集
        """
        with (
            patch("petsard.loader.loader.BenchmarkerRequests") as mock_benchmarker,
            patch.object(LoaderConfig, "_load_benchmark_config") as mock_load_config,
        ):
            mock_load_config.return_value = {
                "adult-income": {
                    "filename": "adult.csv",
                    "access": "public",
                    "region_name": "us-west-2",
                    "bucket_name": "test-bucket",
                    "sha256": "test-hash",
                }
            }

            loader = Loader(filepath="benchmark://adult-income")
            # Benchmarker should not be called during init
            # 初始化期間不應調用 Benchmarker
            mock_benchmarker.assert_not_called()

            assert loader.config.benchmark
            assert loader.config.benchmark_name == "adult-income"

    def test_load_csv(self, sample_csv_path):
        """Test loading CSV file
        測試載入 CSV 檔案
        """
        loader = Loader(filepath=sample_csv_path)

        with (
            patch("pandas.read_csv") as mock_read_csv,
            patch(
                "petsard.metadater.metadater.Metadater.create_schema"
            ) as mock_create_schema,
            patch(
                "petsard.metadater.schema.schema_functions.apply_schema_transformations"
            ) as mock_apply_transformations,
        ):
            # Setup mock returns
            # 設置模擬回傳值
            mock_df = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})
            mock_read_csv.return_value = mock_df.fillna(pd.NA)

            mock_schema_instance = MagicMock()
            mock_create_schema.return_value = mock_schema_instance
            mock_apply_transformations.return_value = mock_df

            # Call load method
            # 調用 load 方法
            data, metadata = loader.load()

            # Assertions
            # 斷言
            mock_read_csv.assert_called_once_with(
                sample_csv_path,
                header="infer",
                names=None,
                na_values=loader.config.na_values,
                dtype=None,
            )
            mock_create_schema.assert_called_once()
            mock_apply_transformations.assert_called_once()
            assert data is not None
            assert metadata is not None

    def test_load_excel(self):
        """Test loading Excel file
        測試載入 Excel 檔案
        """
        excel_path = "path/to/file.xlsx"
        loader = Loader(filepath=excel_path)

        with (
            patch("pandas.read_excel") as mock_read_excel,
            patch(
                "petsard.metadater.metadater.Metadater.create_schema"
            ) as mock_create_schema,
            patch(
                "petsard.metadater.schema.schema_functions.apply_schema_transformations"
            ) as mock_apply_transformations,
            patch("os.path.exists") as mock_exists,
        ):
            # Setup mock returns
            # 設置模擬回傳值
            mock_exists.return_value = True
            mock_df = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})
            mock_read_excel.return_value = mock_df.fillna(pd.NA)

            mock_schema_instance = MagicMock()
            mock_create_schema.return_value = mock_schema_instance
            mock_apply_transformations.return_value = mock_df

            # Call load method
            # 調用 load 方法
            data, metadata = loader.load()

            # Assertions
            # 斷言
            mock_read_excel.assert_called_once_with(
                excel_path,
                header="infer",
                names=None,
                na_values=loader.config.na_values,
                dtype=None,
            )
            mock_create_schema.assert_called_once()
            mock_apply_transformations.assert_called_once()
            assert data is not None
            assert metadata is not None

    def test_benchmark_data_load(self):
        """Test loading benchmark data
        測試載入基準資料
        """
        with (
            patch.object(LoaderConfig, "_load_benchmark_config") as mock_load_config,
            patch("petsard.loader.loader.BenchmarkerRequests") as mock_benchmarker,
            patch("pandas.read_csv") as mock_read_csv,
            patch(
                "petsard.metadater.metadater.Metadater.create_schema"
            ) as mock_create_schema,
            patch(
                "petsard.metadater.schema.schema_functions.apply_schema_transformations"
            ) as mock_apply_transformations,
        ):
            # Setup mock returns
            # 設置模擬回傳值
            mock_load_config.return_value = {
                "adult-income": {
                    "filename": "adult.csv",
                    "access": "public",
                    "region_name": "us-west-2",
                    "bucket_name": "test-bucket",
                    "sha256": "test-hash",
                }
            }
            mock_df = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})
            mock_read_csv.return_value = mock_df.fillna(pd.NA)

            mock_schema_instance = MagicMock()
            mock_create_schema.return_value = mock_schema_instance
            mock_apply_transformations.return_value = mock_df
            mock_benchmarker_instance = MagicMock()
            mock_benchmarker.return_value = mock_benchmarker_instance

            # Create and load benchmark data
            # 創建和載入基準資料
            loader = Loader(filepath="benchmark://adult-income")
            data, metadata = loader.load()

            # Assertions
            # 斷言
            mock_benchmarker.assert_called_once()
            mock_benchmarker_instance.download.assert_called_once()
            mock_read_csv.assert_called_once()
            mock_create_schema.assert_called_once()
            mock_apply_transformations.assert_called_once()
            assert data is not None
            assert metadata is not None

    def test_custom_na_values(self, sample_csv_path):
        """Test loading with custom NA values
        測試使用自定義 NA 值載入資料
        """
        na_values = ["x"]
        loader = Loader(filepath=sample_csv_path, na_values=na_values)

        with (
            patch("pandas.read_csv") as mock_read_csv,
            patch(
                "petsard.metadater.metadater.Metadater.create_schema"
            ) as mock_create_schema,
            patch(
                "petsard.metadater.schema.schema_functions.apply_schema_transformations"
            ) as mock_apply_transformations,
        ):
            # Setup mock returns
            # 設置模擬回傳值
            mock_df = pd.DataFrame({"A": [1, 2, 3], "B": [None, "y", "z"]})
            mock_read_csv.return_value = mock_df.fillna(pd.NA)

            mock_schema_instance = MagicMock()
            mock_create_schema.return_value = mock_schema_instance
            mock_apply_transformations.return_value = mock_df

            # Call load method
            # 調用 load 方法
            data, metadata = loader.load()

            # Assertions
            # 斷言
            mock_read_csv.assert_called_once_with(
                sample_csv_path,
                header="infer",
                names=None,
                na_values=na_values,
                dtype=None,
            )
            mock_create_schema.assert_called_once()
            mock_apply_transformations.assert_called_once()
            assert data is not None
            assert metadata is not None

    def test_custom_header_names(self, sample_csv_path):
        """Test loading with custom header names
        測試使用自定義欄位名稱載入資料
        """
        header_names = ["Col1", "Col2"]
        loader = Loader(filepath=sample_csv_path, header_names=header_names)

        with (
            patch("pandas.read_csv") as mock_read_csv,
            patch(
                "petsard.metadater.metadater.Metadater.create_schema"
            ) as mock_create_schema,
            patch(
                "petsard.metadater.schema.schema_functions.apply_schema_transformations"
            ) as mock_apply_transformations,
        ):
            # Setup mock returns
            # 設置模擬回傳值
            mock_df = pd.DataFrame({"Col1": [1, 2, 3], "Col2": ["x", "y", "z"]})
            mock_read_csv.return_value = mock_df.fillna(pd.NA)

            mock_schema_instance = MagicMock()
            mock_create_schema.return_value = mock_schema_instance
            mock_apply_transformations.return_value = mock_df

            # Call load method
            # 調用 load 方法
            data, metadata = loader.load()

            # Assertions
            # 斷言
            mock_read_csv.assert_called_once_with(
                sample_csv_path,
                header=0,
                names=header_names,
                na_values=loader.config.na_values,
                dtype=None,
            )
            mock_create_schema.assert_called_once()
            mock_apply_transformations.assert_called_once()
            assert data is not None
            assert metadata is not None


class TestLoaderAmbiguousDataFeatures:
    """Test cases for ambiguous data type processing features
    容易誤判、型別判斷模糊資料處理功能的測試案例
    """

    @pytest.fixture
    def ambiguous_sample_csv(self, tmp_path):
        """Create a sample CSV file with ambiguous data types for testing
        創建含有型別判斷模糊資料的測試用 CSV 檔案
        """
        csv_file = tmp_path / "ambiguous_test.csv"
        # Ambiguous data with leading zeros, mixed types, and null values
        test_data = {
            "id_code": ["001", "002", "010", "099"],  # Leading zeros - 前導零代號
            "age": [25, 30, "", 45],  # Integers with null - 含空值整數
            "amount": [
                50000.5,
                60000.7,
                "",
                75000.3,
            ],  # Floats with null - 含空值浮點數
            "score": [85, 90, 78, 92],  # Pure integers - 純整數
            "category": ["A級", "B級", "C級", "A級"],  # Categories - 分類資料
        }
        pd.DataFrame(test_data).to_csv(csv_file, index=False)
        return str(csv_file)

    def test_preserve_raw_data_feature(self, ambiguous_sample_csv):
        """Test preserve_raw_data feature prevents automatic type inference
        測試 preserve_raw_data 功能阻止自動類型推斷
        """
        loader = Loader(
            filepath=ambiguous_sample_csv,
            preserve_raw_data=True,
            auto_detect_leading_zeros=True,
            force_nullable_integers=True,
        )

        with (
            patch("pandas.read_csv") as mock_read_csv,
            patch(
                "petsard.metadater.metadater.Metadater.create_schema"
            ) as mock_create_schema,
            patch(
                "petsard.metadater.schema.schema_functions.apply_schema_transformations"
            ) as mock_apply_transformations,
        ):
            # Setup mock returns
            mock_df = pd.DataFrame(
                {
                    "id_code": ["001", "002", "010", "099"],
                    "age": ["25", "30", "", "45"],
                    "amount": ["50000.5", "60000.7", "", "75000.3"],
                    "score": ["85", "90", "78", "92"],
                    "category": ["A級", "B級", "C級", "A級"],
                }
            )
            mock_read_csv.return_value = mock_df.fillna(pd.NA)

            mock_schema_instance = MagicMock()
            mock_create_schema.return_value = mock_schema_instance
            mock_apply_transformations.return_value = mock_df

            # Call load method
            data, metadata = loader.load()

            # Verify that dtype="object" was used to preserve raw data
            mock_read_csv.assert_called_once_with(
                ambiguous_sample_csv,
                header="infer",
                names=None,
                na_values=loader.config.na_values,
                dtype="object",  # This should be "object" string when preserve_raw_data=True
            )
            mock_create_schema.assert_called_once()
            mock_apply_transformations.assert_called_once()
            assert data is not None
            assert metadata is not None

    def test_leading_zero_detection_config(self, ambiguous_sample_csv):
        """Test auto_detect_leading_zeros configuration
        測試 auto_detect_leading_zeros 配置
        """
        # Test with leading zero detection enabled
        loader_on = Loader(
            filepath=ambiguous_sample_csv,
            auto_detect_leading_zeros=True,
        )
        assert loader_on.config.auto_detect_leading_zeros is True

        # Test with leading zero detection disabled
        loader_off = Loader(
            filepath=ambiguous_sample_csv,
            auto_detect_leading_zeros=False,
        )
        assert loader_off.config.auto_detect_leading_zeros is False

    def test_nullable_integer_config(self, ambiguous_sample_csv):
        """Test force_nullable_integers configuration
        測試 force_nullable_integers 配置
        """
        # Test with nullable integers enabled
        loader_on = Loader(
            filepath=ambiguous_sample_csv,
            force_nullable_integers=True,
        )
        assert loader_on.config.force_nullable_integers is True

        # Test with nullable integers disabled
        loader_off = Loader(
            filepath=ambiguous_sample_csv,
            force_nullable_integers=False,
        )
        assert loader_off.config.force_nullable_integers is False

    def test_ambiguous_data_config_combination(self, ambiguous_sample_csv):
        """Test combination of ambiguous data processing configurations
        測試容易誤判資料處理配置的組合
        """
        loader = Loader(
            filepath=ambiguous_sample_csv,
            preserve_raw_data=True,
            auto_detect_leading_zeros=True,
            force_nullable_integers=True,
        )

        # Verify all configurations are set correctly
        assert loader.config.preserve_raw_data is True
        assert loader.config.auto_detect_leading_zeros is True
        assert loader.config.force_nullable_integers is True

    def test_backward_compatibility(self, ambiguous_sample_csv):
        """Test that new features don't break existing functionality
        測試新功能不會破壞現有功能
        """
        # Test with default settings (all new features disabled)
        loader = Loader(filepath=ambiguous_sample_csv)

        # Verify default values
        assert loader.config.preserve_raw_data is False
        assert loader.config.auto_detect_leading_zeros is False
        assert loader.config.force_nullable_integers is False

        with (
            patch("pandas.read_csv") as mock_read_csv,
            patch(
                "petsard.metadater.metadater.Metadater.create_schema"
            ) as mock_create_schema,
            patch(
                "petsard.metadater.schema.schema_functions.apply_schema_transformations"
            ) as mock_apply_transformations,
        ):
            # Setup mock returns
            mock_df = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})
            mock_read_csv.return_value = mock_df.fillna(pd.NA)

            mock_schema_instance = MagicMock()
            mock_create_schema.return_value = mock_schema_instance
            mock_apply_transformations.return_value = mock_df

            # Call load method
            data, metadata = loader.load()

            # Verify normal behavior (no dtype parameter when preserve_raw_data=False)
            mock_read_csv.assert_called_once_with(
                ambiguous_sample_csv,
                header="infer",
                names=None,
                na_values=loader.config.na_values,
                # No dtype parameter should be passed when preserve_raw_data=False
            )
            assert data is not None
            assert metadata is not None


class TestLoaderFileExt:
    """Test cases for LoaderFileExt class
    LoaderFileExt 類的測試案例
    """

    @pytest.mark.parametrize(
        "file_ext,expected_code",
        [
            (".csv", LoaderFileExt.CSVTYPE),
            (".CSV", LoaderFileExt.CSVTYPE),
            (".xlsx", LoaderFileExt.EXCELTYPE),
            (".XLSX", LoaderFileExt.EXCELTYPE),
            (".xls", LoaderFileExt.EXCELTYPE),
            (".xlsm", LoaderFileExt.EXCELTYPE),
            (".xlsb", LoaderFileExt.EXCELTYPE),
            (".ods", LoaderFileExt.EXCELTYPE),
            (".odt", LoaderFileExt.EXCELTYPE),
        ],
    )
    def test_get_file_ext_code(self, file_ext, expected_code):
        """Test getting file extension code
        測試獲取檔案副檔名類型
        """
        assert LoaderFileExt.get(file_ext) == expected_code

    def test_unsupported_file_ext(self):
        """Test handling of unsupported file extensions
        測試處理不支援的檔案副檔名
        """
        with pytest.raises(KeyError):
            LoaderFileExt.get(".unsupported")
