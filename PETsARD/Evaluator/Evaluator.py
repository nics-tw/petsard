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
            'anonymeter_n_attacks':   kwargs.get('anonymeter_n_attacks', 2000),
            'anonymeter_n_jobs':      kwargs.get('anonymeter_n_jobs', -2),
            'anonymeter_n_neighbors': kwargs.get('anonymeter_n_neighbors', 10),
            'anonymeter_aux_cols':    kwargs.get('anonymeter_aux_cols', None),
            'anonymeter_secret':      kwargs.get('anonymeter_secret', None)
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
