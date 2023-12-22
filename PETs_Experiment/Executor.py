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

        _list_module = ['Loader', 'Splitter', 'Preprocessor', 'Synthesizer']
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
        elif module == 'Spitter':
            # num_sample and train_split_ratio follows default of Splitter
            _num_sample = str(subpara['num_samples']
                              ) if 'num_samples' in subpara else '1'
            _train_split_ratio = str(
                subpara['train_split_ratio']) if 'train_split_ratio' in subpara else '0.8'
            _trial_name = '-'.join([_num_sample, _train_split_ratio])
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

        _split_trial_splits = [
            setting['num_samples'] if 'num_samples' in setting else 1 for setting in self.para['Splitter_setting'].values()]
        _split_trial_split_sum = sum(_split_trial_splits)

        self.loader = {}
        self.splitter = {}
        self.preprocessor = {}
        self.synthesizer = {}
        _trials = {}
        for _load_trial, (_load_trial_name, _load_para) in enumerate(self.para['Loader_setting'].items()):
            _trials['load'] = {'trial': _load_trial+1, 'trial_name': _load_trial_name, 'trial_max': _load_trial_max}
            _load_result = self._run_single_loader(_trials['load'], _load_para)
            self.loader[_load_trial_name] = _load_result

            for _split_trial, (_split_trial_name, _split_para) in enumerate(self.para['Splitter_setting'].items()):
                _trials['split'] = {'trial': _split_trial+1, 'trial_name': _split_trial_name, 'trial_max': _split_trial_max,
                                    'trial_splits': _split_trial_splits, 'trial_split_sum': _split_trial_split_sum}
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
                        _trials['preproc'] = {
                            'trial': _preproc_trial+1, 'trial_name': _preproc_trial_name, 'trial_max': _preproc_trial_max}
                        _preproc_result = self._run_single_preprocessor(
                            _split_data['train'], _trials['preproc'], _preproc_para)
                        _trials['preproc']['trial_data_key'] = self._save_in_submodule(
                            'Preprocessor', _preproc_result.data, _trials)
                        self.preprocessor[(
                            _load_trial_name, _split_trial_name, _preproc_trial_name)] = _preproc_result

                        for _syn_trial, (_syn_trial_name, _syn_para) in enumerate(self.para['Synthesizer_setting'].items()):
                            _trials['syn'] = {
                                'trial': _syn_trial+1, 'trial_name': _syn_trial_name, 'trial_max': _syn_trial_max}
                            _syn_result = self._run_single_synthesizer(
                                _preproc_result.data, _trials['syn'], _syn_para)
                            self._save_in_submodule(
                                'Synthesizer', _syn_result.data_syn, _trials)
                            self.synthesizer[(
                                _load_trial_name, _split_trial_name, _preproc_trial_name, _syn_trial_name)] = _syn_result

        print(f"====== ====== ====== ====== ====== ======")
        print(
            f"Executor: Total execution time: {round(time.time()-_time_start ,4)} sec.")
        print(f"====== ====== ====== ====== ====== ======")



    def _monitor_cpu_usage(self, interval=10):
        import psutil
        import time
        while self.monitor_cpu_usage:
            cpu_usage = psutil.cpu_percent(interval=None)
            print(f"CPU usage: {cpu_usage:>5}%" ,end="\r" ,flush=True)
            time.sleep(interval)


    def run(self):
        import time
        import os
        import threading
        from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
        from tqdm import tqdm

        _time_start = time.time()

        self.monitor_cpu_usage = True
        _monitor_thread = threading.Thread(target=self._monitor_cpu_usage, args=(1,), daemon=True)
        _monitor_thread.start()

        _max_workers = os.cpu_count()

        self._save_in_submodule(module='Executor_Start')

        _load_trial_max = len(self.para['Loader_setting'])
        _split_trial_max = len(self.para['Splitter_setting'])
        _preproc_trial_max = len(self.para['Preprocessor_setting'])
        _syn_trial_max = len(self.para['Synthesizer_setting'])
        _split_trial_splits = [setting['num_samples'] if 'num_samples' in setting else 1 for setting in self.para['Splitter_setting'].values()]
        _split_trial_split_sum = sum(_split_trial_splits)

        self.loader = {}
        self.splitter = {}
        self.preprocessor = {}
        self.synthesizer = {}

        with tqdm(total=_load_trial_max         ,desc='Loading: '      ) as _load_pbar\
            ,tqdm(total=_load_trial_max\
                       *_split_trial_max        ,desc='Splitting: '    ) as _split_pbar\
            ,tqdm(total=_load_trial_max\
                       *_split_trial_split_sum\
                       *_preproc_trial_max      ,desc='Preprocessing: ') as _preproc_pbar:
            with ProcessPoolExecutor(max_workers=_max_workers) as _poolexecutor:

                _trials = {}
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
                                            ,'trial_split_sum' : _split_trial_split_sum}
                        _split_result = _poolexecutor.submit(
                            self._run_single_splitter, _load_result.data, _trials['split'], _split_para).result()
                        _trials['split']['trial_split'] = len(_split_result.data)
                        _trials['split']['trial_data_key'] = _poolexecutor.submit(self._save_in_submodule
                                                                                                  ,'Splitter'
                                                                                                  ,_split_result.data
                                                                                                  ,_trials).result()
                        self.splitter[(_load_trial_name
                                       ,_split_trial_name)] = _split_result
                        _split_pbar.update(1)

                        _trials['split']['data_key'] = {}
                        for _split_data_key ,_split_data in _split_result.data.items():
                            _trials['split']['data_key'] = _split_data_key

                            for _preproc_trial ,(_preproc_trial_name ,_preproc_para) in enumerate(self.para['Preprocessor_setting'].items()):
                                _trials['preproc'] = {'trial'       : _preproc_trial+1
                                                      ,'trial_name' : _preproc_trial_name
                                                      ,'trial_max'  : _preproc_trial_max}
                                _preproc_future = _poolexecutor.submit(self._run_single_preprocessor
                                                                       ,_split_data['train']
                                                                       ,_trials['preproc']
                                                                       ,_preproc_para)
                                _preproc_futures[_preproc_future] = {'name' : (_load_trial_name
                                                                              ,_split_trial_name
                                                                              ,_split_data_key
                                                                              ,_preproc_trial_name)
                                                                    ,'trials' : _trials 
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
                                                                                       ,_trials_preproc).result()
                    _trials_till_preproc[_preproc_name] = _trials_preproc
                    _preproc_pbar.update(1)


        with tqdm(total=_load_trial_max
                       *_split_trial_split_sum\
                       *_preproc_trial_max\
                       *_syn_trial_max          ,desc='Synthesizing: ' ) as _syn_pbar:
            with ThreadPoolExecutor(max_workers=_max_workers) as _threadexecutor:
                _syn_futures = {}
                for _trials_name ,_trials_preproc in _trials_till_preproc.items():
                    for _syn_trial ,(_syn_trial_name ,_syn_para) in enumerate(self.para['Synthesizer_setting'].items()):
                        _trials_preproc['syn'] = {'trial'       : _syn_trial+1
                                                  ,'trial_name' : _syn_trial_name
                                                  ,'trial_max'  : _syn_trial_max}
                        _syn_fullname = _trials_name + (_syn_trial_name,)
                        _syn_future = _threadexecutor.submit(self._run_single_synthesizer
                                                            ,_preproc_result.data
                                                            ,_trials_preproc['syn']
                                                            ,_syn_para
                                                            ,trial_fullname = _syn_fullname)
                        _syn_futures[_syn_future] = {'name': _syn_fullname
                                                    ,'trials' : _trials_preproc}
                
                for _syn_future in as_completed(_syn_futures):
                    _syn_result = _syn_future.result()
                    _syn_trial_name = _syn_futures[_syn_future]['name']
                    _trials_syn = _syn_futures[_syn_future]['trials']
                    _threadexecutor.submit(self._save_in_submodule
                                            ,'Synthesizer'
                                            ,_syn_result.data_syn
                                            ,_trials_syn).result()
                    self.synthesizer[_syn_trial_name] = _syn_result
                    _syn_pbar.update(1)

        self.monitor_cpu_usage = False
        _monitor_thread.join()

        print(f"====== ====== ====== ====== ====== ======")
        print(f"Executor: Total execution time: {round(time.time()-_time_start ,4)} sec.")
        print(f"====== ====== ====== ====== ====== ======")

    def _run_single_loader(self, trial, para, **kwargs):
        import time
        _time_start = time.time()
        from .Loader import Loader
        loader = Loader(**para)
        print(
            f"Executor - Loader: {trial['trial_name']} loading time: {round(time.time()-_time_start ,4)} sec.")
        return loader

    def _run_single_splitter(self, data, trial, para, **kwargs):
        import time
        _time_start = time.time()
        from .Loader import Splitter
        splitter = Splitter(data=data, **para)
        print(
            f"Executor - Splitter: {trial['trial_name']} splitting time: {round(time.time()-_time_start ,4)} sec.")
        return splitter

    def _run_single_preprocessor(self, data, trial, para, **kwargs):
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

    def _save_in_submodule(self, module, data=None, trials=None):
        _filename_rpt = f"{self.outputname}_Executor.txt"
        _exist_module_setting = False
        if not module.startswith('Executor'):
            _str_module_setting = f"Module {module} setting:\n"
            with open(_filename_rpt, 'r') as _rpt:
                for _line in _rpt:
                    if _line == _str_module_setting:
                        _exist_module_setting = True
                        break
            if not _exist_module_setting:
                with open(_filename_rpt, "a") as _rpt:
                    _rpt.write(f"====== ====== ====== ====== ====== ======\n")
                    _rpt.write(_str_module_setting)
                    _rpt.write(f"====== ====== ====== ====== ====== ======\n")

        if module == 'Executor_Start':
            with open(_filename_rpt, "w") as _rpt:
                _rpt.write(f"{self.outputname}\n")
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
            _split_trial_split_sum = trials['split']['trial_split_sum']
            _split_trial_splits = trials['split']['trial_splits']
            _ttl_trial = _load_trial_max * _split_trial_max * _split_trial_split_sum
            _digit_ttl_trial = len(str(_ttl_trial))
            """
            # trial = (# Loading file - 1) * (# TTL Loading x # TTL Splitting)
                    + (Sum of # Splitting setting before this Splitting)
                    + (# Split data key (which add later in loop))
            """
            _trial_key = (_load_trial - 1) * _split_trial_split_sum + \
                sum(_split_trial_splits[:(_split_trial-1)])
            _trial_data_key = {}
            with open(_filename_rpt, "a") as _rpt:
                for _data_key, _data in data.items():
                    _trial_key_now = _trial_key+_data_key
                    _str_trial_key_now = str(
                        _trial_key_now).zfill(_digit_ttl_trial)
                    _str_data_key = str(_data_key).zfill(
                        _digit_split_trial_split)
                    _str_trail = f"Load[{_load_trial_name}]_Split[{_split_trial_name}][{_split_trial_split}-{_str_data_key}]"
                    _rpt.write(f"Trial {_str_trial_key_now} = {_str_trail}.\n")
                    _data['train'].to_csv(
                        f"{self.outputname}_Trial[{_str_trial_key_now}][Ori].csv", index=False)
                    _data['validation'].to_csv(
                        f"{self.outputname}_Trial[{_str_trial_key_now}][Ctrl].csv", index=False)
                    _trial_data_key[_data_key] = (
                        _str_trial_key_now, _str_trail)
            return _trial_data_key

        elif module == 'Preprocessor':
            _str_split_trial_key = trials['split']['trial_data_key'][trials['split']['data_key']][0]
            _str_split_trial = trials['split']['trial_data_key'][trials['split']['data_key']][1]
            _preproc_trial_name = trials['preproc']['trial_name']
            _preproc_trial = trials['preproc']['trial']
            _preproc_trial_max = trials['preproc']['trial_max']
            _digit_preproc_trial_max = len(str(_preproc_trial_max))
            _str_preproc_trial = str(_preproc_trial).zfill(
                _digit_preproc_trial_max)

            _str_trail_key = f"{_str_split_trial_key}-{_str_preproc_trial}"
            _str_trail = f"{_str_split_trial}_Preproc[{_preproc_trial_name}]"

            _trial_data_key = {}
            with open(_filename_rpt, "a") as _rpt:
                _rpt.write(f"Trial {_str_trail_key} = {_str_trail}.\n")
                data.to_csv(
                    f"{self.outputname}_Trial[{_str_trail_key}].csv", index=False)
                _trial_data_key = (_str_trail_key, _str_trail)
            return _trial_data_key

        elif module == 'Synthesizer':
            _str_preproc_trial_key = trials['preproc']['trial_data_key'][0]
            _preproc_trial = trials['preproc']['trial_data_key'][1]
            _syn_trial_name = trials['syn']['trial_name']
            _syn_trial = trials['syn']['trial']
            _syn_trial_max = trials['syn']['trial_max']
            _digit_syn_trial_max = len(str(_syn_trial_max))
            _str_syn_trial = str(_syn_trial).zfill(_digit_syn_trial_max)

            _str_trail_key = f"{_str_preproc_trial_key}-{_str_syn_trial}"
            _str_trail = f"{_preproc_trial}_Syn[{_syn_trial_name}]"

            _trial_data_key = {}
            with open(_filename_rpt, "a") as _rpt:
                _rpt.write(f"Trial {_str_trail_key} = {_str_trail}.\n")
                data.to_csv(
                    f"{self.outputname}_Trial[{_str_trail_key}].csv", index=False)
                _trial_data_key[_str_trail_key] = _str_trail
            return _trial_data_key
