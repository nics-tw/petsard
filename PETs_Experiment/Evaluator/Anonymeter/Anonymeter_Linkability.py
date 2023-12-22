from .Anonymeter import Anonymeter

class Anonymeter_Linkability(Anonymeter):
    def __init__(self,   **kwargs):
        super().__init__(**kwargs)

        import time
        _time_start = time.time()
        print('Evaluator (Anonymeter - Linkability): Now is Linkability Evaluator')
        from anonymeter.evaluators import LinkabilityEvaluator
        _str_aux_cols = "\nand ".join(f"[{', '.join(row)}]" for row in self.aux_cols)
        print(f"Evaluator (Anonymeter - Linkability): aux_cols are {_str_aux_cols}.")
        _evaluator = LinkabilityEvaluator(ori     = self.data_ori
                                         ,syn     = self.data_syn
                                         ,control = self.data_control
                                         ,aux_cols = self.aux_cols
                                         ,n_attacks   = self.n_attacks
                                         ,n_neighbors = self.n_neighbors
                                         ,**kwargs
                                         )
        _evaluator.evaluate(n_jobs=self.n_jobs)
        self.evaluator = _evaluator
        print(f"Evaluator (Anonymeter - Linkability): Evaluator time: {round(time.time()-_time_start ,4)} sec.")