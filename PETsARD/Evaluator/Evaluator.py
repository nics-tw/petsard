from .EvaluatorFactory import EvaluatorFactory


class Evaluator:
    """
    Base class for all "Evaluator".

    The "Evaluator" class defines the common API
    that all the "Evaluator" need to implement, as well as common functionality.

    ...
    Methods:
        Evaluator(DataFrame): Evaluating specified DataFrame.
        Returns:
            Dict: A dict that general evaluation of input data.
    ...

    Args:

    """

    def __init__(self,
                 data: dict,
                 evaluating_method: str,
                 **kwargs):

        _para_Evaluator = {
            'evaluating_method': evaluating_method.lower(),
            **{k: v for k, v in kwargs.items() if k.startswith('anonymeter_')}
        }

        self.data = data
        self.Evaluator = EvaluatorFactory(
            data=data,
            **_para_Evaluator
        ).create_evaluator()

        self.para = {}
        self.para['Evaluator'] = _para_Evaluator

    def eval(self):
        self.Evaluator.eval()
