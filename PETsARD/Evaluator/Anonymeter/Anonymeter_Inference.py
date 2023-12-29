from .Anonymeter import Anonymeter

class Anonymeter_Inference(Anonymeter):
    def __init__(self,   **kwargs):
        super().__init__(**kwargs)
        self._eval_method = 'Inference'

        import time
        _time_start = time.time()
        print('Evaluator (Anonymeter - Inference): Now is Inference Evaluator')
        from anonymeter.evaluators import InferenceEvaluator
        _aux_cols = [col for col in self.data_syn.columns if col != self.secret]
        _Evaluator = InferenceEvaluator(ori      = self.data_ori
                                       ,syn      = self.data_syn
                                       ,control  = self.data_control
                                       ,aux_cols = _aux_cols
                                       ,secret   = self.secret
                                       )
        self._Evaluator = _Evaluator
        print(f"Evaluator (Anonymeter - Inference): Evaluator time: {round(time.time()-_time_start ,4)} sec.")