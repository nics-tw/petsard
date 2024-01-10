from PETsARD.Evaluator.EvaluatorFactory import EvaluatorFactory


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

        self.para: dict = {}
        self.para['Evaluator'] = {
            'evaluating_method': evaluating_method.lower(),
            **{k: v for k, v in kwargs.items() if k.startswith('anonymeter_')}
        }

        self.data: dict = data
        self.Evaluator = EvaluatorFactory(
            data=data,
            **self.para['Evaluator']
        ).create_evaluator()

    def eval(self) -> None:
        self.Evaluator.eval()
