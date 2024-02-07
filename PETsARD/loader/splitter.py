import random
from typing import Dict, Optional, Union

import pandas as pd


class Splitter:
    """
    Splitter is an independent module for Executor use. Incl.:
    a.) split input data via assigned ratio (train_split_ratio)
    b.) resampling assigned times (num_samples)
    c.) output their train/validation indexes (self.index_samples) and pd.DataFrame data (self.data)
    """

    def __init__(
        self,
        data:              pd.DataFrame,
        num_samples:       int = 1,
        train_split_ratio: float = 0.8,
        random_state:      Optional[Union[int, float, str]] = None
    ):
        self.index_samples = self._index_bootstrapping(
            index=data.index.tolist(),
            num_samples=num_samples,
            train_split_ratio=train_split_ratio,
            random_state=random_state
        )
        self.data = self._df_bootstrapping(data)

    def _index_bootstrapping(
            self,
            index:             list,
            num_samples:       int,
            train_split_ratio: float,
            random_state:      Optional[Union[int, float, str]]
    ):
        if random_state is not None:
            random.seed(random_state)

        sample_size = int(len(index) * train_split_ratio)
        # assume max sampling time as num_sample.
        maxattempts = num_samples
        samples_seen = set()
        results = {}
        for n in range(num_samples):
            # re-calculate when success.
            attempts = 0
            while attempts < maxattempts:
                sampled_indices = tuple(
                    sorted(random.sample(index, sample_size))
                )

                if sampled_indices in samples_seen:
                    attempts += 1
                else:
                    samples_seen.add(sampled_indices)
                    results[n+1] = {
                        'train':      list(sampled_indices),
                        'validation': list(set(index) - set(sampled_indices))
                    }
                    break
                if attempts == maxattempts:
                    raise ValueError(
                        f"Splitter - _index_sample_with_replacement: "
                        f"Unable to sample {num_samples} pairs of indexes "
                        f"with a ratio of {train_split_ratio} "
                        f"within {num_samples} attempts due to collisions.\n"
                        f"Please review your data size "
                        f"and choose a suitable sampling ratio."
                    )
        return results

    def _df_bootstrapping(self, data) -> Dict[str, pd.DataFrame]:
        results = {}
        for key, indices in self.index_samples.items():
            df_train = data.iloc[indices['train']]
            df_validation = data.iloc[indices['validation']]
            results[key] = {
                'train':      df_train.reset_index(drop=True),
                'validation': df_validation.reset_index(drop=True)
            }
        return results
