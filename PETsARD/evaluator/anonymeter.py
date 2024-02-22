import re
import time
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
    Union
)
import warnings

from anonymeter.evaluators import (
    SinglingOutEvaluator,
    LinkabilityEvaluator,
    InferenceEvaluator
)
import numpy as np
import pandas as pd

from PETsARD.error import UnfittedError, UnsupportedEvalMethodError


class AnonymeterMap():
    """
    map of Anonymeter
    """
    SINGLINGOUT_UNIVARIATE:   int = 1
    # SINGLINGOUT_MULTIVARIATE: int = 2
    LINKABILITY:              int = 3
    INFERENCE:                int = 4

    @classmethod
    def map(cls, method: str) -> int:
        """
        Get suffixes mapping int value

        Args:
            method (str): evaluating method

        Return:
            (int): The method code.
        """
        try:
            return cls.__dict__[
                re.sub(r"^anonymeter-", "", method).upper()
            ]
        except KeyError:
            raise UnsupportedEvalMethodError


class AnonymeterFactory:
    """
    Factory for "Anonymeter" Evaluator.

    AnonymeterFactory defines which module to use within Anonymeter.
    """

    def __init__(self, **kwargs):
        method: str = kwargs.get('method', None)
        method_code = AnonymeterMap(method) # self.config['method']

        if method_code == AnonymeterMap.SINGLINGOUT_UNIVARIATE:
            self.evaluator = AnonymeterSinglingOutUnivariate()
        # elif method_code == AnonymeterMap.SINGLINGOUT_MULTIVARIATE:
        #     self.evaluator = AnonymeterSinglingOutMultivariate()
        elif method_code == AnonymeterMap.LINKABILITY:
            self.evaluator = AnonymeterLinkability()
        elif method_code == AnonymeterMap.INFERENCE:
            self.evaluator = AnonymeterInference()
        else:
            raise UnsupportedEvalMethodError

    def create(self):
        """
        create()
            return the Evaluator which selected by Factory.
        """
        return self.evaluator


class Anonymeter():
    """
    Base class for all "Anonymeter".
        The "Anonymeter" class defines the common API
        that all the "Anonymeter" need to implement, as well as common functionality.

    Args:
        data (dict): Following data logic defined in Evaluator.
        anonymeter_n_attacks (int): The number of attack attempts using the specified attack method. Default is 2,000.
        anonymeter_n_neighbors (int): Specifies the number of jobs Anonymeter will use.
            -1 means all threads except one. -2 means every thread. Default is -2.
        anonymeter_n_neighbors (int):
            Sets the number of nearest neighbors to consider for each entry in the search.
            Indicating a successful linkability attack
            only if the closest synthetic record matches for both split original records.
            Default is 1.
        anonymeter_aux_cols (Tuple[List[str], List[str]], Optional):
            Features of the records that are given to the attacker as auxiliary information.
            The Anonymeter documentation states it supports 'tuple of int',
                but this is not reflected in their type annotations,
                so we will omit it here and only mention this for reference.
        anonymeter_secret (str | List[str]], Optional):
            The secret attribute(s) of the target records, unknown to the attacker.
                This is what the attacker will try to guess.

    TODO n_attacks recommendation based on the conclusions of Experiment 1.
    TODO Consider use nametupled to replace "data" dict for more certain requirement
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
        self.data_ori = data['ori']
        self.data_syn = data['syn']
        self.data_control = data['control']

        self.n_attacks = anonymeter_n_attacks
        self.n_jobs = anonymeter_n_jobs
        self.n_neighbors = anonymeter_n_neighbors
        self.aux_cols = anonymeter_aux_cols
        self.secret = anonymeter_secret

        self.eval_method = 'Unknown'

    def eval(self):
        """
        Evaluates the privacy risk of the synthetic dataset.

        Defines the sub-evaluator and suppresses specific warnings
            due to known reasons from the Anonymeter library:

            FutureWarning:
                anonymeter\evaluators\singling_out_evaluator.py:97:
                    FutureWarning: is_categorical_dtype is deprecated
                    and will be removed in a future version.
                    Use isinstance(dtype, CategoricalDtype)
                    instead elif is_categorical_dtype(values).

            UserWarning
                anonymeter\stats\confidence.py:215:
                    UserWarning: Attack is as good or worse as baseline model.
                    Estimated rates: attack = ...{float}... ,
                    baseline = ...{float}... .
                    Analysis results cannot be trusted. self._sanity_check()

        """
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=FutureWarning)
            warnings.simplefilter("ignore", category=UserWarning)

            if self._evaluator:
                time_start = time.time()

                print(
                    f"Evaluator (Anonymeter): Evaluating  {self.eval_method}."
                )

                _eval_method_num = AnonymeterMap.map(self.config['method'])
                if _eval_method_num in [0, 1]:
                    _mode = (
                        'univariate' if _eval_method_num == 0
                        else 'multivariate'
                    )
                    try:
                        self._evaluator.evaluate(mode=_mode)
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
                    self._evaluator.evaluate(n_jobs=self.n_jobs)
                    print(
                        f"Evaluator (Anonymeter): "
                        f"Evaluating {self.eval_method} spent "
                        f"{round(time.time()-time_start ,4)} sec."
                    )
                self.evaluation = self._extract_result()
            else:
                raise UnfittedError

    def _extract_result(self) -> dict:
        """
        _extract_result of Anonymeter.
            Uses .risk()/.results() method in Anonymeter
            to extract result from self._evaluator into the designated dictionary.

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
                eval_instance = self._evaluator
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


class AnonymeterSinglingOutUnivariate(Anonymeter):
    """
    Estimation of the SinglingOut attacks of Univariate in the Anonymeter library.

    Returns:
        None. Stores the result in self._evaluator.evaluation.

    TODO SinglingOut attacks of Multi-variate.
    """

    def __init__(self,   **kwargs):
        super().__init__(**kwargs)
        self.eval_method: str = 'SinglingOut - Univariate'

        _time_start = time.time()
        print(
            f"Evaluator (Anonymeter - SinglingOut - Univariate): "
            f"Now is SinglingOut - Univariate Evaluator"
        )

        self._evaluator = SinglingOutEvaluator(
            ori=self.data_ori,
            syn=self.data_syn,
            control=self.data_control,
            n_attacks=self.n_attacks
        )
        print(
            f"Evaluator (Anonymeter - SinglingOut - Univariate): "
            f"Evaluator time: {round(time.time()-_time_start ,4)} sec."
        )


class AnonymeterLinkability(Anonymeter):
    """
    Estimation of the Linkability attacks in the Anonymeter library.

    Returns:
        None. Stores the result in self._evaluator.evaluation.
    """

    def __init__(self,   **kwargs):
        super().__init__(**kwargs)
        self.eval_method: str = 'Linkability'

        _time_start = time.time()
        print(
            f"Evaluator (Anonymeter - Linkability): "
            f"Now is Linkability Evaluator"
        )

        _str_aux_cols = (
            f"\n                                      and "
            .join(f"[{', '.join(row)}]" for row in self.aux_cols)
        )
        print(
            f"Evaluator (Anonymeter - Linkability): "
            f"aux_cols are {_str_aux_cols}."
        )

        self._evaluator = LinkabilityEvaluator(
            ori=self.data_ori,
            syn=self.data_syn,
            control=self.data_control,
            n_attacks=self.n_attacks,
            n_neighbors=self.n_neighbors,
            aux_cols=self.aux_cols
        )
        print(
            f"Evaluator (Anonymeter - Linkability): Evaluator time: "
            f"{round(time.time()-_time_start ,4)} sec."
        )


class AnonymeterInference(Anonymeter):
    """
    Estimation of the Inference attacks in the Anonymeter library.

    Returns:
        None. Stores the result in self._evaluator.evaluation.

    TODO Currently, it calculates a single column as the secret.
            According to the paper, consider handling multiple secrets.
    """

    def __init__(self,   **kwargs):
        super().__init__(**kwargs)
        self.eval_method: str = 'Inference'

        _time_start = time.time()
        print('Evaluator (Anonymeter - Inference): Now is Inference Evaluator')

        _aux_cols = [
            col for col in self.data_syn.columns if col != self.secret
        ]

        self._evaluator = InferenceEvaluator(
            ori=self.data_ori,
            syn=self.data_syn,
            control=self.data_control,
            aux_cols=_aux_cols,
            secret=self.secret
        )

        print(
            f"Evaluator (Anonymeter - Inference): Evaluator time: "
            f"{round(time.time()-_time_start ,4)} sec."
        )
