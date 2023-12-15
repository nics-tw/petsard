class Splitter:
    def __init__(self, data, num_samples=1, train_split_ratio=0.8, random_state=None):
        self.index_samples = self._index_bootstrapping(index=data.index.tolist(
        ), num_samples=num_samples, train_split_ratio=train_split_ratio, random_state=random_state)
        self.data = self._df_bootstrapping(data)

    def _index_bootstrapping(self, index, num_samples, train_split_ratio, random_state):
        import random
        from collections import Counter

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
                    results[_n] = {'train': list(_sampled_indices), 'validation': list(set(index) - set(_sampled_indices))
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

    def _sample(df_data, sample_ratio=0.8, random_state=None):
        __idx_train = df_data.sample(
            frac=sample_ratio, random_state=random_state).index
        __idx_validation = df_data.drop(__idx_train).index

        __df_train = df_data.loc[__idx_train].reset_index(drop=True)
        __df_validation = df_data.loc[__idx_validation].reset_index(drop=True)
        return __df_train, __df_validation, __idx_train, __idx_validation