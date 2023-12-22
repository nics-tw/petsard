# from .Anonymeter import Anonymeter

# class Anonymeter_SinglingOut(Anonymeter):
#     def __init__(self,   data, **kwargs):
#         super().__init__(data, **kwargs)

#         # metadata already create in SDV_SingleTable
#         from sdv.single_table import CopulaGANSynthesizer
#         self._Synthesizer = CopulaGANSynthesizer(self.metadata)




#         import time
#         from anonymeter.evaluators import SinglingOutEvaluator

#         self._eval_method = 'Singling-Out'
#         __time_start = time.time()
#         _evaluator = SinglingOutEvaluator(ori       = self.data_ori
#                                          ,syn       = self.data_syn
#                                          ,control   = self.data_control
#                                          ,**kwargs
#                                          )
#         try:
#             _evaluator.evaluate(mode=mode)
#             self.evaluators['SinglingOut'][mode] = __evaluator
#             self.results[   'SinglingOut'][mode] = self.__Result(self.evaluators['SinglingOut'][mode])
#         except RuntimeError as e:
#             print(f"Singling out evaluation failed with {ex}."
#                    "Please re-run this cell."
#                    "For more stable results increase `n_attacks`. Note that this will "
#                    "make the evaluation slower.")