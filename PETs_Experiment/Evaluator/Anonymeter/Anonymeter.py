
class Anonymeter():

    def __init__(self, **kwargs):
        import warnings

        _data             = kwargs.get('data' ,None)
        self.data_ori     = _data.get('ori'     ,None)
        self.data_syn     = _data.get('syn'     ,None)
        self.data_control = _data.get('control' ,None)

        self.n_attacks = kwargs.get('n_attacks' ,2000)
        self.n_jobs    = kwargs.get('n_jobs'    ,-2  )

        self.n_neighbors = kwargs.get('n_neighbors' ,10  )
        self.aux_cols    = kwargs.get('aux_cols'    ,None)


        with warnings.catch_warnings():
            # anonymeter\evaluators\singling_out_evaluator.py:97:
            # FutureWarning: is_categorical_dtype is deprecated and will be removed in a future version.
            # Use isinstance(dtype, CategoricalDtype) instead elif is_categorical_dtype(values)
            warnings.simplefilter("ignore" ,category=FutureWarning)
            # c:\Program Files\Python310\lib\site-packages\anonymeter\stats\confidence.py:215:
            # UserWarning: Attack is as good or worse as baseline model.
            # Estimated rates: attack = 0.30674239114619767, baseline = 0.30773856438771213.
            # Analysis results cannot be trusted. self._sanity_check()
            warnings.simplefilter("ignore" ,category=UserWarning)

        pass