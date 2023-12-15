class Executor:
    def __init__(self, **kwargs):
        from datetime import datetime
        self.exectime   = datetime.now().strftime('%Y%m%d%H%M%S')
        self.outputname = f"PETsARD{self.exectime}_"

        self.kwargs = kwargs
        self._para_handle()



    def _para_handle(self):
        """
        有三種情況：

        1. 想跑單一種設定的單次執行：module 每個設定都直接表述，例如
             'Loader_filepath'  : '[sunset]/data/[Adt Income] adult.csv'
            ,'Loader_na_values' : {k : '?' for k in ['workclass' ,'occupation' ,'native-country']}
            ,'Spitter_num_samples'       : 2
            ,'Spitter_train_split_ratio' : 0.8
            此時 module 可以留空或設定為 True (default)

        2. 想跳過這個 module
            此時 module 必須寫為 False。
            在 False 情況下，以該 module 打頭的設定全部都會被忽略

        3. 想跑多種設定：多種設定必須以 module 為單位進行字典的打包，例如
            'Loader' : {'adult' : {'filepath' :'[sunset]/data/[Adt Income] adult.csv'
                                  ,'na_values' : {k : '?' for k in ['workclass' ,'occupation' ,'native-country']}
                                  }
                       ,'NHANES' : {filepath = '../[sunset]/data/[NHANES] B.csv'
                                   ,header_exist=False
                                   ,header_names=['gen','age','race','edu','mar','bmi','dep','pir','gh','mets','qm','dia']
                                   }
                       }
            ,'Spitter_num_samples'       : 2
            ,'Spitter_train_split_ratio' : 0.8
            此時 module 必須為一個字典。字典鍵值會用作識別，字典內容在輸入變數時可省略 module
            請注意如果 module 字典已經被給定，外圍 module 打頭的設定會被忽略

        # Postprocessor 必跑所以不考慮
        """
        _para = {}

        _list_module = ['Loader', 'Spitter', 'Preprocessor', 'Synthesizer']
        for _module in _list_module:
            _module_value = self.kwargs.get(_module, True)
            if isinstance(_module_value, dict):
                _para[_module] = True
                _para[_module+'_setting'] = _module_value
            elif _module_value:
                _para[_module] = True
                _para[_module+'_setting'] = {}
                _subpara = {k.replace(_module+'_', '', 1): v
                            for k, v in self.kwargs.items()
                            if k.startswith(_module+'_')}
                _name = self._para_handle_naming(_module ,_subpara)
                _para[_module+'_setting'][_name] = _subpara
            else:
                _para[_module] = False

        if _para['Preprocessor']:
            _para['Postprocessor'] = True
            _para['Postprocessor_setting'] = {}
        self.para = _para



    def _para_handle_naming(self ,module ,subpara):
        if module == 'Loader':
            import os
            # Set the maximum filename length. This value is arbitrarily chosen.
            _max_filename = 36
            _trial_name = os.path.basename(subpara['filepath'])[:_max_filename]\
                            if 'filepath' in subpara else 'Default'
        elif module == 'Spitter':
            # num_sample and train_split_ratio follows default of Splitter
            _num_sample        = str(subpara['num_samples'      ]) if 'num_samples'       in subpara else '1'
            _train_split_ratio = str(subpara['train_split_ratio']) if 'train_split_ratio' in subpara else '0.8'
            _trial_name = 'x'.join([_num_sample ,_train_split_ratio])
        elif module == 'Preprocessor':
            _list_preproc = []
            if 'missing_method'  in subpara:
                _list_preproc.append(subpara['missing_method'])
            if 'outlier_method'  in subpara:
                _list_preproc.append(subpara['outlier_method'])
            if 'encoding_method' in subpara:
                _list_preproc.append(subpara['encoding_method'])
            if 'scaling_method' in subpara:
                _list_preproc.append(subpara['scaling_method'])
            _trial_name = 'x'.join(_list_preproc) if len(_list_preproc) >= 1 else 'Default'
        elif module == 'Synthesizer':
            _trial_name = subpara['synthesizing_method'] if 'synthesizing_method' in subpara else 'Default'
        else:
            _trial_name = 'Default'

        return _trial_name



    def run(self):
        if self.para['Loader']:
            from .Loader import Loader
            self.loader = {}
            for _key ,_para in self.para['Loader_setting'].items():
                self.loader[_key] = Loader(**_para)



    def _run_single_loading(self ,trail):



    #     from concurrent.futures import ProcessPoolExecutor, as_completed



    # def _run_single_loader(self ,trail):


    #     if self.para['Spitter'][trail]:
    #         from .Loader import Spitter
    #         spitter = Spitter(data=loader.data
    #                          ,**self.para['Spitter_setting'][trail])
    #     return loader ,spitter

    # def _run_single_generating_proc(self ,data ,trail):
    #     if self.para['Preprocessor'][trail]:
    #         from .Preprocessor import Preprocessor
    #         preprocessor[trail] = Preprocessor(data=data
    #                                           ,**self.para['Preprocessor_setting'][trail])
    #     return preprocessor

    #     if self.para['Synthesizer']:
    #         from .Synthesizer import Synthesizer
    #         if not hasattr(self ,'preprocessor'):
    #             self.preprocessor = {}
    #         self.synthesizer = Synthesizer(data = _data
    #                                       ,**self.para['Synthesizer_setting'][trail])
    #         self.synthesizer.fit_sample()

    #     if self.para['Postprocessor']:
    #         for _decoder in ['encoder' ,'scaler']:
    #             self.para['Postprocessor_setting'].setdefault(_decoder ,getattr(self.preprocessor ,_decoder ,None))

    #         from .Postprocessor import Postprocessor
    #         self.postpostproc = Postprocessor(data = self.synthesizer.data_syn
    #                                          ,**self.para['Postprocessor_setting'][trail]
    #                                          )
