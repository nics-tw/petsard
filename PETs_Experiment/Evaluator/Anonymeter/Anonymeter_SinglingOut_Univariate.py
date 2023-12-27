from .Anonymeter import Anonymeter

class Anonymeter_SinglingOut_Univariate(Anonymeter):
    def __init__(self,   **kwargs):
        super().__init__(**kwargs)
        self._eval_method = 'SinglingOut - Univariate'

        import time
        _time_start = time.time()
        print('Evaluator (Anonymeter - SinglingOut - Univariate): Now is SinglingOut - Univariate Evaluator')
        from anonymeter.evaluators import SinglingOutEvaluator
        _Evaluator = SinglingOutEvaluator(ori      = self.data_ori
                                          ,syn     = self.data_syn
                                          ,control = self.data_control
                                          ,n_attacks = self.n_attacks
                                          )
        self._Evaluator = _Evaluator
        print(f"Evaluator (Anonymeter - SinglingOut - Univariate): Evaluator time: {round(time.time()-_time_start ,4)} sec.")