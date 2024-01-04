import numpy as np
import pandas as pd
import time
from typing import Dict, List, Optional, Union
import warnings


class Anonymeter():

    def __init__(self,
                 data: Dict[str, pd.DataFrame],
                 anonymeter_n_attacks:   int = 2000,
                 anonymeter_n_jobs:      int = -2,
                 anonymeter_n_neighbors: int = 10,
                 anonymeter_aux_cols:    Optional[List[List[str]]] = None,
                 anonymeter_secret:      Optional[Union[str,
                                                        List[str]]] = None,
                 **kwargs
                 ):
        dataattr = {
            'data_ori':     ('ori',     None),
            'data_syn':     ('syn',     None),
            'data_control': ('control', None)
        }
        for attr, (key, default) in dataattr.items():
            value = data.get(key, default)
            setattr(self, attr, value)

        self.n_attacks = anonymeter_n_attacks
        self.n_jobs = anonymeter_n_jobs
        self.n_neighbors = anonymeter_n_neighbors
        self.aux_cols = anonymeter_aux_cols
        self.secret = anonymeter_secret

        self.eval_method = 'Unknown'

    def eval(self):
        """
        ...

        Exception:

            FutureWarning:
                anonymeter\evaluators\singling_out_evaluator.py:97:
                    FutureWarning: is_categorical_dtype is deprecated
                    and will be removed in a future version.
                    Use isinstance(dtype, CategoricalDtype)
                    instead elif is_categorical_dtype(values).

            UserWarning
                anonymeter\stats\confidence.py:215:
                    UserWarning: Attack is as good or worse as baseline model.
                    Estimated rates: attack = 0.30674239114619767,
                    baseline = 0.30773856438771213.
                    Analysis results cannot be trusted. self._sanity_check()

        """
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=FutureWarning)
            warnings.simplefilter("ignore", category=UserWarning)

            if self._Evaluator:
                _time_start = time.time()

                print(
                    f"Evaluator (Anonymeter): Evaluating  {self.eval_method}."
                )

                _eval_method_num = AnonymeterMethodMap.map(self.eval_method)
                if _eval_method_num in [0, 1]:
                    _mode = (
                        'univariate' if _eval_method_num == 0
                        else 'multivariate'
                    )
                    try:
                        self._Evaluator.evaluate(mode=_mode)
                    except RuntimeError as ex:
                        print(
                            f"Evaluator (Anonymeter): Singling out "
                            f"evaluation failed with {ex}."
                            f"\n                        "
                            f"Please re-run this cell. "
                            f"For more stable results increase `n_attacks`."
                            f"Note that this will make the evaluation slower."
                        )
                else:
                    self._Evaluator.evaluate(n_jobs=self.n_jobs)
                    print(
                        f"Evaluator (Anonymeter): "
                        f"Evaluating {self.eval_method} spent "
                        f"{round(time.time()-_time_start ,4)} sec."
                    )
                self.evaluation = self._extract_result()
            else:
                raise ValueError(
                    f"Evaluator (Anonymeter): .eval() "
                    f"while _Evaluator didn't ready."
                )

    def _extract_result(self):
        dict_result = {}
        para_to_handle = [
            ('Risk',              ['risk()',    'value']),
            ('Risk_CI_btm',       ['risk()',    'ci[0]']),
            ('Risk_CI_top',       ['risk()',    'ci[1]']),
            ('Attack_Rate',       ['results()', 'attack_rate',   'value']),
            ('Attack_Rate_err',   ['results()', 'attack_rate',   'error']),
            ('Baseline_Rate',     ['results()', 'baseline_rate', 'value']),
            ('Baseline_Rate_err', ['results()', 'baseline_rate', 'error']),
            ('Control_Rate',      ['results()', 'control_rate',  'value']),
            ('Control_Rate_err',  ['results()', 'control_rate',  'error'])
        ]

        for key, evals in para_to_handle:
            dict_result[key] = np.nan
            try:
                eval_instance = self._Evaluator
                for eval_command in evals:
                    if '()' in eval_command:
                        method_name = eval_command.split('(')[0]
                        if hasattr(eval_instance, method_name):
                            method = getattr(eval_instance, method_name)
                            if callable(method):
                                eval_instance = method()
                            else:
                                break
                        else:
                            break
                    elif '[' in eval_command:
                        attr_name = eval_command.split('[')[0]
                        index = int(eval_command.split('[')[1].rstrip(']'))
                        if hasattr(eval_instance, attr_name):
                            attr = getattr(eval_instance, attr_name)
                            if isinstance(attr, (list, dict, tuple)):
                                try:
                                    eval_instance = attr[index]
                                except (IndexError, KeyError):
                                    break
                        else:
                            break
                    else:
                        eval_instance = getattr(eval_instance, eval_command)
                dict_result[key] =eval_instance
            except Exception as ex:
                pass
        return dict_result


class AnonymeterMethodMap():
    method_map = {
        'singlingout - univariate':   0,
        'singlingout - multivariate': 1,
        'linkability':                2,
        'inference':                  3
    }

    @classmethod
    def map(cls, method_name: str) -> int:
        try:
            return cls.method_map[method_name.lower()]
        except KeyError as ex:
            print(
                f"Evaluator (Anonymeter): Method "
                f"{method_name} not recognized.\n"
                f"{ex}"
            )
