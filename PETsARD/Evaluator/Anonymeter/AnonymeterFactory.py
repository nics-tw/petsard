from .Anonymeter_SinglingOut_Univariate import Anonymeter_SinglingOut_Univariate
from .Anonymeter_Linkability import Anonymeter_Linkability
from .Anonymeter_Inference import Anonymeter_Inference
# TODO As AnonymeterMethodMap, use class define mapping of string and int,
#      don't use string condition.

class AnonymeterFactory:
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
        return self.Evaluator