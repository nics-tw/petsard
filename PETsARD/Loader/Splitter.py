class Splitter:
    """
    Splitter is an independent module for Executor use. Incl.:
    a.) split input data via assigned ratio (train_split_ratio)
    b.) resampling assigned times (num_samples)
    c.) output their train/validation indexes (self.index_samples) and pd.DataFrame data (self.data)
    """
    def __init__(self, data, num_samples=1, train_split_ratio=0.8, random_state=None):
        self.index_samples = self._index_bootstrapping(index=data.index.tolist(
        ), num_samples=num_samples, train_split_ratio=train_split_ratio, random_state=random_state)
        self.data = self._df_bootstrapping(data)

    def _index_bootstrapping(self, index, num_samples, train_split_ratio, random_state):
        import random

        if random_state is not None:
            random.seed(random_state)

        _sample_size = int(len(index) * train_split_ratio)
        _max_attempts = num_samples  # assume max sampling time as num_sample.
        _samples_seen = set()
        results = {}
        for _n in range(num_samples):
            _attempts = 0  # re-calculate when success.
            while _attempts < _max_attempts:
                _sampled_indices = tuple(
                    sorted(random.sample(index, _sample_size)))

                if _sampled_indices in _samples_seen:
                    _attempts += 1
                else:
                    _samples_seen.add(_sampled_indices)
                    results[_n+1] = {'train': list(_sampled_indices), 'validation': list(set(index) - set(_sampled_indices))
                                     }
                    break
                if _attempts == _max_attempts:
                    raise ValueError(
                        f"Splitter - _index_sample_with_replacement: Unable to sample {num_sample} pairs of indexes with a ratio of {sample_ratio} within {num_sample} attempts due to collisions."
                        f"Please review your data size and choose a suitable sampling ratio."
                    )
        return results

    def _df_bootstrapping(self, data):
        results = {}
        for key, indices in self.index_samples.items():
            results[key] = {'train': data.iloc[indices['train']].reset_index(
                drop=True), 'validation': data.iloc[indices['validation']].reset_index(drop=True)}
        return results
