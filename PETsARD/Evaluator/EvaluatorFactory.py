class EvaluatorFactory:
    def __init__(self, **kwargs):
        evaluating_method = kwargs.get('evaluating_method', None)

        if evaluating_method.startswith('anonymeter'):
            from .Anonymeter.AnonymeterFactory import AnonymeterFactory
            _Evaluator = AnonymeterFactory(**kwargs).create_evaluator()
        else:
            raise ValueError(
                f"Evaluator - EvaluatorFactory: evaluating_method {evaluating_method} didn't support.")

        self.Evaluator = _Evaluator

    def create_evaluator(self):
        return self.Evaluator