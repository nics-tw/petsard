import random
from typing import Optional, Union

import pandas as pd

from petsard.exceptions import ConfigError
from petsard.loader.loader import Loader
from petsard.metadater import SchemaMetadata


class Splitter:
    """
    Splitter is an independent module for Executor use. Included:
    a.) split input data via assigned ratio (train_split_ratio)
    b.) resampling assigned times (num_samples)
    c.) output their train/validation indexes (self.index_samples) and pd.DataFrame data (self.data)

    When method is 'custom_data', the data will be loaded from the filepath.
    """

    def __init__(
        self,
        method: str = None,
        num_samples: Optional[int] = 1,
        train_split_ratio: Optional[float] = 0.8,
        random_state: Optional[Union[int, float, str]] = None,
        **kwargs,
    ):
        """
        Args:
            method (str, optional):
                Supports loading existing split data, only accepting 'custom_data'.
                Default is None.
            num_samples (int, optional):
                Number of times to resample the data. Default is 1.
            train_split_ratio (float, optional):
                Ratio of data to assign to the training set,
                must between 0 ~ 1. Default is 0.8.
            random_state (int | float | str, optional):
                Seed for random number generation. Default is None.
            **kwargs (optional):
                For method 'custom_data' only. Apply Loader's config.

        Attr:
            config (dict):
                The configuration of Splitter.
                If method is None,
                    it contains num_samples, train_split_ratio, random_state.
                If method is 'custom_data',
                    it contains method, filepath, and Loader's config.

            data (dict):
                The split data of train and validation set.
                Following the format:
                {sample_num: {'train': pd.DataFrame, 'validation': pd.DataFrame}}
        """
        self.data: dict = {}
        self.config: dict = {}

        # Normal Splitter use case
        if method is None:
            if not (0 <= train_split_ratio <= 1):
                raise ConfigError(
                    "Splitter:  train_split_ratio must be a float between 0 and 1."
                )
            self.config = {
                "num_samples": num_samples,
                "train_split_ratio": train_split_ratio,
                "random_state": random_state,
            }

        # custom_data Splitter use case
        else:
            if method.lower() != "custom_data":
                raise ConfigError

            filepath = kwargs.get("filepath", None)
            if filepath is None or not isinstance(filepath, dict):
                raise ConfigError
            if not all(k in filepath for k in ("ori", "control")):
                raise ConfigError

            config = kwargs
            self.loader: dict = {}

            for key in ["ori", "control"]:
                self.loader[key] = Loader(
                    filepath=filepath[key],
                    **{
                        k: config.get(k)
                        for k in [
                            "column_types",
                            "header_names",
                            "na_values",
                        ]
                        if config.get(k) is not None
                    },
                )

            config["method"] = method
            config["filepath"] = filepath
            self.config = config

    def split(
        self,
        data: pd.DataFrame = None,
        exclude_index: list[int] = None,
    ) -> tuple[dict, SchemaMetadata]:
        """
        Perform index bootstrapping on the Splitter-initialized data
            and split it into train and validation sets
            using the generated index samples.

        When method is 'custom_data', the data will be loaded from the filepath.

        Args:
            data (pd.DataFrame, optional): The dataset which wait for split.
            exclude_index (list[int], optional):
                The exist index we want to exclude them from our sampling.

        Returns:
            tuple[dict, SchemaMetadata]: Split data and metadata
        """
        if "method" in self.config:
            # Custom data method - load from files
            ori_data, ori_metadata = self.loader["ori"].load()
            ctrl_data, _ = self.loader["control"].load()

            self.data[1] = {
                "train": ori_data,
                "validation": ctrl_data,
            }

            # Use the metadata from training data and update row counts
            metadata = self._update_metadata_with_split_info(
                ori_metadata, ori_data.shape[0], ctrl_data.shape[0]
            )

        else:
            # Normal splitting method
            if data is None:
                raise ConfigError("Data must be provided for normal splitting method")

            data.reset_index(drop=True, inplace=True)  # avoid unexpected index

            self.index = self._index_bootstrapping(
                index=data.index.tolist(), exclude_index=exclude_index
            )

            for key, index in self.index.items():
                self.data[key] = {
                    "train": data.iloc[index["train"]].reset_index(drop=True),
                    "validation": data.iloc[index["validation"]].reset_index(drop=True),
                }

            # Create basic metadata for split data
            metadata = self._create_split_metadata(
                self.data[1]["train"].shape[0], self.data[1]["validation"].shape[0]
            )

        return self.data, metadata

    def _update_metadata_with_split_info(
        self, metadata: SchemaMetadata, train_rows: int, validation_rows: int
    ) -> SchemaMetadata:
        """
        Update metadata with split information using functional approach.

        Args:
            metadata: Original metadata from training data
            train_rows: Number of training rows
            validation_rows: Number of validation rows

        Returns:
            Updated metadata with split information
        """
        # Create new properties with split information
        updated_properties = metadata.properties.copy() if metadata.properties else {}
        updated_properties["row_num_after_split"] = {
            "train": train_rows,
            "validation": validation_rows,
        }

        # Create new metadata instance with updated properties
        return SchemaMetadata(
            schema_id=metadata.schema_id,
            name=metadata.name,
            description=metadata.description,
            fields=metadata.fields,
            properties=updated_properties,
        )

    def _create_split_metadata(
        self, train_rows: int, validation_rows: int
    ) -> SchemaMetadata:
        """
        Create basic metadata for split data.

        Args:
            train_rows: Number of training rows
            validation_rows: Number of validation rows

        Returns:
            Basic metadata with split information
        """
        return SchemaMetadata(
            schema_id="split_data",
            name="Split Data Schema",
            description="Metadata for split data",
            fields=[],  # Will be populated if needed
            properties={
                "row_num_after_split": {
                    "train": train_rows,
                    "validation": validation_rows,
                }
            },
        )

    def _index_bootstrapping(
        self, index: list, exclude_index: list[int] = None
    ) -> dict[int, list[int]]:
        """
        Generate randomized index samples for splitting data.

        Args
            index (list)
                The index list of dataset which wait for split.
            exclude_index (list[int])
                The exist index we want to exclude them from our sampling.
        """
        if self.config["random_state"] is not None:
            random.seed(self.config["random_state"])

        sample_size = int(len(index) * self.config["train_split_ratio"])

        sampled_seen = set()
        if exclude_index:  # external samples seen\
            sampled_seen.add(tuple(exclude_index))

        sampled_index = {}
        # assume max sampling time as num_sample.
        maxattempts = self.config["num_samples"]
        for n in range(self.config["num_samples"]):
            # re-calculate when success.
            attempts = 0
            while attempts < maxattempts:
                sampled_indices = tuple(sorted(random.sample(index, sample_size)))

                if sampled_indices in sampled_seen:
                    attempts += 1
                else:
                    sampled_seen.add(sampled_indices)
                    sampled_index[n + 1] = {
                        "train": list(sampled_indices),
                        "validation": list(set(index) - set(sampled_indices)),
                    }
                    break
                if attempts == maxattempts:
                    raise ConfigError(
                        f"Splitter: "
                        f"Unable to sample {self.config['num_samples']} pairs of index "
                        f"with a ratio of {self.config['train_split_ratio']} "
                        f"within {maxattempts} attempts due to collisions.\n"
                        f"Please review your data size "
                        f"and choose a suitable sampling ratio."
                    )
        return sampled_index
