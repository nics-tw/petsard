import pandas as pd

from petsard.util import safe_round


class Metadata:
    def __init__(self):
        self.metadata = None

    def build_metadata(self, data: pd.DataFrame) -> None:
        """
        Create metadata from the data and infer data types from the metadata,
        which is used for generating config and `to_sdv` method.

        The infer data types can be one of the following:
        'numerical', 'categorical', 'datetime', and 'object'.

        Args:
            data (pd.DataFrame): The dataframe used for building metadata.
        """
        self._check_dataframe_valid(data)

        metadata = {"col": None, "global": {}}

        metadata["global"]["row_num"] = data.shape[0]
        metadata["global"]["col_num"] = data.shape[1]
        metadata["global"]["na_percentage"] = safe_round(data.isna().any(axis=1).mean())

        # create type and na_percentage keys and values automatically
        metadata_df = (
            data.dtypes.reset_index(name="dtype")
            .merge(
                safe_round(data.isna().mean(axis=0).reset_index(name="na_percentage")),
                on="index",
            )
            .set_index("index")
        )

        # infer dtypes
        metadata_df["infer_dtype"] = metadata_df["dtype"].apply(self._convert_dtypes)

        metadata["col"] = metadata_df.to_dict("index")

        self.metadata = metadata

    def set_col_infer_dtype(self, col: str, dtype: str) -> None:
        """
        Set the inferred data type for the column.

        Args:
            col (str): The column name.
            dtype (str): The inferred data type.
        """
        if self.metadata is None:
            raise ValueError(
                "Please use `build_metadata()` to construct the metadata first."
            )

        if col not in self.metadata["col"]:
            raise ValueError(f"{col} is not in the metadata.")

        if dtype not in ["numerical", "categorical", "datetime", "object"]:
            raise ValueError(f"{dtype} is invalid.")

        self.metadata["col"][col]["infer_dtype"] = dtype

    def _check_dataframe_valid(self, data: pd.DataFrame) -> None:
        """
        Check the validity of dataframe.

        Args:
            data (pd.DataFrame): The dataframe to be checked.
        """

        if not isinstance(data, pd.DataFrame):
            raise TypeError("Data should be a pd.DataFrame.")

        if data.shape[0] <= 0:
            raise ValueError("There should be at least one row in the dataframe.")

        if data.shape[1] <= 0:
            raise ValueError("There should be at least one column in the dataframe.")

    @classmethod
    def _convert_dtypes(cls, dtype: type) -> str:
        """
        Auxiliary function for inferring dtypes.

        Args:
            dtype (type): The data type from the data.

        Return:
            (str): The inferred data type.
        """
        if dtype is None:
            raise ValueError(f"{dtype} is invalid.")

        if pd.api.types.is_bool_dtype(dtype):
            return "categorical"
        elif pd.api.types.is_numeric_dtype(dtype):
            return "numerical"
        elif isinstance(dtype, pd.CategoricalDtype):
            return "categorical"
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            return "datetime"
        elif pd.api.types.is_object_dtype(dtype):
            return "object"
        else:
            raise ValueError(f"{dtype} is invalid.")
