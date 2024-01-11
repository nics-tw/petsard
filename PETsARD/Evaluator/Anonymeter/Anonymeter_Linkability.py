import time

from anonymeter.evaluators import LinkabilityEvaluator

from PETsARD.Evaluator.Anonymeter import Anonymeter


class Anonymeter_Linkability(Anonymeter):
    """
    Estimation of the Linkability attacks in the Anonymeter library.

    ...
    Returns:
        None
            Notes: Stores the result in self._Evaluator.evaluation.

    """

    def __init__(self,   **kwargs):
        super().__init__(**kwargs)
        self.eval_method: str = 'Linkability'

        _time_start = time.time()
        print(
            f"Evaluator (Anonymeter - Linkability): "
            f"Now is Linkability Evaluator"
        )

        _str_aux_cols = (
            f"\n                                      and "
            .join(f"[{', '.join(row)}]" for row in self.aux_cols)
        )
        print(
            f"Evaluator (Anonymeter - Linkability): "
            f"aux_cols are {_str_aux_cols}."
        )

        self._Evaluator = LinkabilityEvaluator(
            ori=self.data_ori,
            syn=self.data_syn,
            control=self.data_control,
            n_attacks=self.n_attacks,
            n_neighbors=self.n_neighbors,
            aux_cols=self.aux_cols
        )
        print(
            f"Evaluator (Anonymeter - Linkability): Evaluator time: "
            f"{round(time.time()-_time_start ,4)} sec."
        )
