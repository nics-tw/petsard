class AnonymeterFactory:
    def __init__(self, **kwargs):
        evaluating_method = kwargs.get('evaluating_method', None)

        if evaluating_method.startswith('anonymeter-linkability'):
            from .Anonymeter_Linkability import Anonymeter_Linkability
            _Evaluator = Anonymeter_Linkability(**kwargs).create_evaluator()
        else:
            raise ValueError(
                f"Evaluator (Anonymeter - AnonymeterFactory): evaluating_method {evaluating_method} didn't support.")

        _Evaluator = {}

        self.Evaluator = _Evaluator

    def create_evaluator(self):
        return self.Evaluator