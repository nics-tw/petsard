import random
from typing import Optional, Union

import pandas as pd

from petsard.exceptions import ConfigError
from petsard.loader.loader import Loader
from petsard.loader.metadata import Metadata


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

            metadata (Metadata):
                The metadata of the data.

            loader (dict, optional):
                The loader for 'custom_data' method.
                Contains 'ori' and 'control' loader for train and validation data.
        """
        self.data: dict = {}
        self.config: dict = {}
        self.metadata: Metadata = None

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
        metadata: Metadata = None,
    ):
        """
        Perform index bootstrapping on the Splitter-initialized data
            and split it into train and validation sets
            using the generated index samples.

        When method is 'custom_data', the data will be loaded from the filepath.

        Args:
            data (pd.DataFrame, optional): The dataset which wait for split.
            exclude_index (list[int], optional):
                The exist index we want to exclude them from our sampling.
            metadata (Metadata, optional): The metadata class of the data.
        """
        if "method" in self.config:
            ori_data, ori_metadata = self.loader["ori"].load()
            ctrl_data, _ = self.loader["control"].load()
            self.data[1] = {
                "train": ori_data,
                "validation": ctrl_data,
            }
            # Setting metadata by train
            metadata = ori_metadata
            if "row_num" in metadata.metadata["global"]:
                metadata.metadata["global"]["row_num_after_split"] = metadata.metadata[
                    "global"
                ].pop("row_num")
            self.metadata = metadata
        else:
            data.reset_index(drop=True, inplace=True)  # avoid unexpected index

            self.index = self._index_bootstrapping(
                index=data.index.tolist(), exclude_index=exclude_index
            )

            for key, index in self.index.items():
                self.data[key] = {
                    "train": data.iloc[index["train"]].reset_index(drop=True),
                    "validation": data.iloc[index["validation"]].reset_index(drop=True),
                }

        if metadata is not None:
            self.metadata = metadata
            self.metadata.metadata["global"]["row_num_after_split"] = {
                "train": self.data[1]["train"].shape[0],
                "validation": self.data[1]["validation"].shape[0],
            }

    def _index_bootstrapping(
        self, index: list, exclude_index: list[int] = None
    ) -> dict[int, list[int]]:
        """
        Generate randomized index samples for splitting data.

        Args
            index (list)
                The index list of dataset which wait for split.
            exist_index (dict[int, list[int]])
                same as split()
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
