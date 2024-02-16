import re

from PETsARD.evaluator.anonymeter import AnonymeterFactory
from PETsARD.evaluator.sdmetrics import SDMetrics


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
        ...
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
        except KeyError as ex:
            print(
                f"Evaluator (SDMetrics): Method "
                f"{method} not recognized.\n"
                f"{ex}"
            )


class EvaluatorFactory:
    """
    Factory for "Evaluator".

    EvaluatorFactory defines which library to use
        and implements the Factory for that library.

    ...

    Args:
        method (str):
            Follow the 'method' logic defined in Evaluator.

    ...
    Returns:
        None

    """

    def __init__(self, **kwargs):
        # TODO don't use kwargs
        method = kwargs.get('method', None)

        # Factory method for implementing the specified Loader class
        if EvaluatorMethodMap.getext(method) == EvaluatorMethodMap.ANONYMETER:
            self.Evaluator = AnonymeterFactory(**kwargs).create_evaluator()
        elif EvaluatorMethodMap.getext(method) == EvaluatorMethodMap.SDMETRICS:
            self.Evaluator = SDMetrics(**kwargs).create_evaluator()
        else:
            raise ValueError(
                f"Evaluator - EvaluatorFactory: method {method} didn't support.")

        self.Evaluator = _Evaluator

    def create_evaluator(self):
        """
        Factory method to designated the selected evaluator.
        ...
        TODO As Loader,
                transform the Factory into the main module
                and create a Base module for inheritance
                to address the 'One Library, One Code' issue."

        """
        return self.Evaluator
