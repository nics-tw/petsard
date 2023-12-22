class Synthesizer:
    """
    Base class for all "Synthesizer".

    The "Synthesizer" class defines the common API
    that all the "Synthesizer" need to implement, as well as common functionality.

    ...
    Methods:
        Synthesizer(DataFrame): Synthesizing specified DataFrame.
        Returns:
            DataFrame: A pandas DataFrame that input data after synthesizing
    ...

    Args:

    """

    def __init__(self, data, synthesizing_method: str, **kwargs):

        _para_Synthesizer = {
            'synthesizing_method': synthesizing_method.lower()
        }

        from .SynthesizerFactory import SynthesizerFactory
        Synthesizer = SynthesizerFactory(
            data=data, **_para_Synthesizer).create_synthesizer()
        # data = Synthesizer.train_sample()

        self.data_ori = data
        self.Synthesizer = Synthesizer
        self.para = {}
        self.para['Synthesizer'] = _para_Synthesizer

    def fit(self):
        self.Synthesizer.fit()

    def sample(self):
        self.data_syn = self.Synthesizer.sample()

    def fit_sample(self):
        self.data_syn = self.Synthesizer.fit_sample()



        # _para_Synthesizer['SDV'] = {
        #     'SingleTable_sample_num_rows': kwargs.get('SDV_SingleTable_sample_num_rows', None)
        #    ,'SingleTable_sample_batch_size': kwargs.get('SDV_SingleTable_sample_batch_size', None)
        # }