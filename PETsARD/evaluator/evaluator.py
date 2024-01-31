from PETsARD.evaluator.evaluator_factory import EvaluatorFactory


class Evaluator:
    """
    Base class for all "Evaluator".

    The "Evaluator" class defines the common API
    that all "Evaluators" need to implement, as well as common functionality.

    ...

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

    ...
    Returns:
        None

    ...
    TODO Extract and process the result.

    """

    def __init__(self, data: dict, evaluating_method: str, **kwargs):

        _para_Evaluator = {
            'evaluating_method': evaluating_method.lower(),
            # Anonymeter
            'anonymeter_n_attacks': kwargs.get('anonymeter_n_attacks', 2000),
            'anonymeter_n_jobs': kwargs.get('anonymeter_n_jobs', -2),
            'anonymeter_n_neighbors': kwargs.get('anonymeter_n_neighbors', 10),
            'anonymeter_aux_cols': kwargs.get('anonymeter_aux_cols', None),
            'anonymeter_secret': kwargs.get('anonymeter_secret', None)
        }
        self.Evaluator = EvaluatorFactory(data=data, **_para_Evaluator)\
            .create_evaluator()

    def eval(self) -> None:
        """
        eval()
            Call the evaluating method within implementation after Factory.
        """
        self.Evaluator.eval()
