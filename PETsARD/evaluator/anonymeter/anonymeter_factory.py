from PETsARD.evaluator.anonymeter import Anonymeter_SinglingOut_Univariate
from PETsARD.evaluator.anonymeter import Anonymeter_Linkability
from PETsARD.evaluator.anonymeter import Anonymeter_Inference


class AnonymeterFactory:
    """
    Factory for "Anonymeter" Evaluator.

    AnonymeterFactory defines which module to use within Anonymeter.

    ...
    TODO As AnonymeterMethodMap,
            use a class to define mappings of string and int,
            avoiding string conditions.

    """

    def __init__(self, **kwargs):
        evaluating_method: str = kwargs.get('evaluating_method', None)

        if evaluating_method.startswith('anonymeter-singlingout-univariate'):
            self.Evaluator = Anonymeter_SinglingOut_Univariate(**kwargs)
        elif evaluating_method.startswith('anonymeter-linkability'):
            self.Evaluator = Anonymeter_Linkability(**kwargs)
        elif evaluating_method.startswith('anonymeter-inference'):
            self.Evaluator = Anonymeter_Inference(**kwargs)
        else:
            raise ValueError(
                f"Evaluator (Anonymeter - AnonymeterFactory): "
                f"evaluating_method {evaluating_method} didn't support."
            )

    def create_evaluator(self):
        """
        create_evaluator()
            return the Evaluator which selected by Factory.
        """
        return self.Evaluator
