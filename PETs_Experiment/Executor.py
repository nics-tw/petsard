class Executor:
    def __init__(self ,**kwargs):
        _para = {}

        _list_module = ['Loader' ,'Preprocessor' ,'Synthesizer' ,'Postprocessor']
        for _module in _list_module:
            _para[_module] = kwargs.get(_module, True)
            if _para[_module]:
                _para[_module+'_setting'] = {k.replace(_module+'_', '', 1): v
                                             for k, v in kwargs.items()
                                             if k.startswith(_module+'_')}
            else:
                _para[_module+'_setting'] = {}
    
        self.para = _para


    def run(self):
        if self.para['Loader']:
            from .Loader import Loader
            self.loader = Loader(**self.para['Loader_setting'])

        if self.para['Preprocessor']:
            from .Preprocessor import Preprocessor
            self.preprocessor = Preprocessor(data=self.loader.data
                                            ,**self.para['Preprocessor_setting'])

        if self.para['Synthesizer']:
            from .Synthesizer import Synthesizer
            self.synthesizer = Synthesizer(data = self.preprocessor.data
                                          ,**self.para['Synthesizer_setting'])
            self.synthesizer.fit_sample()

        if self.para['Postprocessor']:
            for _decoder in ['encoder' ,'scaler']:
                self.para['Postprocessor_setting'].setdefault(_decoder ,getattr(self.preprocessor ,_decoder ,None))

            from .Postprocessor import Postprocessor
            # self.postpostproc = Postprocessor(data = self.synthesizer.data_syn
            #                                  ,**self.para['Postprocessor_setting']
            #                                  )

