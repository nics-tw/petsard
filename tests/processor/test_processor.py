import numpy as np
import pandas as pd
import pytest

from petsard.exceptions import ConfigError, UnfittedError
from petsard.metadater import FieldMetadata, SchemaMetadata
from petsard.metadater.field.field_types import FieldStats
from petsard.metadater.types.data_types import DataType
from petsard.processor.processor import DefaultProcessorMap, Processor


class TestProcessor:
    """Test the main Processor class functionality"""

    @pytest.fixture
    def sample_metadata(self):
        """Create sample metadata for testing"""
        fields = [
            FieldMetadata(
                name="numerical_col", data_type=DataType.FLOAT64, source_dtype="float64"
            ),
            FieldMetadata(
                name="categorical_col", data_type=DataType.STRING, source_dtype="object"
            ),
            FieldMetadata(
                name="datetime_col",
                data_type=DataType.TIMESTAMP,
                source_dtype="datetime64[ns]",
            ),
        ]
        return SchemaMetadata(schema_id="test_schema", fields=fields)

    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing"""
        return pd.DataFrame(
            {
                "numerical_col": [1.0, 2.0, 3.0, np.nan, 5.0],
                "categorical_col": ["A", "B", "A", "C", "B"],
                "datetime_col": pd.to_datetime(
                    [
                        "2024-01-01",
                        "2024-01-02",
                        "2024-01-03",
                        "2024-01-04",
                        "2024-01-05",
                    ]
                ),
            }
        )

    def test_processor_initialization(self, sample_metadata):
        """Test Processor initialization"""
        processor = Processor(sample_metadata)

        assert processor._metadata == sample_metadata
        assert not processor._is_fitted
        assert processor._config is not None
        assert processor._sequence is None
        assert processor.DEFAULT_SEQUENCE == ["missing", "outlier", "encoder", "scaler"]

    def test_processor_initialization_with_config(self, sample_metadata):
        """Test Processor initialization with custom config"""
        custom_config = {"missing": {"numerical_col": "missing_median"}}

        processor = Processor(sample_metadata, config=custom_config)
        assert processor._config is not None

    def test_generate_config(self, sample_metadata):
        """Test config generation based on metadata"""
        processor = Processor(sample_metadata)

        # Check that config is generated for all processor types
        for proc_type in DefaultProcessorMap.VALID_TYPES:
            assert proc_type in processor._config

        # Check that all fields are in each processor config
        field_names = [field.name for field in sample_metadata.fields]
        for proc_type in processor._config:
            for field_name in field_names:
                assert field_name in processor._config[proc_type]

    def test_get_config(self, sample_metadata):
        """Test getting processor config"""
        processor = Processor(sample_metadata)

        # Get all config
        all_config = processor.get_config()
        assert isinstance(all_config, dict)

        # Get specific columns config
        specific_config = processor.get_config(col=["numerical_col"])
        assert "numerical_col" in specific_config["missing"]
        assert "categorical_col" not in specific_config["missing"]

    def test_update_config(self, sample_metadata):
        """Test updating processor config"""
        processor = Processor(sample_metadata)

        # Test string config update
        update_config = {"missing": {"numerical_col": "missing_median"}}
        processor.update_config(update_config)

        # Test dict config update
        update_config_dict = {"scaler": {"numerical_col": {"method": "scaler_minmax"}}}
        processor.update_config(update_config_dict)

        # Test None config update
        update_config_none = {"encoder": {"numerical_col": None}}
        processor.update_config(update_config_none)

        # Test invalid config
        with pytest.raises(ConfigError):
            processor.update_config({"missing": {"numerical_col": ["invalid_type"]}})

    def test_sequence_validation(self, sample_metadata):
        """Test sequence validation"""
        processor = Processor(sample_metadata)

        # Test valid sequence
        valid_sequence = ["missing", "encoder"]
        processor._check_sequence_valid(valid_sequence)

        # Test invalid type
        with pytest.raises(TypeError):
            processor._check_sequence_valid("not_a_list")

        # Test empty sequence
        with pytest.raises(ValueError):
            processor._check_sequence_valid([])

        # Test too long sequence
        with pytest.raises(ValueError):
            processor._check_sequence_valid(
                ["missing", "outlier", "encoder", "scaler", "extra"]
            )

        # Test duplicate processors
        with pytest.raises(ValueError):
            processor._check_sequence_valid(["missing", "missing"])

        # Test invalid processor
        with pytest.raises(ValueError):
            processor._check_sequence_valid(["invalid_processor"])

        # Test discretizing with encoder
        with pytest.raises(ValueError):
            processor._check_sequence_valid(["encoder", "discretizing"])

        # Test discretizing not at end
        with pytest.raises(ValueError):
            processor._check_sequence_valid(["discretizing", "scaler"])

    def test_fit_default_sequence(self, sample_metadata, sample_data):
        """Test fitting with default sequence"""
        processor = Processor(sample_metadata)
        processor.fit(sample_data)

        assert processor._is_fitted
        assert processor._sequence == processor.DEFAULT_SEQUENCE
        assert processor._fitting_sequence is not None

    def test_fit_custom_sequence(self, sample_metadata, sample_data):
        """Test fitting with custom sequence"""
        processor = Processor(sample_metadata)
        custom_sequence = ["missing", "encoder"]
        processor.fit(sample_data, sequence=custom_sequence)

        assert processor._is_fitted
        assert processor._sequence == custom_sequence

    def test_transform_before_fit(self, sample_metadata, sample_data):
        """Test transform before fit raises error"""
        processor = Processor(sample_metadata)

        with pytest.raises(UnfittedError):
            processor.transform(sample_data)

    def test_transform_after_fit(self, sample_metadata, sample_data):
        """Test transform after fit"""
        processor = Processor(sample_metadata)
        processor.fit(sample_data)

        transformed = processor.transform(sample_data)
        assert isinstance(transformed, pd.DataFrame)
        assert (
            transformed.shape[1] >= sample_data.shape[1]
        )  # May have more columns after encoding

    def test_inverse_transform_before_fit(self, sample_metadata, sample_data):
        """Test inverse transform before fit raises error"""
        processor = Processor(sample_metadata)

        with pytest.raises(UnfittedError):
            processor.inverse_transform(sample_data)

    def test_inverse_transform_after_fit(self, sample_metadata, sample_data):
        """Test inverse transform after fit"""
        processor = Processor(sample_metadata)
        processor.fit(sample_data)

        transformed = processor.transform(sample_data)
        inverse_transformed = processor.inverse_transform(transformed)

        assert isinstance(inverse_transformed, pd.DataFrame)
        # Note: exact equality may not hold due to processing effects
        assert inverse_transformed.shape == sample_data.shape

    def test_get_changes(self, sample_metadata):
        """Test getting configuration changes"""
        processor = Processor(sample_metadata)

        # Initially no changes
        changes = processor.get_changes()
        assert isinstance(changes, pd.DataFrame)

        # Make some changes
        processor.update_config({"missing": {"numerical_col": "missing_median"}})

        changes = processor.get_changes()
        assert len(changes) > 0

    def test_field_metadata_methods(self, sample_metadata):
        """Test field metadata helper methods"""
        processor = Processor(sample_metadata)

        # Test field names
        field_names = processor._get_field_names()
        assert "numerical_col" in field_names
        assert "categorical_col" in field_names
        assert "datetime_col" in field_names

        # Test field dtype inference
        assert processor._get_field_infer_dtype("numerical_col") == "numerical"
        assert processor._get_field_infer_dtype("categorical_col") == "categorical"
        assert processor._get_field_infer_dtype("datetime_col") == "datetime"

        # Test invalid field
        with pytest.raises(ValueError):
            processor._get_field_infer_dtype("nonexistent_field")


class TestProcessorWithMissingValues:
    """Test Processor with various missing value scenarios"""

    @pytest.fixture
    def metadata_with_stats(self):
        """Create metadata with statistics for missing value testing"""

        fields = [
            FieldMetadata(
                name="col_with_na",
                data_type=DataType.FLOAT64,
                source_dtype="float64",
                stats=FieldStats(row_count=100, na_count=20, na_percentage=0.2),
            ),
            FieldMetadata(
                name="col_no_na",
                data_type=DataType.STRING,
                source_dtype="object",
                stats=FieldStats(row_count=100, na_count=0, na_percentage=0.0),
            ),
        ]
        return SchemaMetadata(schema_id="test_schema_with_stats", fields=fields)

    @pytest.fixture
    def data_with_missing(self):
        """Create data with missing values"""
        return pd.DataFrame(
            {
                "col_with_na": [1.0, np.nan, 3.0, np.nan, 5.0],
                "col_no_na": ["A", "B", "C", "D", "E"],
            }
        )

    def test_global_na_percentage(self, metadata_with_stats):
        """Test global NA percentage calculation"""
        processor = Processor(metadata_with_stats)

        # Should calculate global NA percentage from metadata
        global_na = processor._get_global_na_percentage()
        assert isinstance(global_na, float)
        assert 0 <= global_na <= 1

    def test_field_na_percentage(self, metadata_with_stats):
        """Test field-specific NA percentage"""
        processor = Processor(metadata_with_stats)

        na_pct_with_na = processor._get_field_na_percentage("col_with_na")
        na_pct_no_na = processor._get_field_na_percentage("col_no_na")

        assert na_pct_with_na == 0.2
        assert na_pct_no_na == 0.0


class TestProcessorWithExtremeData:
    """Test Processor with extreme data scenarios"""

    @pytest.fixture
    def extreme_metadata(self):
        """Create metadata for extreme data testing"""
        fields = [
            FieldMetadata(
                name="large_numbers", data_type=DataType.FLOAT64, source_dtype="float64"
            ),
            FieldMetadata(
                name="small_numbers", data_type=DataType.FLOAT64, source_dtype="float64"
            ),
            FieldMetadata(
                name="high_cardinality",
                data_type=DataType.STRING,
                source_dtype="object",
            ),
        ]
        return SchemaMetadata(schema_id="extreme_schema", fields=fields)

    @pytest.fixture
    def extreme_data(self):
        """Create extreme data for testing"""
        return pd.DataFrame(
            {
                "large_numbers": [1e10, 1e15, 1e20, -1e10, 0],
                "small_numbers": [1e-10, 1e-15, 1e-20, -1e-10, 0],
                "high_cardinality": [f"cat_{i}" for i in range(5)],
            }
        )

    def test_extreme_values_processing(self, extreme_metadata, extreme_data):
        """Test processing of extreme values"""
        processor = Processor(extreme_metadata)
        processor.fit(extreme_data)

        transformed = processor.transform(extreme_data)
        assert isinstance(transformed, pd.DataFrame)

        # Should handle extreme values without crashing
        assert not transformed.isnull().all().any()


class TestProcessorEdgeCases:
    """Test Processor edge cases and error conditions"""

    def test_empty_metadata(self):
        """Test with empty metadata"""
        empty_metadata = SchemaMetadata(schema_id="empty_schema", fields=[])
        processor = Processor(empty_metadata)

        # Should handle empty metadata gracefully
        assert processor._get_field_names() == []
        assert processor._get_global_na_percentage() == 0.0

    def test_single_column_data(self):
        """Test with single column data"""
        metadata = SchemaMetadata(
            schema_id="single_col_schema",
            fields=[
                FieldMetadata(
                    name="single_col",
                    data_type=DataType.FLOAT64,
                    source_dtype="float64",
                )
            ],
        )

        data = pd.DataFrame({"single_col": [1.0, 2.0, 3.0]})

        processor = Processor(metadata)
        processor.fit(data)
        transformed = processor.transform(data)

        assert isinstance(transformed, pd.DataFrame)
        assert transformed.shape[0] == data.shape[0]

    def test_all_missing_data(self):
        """Test with all missing data"""
        metadata = SchemaMetadata(
            schema_id="all_na_schema",
            fields=[
                FieldMetadata(
                    name="all_na_col",
                    data_type=DataType.FLOAT64,
                    source_dtype="float64",
                )
            ],
        )

        data = pd.DataFrame({"all_na_col": [np.nan, np.nan, np.nan]})

        processor = Processor(metadata)
        processor.fit(data)

        # Should handle all-NA data without crashing
        transformed = processor.transform(data)
        assert isinstance(transformed, pd.DataFrame)
