class SDV_SingleTableFactory:
    def __init__(self, data, **kwargs):
        synthesizing_method = kwargs.get('synthesizing_method', None)
        # _para = {
        #     'sample_num_rows': kwargs.get('sample_num_rows', None)
        #    ,'sample_batch_size': kwargs.get('sample_batch_size', None)
        # }
        #  ,**_para

        if   synthesizing_method == 'sdv-singletable-coupulagan':
            from .SDV_SingleTable_CoupulaGAN import SDV_SingleTable_CoupulaGAN
            _Synthesizer = SDV_SingleTable_CoupulaGAN(data=data)
        elif synthesizing_method == 'sdv-singletable-ctgan':
            from .SDV_SingleTable_CTGAN import SDV_SingleTable_CTGAN
            _Synthesizer = SDV_SingleTable_CTGAN(data=data)
        elif synthesizing_method == 'sdv-singletable-gaussiancoupula':
            from .SDV_SingleTable_GaussianCoupula import SDV_SingleTable_GaussianCoupula
            _Synthesizer = SDV_SingleTable_GaussianCoupula(data=data)
        elif synthesizing_method == 'sdv-singletable-tvae':
            from .SDV_SingleTable_TVAE import SDV_SingleTable_TVAE
            _Synthesizer = SDV_SingleTable_TVAE(data=data)
        else:
            raise ValueError(
                f"Synthesizer (SDV - SDV_SingleTableFactory): synthesizing_method {synthesizing_method} didn't support.")

        self.Synthesizer = _Synthesizer

    def create_synthesizer(self):
        return self.Synthesizer




