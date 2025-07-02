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
        max_overlap_ratio: Optional[float] = 1.0,
        max_attempts: Optional[int] = 30,
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
            max_overlap_ratio (float, optional):
                Maximum allowed overlap ratio between samples.
                Default is 1.0 (100%). Set to 0.0 for no overlap.
            max_attempts (int, optional):
                Maximum number of attempts for sampling. Default is 30.
            **kwargs (optional):
                For method 'custom_data' only. Apply Loader's config.

        Attr:
            config (dict):
                The configuration of Splitter.
                If method is None,
                    it contains num_samples, train_split_ratio, random_state, max_overlap_ratio, max_attempts.
                If method is 'custom_data',
                    it contains method, filepath, and Loader's config.

        """
        self.config: dict = {}

        # Normal Splitter use case
        if method is None:
            if not (0 <= train_split_ratio <= 1):
                raise ConfigError(
                    "Splitter:  train_split_ratio must be a float between 0 and 1."
                )
            if not (0 <= max_overlap_ratio <= 1):
                raise ConfigError(
                    "Splitter: max_overlap_ratio must be a float between 0 and 1."
                )
            self.config = {
                "num_samples": num_samples,
                "train_split_ratio": train_split_ratio,
                "random_state": random_state,
                "max_overlap_ratio": max_overlap_ratio,
                "max_attempts": max_attempts,
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
        exist_train_indices: list[set] = None,
    ) -> tuple[dict, dict, list[set]]:
        """
        Perform index bootstrapping on the Splitter-initialized data
            and split it into train and validation sets
            using the generated index samples.

        When method is 'custom_data', the data will be loaded from the filepath.

        Args:
            data (pd.DataFrame, optional): The dataset which wait for split.
            exist_train_indices (list[set], optional):
                The existing train index sets we want to avoid overlapping with.

        Returns:
            tuple[dict, dict, list[set]]:
                - Split data: {1: {train: pd.DataFrame, validation: pd.DataFrame}, 2: ...}
                - Metadata: {1: {train: SchemaMetadata, validation: SchemaMetadata}, 2: ...}
                - Train indices: [{train_indices_set1}, {train_indices_set2}, ...]
        """
        if "method" in self.config:
            # Custom data method - load from files
            ori_data, ori_metadata = self.loader["ori"].load()
            ctrl_data, _ = self.loader["control"].load()

            split_data = {
                1: {
                    "train": ori_data,
                    "validation": ctrl_data,
                }
            }

            # Create metadata for both train and validation
            train_metadata = self._update_metadata_with_split_info(
                ori_metadata, ori_data.shape[0], ctrl_data.shape[0]
            )
            validation_metadata = self._create_split_metadata(
                ori_data.shape[0], ctrl_data.shape[0]
            )

            metadata_dict = {
                1: {
                    "train": train_metadata,
                    "validation": validation_metadata,
                }
            }

            train_indices_list = [set(ori_data.index.tolist())]

        else:
            # Normal splitting method
            if data is None:
                raise ConfigError("Data must be provided for normal splitting method")

            data.reset_index(drop=True, inplace=True)  # avoid unexpected index

            index_result = self._bootstrapping(
                index=data.index.tolist(), exist_train_indices=exist_train_indices
            )

            split_data = {}
            metadata_dict = {}
            train_indices_list = []

            for key, index in index_result.items():
                split_data[key] = {
                    "train": data.iloc[index["train"]].reset_index(drop=True),
                    "validation": data.iloc[index["validation"]].reset_index(drop=True),
                }

                # Create metadata for both train and validation
                train_metadata = self._create_split_metadata(
                    len(index["train"]), len(index["validation"])
                )
                validation_metadata = self._create_split_metadata(
                    len(index["train"]), len(index["validation"])
                )

                metadata_dict[key] = {
                    "train": train_metadata,
                    "validation": validation_metadata,
                }

                train_indices_list.append(set(index["train"]))

        return split_data, metadata_dict, train_indices_list

    def get_train_indices(self) -> list[set]:
        """
        取得最後一次分割的訓練索引列表，用於向後相容性。

        Returns:
            list[set]: 訓練索引集合列表
        """
        # 這個方法主要用於向後相容，實際使用建議直接使用 split() 的返回值
        if hasattr(self, "_last_train_indices"):
            return self._last_train_indices
        return []

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

    def _bootstrapping(
        self, index: list, exist_train_indices: list[set] = None
    ) -> dict[int, dict[str, list[int]]]:
        """
        拔靴法生成隨機索引樣本用於資料分割。

        Args:
            index (list): 待分割資料集的索引列表
            exist_train_indices (list[set]): 現有的訓練索引集合列表，用於避免重疊
        """
        if self.config["random_state"] is not None:
            random.seed(self.config["random_state"])

        sample_size = int(len(index) * self.config["train_split_ratio"])

        # 初始化現有訓練索引集合列表
        existing_train_sets = []
        if exist_train_indices:
            existing_train_sets = [
                set(idx_set) if not isinstance(idx_set, set) else idx_set
                for idx_set in exist_train_indices
            ]

        sampled_index = {}

        for n in range(self.config["num_samples"]):
            attempts = 0
            while attempts < self.config["max_attempts"]:
                sampled_indices = set(random.sample(index, sample_size))

                # 檢查是否與現有訓練集合重疊過多
                if self._check_overlap_acceptable(sampled_indices, existing_train_sets):
                    # 將當前樣本加入現有訓練集合列表，供後續比較使用
                    existing_train_sets.append(sampled_indices)

                    sampled_index[n + 1] = {
                        "train": list(sampled_indices),
                        "validation": list(set(index) - sampled_indices),
                    }
                    break

                attempts += 1

            if attempts == self.config["max_attempts"]:
                raise ConfigError(
                    f"Splitter: "
                    f"Unable to sample {self.config['num_samples']} pairs of index "
                    f"with a ratio of {self.config['train_split_ratio']} "
                    f"and max overlap ratio of {self.config['max_overlap_ratio']:.1%} "
                    f"within {self.config['max_attempts']} attempts.\n"
                    f"Consider reducing num_samples, increasing max_overlap_ratio, "
                    f"or increasing max_attempts."
                )
        return sampled_index

    def _check_overlap_acceptable(
        self, new_train_sample: set, existing_train_sets: list[set]
    ) -> bool:
        """
        檢查新訓練樣本與現有訓練集合的重疊是否可接受。

        Args:
            new_train_sample (set): 新的訓練樣本索引集合
            existing_train_sets (list[set]): 現有的訓練索引集合列表

        Returns:
            bool: 如果重疊可接受則返回 True，否則返回 False
        """
        max_overlap_ratio = self.config["max_overlap_ratio"]

        for existing_train_set in existing_train_sets:
            # 1. 檢查是否完全一致
            if new_train_sample == existing_train_set:
                return False

            # 2. 檢查重疊比率是否超過限制
            if max_overlap_ratio < 1.0:  # 只有在不是 100% 時才檢查
                overlap_size = len(new_train_sample.intersection(existing_train_set))
                overlap_ratio = overlap_size / len(new_train_sample)

                if overlap_ratio > max_overlap_ratio:
                    return False

        return True
