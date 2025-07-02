from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from petsard.exceptions import ConfigError
from petsard.loader import Splitter
from petsard.metadater import SchemaMetadata


class TestSplitter:
    """Test cases for Splitter class
    Splitter 類的測試案例
    """

    @pytest.fixture
    def sample_data(self):
        """Create sample DataFrame for testing
        創建測試用的範例 DataFrame
        """
        return pd.DataFrame(
            {
                "A": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                "B": ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"],
            }
        )

    @pytest.fixture
    def sample_csv_files(self, tmp_path):
        """Create temporary CSV files for testing custom_data method
        創建臨時 CSV 檔案用於測試 custom_data 方法
        """
        # Create training data file
        train_data = pd.DataFrame(
            {"A": [1, 2, 3, 4, 5], "B": ["a", "b", "c", "d", "e"]}
        )
        train_file = tmp_path / "train.csv"
        train_data.to_csv(train_file, index=False)

        # Create validation data file
        val_data = pd.DataFrame({"A": [6, 7, 8], "B": ["f", "g", "h"]})
        val_file = tmp_path / "val.csv"
        val_data.to_csv(val_file, index=False)

        return {"ori": str(train_file), "control": str(val_file)}

    def test_splitter_init_normal(self):
        """Test normal Splitter initialization
        測試正常的 Splitter 初始化
        """
        splitter = Splitter(num_samples=2, train_split_ratio=0.7, random_state=42)

        assert splitter.config["num_samples"] == 2
        assert splitter.config["train_split_ratio"] == 0.7
        assert splitter.config["random_state"] == 42
        # 移除 data 屬性檢查，因為函數化編程不再存儲狀態
        assert hasattr(splitter, "config")

    def test_splitter_init_invalid_ratio(self):
        """Test Splitter initialization with invalid train_split_ratio
        測試使用無效 train_split_ratio 初始化 Splitter
        """
        with pytest.raises(ConfigError):
            Splitter(train_split_ratio=1.5)

        with pytest.raises(ConfigError):
            Splitter(train_split_ratio=-0.1)

    def test_splitter_init_custom_data_valid(self, sample_csv_files):
        """Test Splitter initialization with custom_data method
        測試使用 custom_data 方法初始化 Splitter
        """
        splitter = Splitter(method="custom_data", filepath=sample_csv_files)

        assert splitter.config["method"] == "custom_data"
        assert splitter.config["filepath"] == sample_csv_files
        assert "ori" in splitter.loader
        assert "control" in splitter.loader

    def test_splitter_init_custom_data_invalid_method(self):
        """Test Splitter initialization with invalid custom method
        測試使用無效自訂方法初始化 Splitter
        """
        with pytest.raises(ConfigError):
            Splitter(method="invalid_method")

    def test_splitter_init_custom_data_invalid_filepath(self):
        """Test Splitter initialization with invalid filepath for custom_data
        測試使用無效檔案路徑初始化 custom_data Splitter
        """
        with pytest.raises(ConfigError):
            Splitter(method="custom_data", filepath="invalid")

        with pytest.raises(ConfigError):
            Splitter(
                method="custom_data", filepath={"ori": "file1.csv"}
            )  # missing control

    def test_split_normal_method(self, sample_data):
        """Test normal splitting method
        測試正常分割方法
        """
        splitter = Splitter(num_samples=1, train_split_ratio=0.8, random_state=42)

        split_data, metadata, train_indices = splitter.split(data=sample_data)

        # Check data structure
        assert 1 in split_data
        assert "train" in split_data[1]
        assert "validation" in split_data[1]

        # Check split ratio (approximately)
        train_size = len(split_data[1]["train"])
        val_size = len(split_data[1]["validation"])
        total_size = train_size + val_size

        assert total_size == len(sample_data)
        assert abs(train_size / total_size - 0.8) < 0.1  # Allow some tolerance

        # Check metadata - 現在是字典格式
        assert isinstance(metadata, dict)
        assert 1 in metadata
        assert "train" in metadata[1]
        assert "validation" in metadata[1]
        assert isinstance(metadata[1]["train"], SchemaMetadata)

        # Check train_indices - 現在是 list[set] 格式
        assert isinstance(train_indices, list)
        assert len(train_indices) == 1
        assert isinstance(train_indices[0], set)
        assert len(train_indices[0]) == train_size

    def test_split_normal_method_no_data(self):
        """Test normal splitting method without providing data
        測試正常分割方法但未提供資料
        """
        splitter = Splitter(num_samples=1, train_split_ratio=0.8)

        with pytest.raises(ConfigError):
            splitter.split()

    def test_split_multiple_samples(self, sample_data):
        """Test splitting with multiple samples
        測試多次取樣分割
        """
        splitter = Splitter(
            num_samples=3,
            train_split_ratio=0.6,
            random_state=42,
            max_overlap_ratio=0.5,
        )

        split_data, metadata, train_indices = splitter.split(data=sample_data)

        # Check that we have 3 samples
        assert len(split_data) == 3
        for i in range(1, 4):
            assert i in split_data
            assert "train" in split_data[i]
            assert "validation" in split_data[i]

        # Check train_indices - 現在是 list[set] 格式
        assert len(train_indices) == 3
        for i in range(3):
            assert isinstance(train_indices[i], set)

    def test_split_custom_data_method(self, sample_csv_files):
        """Test custom_data splitting method
        測試 custom_data 分割方法
        """
        with (
            patch(
                "petsard.metadater.metadater.Metadater.create_schema"
            ) as mock_create_schema,
            patch(
                "petsard.metadater.schema.schema_functions.apply_schema_transformations"
            ) as mock_apply_transformations,
            patch("pandas.read_csv") as mock_read_csv,
        ):
            # Setup mocks
            train_data = pd.DataFrame({"A": [1, 2, 3], "B": ["a", "b", "c"]})
            val_data = pd.DataFrame({"A": [4, 5], "B": ["d", "e"]})

            mock_read_csv.side_effect = [
                train_data.fillna(pd.NA),  # First call for training data
                val_data.fillna(pd.NA),  # Second call for validation data
            ]

            mock_schema = MagicMock()
            mock_schema.schema_id = "test_schema"
            mock_schema.name = "Test Schema"
            mock_schema.description = "Test Description"
            mock_schema.fields = []
            mock_schema.properties = {"original_rows": 3}

            mock_create_schema.return_value = mock_schema
            mock_apply_transformations.side_effect = [train_data, val_data]

            # Create splitter and split
            splitter = Splitter(method="custom_data", filepath=sample_csv_files)
            split_data, metadata, train_indices = splitter.split()

            # Check data structure
            assert 1 in split_data
            assert "train" in split_data[1]
            assert "validation" in split_data[1]

            # Check data content
            pd.testing.assert_frame_equal(split_data[1]["train"], train_data)
            pd.testing.assert_frame_equal(split_data[1]["validation"], val_data)

            # Check metadata - 現在是字典格式
            assert isinstance(metadata, dict)
            assert 1 in metadata
            assert "train" in metadata[1]
            assert "validation" in metadata[1]
            assert isinstance(metadata[1]["train"], SchemaMetadata)

    def test_split_basic_functionality(self, sample_data):
        """Test basic splitting functionality
        測試基本分割功能
        """
        splitter = Splitter(num_samples=1, train_split_ratio=0.8, random_state=42)

        # Test basic split functionality
        split_data, metadata, train_indices = splitter.split(data=sample_data)

        # Check basic functionality
        assert 1 in split_data
        assert "train" in split_data[1]
        assert "validation" in split_data[1]

        # Total data should be preserved
        train_size = len(split_data[1]["train"])
        val_size = len(split_data[1]["validation"])
        assert train_size + val_size == len(sample_data)

        # Check metadata - 現在是字典格式
        assert isinstance(metadata, dict)
        assert 1 in metadata
        assert "train" in metadata[1]
        assert "validation" in metadata[1]
        assert isinstance(metadata[1]["train"], SchemaMetadata)

    def test_index_bootstrapping_collision_handling(self):
        """Test index bootstrapping with collision handling
        測試索引自助抽樣的碰撞處理
        """
        # Create a scenario where collisions are likely
        splitter = Splitter(num_samples=100, train_split_ratio=0.5, random_state=42)

        # With only 4 data points and 50% split, collisions are very likely
        small_data = pd.DataFrame({"A": [1, 2, 3, 4]})

        with pytest.raises(ConfigError):
            splitter.split(data=small_data)

    def test_metadata_update_functional_approach(self):
        """Test metadata update using functional approach
        測試使用函數式方法更新詮釋資料
        """
        splitter = Splitter()

        # Create original metadata
        original_metadata = SchemaMetadata(
            schema_id="test",
            name="Test Schema",
            description="Original schema",
            fields=[],
            properties={"original_prop": "value"},
        )

        # Update metadata
        updated_metadata = splitter._update_metadata_with_split_info(
            original_metadata, 100, 50
        )

        # Check that original metadata is unchanged
        assert "row_num_after_split" not in original_metadata.properties

        # Check that updated metadata has new information
        assert "row_num_after_split" in updated_metadata.properties
        assert updated_metadata.properties["row_num_after_split"]["train"] == 100
        assert updated_metadata.properties["row_num_after_split"]["validation"] == 50
        assert (
            updated_metadata.properties["original_prop"] == "value"
        )  # Original props preserved

    def test_create_split_metadata(self):
        """Test creation of basic split metadata
        測試建立基本分割詮釋資料
        """
        splitter = Splitter()

        metadata = splitter._create_split_metadata(80, 20)

        assert isinstance(metadata, SchemaMetadata)
        assert metadata.schema_id == "split_data"
        assert metadata.name == "Split Data Schema"
        assert "row_num_after_split" in metadata.properties
        assert metadata.properties["row_num_after_split"]["train"] == 80
        assert metadata.properties["row_num_after_split"]["validation"] == 20

    def test_max_overlap_ratio_parameter(self):
        """Test max_overlap_ratio parameter initialization
        測試 max_overlap_ratio 參數初始化
        """
        # Test default value
        splitter = Splitter()
        assert splitter.config["max_overlap_ratio"] == 1.0

        # Test custom value
        splitter = Splitter(max_overlap_ratio=0.2)
        assert splitter.config["max_overlap_ratio"] == 0.2

        # Test invalid value
        with pytest.raises(ConfigError):
            Splitter(max_overlap_ratio=1.5)

        with pytest.raises(ConfigError):
            Splitter(max_overlap_ratio=-0.1)

    def test_overlap_control_functionality(self, sample_data):
        """Test overlap control functionality
        測試重疊控制功能
        """
        # Create larger dataset for better testing
        large_data = pd.DataFrame(
            {"A": list(range(100)), "B": [f"item_{i}" for i in range(100)]}
        )

        # Test with reasonable overlap control
        splitter = Splitter(
            num_samples=2,
            train_split_ratio=0.3,
            max_overlap_ratio=0.2,
            random_state=42,
        )

        split_data, metadata, train_indices = splitter.split(data=large_data)

        # Check that we got the expected number of samples
        assert len(split_data) == 2
        assert len(train_indices) == 2

        # Check overlap between samples - train_indices 現在是 list[set]
        for i in range(len(train_indices)):
            for j in range(i + 1, len(train_indices)):
                overlap = len(train_indices[i].intersection(train_indices[j]))
                overlap_percentage = overlap / len(train_indices[i])
                assert overlap_percentage <= 0.2, (
                    f"Overlap {overlap_percentage:.2%} exceeds limit"
                )

    def test_exclude_index_functionality(self, sample_data):
        """Test exclude_index functionality with sets
        測試使用集合的 exclude_index 功能
        """
        # Create existing index sets to exclude
        existing_indices = [
            {0, 1, 2, 3},  # First existing sample
            {4, 5, 6, 7},  # Second existing sample
        ]

        splitter = Splitter(
            num_samples=1,
            train_split_ratio=0.2,
            max_overlap_ratio=0.5,
            random_state=42,
        )

        split_data, metadata, train_indices = splitter.split(
            data=sample_data, exist_train_indices=existing_indices
        )

        # Check that new samples respect overlap constraints with existing ones
        # train_indices 現在是 list[set] 格式
        for sample_set in train_indices:
            for existing_set in existing_indices:
                overlap = len(sample_set.intersection(existing_set))
                overlap_percentage = overlap / len(sample_set)
                assert overlap_percentage <= 0.5, (
                    f"Overlap {overlap_percentage:.2%} exceeds limit"
                )
