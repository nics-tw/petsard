import random
from typing import Dict, List, Optional, Union

import pandas as pd

from PETsARD.error import ConfigError


class Splitter:
    """
    Splitter is an independent module for Executor use.
    
    Included:
    a.) split input data via assigned ratio (train_split_ratio)
    b.) resampling assigned times (num_samples)
    c.) output their train/validation indexes (self.index_samples) and pd.DataFrame data (self.data)
    """
    DEFAULT_NUM_SAMPLES = 1
    DEFAULT_TRAIN_SPLIT_RATIO = 0.8

    def __init__(
        self,
        num_samples:       int = DEFAULT_NUM_SAMPLES,
        train_split_ratio: float = DEFAULT_TRAIN_SPLIT_RATIO,
        random_state:      Optional[Union[int, float, str]] = None
    ):
        """
        Args
            num_samples (int)
                Number of times to resample the data. Default is 1.
            train_split_ratio (float)
                Ratio of data to assign to the training set,
                must be a float between 0 ~ 1. Default is 0.8.
            random_state (int, float, str. Optional)
                Seed for random number generation. Default is None.
        """
        if not (0 <= train_split_ratio <= 1):
            raise ConfigError(
                "Splitter:  train_split_ratio must be a float between 0 and 1.")
        self.num_samples = num_samples
        self.train_split_ratio = train_split_ratio
        self.random_state = random_state

    def split(self, data: pd.DataFrame, exclude_index: List[int] = None):
        """
        Initialize the Splitter with data and perform index bootstrapping.
        than split the input data into train and validation sets
        based on the initialized index samples.
        ...
        Args
            data (pd.DataFrame)
                The dataset which wait for split.
            exclude_index (Dict[int, List[int]])
                The exist index we want to exclude them from our sampling.
                Just send the index from other Splitter is fine.
        """
        data.reset_index(drop=True, inplace=True)  # avoid unexpected index

        self.index = self._index_bootstrapping(
            index=data.index.tolist(),
            exclude_index=exclude_index
        )

        self.data: dict = {}
        for key, index in self.index.items():
            self.data[key] = {
                'train': data.iloc[index['train']].reset_index(drop=True),
                'validation': data.iloc[index['validation']].reset_index(drop=True)
            }

    def _index_bootstrapping(
        self,
        index: list,
        exclude_index: List[int] = None
    ) -> Dict[int, List[int]]:
        """
        Generate randomized index samples for splitting data.
        ...
        Args
            index (list)
                The index list of dataset which wait for split.
            exist_index (Dict[int, List[int]])
                same as split()
        """
        if self.random_state is not None:
            random.seed(self.random_state)

        sample_size = int(len(index) * self.train_split_ratio)

        sampled_seen = set()
        if exclude_index:  # external samples seen\
            sampled_seen.add(tuple(exclude_index))

        sampled_index = {}
        # assume max sampling time as num_sample.
        maxattempts = self.num_samples
        for n in range(self.num_samples):
            # re-calculate when success.
            attempts = 0
            while attempts < maxattempts:
                sampled_indices = tuple(
                    sorted(random.sample(index, sample_size))
                )

                if sampled_indices in sampled_seen:
                    attempts += 1
                else:
                    sampled_seen.add(sampled_indices)
                    sampled_index[n+1] = {
                        'train':      list(sampled_indices),
                        'validation': list(set(index) - set(sampled_indices))
                    }
                    break
                if attempts == maxattempts:
                    raise ConfigError(
                        f"Splitter: "
                        f"Unable to sample {self.num_samples} pairs of index "
                        f"with a ratio of {self.train_split_ratio} "
                        f"within {maxattempts} attempts due to collisions.\n"
                        f"Please review your data size "
                        f"and choose a suitable sampling ratio."
                    )
        return sampled_index
