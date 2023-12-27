class AnonymeterFactory:
    def __init__(self, **kwargs):
        evaluating_method = kwargs.get('evaluating_method', None)

        if evaluating_method.startswith('anonymeter-singlingout-univariate'):
            from .Anonymeter_SinglingOut_Univariate import Anonymeter_SinglingOut_Univariate
            _Evaluator = Anonymeter_SinglingOut_Univariate(**kwargs)
        elif evaluating_method.startswith('anonymeter-linkability'):
            from .Anonymeter_Linkability import Anonymeter_Linkability
            _Evaluator = Anonymeter_Linkability(**kwargs)
        elif evaluating_method.startswith('anonymeter-inference'):
            from .Anonymeter_Inference import Anonymeter_Inference
            _Evaluator = Anonymeter_Inference(**kwargs)
        else:
            raise ValueError(f"Evaluator (Anonymeter - AnonymeterFactory): evaluating_method {evaluating_method} didn't support.")

        self.Evaluator = _Evaluator

    def create_evaluator(self):
        return self.Evaluator