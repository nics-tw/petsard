import re

from PETsARD.evaluator.anonymeter import AnonymeterFactory
from PETsARD.evaluator.sdmetrics import SDMetrics

from PETsARD.error import UnsupportedSynMethodError


class EvaluatorMethodMap():
    """
    Mapping of SDMetrics.
    """
    ANONYMETER: int = 1
    SDMETRICS: int = 2

    @classmethod
    def getext(cls, method: str) -> int:
        """
        Get suffixes mapping int value before 1st dash (-)

        Args:
            method (str):
                evaluating method
        """
        try:
            # Get the string before 1st dash, if not exist, get emply ('').
            method_1st_match = re.match(
                r'^[^-]*', method)
            method_1st = (
                method_1st_match.group()
                if method_1st_match
                else ''
            )
            return cls.__dict__[method_1st.upper()]
        except KeyError:
            raise UnsupportedSynMethodError

class Evaluator:
    """
    Base class for all "Evaluator".

    The "Evaluator" class defines the common API
    that all "Evaluators" need to implement, as well as common functionality.

    Args:
        data (dict)
            The dictionary contains necessary information.
            For now, we adhere to the Anonymeter requirements,
            so you should include:
            data = {
                'ori' : pd.DataFrame   # Original data used for synthesis
                'syn' : pd.DataFrame   # Synthetic data generated from 'ori'
                'control: pd.DataFrame # Original data but NOT used for synthesis
            }
            Note: So it is recommended to split your original data before synthesizing it.
                (We recommend to use our pipeline!)

        evaluating_method (str):
            The method of how you evaluating data. Case insensitive.
                The format should be: {library name}{function name},
                e.g., 'anonymeter_singlingout_univariate'.

    Returns:
        None

    TODO Extract and process the result.

    """

    def __init__(self, method: str, **kwargs):

        self.config = {
            'method': method.lower(),
            'n_attacks': kwargs.get('n_attacks', 2000),
            'n_jobs': kwargs.get('n_jobs', -2),
            'n_neighbors': kwargs.get('n_neighbors', 10),
            'aux_cols': kwargs.get('aux_cols', None),
            'secret': kwargs.get('secret', None)
        }

    def create(self, data: dict) -> None:
        """
        Create a Evaluator object with the given data.

        Args:
            data (dict): The input data for evaluating.
        """
        self.config['data'] = data

        # TODO: verify method in __init__
        method = self.config['method']
        if EvaluatorMethodMap.getext(method) == EvaluatorMethodMap.ANONYMETER:
            self.evaluator = AnonymeterFactory(**self.config).create()
        elif EvaluatorMethodMap.getext(method) == EvaluatorMethodMap.SDMETRICS:
            self.evaluator = SDMetrics(**self.config).create()
        else:
            raise UnsupportedSynMethodError

    def eval(self) -> None:
        """
        eval()
            Call the evaluating method within implementation after Factory.
        """
        self.evaluator.eval()
