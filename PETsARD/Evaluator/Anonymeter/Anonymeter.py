import time
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
    Union
)
import warnings

import numpy as np
import pandas as pd


class Anonymeter():
    """
    Base class for all "Evaluator".

    The "Evaluator" class defines the common API
    that all the "Evaluator" need to implement, as well as common functionality.

    ...

    Args:
        data (dict)
            Following data logic defined in Evaluator.

        anonymeter_n_attacks (int):
            The number of attack attempts within the specified attack method.
            Default is 2,000.

        anonymeter_n_neighbors (int):
            Specifies the number of jobs Anonymeter will use.
            -1 means all threads except one.
            -2 means every thread.
            Default is -2.

        anonymeter_n_neighbors (int):
            Sets the number of nearest neighbors to consider for each entry in the search.
            Default is 1. Indicating a successful linkability attack
                only if the closest synthetic record matches
                for both split original records."

        anonymeter_aux_cols (Tuple[List[str], List[str]]):
            Tuple of two lists of strings.
            Features of the records that are given to
                the attacker as auxiliary information.
            Optional.
            The Anonymeter documentation states it supports 'tuple of int',
                but this is not reflected in their type annotations,
                so we will omit it here and only mention this for reference.

        anonymeter_secret (str | List[str]]):
            The secret attribute(s) of the target records, unknown to the attacker.
                This is what the attacker will try to guess.
            Optional.

    ...
    Returns:
        None

    ...
    TODO n_attacks recommendation based on the conclusions of Experiment 1.

    """

    def __init__(self,
                 data: Dict[str, pd.DataFrame],
                 anonymeter_n_attacks:   int = 2000,
                 anonymeter_n_jobs:      int = -2,
                 anonymeter_n_neighbors: int = 1,
                 anonymeter_aux_cols:    Tuple[List[str], List[str]] = None,
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
        eval() of Anonymeter.
            Defines the sub-evaluator and suppresses specific warnings
            due to known reasons from the Anonymeter library

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
                time_start = time.time()

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
                        f"{round(time.time()-time_start ,4)} sec."
                    )
                self.evaluation = self._extract_result()
            else:
                raise ValueError(
                    f"Evaluator (Anonymeter): .eval() "
                    f"while _Evaluator didn't ready."
                )

    def _extract_result(self) -> dict:
        """
        _extract_result of Anonymeter.
            Uses .risk()/.results() method in Anonymeter
            to extract result from self._Evaluator into the designated dictionary.

        ...
        Return
            (dict)
                Contains the following key-value pairs

                Risk (float)
                    Privacy Risk value of specified attacks.
                    Ranging from 0 to 1.
                    A value of 0 indicates no risk, and 1 indicates full risk.
                    Includes CI_btm and CI_top for the bottom and top of the confidence interval.

                Attack_Rate (float)
                    Main attack rate of specified attacks,
                        which the attacker uses the synthetic dataset
                        to deduce private information of records
                        in the original/training dataset.
                    Ranging from 0 to 1.
                    A value of 0 indicates none of success attack,
                        and 1 indicates totally success attack.
                    Includes _err for its error rate.

                Baseline_Rate (float)
                    Naive, or Baseline attack rate of specified attacks,
                        which is carried out based on random guessing,
                        to provide a baseline against
                        which the strength of the “main” attack can be compared.
                    Ranging from 0 to 1.
                    A value of 0 indicates none of success attack,
                        and 1 indicates totally success attack.
                    Includes _err for its error rate.

                Control_Rate (float)
                    Control attack rate of specified attacks,
                        which is conducted on a set of control dataset,
                        to distinguish the concrete privacy risks
                        of the original data records (i.e., specific information)
                        from general risks intrinsic
                        to the whole population (i.e., generic information).
                    Ranging from 0 to 1.
                    A value of 0 indicates none of success attack,
                        and 1 indicates totally success attack.
                    Includes _err for its error rate.

        ...

        TODO  Consider using alternative methods to extract results
                and evaluate migrating this functionality to the Reporter.

        """
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
                dict_result[key] = eval_instance
            except Exception as ex:
                pass
        return dict_result


class AnonymeterMethodMap():
    """
    map of Anonymeter
    ...
    TODO Consider YAML
    """
    method_map = {
        'singlingout - univariate':   0,
        'singlingout - multivariate': 1,
        'linkability':                2,
        'inference':                  3
    }

    @classmethod
    def map(cls, method_name: str) -> int:
        """
        mapping method and handle exception
        """
        try:
            return cls.method_map[method_name.lower()]
        except KeyError as ex:
            print(
                f"Evaluator (Anonymeter): Method "
                f"{method_name} not recognized.\n"
                f"{ex}"
            )
