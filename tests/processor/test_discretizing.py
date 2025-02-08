import random

import numpy as np
import pandas as pd

from petsard.processor.discretizing import DiscretizingKBins


class Test_Discretizing:
    def test_inverse_transform_with_na(self):
        """
        Test case for `inverse_transform` method of `DiscretizingKBins` class.
            - for issue 440

        - DiscretizingKBins will successfully return a inverse transformation when:
            - with np.nan
            - with pd.NA
            - with None
        """
        n_samples: int = 100
        sample_data: pd.Series = pd.Series(
            [random.choice([0, 1, 2, 3]) for _ in range(n_samples)],
        )
        modified_data: pd.Series = sample_data.copy()
        data_dict: dict = {
            "with np.nan": {
                "na_ratio": 0.25,
                "value": np.nan,
            },
            "with pd.NA": {
                "na_ratio": 0.25,
                "value": pd.NA,
            },
            "with None": {
                "na_ratio": 0.25,
                "value": None,
            },
        }

        n_replace: int = None
        indices_to_replace: list = None
        postproc_data: pd.Series = None

        proc = DiscretizingKBins()
        proc.fit(sample_data)
        for setting in data_dict.values():
            n_replace = int(n_samples * setting["na_ratio"])
            indices_to_replace = random.sample(list(sample_data.index), n_replace)
            modified_data.iloc[indices_to_replace] = setting["value"]

            postproc_data = pd.Series(proc.inverse_transform(modified_data).ravel())
            assert postproc_data.isna().sum() == 0

            modified_data = sample_data.copy()
