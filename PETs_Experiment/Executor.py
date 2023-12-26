class Executor:

    def __init__(self, **kwargs):
        from datetime import datetime
        self.exectime = datetime.now().strftime('%Y%m%d-%H%M%S')
        self.outputname = f"PETsARD[{self.exectime}]"

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

        _list_module = ['Loader', 'Splitter', 'Preprocessor', 'Synthesizer', 'Evaluator']
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
                _name = self._para_handle_naming(_module, _subpara)
                _para[_module+'_setting'][_name] = _subpara
            else:
                _para[_module] = False

        if _para['Preprocessor']:
            _para['Postprocessor'] = True
            _para['Postprocessor_setting'] = {}
        self.para = _para

    def _para_handle_naming(self, module, subpara):
        if module == 'Loader':
            import os
            # Set the maximum filename length. This value is arbitrarily chosen.
            _max_filename = 36
            _trial_name = os.path.basename(subpara['filepath'])[:_max_filename]\
                if 'filepath' in subpara else 'Default'
        elif module == 'Splitter':
            # num_samples and train_split_ratio follows default of Splitter
            _num_samples = str(subpara['num_samples']) if 'num_samples' in subpara else '1'
            _train_split_ratio = str(subpara['train_split_ratio']) if 'train_split_ratio' in subpara else '0.8'
            _trial_name = f"{_train_split_ratio}x{_num_samples}"
        elif module == 'Preprocessor':
            _list_preproc = []
            if 'missing_method' in subpara:
                _list_preproc.append(subpara['missing_method'])
            if 'outlier_method' in subpara:
                _list_preproc.append(subpara['outlier_method'])
            if 'encoding_method' in subpara:
                _list_preproc.append(subpara['encoding_method'])
            if 'scaling_method' in subpara:
                _list_preproc.append(subpara['scaling_method'])
            _trial_name = '-'.join(_list_preproc) if len(
                _list_preproc) >= 1 else 'Default'
        elif module == 'Synthesizer':
            _trial_name = subpara['synthesizing_method'] if 'synthesizing_method' in subpara else 'Default'
        elif module == 'Evaluator':
            # num_samples follows default of Splitter
            _num_samples = str(subpara['num_samples']) if 'num_samples' in subpara else '1'
            _eval_method = subpara['evaluating_method'] if 'evaluating_method' in subpara else 'Default'
            _trial_name = f"{_eval_method}x{_num_samples}"
        else:
            _trial_name = 'Default'

        return _trial_name

    def run_single_process(self):
        import time
        _time_start = time.time()

        self._save_in_submodule(module='Executor_Start')

        _load_trial_max = len(self.para['Loader_setting'])
        _split_trial_max = len(self.para['Splitter_setting'])
        _preproc_trial_max = len(self.para['Preprocessor_setting'])
        _syn_trial_max = len(self.para['Synthesizer_setting'])
        _eval_trial_max = len(self.para['Evaluator_setting'])

        _split_trial_splits = [setting['num_samples'] if 'num_samples' in setting else 1
                               for setting in self.para['Splitter_setting'].values()]
        _split_trial_splits_sum = sum(_split_trial_splits)
        _eval_trial_evals = [setting['num_samples'] if 'num_samples' in setting else 1
                              for setting in self.para['Evaluator_setting'].values()]
        _eval_trial_evals_sum = sum(_eval_trial_evals)

        self.loader = {}
        self.splitter = {}
        self.preprocessor = {}
        self.synthesizer = {}
        self.evaluator = {}
        _trials = {}
        for _load_trial, (_load_trial_name, _load_para) in enumerate(self.para['Loader_setting'].items()):
            _trials['load'] = {'trial': _load_trial+1, 'trial_name': _load_trial_name, 'trial_max': _load_trial_max}
            _load_result = self._run_single_loader(_trials['load'], _load_para)
            self.loader[_load_trial_name] = _load_result

            for _split_trial, (_split_trial_name, _split_para) in enumerate(self.para['Splitter_setting'].items()):
                _trials['split'] = {'trial': _split_trial+1, 'trial_name': _split_trial_name, 'trial_max': _split_trial_max,
                                    'trial_splits': _split_trial_splits, 'trial_split_sum': _split_trial_splits_sum}
                _split_result = self._run_single_splitter(
                    _load_result.data, _trials['split'], _split_para)
                _trials['split']['trial_split'] = len(_split_result.data)
                _trials['split']['trial_data_key'] = self._save_in_submodule(
                    'Splitter', _split_result.data, _trials)
                self.splitter[(_load_trial_name, _split_trial_name)
                              ] = _split_result

                for _split_data_key, _split_data in _split_result.data.items():
                    _trials['split']['data_key'] = _split_data_key

                    for _preproc_trial, (_preproc_trial_name, _preproc_para) in enumerate(self.para['Preprocessor_setting'].items()):
                        _trials['preproc'] = {'trial': _preproc_trial+1, 'trial_name': _preproc_trial_name, 'trial_max': _preproc_trial_max}
                        _preproc_result = self._run_single_preprocessor(
                            _split_data['train'], _trials['preproc'], _preproc_para)
                        _trials['preproc']['trial_data_key'] = self._save_in_submodule(
                            'Preprocessor', _preproc_result.data, _trials)
                        self.preprocessor[(_load_trial_name
                                           ,_split_trial_name
                                           ,_split_data_key
                                           ,_preproc_trial_name)] = _preproc_result

                        for _syn_trial, (_syn_trial_name, _syn_para) in enumerate(self.para['Synthesizer_setting'].items()):
                            _trials['syn'] = {'trial': _syn_trial+1, 'trial_name': _syn_trial_name, 'trial_max': _syn_trial_max}
                            _syn_result = self._run_single_synthesizer(
                                _preproc_result.data, _trials['syn'], _syn_para)
                            _trials['syn']['trial_data_key'] = self._save_in_submodule(
                                'Synthesizer', _syn_result.data_syn, _trials)
                            self.synthesizer[(_load_trial_name
                                             ,_split_trial_name
                                             ,_split_data_key
                                             ,_preproc_trial_name
                                             ,_syn_trial_name)] = _syn_result

                                            #   'missingist' : getattr(_preproc_result ,'missingist' ,None)
                            _postproc_para = {'encoder'    : getattr(_preproc_result ,'encoder'    ,None)
                                             ,'scaler'     : getattr(_preproc_result ,'scaler'     ,None)
                            }
                            _trials['postproc'] = {'trial_name': _preproc_trial_name}
                            _postproc_result = self._run_single_postprocessor(
                                _syn_result.data_syn, _trials['postproc'] ,_postproc_para)
                            _trials['postproc']['trial_data_key'] = self._save_in_submodule(
                                'Postprocessor', _postproc_result.data, _trials)

                            for _eval_trial, (_eval_trial_name, _eval_para) in enumerate(self.para['Evaluator_setting'].items()):
                                _trials['eval'] = {'trial': _eval_trial+1, 'trial_name': _eval_trial_name, 'trial_max': _eval_trial_max
                                                  ,'trial_evals': _eval_trial_evals, 'trial_evals_sum': _eval_trial_evals_sum}
                                for _eval_trial_key in range(_eval_trial_evals[_eval_trial]):
                                    _trials['eval']['eval_trial_key'] = _eval_trial_key+1
                                    _eval_result = self._run_single_evaluator(
                                        {'ori'     : _split_data['train']
                                        ,'syn'     : _postproc_result.data
                                        ,'control' : _split_data['validation']
                                        }, _trials['eval'], _eval_para)
                                    _eval_name = (_load_trial_name
                                                 ,_split_trial_name
                                                 ,_split_data_key
                                                 ,_preproc_trial_name
                                                 ,_syn_trial_name
                                                 ,_eval_trial_name
                                                 ,_eval_trial_key+1)
                                    
                                    from . import __version__
                                    _eval_fullname = (__version__
                                                     ,self.exectime
                                                     ,_load_trial_name
                                                     ,_split_trial_name
                                                     ,_trials['split']['trial_split']
                                                     ,_split_data_key
                                                     ,_preproc_trial_name.split('-')[0]
                                                     ,_preproc_trial_name.split('-')[1]
                                                     ,_preproc_trial_name.split('-')[2]
                                                     ,_preproc_trial_name.split('-')[3]
                                                     ,_syn_trial_name.split('-')[0]
                                                     ,'-'.join(_syn_trial_name.split('-')[1:])
                                                     ,_eval_trial_name.split('-')[0]
                                                     ,'-'.join(_eval_trial_name.split('-')[1:])
                                                     ,_eval_trial_evals[_eval_trial]
                                                     ,_eval_trial_key+1
                                                     )
                                    _trials['eval']['trial_data_key'] = self._save_in_submodule('Evaluator'
                                                           ,(_eval_fullname
                                                            ,_eval_result)
                                                            ,_trials)
                                    self.evaluator[_eval_name] = _eval_result

        print(f"====== ====== ====== ====== ====== ======")
        print(f"Executor (run_single_process): Total execution time: {round(time.time()-_time_start ,4)} sec.")
        print(f"====== ====== ====== ====== ====== ======")



    # def _monitor_cpu_usage(self, interval=10):
    #     import psutil
    #     import time
    #     while self.monitor_cpu_usage:
    #         cpu_usage = psutil.cpu_percent(interval=None)
    #         print(f"CPU usage: {cpu_usage:>5}%" ,end="\r" ,flush=True)
    #         time.sleep(interval)


    def run(self):
        import time
        import os
        # import threading
        from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
        from tqdm import tqdm
        from copy import deepcopy

        _time_start = time.time()

        # self.monitor_cpu_usage = True
        # _monitor_thread = threading.Thread(target=self._monitor_cpu_usage, args=(1,), daemon=True)
        # _monitor_thread.start()

        _max_workers = os.cpu_count()

        self._save_in_submodule(module='Executor_Start')

        _load_trial_max = len(self.para['Loader_setting'])
        _split_trial_max = len(self.para['Splitter_setting'])
        _preproc_trial_max = len(self.para['Preprocessor_setting'])
        _syn_trial_max = len(self.para['Synthesizer_setting'])
        _eval_trial_max = len(self.para['Evaluator_setting'])

        _split_trial_splits = [setting['num_samples'] if 'num_samples' in setting else 1 for setting in self.para['Splitter_setting'].values()]
        _split_trial_splits_sum = sum(_split_trial_splits)

        _eval_trial_evals = [setting['num_samples'] if 'num_samples' in setting else 1 for setting in self.para['Evaluator_setting'].values()]
        _eval_trial_evals_sum = sum(_eval_trial_evals)

        self.loader = {}
        self.splitter = {}
        self.preprocessor = {}
        self.synthesizer = {}
        self.postprocessor = {}
        self.evaluator = {}

        _trials = {}
        with tqdm(total=_load_trial_max         ,desc='Loading: '      ) as _load_pbar\
            ,tqdm(total=_load_trial_max\
                       *_split_trial_max        ,desc='Splitting: '    ) as _split_pbar\
            ,tqdm(total=_load_trial_max\
                       *_split_trial_splits_sum\
                       *_preproc_trial_max      ,desc='Preprocessing: ') as _preproc_pbar:
            with ProcessPoolExecutor(max_workers=_max_workers) as _poolexecutor:
                _preproc_futures = {}
                for _load_trial, (_load_trial_name, _load_para) in enumerate(self.para['Loader_setting'].items()):
                    _trials['load'] = {'trial'       : _load_trial+1
                                       ,'trial_name' : _load_trial_name
                                       ,'trial_max'  : _load_trial_max}
                    _load_result = _poolexecutor.submit(
                        self._run_single_loader, _trials['load'], _load_para).result()
                    self.loader[_load_trial_name] = _load_result
                    _load_pbar.update(1)

                    for _split_trial, (_split_trial_name, _split_para) in enumerate(self.para['Splitter_setting'].items()):
                        _trials['split'] = {'trial'            : _split_trial+1
                                            ,'trial_name'      : _split_trial_name
                                            ,'trial_max'       : _split_trial_max
                                            ,'trial_splits'    : _split_trial_splits
                                            ,'trial_split_sum' : _split_trial_splits_sum}
                        _split_result = _poolexecutor.submit(
                            self._run_single_splitter, _load_result.data, _trials['split'], _split_para).result()
                        _trials['split']['trial_split'] = len(_split_result.data)
                        _trials['split']['trial_data_key'] = _poolexecutor.submit(self._save_in_submodule
                                                                                 ,'Splitter'
                                                                                 ,_split_result.data
                                                                                 ,deepcopy(_trials)).result()
                        self.splitter[(_load_trial_name
                                      ,_split_trial_name)] = _split_result
                        _split_pbar.update(1)

                        _trials['split']['data_key'] = {}
                        for _split_data_key ,_split_data in _split_result.data.items():
                            _trials['split']['data_key'] = _split_data_key

                            for _preproc_trial ,(_preproc_trial_name ,_preproc_para) in enumerate(self.para['Preprocessor_setting'].items()):
                                _trials['preproc'] = {'trial'      : _preproc_trial+1
                                                     ,'trial_name' : _preproc_trial_name
                                                     ,'trial_max'  : _preproc_trial_max}
                                _preproc_future = _poolexecutor.submit(self._run_single_preprocessor
                                                                       ,_split_data['train']
                                                                       ,deepcopy(_trials['preproc'])
                                                                       ,_preproc_para)
                                _preproc_futures[_preproc_future] = {'name' : (_load_trial_name
                                                                              ,_split_trial_name
                                                                              ,_split_data_key
                                                                              ,_preproc_trial_name)
                                                                    ,'trials' : deepcopy(_trials)
                                }

                # Should wait all preprocessing done due to SDV share same temp file '.sample.csv.temp' in synthesizing, will cause Permission Error
                # PermissionError: [WinError 32] 程序無法存取檔案，因為檔案正由另一個程序使用。: '.sample.csv.temp'
                _trials_till_preproc = {}
                for _preproc_future in as_completed(_preproc_futures):
                    _preproc_result = _preproc_future.result()
                    _preproc_name = _preproc_futures[_preproc_future]['name']
                    self.preprocessor[_preproc_name] = _preproc_result
                    _trials_preproc = _preproc_futures[_preproc_future]['trials']
                    _trials_preproc['preproc']['trial_data_key'] = _poolexecutor.submit(self._save_in_submodule
                                                                                       ,'Preprocessor'
                                                                                       ,_preproc_result.data
                                                                                       ,deepcopy(_trials_preproc)).result()
                    _trials_till_preproc[_preproc_name] = _trials_preproc
                    _preproc_pbar.update(1)


        with tqdm(total=_load_trial_max
                       *_split_trial_splits_sum\
                       *_preproc_trial_max\
                       *_syn_trial_max          ,desc='Synthesizing: ' ) as _syn_pbar\
            ,tqdm(total=_load_trial_max
                       *_split_trial_splits_sum\
                       *_preproc_trial_max\
                       *_syn_trial_max          ,desc='Postprocessing: ' ) as _postproc_pbar\
            ,tqdm(total=_load_trial_max
                       *_split_trial_splits_sum\
                       *_preproc_trial_max\
                       *_syn_trial_max\
                       *_eval_trial_evals_sum  ,desc='Evaluating: ') as _eval_pbar:
            with ThreadPoolExecutor(max_workers=_max_workers) as _threadexecutor:
                _syn_futures = {}
                for _trials_name ,_trials_preproc in _trials_till_preproc.items():
                    for _syn_trial ,(_syn_trial_name ,_syn_para) in enumerate(self.para['Synthesizer_setting'].items()):
                        _trials_preproc['syn'] = {'trial'      : _syn_trial+1
                                                 ,'trial_name' : _syn_trial_name
                                                 ,'trial_max'  : _syn_trial_max}
                        import random
                        _syn_fullname = _trials_name + (_syn_trial_name, )
                        _syn_future = _threadexecutor.submit(self._run_single_synthesizer
                                                            ,_preproc_result.data
                                                            ,_trials_preproc['syn']
                                                            ,_syn_para
                                                            ,trial_fullname = _syn_fullname+(str(random.uniform(0, 99999999)).zfill(8), ))
                        _syn_futures[_syn_future] = {'name': _syn_fullname
                                                    ,'trials' : deepcopy(_trials_preproc)}
                
                for _syn_future in as_completed(_syn_futures):
                    _syn_result = _syn_future.result()
                    _syn_name   = _syn_futures[_syn_future]['name']
                    _trials_syn = _syn_futures[_syn_future]['trials']
                    self.synthesizer[_syn_name] = _syn_result
                    _trials_syn['syn']['trial_data_key'] = _threadexecutor.submit(self._save_in_submodule
                                                                                ,'Synthesizer'
                                                                                ,_syn_result.data_syn
                                                                                ,deepcopy(_trials_syn)).result()
                    _syn_pbar.update(1)

                    _trials_syn['postproc'] = {'trial_name': _preproc_trial_name}
                                    #   'missingist' : getattr(self.preprocessor[_syn_trial_name[0:-1]] ,'missingist' ,None)
                    _postproc_para = {'encoder': getattr(self.preprocessor[_syn_name[0:-1]] ,'encoder'    ,None)
                                     ,'scaler' : getattr(self.preprocessor[_syn_name[0:-1]] ,'scaler'     ,None)
                    }
                    _postproc_result = _threadexecutor.submit(self._run_single_postprocessor
                                                             ,_syn_result.data_syn
                                                             ,deepcopy(_trials_syn['postproc'])
                                                             ,_postproc_para).result()
                    _postproc_name = _syn_name
                    self.postprocessor[_postproc_name] = _postproc_result
                    _trials_syn['postproc']['trial_data_key'] = self._save_in_submodule('Postprocessor'
                                                                                  ,_postproc_result.data, deepcopy(_trials_syn))
                    _postproc_pbar.update(1)

                    for _eval_trial, (_eval_trial_name, _eval_para) in enumerate(self.para['Evaluator_setting'].items()):
                        _trials_syn['eval'] = {'trial': _eval_trial+1, 'trial_name': _eval_trial_name, 'trial_max': _eval_trial_max
                                          ,'trial_evals': _eval_trial_evals, 'trial_evals_sum': _eval_trial_evals_sum}
                        for _eval_trial_key in range(_eval_trial_evals[_eval_trial]):
                            _trials_syn['eval']['eval_trial_key'] = _eval_trial_key+1
                            _eval_result = _threadexecutor.submit(self._run_single_evaluator
                                                                ,{'ori'     : self.splitter[_syn_fullname[0:2]].data[_syn_fullname[2]]['train']
                                                                    ,'syn'     : _postproc_result.data
                                                                    ,'control' : self.splitter[_syn_fullname[0:2]].data[_syn_fullname[2]]['validation']
                                                                    }
                                                                ,deepcopy(_trials_syn['eval'])
                                                                ,_eval_para).result()
                            _eval_name = _postproc_name + (_eval_trial_name,_eval_trial_key+1)
                            from . import __version__
                            _eval_fullname = (__version__
                                             ,self.exectime
                                             ,_load_trial_name
                                             ,_split_trial_name
                                             ,_trials['split']['trial_split']
                                             ,_split_data_key
                                             ,_preproc_trial_name.split('-')[0]
                                             ,_preproc_trial_name.split('-')[1]
                                             ,_preproc_trial_name.split('-')[2]
                                             ,_preproc_trial_name.split('-')[3]
                                             ,_syn_trial_name.split('-')[0]
                                             ,'-'.join(_syn_trial_name.split('-')[1:])
                                             ,_eval_trial_name.split('-')[0]
                                             ,'-'.join(_eval_trial_name.split('-')[1:])
                                             ,_eval_trial_evals[_eval_trial]
                                             ,_eval_trial_key+1
                                             )
                            _trials_syn['eval']['trial_data_key'] = _threadexecutor.submit(self._save_in_submodule
                                                                                        ,'Evaluator'
                                                                                        ,(_eval_fullname ,_eval_result)
                                                                                        ,deepcopy(_trials_syn)).result()
                            self.evaluator[_eval_name] = _eval_result
                            _eval_pbar.update(1)



        # self.monitor_cpu_usage = False
        # _monitor_thread.join()

        print(f"====== ====== ====== ====== ====== ======")
        print(f"Executor (run): Total execution time: {round(time.time()-_time_start ,4)} sec.")
        print(f"====== ====== ====== ====== ====== ======")

    def _run_single_loader(self, trial, para, **kwargs):
        import time
        _time_start = time.time()
        from .Loader import Loader
        loader = Loader(**para)
        print(
            f"Executor - Loader: {trial['trial_name']} loading time: {round(time.time()-_time_start ,4)} sec.")
        return loader

    def _run_single_splitter(self, data, trial, para):
        import time
        _time_start = time.time()
        from .Loader import Splitter
        splitter = Splitter(data=data, **para)
        print(
            f"Executor - Splitter: {trial['trial_name']} splitting time: {round(time.time()-_time_start ,4)} sec.")
        return splitter

    def _run_single_preprocessor(self, data, trial, para):
        import time
        _time_start = time.time()
        from .Preprocessor import Preprocessor
        preprocessor = Preprocessor(data=data, **para)
        print(
            f"Executor - Preprocessor: {trial['trial_name']} preprocessing time: {round(time.time()-_time_start ,4)} sec.")
        return preprocessor

    def _run_single_synthesizer(self, data, trial, para, **kwargs):
        import time
        _time_start = time.time()
        from .Synthesizer import Synthesizer
        synthesizer = Synthesizer(data=data, **para)
        _trial_fullname = kwargs.get('trial_fullname' ,None)
        if _trial_fullname:
            import os
            _trial_tempfile = f".sample.csv.temp.{'-'.join(str(item) for item in _trial_fullname)}"
            synthesizer.fit_sample(output_file_path=_trial_tempfile)
            if os.path.exists(_trial_tempfile):
                os.remove(_trial_tempfile)
        else:
            synthesizer.fit_sample()
        print(f"Executor - Synthesizer: {trial['trial_name']} synthesizing time: {round(time.time()-_time_start ,4)} sec.")
        return synthesizer

    def _run_single_postprocessor(self, data, trial ,para):
        import time
        _time_start = time.time()
        from .Postprocessor import Postprocessor
        postprocessor = Postprocessor(data=data ,**para)
        print(f"Executor - Postprocessor: postprocessing time: {round(time.time()-_time_start ,4)} sec.")
        return postprocessor

    def _run_single_evaluator(self, data, trial, para):
        import time
        _time_start = time.time()
        from .Evaluator import Evaluator
        if trial['trial_name'].endswith('inference'):
            _columns = data['syn'].columns
            evaluator = {}
            for _column in _columns:
                para['anonymeter_secret'] = _column
                evaluator[_column] = Evaluator(data=data ,**para)
                evaluator[_column].eval()
        else:
            evaluator = Evaluator(data=data ,**para)
            evaluator.eval()
        print(f"Executor - Evaluator: {trial['trial_name']} at {trial['eval_trial_key']} trials evaluating time: {round(time.time()-_time_start ,4)} sec.")
        return evaluator

    def _save_in_submodule(self, module, data=None, trials=None):
        _filename_prog = f"{self.outputname}_Executor.txt"
        _exist_module_setting = False
        if not module.startswith('Executor'):
            _str_module_setting = f"Module {module} setting:\n"
            with open(_filename_prog, 'r') as _prog:
                for _line in _prog:
                    if _line == _str_module_setting:
                        _exist_module_setting = True
                        break
            if not _exist_module_setting:
                with open(_filename_prog, "a") as _prog:
                    _prog.write(f"====== ====== ====== ====== ====== ======\n")
                    _prog.write(_str_module_setting)
                    _prog.write(f"====== ====== ====== ====== ====== ======\n")

        if module == 'Executor_Start':
            with open(_filename_prog, "w") as _prog:
                _prog.write(f"{self.outputname}\n")
            return None

        elif module == 'Splitter':
            _load_trial = trials['load']['trial']
            _split_trial = trials['split']['trial']
            _load_trial_name = trials['load']['trial_name']
            _split_trial_name = trials['split']['trial_name']
            _load_trial_max = trials['load']['trial_max']
            _split_trial_max = trials['split']['trial_max']
            _split_trial_split = trials['split']['trial_split']
            _digit_split_trial_split = len(str(_split_trial_split))
            _split_trial_splits_sum = trials['split']['trial_split_sum']
            _split_trial_splits = trials['split']['trial_splits']
            _ttl_trial = _load_trial_max * _split_trial_max * _split_trial_splits_sum
            _digit_ttl_trial = len(str(_ttl_trial))
            """
            # trial = (# Loading file - 1) * (# TTL Loading x # TTL Splitting)
                    + (Sum of # Splitting setting before this Splitting)
                    + (# Split data key (which add later in loop))
            """
            _trial_key = (_load_trial - 1) * _split_trial_splits_sum + \
                sum(_split_trial_splits[:(_split_trial-1)])
            _trial_data_key = {}
            with open(_filename_prog, "a") as _prog:
                for _data_key, _data in data.items():
                    _trial_key_now = _trial_key+_data_key
                    _str_trial_key_now = str(
                        _trial_key_now).zfill(_digit_ttl_trial)
                    _str_data_key = str(_data_key).zfill(
                        _digit_split_trial_split)
                    _str_trial = f"Load[{_load_trial_name}]_Split[{_split_trial_name}][{_split_trial_split}-{_str_data_key}]"
                    _prog.write(f"Trial {_str_trial_key_now} = {_str_trial}.\n")
                    _data['train'].to_csv(
                        f"{self.outputname}_Trial[{_str_trial_key_now}][Ori].csv", index=False)
                    _data['validation'].to_csv(
                        f"{self.outputname}_Trial[{_str_trial_key_now}][Ctrl].csv", index=False)
                    _trial_data_key[_data_key] = (_str_trial_key_now, _str_trial)
            return _trial_data_key

        elif module == 'Preprocessor':
            _str_split_trial_key = trials['split']['trial_data_key'][trials['split']['data_key']][0]
            _str_split_trial = trials['split']['trial_data_key'][trials['split']['data_key']][1]
            _preproc_trial_name = trials['preproc']['trial_name']
            _preproc_trial = trials['preproc']['trial']
            _preproc_trial_max = trials['preproc']['trial_max']
            _digit_preproc_trial_max = len(str(_preproc_trial_max))
            _str_preproc_trial = str(_preproc_trial).zfill(_digit_preproc_trial_max)

            _str_trial_key = f"{_str_split_trial_key}-{_str_preproc_trial}"
            _str_trial = f"{_str_split_trial}_Preproc[{_preproc_trial_name}]"

            _trial_data_key = (_str_trial_key, _str_trial)
            with open(_filename_prog, "a") as _prog:
                _prog.write(f"Trial {_str_trial_key} = {_str_trial}.\n")
                data.to_csv(
                    f"{self.outputname}_Trial[{_str_trial_key}].csv", index=False)
            return _trial_data_key

        elif module == 'Synthesizer':
            _str_preproc_trial_key = trials['preproc']['trial_data_key'][0]
            _preproc_trial = trials['preproc']['trial_data_key'][1]
            _syn_trial_name = trials['syn']['trial_name']
            _syn_trial = trials['syn']['trial']
            _syn_trial_max = trials['syn']['trial_max']
            _digit_syn_trial_max = len(str(_syn_trial_max))
            _str_syn_trial = str(_syn_trial).zfill(_digit_syn_trial_max)

            _str_trial_key = f"{_str_preproc_trial_key}-{_str_syn_trial}"
            _str_trial = f"{_preproc_trial}_Syn[{_syn_trial_name}]"

            _trial_data_key = (_str_trial_key, _str_trial)
            with open(_filename_prog, "a") as _prog:
                _prog.write(f"Trial {_str_trial_key} = {_str_trial}.\n")
                data.to_csv(
                    f"{self.outputname}_Trial[{_str_trial_key}].csv", index=False)
            return _trial_data_key

        elif module == 'Postprocessor':
            _str_trial_key = trials['syn']['trial_data_key'][0]
            _str_trial = trials['syn']['trial_data_key'][1]

            _trial_data_key = (_str_trial_key, _str_trial)
            with open(_filename_prog, "a") as _prog:
                _prog.write(f"Trial {_str_trial_key} = {_str_trial}.\n")
                data.to_csv(f"{self.outputname}_Trial[{_str_trial_key}]Postproc.csv", index=False)
            return _trial_data_key


        elif module == 'Evaluator':
            import os

            _str_postproc_trial_key = trials['postproc']['trial_data_key'][0]
            _postproc_trial = trials['postproc']['trial_data_key'][1]
            _eval_trial_name = trials['eval']['trial_name']
            _eval_trial = trials['eval']['trial']
            _eval_trial_max = trials['eval']['trial_max']
            _digit_eval_trial_max = len(str(_eval_trial_max))
            _str_eval_trial = str(_eval_trial).zfill(_digit_eval_trial_max)

            _eval_trial_key = trials['eval']['eval_trial_key']
            _eval_trial_key_max = max(trials['eval']['trial_evals'])
            _digit_eval_trial_key_max = len(str(_eval_trial_key_max))
            _str_eval_trial_key = str(_eval_trial_key).zfill(_digit_eval_trial_key_max)

            _str_trial_key = f"{_str_postproc_trial_key}-{_str_eval_trial}-{_str_eval_trial_key}"
            _str_trial = f"{_postproc_trial}_Eval[{_eval_trial_name}-{_str_eval_trial_key}]"

            _trial_data_key = (_str_trial_key, _str_trial)
            with open(_filename_prog, "a") as _prog:
                _prog.write(f"Trial {_str_trial_key} = {_str_trial}.\n")

            _rpt_columns = ','.join(['PETsARD_version'
                                    ,'exec_exectime'
                                    ,'exec_trial'
                                    ,'load_filename'
                                    ,'split_ratio'
                                    ,'split_samples'
                                    ,'split_Num'
                                    ,'preproc_missing_method'
                                    ,'preproc_outlier_method'
                                    ,'preproc_encoding_method'
                                    ,'preproc_scaling_method'
                                    ,'syn_method_library'
                                    ,'syn_method'
                                    ,'eval_method_library'
                                    ,'eval_method'
                                    ,'eval_samples'
                                    ,'eval_Num'
                                    ])
            _data_infor = data[0][:2]+(_str_trial_key,)+data[0][2:]
            _rpt_line = ','.join([str(item) for item in _data_infor])
            if _eval_trial_name.startswith('anonymeter'):
                _eval_module = 'Anonymeter'
                _rpt_columns += ','+','.join(['secret'
                                             ,'Risk'
                                             ,'Risk_CI_btm'
                                             ,'Risk_CI_top'
                                             ,'Attack_Rate'
                                             ,'Attack_Rate_err'
                                             ,'Baseline_Rate'
                                             ,'Baseline_Rate_err'
                                             ,'Control_Rate'
                                             ,'Control_Rate_err'
                                             ])

                if _eval_trial_name.endswith('inference'):
                    for _data_secret ,_data_Evaluator in data[1].items():
                        _data_score  = _data_Evaluator.Evaluator.evaluation
                        _data_score = ','.join([f"{item:.16f}" for item in 
                                                        [_data_score['Risk'             ]
                                                        ,_data_score['Risk_CI_btm'      ]
                                                        ,_data_score['Risk_CI_top'      ]
                                                        ,_data_score['Attack_Rate'      ]
                                                        ,_data_score['Attack_Rate_err'  ]
                                                        ,_data_score['Baseline_Rate'    ]
                                                        ,_data_score['Baseline_Rate_err']
                                                        ,_data_score['Control_Rate'     ]
                                                        ,_data_score['Control_Rate_err' ]
                                                        ]
                                            ])
                        _rpt_line += f",{_data_secret},{_data_score}"
                else:
                    _data_secret = ''
                    _data_score  = data[1].Evaluator.evaluation
                    _data_score = ','.join([f"{item:.16f}" for item in 
                                                    [_data_score['Risk'             ]
                                                    ,_data_score['Risk_CI_btm'      ]
                                                    ,_data_score['Risk_CI_top'      ]
                                                    ,_data_score['Attack_Rate'      ]
                                                    ,_data_score['Attack_Rate_err'  ]
                                                    ,_data_score['Baseline_Rate'    ]
                                                    ,_data_score['Baseline_Rate_err']
                                                    ,_data_score['Control_Rate'     ]
                                                    ,_data_score['Control_Rate_err' ]
                                                    ]
                                        ])
                    _rpt_line += f",{_data_secret},{_data_score}"
            else:
                _eval_module = 'Unknown'
                _rpt_columns += ',Unknown'
                _rpt_line    += f',{data[1]}'
            _filename_rpt = f"{self.outputname}_Report_{_eval_module}.csv"

            if not os.path.exists(_filename_rpt):
                with open(_filename_rpt, "w") as _rpt:
                    _rpt.write(f"{_rpt_columns}\n")

            with open(_filename_rpt, "a") as _rpt:
                _rpt.write(f"{_rpt_line}\n")

            return _trial_data_key
