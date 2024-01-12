import time

from anonymeter.evaluators import SinglingOutEvaluator

from PETsARD.Evaluator.Anonymeter import Anonymeter


class Anonymeter_SinglingOut_Univariate(Anonymeter):
    """
    Estimation of the SinglingOut attacks of Univariate in the Anonymeter library.

    ...
    Returns:
        None
            Notes: Stores the result in self._Evaluator.evaluation.

    ...
    TODO SinglingOut attacks of Multi-variate.

    """

    def __init__(self,   **kwargs):
        super().__init__(**kwargs)
        self.eval_method: str = 'SinglingOut - Univariate'

        _time_start = time.time()
        print(
            f"Evaluator (Anonymeter - SinglingOut - Univariate): "
            f"Now is SinglingOut - Univariate Evaluator"
        )

        self._Evaluator = SinglingOutEvaluator(
            ori=self.data_ori,
            syn=self.data_syn,
            control=self.data_control,
            n_attacks=self.n_attacks
        )
        print(
            f"Evaluator (Anonymeter - SinglingOut - Univariate): "
            f"Evaluator time: {round(time.time()-_time_start ,4)} sec."
        )
