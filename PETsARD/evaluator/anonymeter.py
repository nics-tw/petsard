from abc import abstractmethod
import re
from typing import (
    Optional,
    Union,
)
import warnings

from anonymeter.evaluators import (
    SinglingOutEvaluator,
    LinkabilityEvaluator,
    InferenceEvaluator
)
import pandas as pd

from PETsARD.evaluator.evaluator_base import EvaluatorBase
from PETsARD.error import (
    ConfigError,
    UnableToEvaluateError,
    UnfittedError,
    UnsupportedMethodError
)
from PETsARD.util import safe_round


class AnonymeterMap():
    """
    map of Anonymeter
    """
    SINGLINGOUT: int = 1
    LINKABILITY: int = 3
    INFERENCE: int = 4

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
            raise UnsupportedMethodError


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
                - n_cols (int, Optional): The number of columns used for generating
                    singling-out queries. Default is 3.
                - max_attempts (int, Optional): The maximum number of attempts to find a
                    successful attack. Default is 500000.
                - n_neighbors (int, Optional):
                    Sets the number of nearest neighbors to consider for each entry in the search.
                    Indicating a successful linkability attack only if
                    the closest synthetic record matches for both split original records.
                    Default is 1.
                - aux_cols (tuple[List[str], List[str]] | List[str], Optional):
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
            'n_cols': 3,       # int
            'max_attempts': 500000,  # int
            'n_neighbors': 1,  # int
            'aux_cols': None,  # tuple[List[str], List[str]]
            'secret': None    # Optional[Union[str, List[str]]]
        }
        for key, value in default_config.items():
            config.setdefault(key, value)
        self.config['method_code'] = AnonymeterMap.map(self.config['method'])

        self.evaluator = None

    def create(self, data: dict) -> None:
        """
        Create a new instance of the anonymeter class with the given data.

        Args:
            data (dict): The data to be stored in the anonymeter instance.

        Resurn:
            None. Anonymeter class store in self.evaluator.

        """
        if 'ori' not in data or 'syn' not in data or 'control' not in data:
            raise ConfigError
        self.data = data

        self.config['n_max_attacks'] = self._calculate_n_max_attacks()

        if self.config['method_code'] == AnonymeterMap.SINGLINGOUT:
            self.config['singlingout_mode'] = 'multivariate'
            self.evaluator = SinglingOutEvaluator(
                ori=self.data['ori'],
                syn=self.data['syn'],
                control=self.data['control'],
                n_attacks=self.config['n_attacks'],
                n_cols=self.config['n_cols'],
                max_attempts=self.config['max_attempts']
            )
        elif self.config['method_code'] == AnonymeterMap.LINKABILITY:
            if 'aux_cols' not in self.config\
                or self.config['aux_cols'] is None:
                raise ConfigError
            self.evaluator = LinkabilityEvaluator(
                ori=self.data['ori'],
                syn=self.data['syn'],
                control=self.data['control'],
                n_attacks=self.config['n_attacks'],
                n_neighbors=self.config['n_neighbors'],
                aux_cols=self.config['aux_cols']
            )
        elif self.config['method_code'] == AnonymeterMap.INFERENCE:
            if self.config['aux_cols'] is None:
                aux_cols = [
                    col for col in self.data['ori'].columns
                    if col != self.config['secret']
                ]
            else:
                if self.config['secret'] in self.config['aux_cols']:
                    raise ConfigError
                else:
                    aux_cols = self.config['aux_cols']
            self.evaluator = InferenceEvaluator(
                ori=self.data['ori'],
                syn=self.data['syn'],
                control=self.data['control'],
                n_attacks=self.config['n_attacks'],
                aux_cols=aux_cols,
                secret=self.config['secret']
            )
        else:
            raise UnsupportedMethodError

    def _calculate_n_max_attacks(self) -> int:
        """
        Calculate the theoretically maximum number of attacks.
            SinglingOut: Not supported.
            Linkability: the n_rows of the control dataset.
            Inference: the n_rows of the control dataset.

        Returns:
            n_max_attacks (int): The maximum number of attacks.
                Returns None if the method is SinglingOut.
        """
        method_code: int = self.config['method_code']
        if method_code == AnonymeterMap.SINGLINGOUT:
            return None
        elif method_code in [
            AnonymeterMap.LINKABILITY, AnonymeterMap.INFERENCE
        ]:
            return self.data['control'].shape[0]
        else:
            raise UnsupportedMethodError

    def _extract_result(self) -> dict:
        """
        _extract_result of Anonymeter.
            Uses .risk()/.results() method in Anonymeter
            to extract result from self.evaluator into the designated dictionary.

        Return
            (dict). Result as specific format describe in eval().
        """

        result = {}

        # Handle the risk
        try:
            risk = self.evaluator.risk()
            result['risk'] = safe_round(risk.value)
            result['risk_CI_btm'] = safe_round(risk.ci[0])
            result['risk_CI_top'] = safe_round(risk.ci[1])
        except Exception:
            result['risk'] = pd.NA
            result['risk_CI_btm'] = pd.NA
            result['risk_CI_top'] = pd.NA

        # Handle the attack_rate, baseline_rate, control_rate
        try:
            results = self.evaluator.results()
            for rate_type in ['attack_rate', 'baseline_rate', 'control_rate']:
                rate_result = getattr(results, rate_type, None)
                if rate_result:
                    result[f'{rate_type}'] = safe_round(rate_result.value)
                    result[f'{rate_type}_err'] = safe_round(rate_result.error)
                else:
                    result[f'{rate_type}'] = pd.NA
                    result[f'{rate_type}_err'] = pd.NA
        except Exception:
            for rate_type in ['attack_rate', 'baseline_rate', 'control_rate']:
                result[f'{rate_type}'] = pd.NA
                result[f'{rate_type}_err'] = pd.NA

        return result

    def eval(self) -> dict:
        """
        Evaluate the anonymization process.

        Keep the known warnings from the Anonymeter library:
            UserWarning: anonymeter\stats\confidence.py:215:
                UserWarning: Attack is as good or worse as baseline model.
                Estimated rates: attack = ...{float}... ,
                baseline = ...{float}... .
                Analysis results cannot be trusted. self._sanity_check()
            - warnings.simplefilter("ignore", category=UserWarning)

        Suppressed the known warnings from the Anonymeter SinglingOut:
            FutureWarning: anonymeter\evaluators\singling_out_evaluator.py:97:
                FutureWarning: is_categorical_dtype is deprecated
                and will be removed in a future version.
                Use isinstance(dtype, CategoricalDtype)
                instead elif is_categorical_dtype(values).

        Return
            (dict). Result as following key-value pairs:
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

        Exception:
            UnfittedError: If the anonymeter has not been create() yet.
        """
        if not self.evaluator:
            raise UnfittedError

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=FutureWarning)
            try:
                if self.config['method_code'] == AnonymeterMap.SINGLINGOUT:
                    # SinglingOut
                    self.evaluator.evaluate(mode=self.config['singlingout_mode'])
                elif self.config['method_code'] in [
                    AnonymeterMap.LINKABILITY, AnonymeterMap.INFERENCE]:
                    # Linkability and Inference
                    self.evaluator.evaluate(n_jobs=self.config['n_jobs'])
                else:
                    raise UnsupportedMethodError
            except RuntimeError:
                warnings.warn(
                    f"Evaluator - Anonymeter: "
                    f"Please re-run this cell. "
                    f"For more stable results, increase `n_attacks`. "
                    f"Note that this will make the evaluation slower.",
                    RuntimeWarning
                )
                pass

        # self._extract_result() already handle the exception by assign NA
        self.result = self._extract_result()

    def get_global(self) -> Union[pd.DataFrame, None]:
        """
        Retrieves the global result from the Anonymeter.

        Returns:
            pd.DataFrame: A DataFrame with the global evaluation result.
                One row only for representing the whole data result.
        """
        if not self.result:
            raise UnfittedError

        return pd.DataFrame.from_dict(
            data={'result': self.result},
            orient='columns'
        ).T

    def get_columnwise(self) -> Union[pd.DataFrame, None]:
        """
        Retrieves the column-wise result from the Anonymeter.

        Returns:
            pd.DataFrame: None for Anonymeter didn't have column-wise result.
        """
        return None

    def get_pairwise(self) -> Union[pd.DataFrame, None]:
        """
        Retrieves the pairwise result from the Anonymeter.

        Returns:
            pd.DataFrame: None for Anonymeter didn't have pairwise result.
        """
        return None

    def get_details(self) -> dict:
        """
        Retrieves the specify details of the evaluation.

        Returns:
            None. self.result['details'] will store the non-specific data.
        """
        details = {}

        if self.config['method_code'] == AnonymeterMap.SINGLINGOUT:
            # SinglingOut attacks of Univariate
            #   control queries didn't been stored
            details['attack_queries']   = self.evaluator._attack_queries
            details['baseline_queries'] = self.evaluator._baseline_queries
        elif self.config['method_code'] == AnonymeterMap.LINKABILITY:
            # Linkability: Dict[int, Set(int)]
            #   aux_cols[0] indexes links to aux_cols[1]
            n_neighbors = self.config['n_neighbors']
            details['attack_links'] = \
                self.evaluator._attack_links.find_links(n_neighbors=n_neighbors)
            details['baseline_links'] = \
                self.evaluator._baseline_links.find_links(n_neighbors=n_neighbors)
            details['control_links'] = \
                self.evaluator._control_links.find_links(n_neighbors=n_neighbors)
        elif self.config['method_code'] == AnonymeterMap.INFERENCE:
            # Inference
            pass # Inference queries didn't been stored
        else:
            raise UnsupportedMethodError

        self.result['details'] = details
