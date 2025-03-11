import numpy as np
import pandas as pd
import pytest

from petsard.loader.metadata import Metadata


class TestMetadata:
    """Test cases for Metadata functionality"""

    @pytest.fixture
    def sample_df(self):
        """Create a sample DataFrame with various data types"""
        df = pd.DataFrame(
            {
                "numerical": [1.0, 2.0, 3.0, None],
                "categorical": pd.Categorical(["A", "B", "A", None]),
                "datetime": pd.date_range("2021-01-01", periods=4),
                "boolean": pd.Categorical([True, False, True, None]),
            }
        )
        return df

    def test_metadata_init(self):
        """Test initialization of Metadata"""
        metadata = Metadata()
        assert metadata.metadata is None

    def test_build_metadata(self, sample_df):
        """Test building metadata from DataFrame"""
        metadata = Metadata()
        metadata.build_metadata(sample_df)

        # Validate basic metadata
        assert metadata.metadata is not None
        assert metadata.metadata["global"]["row_num"] == 4
        assert metadata.metadata["global"]["col_num"] == 4
        assert "na_percentage" in metadata.metadata["global"]

        # Validate inferred types
        assert metadata.metadata["col"]["numerical"]["infer_dtype"] == "numerical"
        assert metadata.metadata["col"]["categorical"]["infer_dtype"] == "categorical"
        assert metadata.metadata["col"]["datetime"]["infer_dtype"] == "datetime"
        assert metadata.metadata["col"]["boolean"]["infer_dtype"] == "categorical"

        # Validate original dtypes are preserved
        assert str(metadata.metadata["col"]["numerical"]["dtype"]) == "float64"
        assert str(metadata.metadata["col"]["categorical"]["dtype"]) == "category"
        assert str(metadata.metadata["col"]["boolean"]["dtype"]) == "category"

    def test_invalid_dataframe(self):
        """Test handling of invalid DataFrames"""
        metadata = Metadata()

        # Test with non-DataFrame input
        with pytest.raises(TypeError):
            metadata.build_metadata([1, 2, 3])

        # Test with empty DataFrame
        with pytest.raises(ValueError):
            metadata.build_metadata(pd.DataFrame())

    def test_set_col_infer_dtype(self, sample_df):
        """Test setting inferred dtype for columns"""
        metadata = Metadata()
        metadata.build_metadata(sample_df)

        # Test valid column and type
        metadata.set_col_infer_dtype("numerical", "numerical")
        assert metadata.metadata["col"]["numerical"]["infer_dtype"] == "numerical"

        # Test non-existent column
        with pytest.raises(ValueError):
            metadata.set_col_infer_dtype("nonexistent", "numerical")

        # Test invalid type
        with pytest.raises(ValueError):
            metadata.set_col_infer_dtype("numerical", "invalid_type")

    def test_convert_dtypes(self):
        """Test dtype conversion logic"""
        metadata = Metadata()

        # Test numeric dtypes
        assert metadata._convert_dtypes(np.dtype("int64")) == "numerical"
        assert metadata._convert_dtypes(np.dtype("float64")) == "numerical"

        # Test categorical dtypes
        assert metadata._convert_dtypes(pd.CategoricalDtype()) == "categorical"

        # Test datetime dtypes
        assert metadata._convert_dtypes(np.dtype("datetime64[ns]")) == "datetime"

        # Test boolean dtype (should be categorical)
        df = pd.DataFrame({"bool_col": [True, False]})
        assert metadata._convert_dtypes(df["bool_col"].dtype) == "categorical"

        # Test None dtype
        with pytest.raises(ValueError):
            metadata._convert_dtypes(None)
