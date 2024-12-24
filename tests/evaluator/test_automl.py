import random
from typing import Dict
import warnings

import numpy as np
import pandas as pd
import pytest

from petsard.evaluator import AutoML


# shared evaluation data
@pytest.fixture
def sample_evaluator_input():
    def _data_creator(n: int = 100) -> pd.DataFrame:
        data: pd.DataFrame = pd.DataFrame(data={
            'y_cont_normal': np.random.rand(n),
            'y_cont_uniform': np.random.uniform(size=n),
            'y_discr_num_same': np.ones(n),
            'y_discr_str_same': ['value1']*n,
            'y_discr_int_low_card': np.random.randint(0, 2, size=n),
            'y_discr_int_high_card': np.random.randint(0, 15, size=n),
            'y_discr_str_low_card': [random.choice([
                f'value{i}' for i in range(3)]) for _ in range(n)],
            'y_discr_str_high_card': [random.choice([
                f'value{i}' for i in range(16)]) for _ in range(n)],
        })
        return data

    def _sample_evaluator_input(
        case: Dict[str, int] = None,
    ) -> dict:
        default_case: Dict[str, int] = {
            'ori': 100,
            'syn': 100,
            'control': 100,
        }
        if case is not None:
            default_case.update(case)
        case = default_case

        data: dict = {}
        for key, n in case.items():
            if key != 'testcase':
                data[key] = _data_creator(n).copy()

        if 'testcase' in case:
            if case['testcase'] in [
                'only_1_level_y_in_ori',
                'only_1_level_y_in_syn',
                'only_1_level_y_both_ori_syn'
            ]:
                same: str = 'y_discr_str_same'
                non_same: str = 'y_discr_str_low_card'
                data['control'].loc[:,'unmatch_discr'] = data['control'][non_same]
                if case['testcase'] == 'only_1_level_y_in_ori':
                    data['ori'].loc[:,'unmatch_discr'] = data['ori'][same]
                    data['syn'].loc[:,'unmatch_discr'] = data['syn'][non_same]
                elif case['testcase'] == 'only_1_level_y_in_syn':
                    data['ori'].loc[:,'unmatch_discr'] = data['ori'][non_same]
                    data['syn'].loc[:,'unmatch_discr'] = data['syn'][same]
                elif case['testcase'] == 'only_1_level_y_both_ori_syn':
                    data['ori'].loc[:,'unmatch_discr'] = data['ori'][same]
                    data['syn'].loc[:,'unmatch_discr'] = data['syn'][same]
        return data
    return _sample_evaluator_input


class Test_automl:

    def test_classification_of_single_value(self, sample_evaluator_input):
        """
        Test case for `create()` function of _classification class.
            - for issue 430

        - AutoML will successfully return a report when:
            - the target of syn have only 1 level.
        """
        # ...\petsard\petsard\evaluator\automl.py:364:
        #   UserWarning: Only one class in the target,
        #   the model training is impossible. The score is set to NaN.
        warnings.simplefilter("ignore", UserWarning)

        for testcase in [
            'only_1_level_y_in_ori',
            'only_1_level_y_in_syn',
            'only_1_level_y_both_ori_syn',
        ]:
            eval = AutoML(config={
                'method': 'automl-classification',
                'target': 'unmatch_discr',
            })
            eval.create(data=sample_evaluator_input(case={'testcase': testcase,}))
            eval.eval()
            result = eval.get_global()

            if testcase in [
                'only_1_level_y_in_ori',
                'only_1_level_y_both_ori_syn']:
                assert pd.isna(result.loc[0,'ori_mean'])
                assert pd.isna(result.loc[0,'ori_std'])
            else:
                assert result.loc[0,'ori_mean'] >= 0.0
                assert result.loc[0,'ori_std'] >= 0.0

            if testcase in [
                'only_1_level_y_in_syn',
                'only_1_level_y_both_ori_syn']:
                assert pd.isna(result.loc[0,'syn_mean'])
                assert pd.isna(result.loc[0,'syn_std'])
            else:
                assert result.loc[0,'syn_mean'] >= 0.0
                assert result.loc[0,'syn_std'] >= 0.0

            assert pd.isna(result.loc[0,'pct_change'])
