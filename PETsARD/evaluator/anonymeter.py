from abc import abstractmethod
import re
from typing import (
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

from PETsARD.evaluator.evaluator_base import EvaluatorBase
from PETsARD.error import UnableToEvaluateError, UnfittedError, UnsupportedEvalMethodError


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


class Anonymeter(EvaluatorBase):
    """
    Factory for "Anonymeter" Evaluator.
        AnonymeterFactory defines which module to use within Anonymeter.

    TODO n_attacks recommendation based on the conclusions of Experiment 1.
    TODO Consider use nametupled to replace "data" dict for more certain requirement
    """

    def __init__(self, config: dict):
        """
        Args:
            config (dict): A dictionary containing the configuration settings.
                - method (str): The method of how you evaluating data.
                - n_attack (int):
                    The number of attack attempts using the specified attack method.
                    Default is 2,000.
                - n_jobs (int, Optional): Specifies the number of jobs Anonymeter will use.
                    -1 means all threads except one. -2 means every thread.
                    Default is -2.
                - n_neighbors (int, Optional):
                    Sets the number of nearest neighbors to consider for each entry in the search.
                    Indicating a successful linkability attack only if
                    the closest synthetic record matches for both split original records.
                    Default is 1.
                - aux_cols (Tuple[List[str], List[str]], Optional):
                    Features of the records that are given to the attacker as auxiliary information.
                    The Anonymeter documentation states it supports 'tuple of int',
                    but this is not reflected in their type annotations,
                    so we will omit it here and only mention this for reference.
                - secret (str | List[str]], Optional):
                    The secret attribute(s) of the target records, unknown to the attacker.
                    This is what the attacker will try to guess.

        Attr:
            config (dict):
                A dictionary containing the configuration settings.
            data (Dict[str, pd.DataFrame]):
                A dictionary to store evaluation data. Default is an empty.
            result (dict):
                A dictionary to store the result of the description/evaluation. Default is an empty.
            evaluator (Anonymeter):
                Anonymeter class for implementing the Anonymeter.
        """
        super().__init__(config=config)

        default_config = {
            'n_attacks': 2000,  # int
            'n_jobs': -2,      # int
            'n_neighbors': 1,  # int
            'aux_cols': None,  # Tuple[List[str], List[str]]
            'secret': None,    # Optional[Union[str, List[str]]]
        }
        for key, value in default_config.items():
            config.setdefault(key, value)
        self.evaluator = None

    def create(self, data: dict) -> None:
        """
        Create a new instance of the anonymeter class with the given data.

        Args:
            data (dict): The data to be stored in the anonymeter instance.

        Resurn:
            None. Anonymeter class store in self.evaluator.

        TODO SinglingOut attacks of Multi-variate.
        """
        self.data = data

        method_code = AnonymeterMap.map(self.config['method'])

        if method_code == AnonymeterMap.SINGLINGOUT_UNIVARIATE:
            self.config['singlingout_mode'] = 'univariate'
            self.evaluator = SinglingOutEvaluator(
                ori=self.data['ori'],
                syn=self.data['syn'],
                control=self.data['control'],
                n_attacks=self.config['n_attacks']
            )
        # elif method_code == AnonymeterMap.SINGLINGOUT_MULTIVARIATE:
        #     self.config['singlingout_mode'] = 'multivariate'
        #     self.evaluator = SinglingOutEvaluator(
        #         ori=self.data['ori'],
        #         syn=self.data['syn'],
        #         control=self.data['control'],
        #         n_attacks=self.config['n_attacks']
        #     )
        elif method_code == AnonymeterMap.LINKABILITY:
            self.evaluator = LinkabilityEvaluator(
                ori=self.data['ori'],
                syn=self.data['syn'],
                control=self.data['control'],
                n_attacks=self.config['n_attacks'],
                n_neighbors=self.config['n_neighbors'],
                aux_cols=self.config['aux_cols']
            )
        elif method_code == AnonymeterMap.INFERENCE:
            aux_cols = [
                col for col in self.data_syn.columns if col != self.secret
            ]
            self.evaluator = InferenceEvaluator(
                ori=self.data['ori'],
                syn=self.data['syn'],
                control=self.data['control'],
                n_attacks=self.config['n_attacks'],
                aux_cols=aux_cols,
                secret=self.config['secret']
            )
        else:
            raise UnsupportedEvalMethodError

    def eval(self) -> None:
        """
        Evaluate the anonymization process.

        Keep the known warnings from the Anonymeter library:
            UserWarning: anonymeter\stats\confidence.py:215:
                UserWarning: Attack is as good or worse as baseline model.
                Estimated rates: attack = ...{float}... ,
                baseline = ...{float}... .
                Analysis results cannot be trusted. self._sanity_check()
            - warnings.simplefilter("ignore", category=UserWarning)

        Inhited the known warnings from the Anonymeter SinglingOut:
            FutureWarning: anonymeter\evaluators\singling_out_evaluator.py:97:
                FutureWarning: is_categorical_dtype is deprecated
                and will be removed in a future version.
                Use isinstance(dtype, CategoricalDtype)
                instead elif is_categorical_dtype(values).

        Exception:
            UnfittedError: If the anonymeter has not been create() yet.
        """
        if self.evaluator:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=FutureWarning)
                try:
                    if self.config['singlingout_mode'] == 'univariate':
                        # SinglingOut attacks of Univariate
                        self.evaluator.evaluate(mode=self.config['singlingout_mode'])
                    else:
                        # Linkability and Inference
                        self.evaluator.evaluate(n_jobs=self.config['n_jobs'])
                except RuntimeError:
                    # Please re-run this cell.
                    # "For more stable results increase `n_attacks`.
                    # Note that this will make the evaluation slower.
                    raise UnableToEvaluateError
        else:
            raise UnfittedError
        self._extract_result()

    def _extract_result(self) -> dict:
        """
        _extract_result of Anonymeter.
            Uses .risk()/.results() method in Anonymeter
            to extract result from self._evaluator into the designated dictionary.

        Return
            None. Result contains in self.result as following key-value pairs
            - risk (float)
                Privacy Risk value of specified attacks. Ranging from 0 to 1.
                    A value of 0 indicates no risk, and 1 indicates full risk.
                Includes risk_ci_btm and risk_ci_top
                    for the bottom and top of the confidence interval.
            - attack_Rate (float)
                Main attack rate of specified attacks, which the attacker
                    uses the synthetic datase to deduce private information of records
                    in the original/training dataset. Ranging from 0 to 1.
                A value of 0 indicates none of success attack,
                    and 1 indicates totally success attack.
                Includes attack_Rate_err for its error rate.
            - baseline_Rate (float)
                Naive, or Baseline attack rate of specified attacks, which is
                    carried out based on random guessing, to provide a baseline against
                    which the strength of the “main” attack can be compared.
                    Ranging from 0 to 1.
                A value of 0 indicates none of success attack,
                    and 1 indicates totally success attack.
                Includes baseline_Rate_err for its error rate.
            - control_Rate (float)
                Control attack rate of specified attacks,  hich is conducted on
                    a set of control dataset, to distinguish the concrete privacy risks
                    of the original data records (i.e., specific information)
                    from general risks intrinsic to the whole population (i.e., generic information).
                    Ranging from 0 to 1.
                A value of 0 indicates none of success attack,
                    and 1 indicates totally success attack.
                Includes control_Rate_err for its error rate.
        """
        def _safe_round(value, digits=6):
            """
            Safely rounds a given value to the specified number of digits.

            Args:
                value (float): The value to be rounded.
                digits (int, optional): The number of digits to round to. Defaults to 6.

            Returns:
                float or None: The rounded value, or None if an exception occurs.
            """
            try:
                return round(value, digits)
            except Exception:
                return pd.NA

        # Handle the risk
        try:
            risk = self.evaluator.risk()
            self.result['risk'] = _safe_round(risk.value)
            self.result['risk_CI_btm'] = _safe_round(risk.ci[0])
            self.result['risk_CI_top'] = _safe_round(risk.ci[1])
        except Exception:
            self.result['risk'] = pd.NA
            self.result['risk_CI_btm'] = pd.NA
            self.result['risk_CI_top'] = pd.NA

        # Handle the attack_rate, baseline_rate, control_rate
        try:
            results = self.evaluator.results()
            for rate_type in ['attack_rate', 'baseline_rate', 'control_rate']:
                rate_result = getattr(results, rate_type, None)
                if rate_result:
                    self.result[f'{rate_type}'] = _safe_round(rate_result.value)
                    self.result[f'{rate_type}_err'] = _safe_round(rate_result.error)
                else:
                    self.result[f'{rate_type}'] = pd.NA
                    self.result[f'{rate_type}_err'] = pd.NA
        except Exception:
            for rate_type in ['attack_rate', 'baseline_rate', 'control_rate']:
                self.result[f'{rate_type}'] = pd.NA
                self.result[f'{rate_type}_err'] = pd.NA

    def get_global(self) -> pd.DataFrame:
        pass

    def get_columnwise(self) -> pd.DataFrame:
        pass

    def get_pairwise(self) -> pd.DataFrame:
        pass
