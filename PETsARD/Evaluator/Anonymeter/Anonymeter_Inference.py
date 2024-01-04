import time

from anonymeter.evaluators import InferenceEvaluator

from .Anonymeter import Anonymeter


class Anonymeter_Inference(Anonymeter):
    def __init__(self,   **kwargs):
        super().__init__(**kwargs)
        self.eval_method: str = 'Inference'

        _time_start = time.time()
        print('Evaluator (Anonymeter - Inference): Now is Inference Evaluator')

        _aux_cols = [
            col for col in self.data_syn.columns if col != self.secret
        ]

        self._Evaluator = InferenceEvaluator(
            ori=self.data_ori,
            syn=self.data_syn,
            control=self.data_control,
            aux_cols=_aux_cols,
            secret=self.secret
        )

        print(
            f"Evaluator (Anonymeter - Inference): Evaluator time: "
            f"{round(time.time()-_time_start ,4)} sec."
        )
