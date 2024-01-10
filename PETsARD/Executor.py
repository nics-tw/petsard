from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from copy import deepcopy
from datetime import datetime
import os
# import psutil
import random
import time
# import threading
from tqdm import tqdm

# TODO get __version__
#     ImportError: cannot import name '__version__'
#     from partially initialized module 'PETsARD'
#     (most likely due to a circular import)
#     (...\PETsARD\PETsARD\__init__.py)
# from . import __version__
__version__ = '0.0.3'
from PETsARD.Loader import Loader
from PETsARD.Loader import Splitter
from PETsARD.Preprocessor import Preprocessor
from PETsARD.Synthesizer import Synthesizer
from PETsARD.Postprocessor import Postprocessor
from PETsARD.Evaluator import Evaluator


class Executor:

    def __init__(self, **kwargs):
        self.exectime = datetime.now().strftime('%Y%m%d-%H%M%S')
        self.outputname = f"PETsARD[{self.exectime}]"

        self.kwargs = kwargs
        self.para_handle()

    def para_handle(self):
        """
        有三種情況：

        1. 想跑單一種設定的單次執行：module 每個設定都直接表述，例如
            'Loader_filepath':  'adult.csv',
            'Loader_na_values': {k : '?' for k in [
                    'workclass',
                    'occupation',
                    'native-country'
                ]
            }
            'Spitternum_samples': 2,
            'Spittertrain_split_ratio': 0.8
            此時 module 可以留空或設定為 True (default)

        2. 想跳過這個 module
            此時 module 必須寫為 False。
            在 False 情況下，以該 module 打頭的設定全部都會被忽略

        3. 想跑多種設定：多種設定必須以 module 為單位進行字典的打包，例如
            'Loader' : {
                'adult' : {
                    'filepath': 'adult.csv',
                    'na_values': k : '?' for k in [
                        'workclass',
                        'occupation',
                        'native-country'
                    ]
                },
                'NHANES' : {
                    filepath = '../[sunset]/data/[NHANES] B.csv',
                    header_exist = False,
                    headernames=[
                        'gen','age','race','edu','mar',
                        'bmi','dep','pir','gh','mets','qm','dia'
                    ]
                }
            }
            'Spitternum_samples': 2,
            'Spittertrain_split_ratio': 0.8
            此時 module 必須為一個字典。
            字典鍵值會用作識別，字典內容在輸入變數時可省略 module
            請注意如果 module 字典已經被給定，外圍 module 打頭的設定會被忽略

        # Postprocessor 必跑所以不考慮
        """

        para = {}
        list_module = [
            'Loader',
            'Splitter',
            'Preprocessor',
            'Synthesizer',
            'Evaluator'
        ]

        for module in list_module:
            module_value = self.kwargs.get(module, True)
            if isinstance(module_value, dict):
                para[module] = True
                para[module+'_setting'] = module_value
            elif module_value:
                para[module] = True
                para[module+'_setting'] = {}
                subpara = {k.replace(module+'_', '', 1): v
                           for k, v in self.kwargs.items()
                           if k.startswith(module+'_')}
                name = self.para_handle_naming(module, subpara)
                para[module+'_setting'][name] = subpara
            else:
                para[module] = False

        if para['Preprocessor']:
            para['Postprocessor'] = True
            para['Postprocessor_setting'] = {}
        self.para = para

    def para_handle_naming(self, module, subpara):
        # Set the maximum filename length. This value is arbitrarily chosen.
        MAX_FILENAME = 36

        if module == 'Loader':
            trial_name = 'Default'
            if 'filepath' in subpara:
                filepath = os.path.basename(subpara['filepath'])
                trial_name = filepath[:MAX_FILENAME]
        elif module == 'Splitter':
            # num_samples and train_split_ratio follows default of Splitter
            num_samples = (
                str(subpara['num_samples']) if 'num_samples' in subpara
                else '1'
            )
            train_split_ratio = (
                str(subpara['train_split_ratio'])
                if 'train_split_ratio' in subpara
                else '0.8'
            )
            trial_name = f"{train_split_ratio}x{num_samples}"
        elif module == 'Preprocessor':
            list_preproc = []
            if 'missing_method' in subpara:
                list_preproc.append(subpara['missing_method'])
            if 'outlier_method' in subpara:
                list_preproc.append(subpara['outlier_method'])
            if 'encoding_method' in subpara:
                list_preproc.append(subpara['encoding_method'])
            if 'scaling_method' in subpara:
                list_preproc.append(subpara['scaling_method'])
            trial_name = '-'.join(list_preproc) if len(
                list_preproc) >= 1 else 'Default'
        elif module == 'Synthesizer':
            trial_name = (
                subpara['synthesizing_method']
                if 'synthesizing_method' in subpara
                else 'Default'
            )
        elif module == 'Evaluator':
            # num_samples follows default of Splitter
            num_samples = (
                str(subpara['num_samples']) if 'num_samples' in subpara
                else '1'
            )
            eval_method = (
                subpara['evaluating_method']
                if 'evaluating_method' in subpara
                else 'Default'
            )
            trial_name = f"{eval_method}x{num_samples}"
        else:
            trial_name = 'Default'

        return trial_name

    def run(self):
        time_start = time.time()

        self._save_in_submodule(module='Executor_Start')

        load_trial_max = len(self.para['Loader_setting'])
        split_trial_max = len(self.para['Splitter_setting'])
        preproc_trial_max = len(self.para['Preprocessor_setting'])
        syn_trial_max = len(self.para['Synthesizer_setting'])
        eval_trial_max = len(self.para['Evaluator_setting'])

        split_trial_splits = [
            setting['num_samples'] if 'num_samples' in setting else 1
            for setting in self.para['Splitter_setting'].values()
        ]
        split_trial_splits_sum = sum(split_trial_splits)
        eval_trial_evals = [
            setting['num_samples'] if 'num_samples' in setting else 1
            for setting in self.para['Evaluator_setting'].values()
        ]
        eval_trial_evals_sum = sum(eval_trial_evals)

        self.loader = {}
        self.splitter = {}
        self.preprocessor = {}
        self.synthesizer = {}
        self.evaluator = {}
        trials = {}
        for load_trial, (load_trial_name, load_para) in \
                enumerate(self.para['Loader_setting'].items()):
            trials['load'] = {
                'trial': load_trial+1,
                'trial_name': load_trial_name,
                'trial_max': load_trial_max
            }
            load_result = self._run_single_loader(trials['load'], load_para)
            self.loader[load_trial_name] = load_result

            for split_trial, (split_trial_name, split_para) in \
                    enumerate(self.para['Splitter_setting'].items()):
                trials['split'] = {
                    'trial': split_trial+1,
                    'trial_name': split_trial_name,
                    'trial_max': split_trial_max,
                    'trial_splits': split_trial_splits,
                    'trial_split_sum': split_trial_splits_sum
                }
                split_result = self._run_single_splitter(
                    load_result.data,
                    trials['split'],
                    split_para
                )
                trials['split']['trial_split'] = len(split_result.data)
                trials['split']['trial_data_key'] = self._save_in_submodule(
                    'Splitter',
                    split_result.data, trials
                )
                self.splitter[
                    (load_trial_name,
                     split_trial_name)
                ] = split_result

                for split_data_key, split_data in split_result.data.items():
                    trials['split']['data_key'] = split_data_key

                    for preproc_trial, (preproc_trial_name, preproc_para) in \
                            enumerate(
                                self.para['Preprocessor_setting'].items()
                    ):
                        trials['preproc'] = {
                            'trial': preproc_trial+1,
                            'trial_name': preproc_trial_name,
                            'trial_max': preproc_trial_max
                        }
                        preproc_result = self._run_single_preprocessor(
                            split_data['train'],
                            trials['preproc'],
                            preproc_para
                        )
                        trials['preproc']['trial_data_key'] = \
                            self._save_in_submodule(
                                'Preprocessor',
                                preproc_result.data,
                                trials
                        )
                        self.preprocessor[
                            (load_trial_name,
                             split_trial_name,
                             split_data_key,
                             preproc_trial_name)
                        ] = preproc_result

                        for syn_trial, (syn_trial_name, syn_para) in \
                                enumerate(
                                    self.para['Synthesizer_setting'].items()
                        ):
                            trials['syn'] = {
                                'trial': syn_trial+1,
                                'trial_name': syn_trial_name,
                                'trial_max': syn_trial_max
                            }
                            syn_result = self._run_single_synthesizer(
                                preproc_result.data, trials['syn'],
                                syn_para
                            )
                            trials['syn']['trial_data_key'] = \
                                self._save_in_submodule(
                                    'Synthesizer',
                                    syn_result.data_syn,
                                    trials
                            )
                            self.synthesizer[
                                (load_trial_name,
                                 split_trial_name,
                                 split_data_key,
                                 preproc_trial_name,
                                 syn_trial_name)
                            ] = syn_result

                            # TODO add back missingist when ready
                            # 'missingist' : getattr(preproc_result,
                            #     'missingist',
                            #     None
                            # )
                            postproc_para = {
                                'encoder': getattr(
                                    preproc_result,
                                    'encoder',
                                    None
                                ),
                                'scaler': getattr(
                                    preproc_result,
                                    'scaler',
                                    None
                                )
                            }
                            trials['postproc'] = {
                                'trial_name': preproc_trial_name
                            }
                            postproc_result = self._run_single_postprocessor(
                                syn_result.data_syn,
                                trials['postproc'],
                                postproc_para
                            )
                            trials['postproc']['trial_data_key'] = \
                                self._save_in_submodule(
                                    'Postprocessor',
                                    postproc_result.data,
                                    trials
                            )

                            for eval_trial, (eval_trial_name, eval_para) \
                                    in enumerate(
                                        self.para['Evaluator_setting'].items()
                            ):
                                trials['eval'] = {
                                    'trial': eval_trial+1,
                                    'trial_name': eval_trial_name,
                                    'trial_max': eval_trial_max,
                                    'trial_evals': eval_trial_evals,
                                    'trial_evals_sum': eval_trial_evals_sum
                                }
                                for eval_trial_key in \
                                        range(eval_trial_evals[eval_trial]):
                                    trials['eval']['eval_trial_key'] = \
                                        eval_trial_key+1
                                    eval_result = self._run_single_evaluator(
                                        {'ori': split_data['train'],
                                         'syn': postproc_result.data,
                                         'control': split_data['validation']
                                         },
                                        trials['eval'],
                                        eval_para
                                    )

                                    eval_name = (
                                        load_trial_name,
                                        split_trial_name,
                                        split_data_key,
                                        preproc_trial_name,
                                        syn_trial_name,
                                        eval_trial_name,
                                        eval_trial_key+1
                                    )
                                    eval_fullname = (
                                        __version__,
                                        self.exectime,
                                        load_trial_name,
                                        split_trial_name,
                                        trials['split']['trial_split'],
                                        split_data_key,
                                        preproc_trial_name.split('-')[0],
                                        preproc_trial_name.split('-')[1],
                                        preproc_trial_name.split('-')[2],
                                        preproc_trial_name.split('-')[3],
                                        syn_trial_name.split('-')[0],
                                        '-'.join(syn_trial_name.split('-')
                                                 [1:]),
                                        eval_trial_name.split('-')[0],
                                        '-'.join(eval_trial_name.split('-')
                                                 [1:]),
                                        eval_trial_evals[eval_trial],
                                        eval_trial_key+1
                                    )

                                    trials['eval']['trial_data_key'] = \
                                        self._save_in_submodule(
                                            'Evaluator',
                                            (eval_fullname,
                                             eval_result
                                             ),
                                            trials
                                    )
                                    self.evaluator[eval_name] = eval_result

        print(f"====== ====== ====== ====== ====== ======")
        print(
            f"Executor (run - single process): "
            f"Total execution time: {round(time.time()-time_start ,4)} sec."
        )
        print(f"====== ====== ====== ====== ====== ======")

    # def _monitor_cpu_usage(self, interval=10):
    #     while self.monitor_cpu_usage:
    #         cpu_usage = psutil.cpu_percent(interval=None)
    #         print(f"CPU usage: {cpu_usage:>5}%" ,end="\r" ,flush=True)
    #         time.sleep(interval)

    def run_parallel(self):
        time_start = time.time()

        # self.monitor_cpu_usage = True
        # monitor_thread = threading.Thread(
        #     target=self._monitor_cpu_usage,
        #     args=(1,),
        #     daemon=True
        # )
        # monitor_thread.start()

        max_workers = os.cpu_count()

        self._save_in_submodule(module='Executor_Start')

        load_trial_max = len(self.para['Loader_setting'])
        split_trial_max = len(self.para['Splitter_setting'])
        preproc_trial_max = len(self.para['Preprocessor_setting'])
        syn_trial_max = len(self.para['Synthesizer_setting'])
        eval_trial_max = len(self.para['Evaluator_setting'])

        split_trial_splits = [
            setting['num_samples'] if 'num_samples' in setting
            else 1
            for setting in self.para['Splitter_setting'].values()
        ]
        split_trial_splits_sum = sum(split_trial_splits)

        eval_trial_evals = [
            setting['num_samples'] if 'num_samples' in setting
            else 1
            for setting in self.para['Evaluator_setting'].values()
        ]
        eval_trial_evals_sum = sum(eval_trial_evals)

        self.loader = {}
        self.splitter = {}
        self.preprocessor = {}
        self.synthesizer = {}
        self.postprocessor = {}
        self.evaluator = {}

        trials = {}
        ttl_trials_till_load = load_trial_max
        ttl_trials_till_split = ttl_trials_till_load * split_trial_max
        ttl_trials_till_preproc = ttl_trials_till_split * preproc_trial_max
        with tqdm(total=ttl_trials_till_load, desc='Loading: ') as load_pbar, \
                tqdm(total=ttl_trials_till_split, desc='Splitting: ') as split_pbar, \
                tqdm(total=ttl_trials_till_preproc, desc='Preprocessing: ') as preproc_pbar:
            with ProcessPoolExecutor(max_workers=max_workers) as pool_executor:
                preproc_futures = {}
                for load_trial, (load_trial_name, load_para) in \
                        enumerate(self.para['Loader_setting'].items()):
                    trials['load'] = {
                        'trial': load_trial+1,
                        'trial_name': load_trial_name,
                        'trial_max': load_trial_max
                    }
                    load_result = pool_executor.submit(
                        self._run_single_loader,
                        trials['load'],
                        load_para
                    ).result()
                    self.loader[load_trial_name] = load_result

                    load_pbar.update(1)

                    for split_trial, (split_trial_name, split_para) in \
                            enumerate(self.para['Splitter_setting'].items()):
                        trials['split'] = {
                            'trial': split_trial+1,
                            'trial_name': split_trial_name,
                            'trial_max': split_trial_max,
                            'trial_splits': split_trial_splits,
                            'trial_split_sum': split_trial_splits_sum
                        }
                        split_result = pool_executor.submit(
                            self._run_single_splitter,
                            load_result.data,
                            trials['split'],
                            split_para
                        ).result()
                        trials['split']['trial_split'] = len(split_result.data)
                        trials['split']['trial_data_key'] = pool_executor.submit(
                            self._save_in_submodule,
                            'Splitter',
                            split_result.data,
                            deepcopy(trials)
                        ).result()
                        self.splitter[
                            (load_trial_name,
                             split_trial_name)
                        ] = split_result

                        split_pbar.update(1)

                        trials['split']['data_key'] = {}
                        for split_data_key, split_data in split_result.data.items():
                            trials['split']['data_key'] = split_data_key

                            for preproc_trial, (preproc_trial_name,
                                                preproc_para) in \
                                enumerate(
                                    self.para['Preprocessor_setting'].items()
                            ):
                                trials['preproc'] = {
                                    'trial': preproc_trial+1,
                                    'trial_name': preproc_trial_name,
                                    'trial_max': preproc_trial_max
                                }
                                preproc_future = pool_executor.submit(
                                    self._run_single_preprocessor,
                                    split_data['train'],
                                    deepcopy(trials['preproc']),
                                    preproc_para
                                )
                                preproc_futures[preproc_future] = {
                                    'name': (load_trial_name,
                                             split_trial_name,
                                             split_data_key,
                                             preproc_trial_name
                                             ),
                                    'trials': deepcopy(trials)
                                }

                # Should wait all preprocessing done
                #     due to SDV share same temp file
                #     '.sample.csv.temp' in synthesizing,
                #     will cause Permission Error:
                # PermissionError: [WinError 32]
                #     程序無法存取檔案，因為檔案正由另一個程序使用。:
                #     '.sample.csv.temp'
                trials_till_preproc = {}
                for preproc_future in as_completed(preproc_futures):
                    preproc_result = preproc_future.result()
                    preproc_name = preproc_futures[preproc_future]['name']
                    self.preprocessor[preproc_name] = preproc_result
                    trials_preproc = preproc_futures[preproc_future]['trials']
                    trials_preproc['preproc']['trial_data_key'] = \
                        pool_executor.submit(
                            self._save_in_submodule,
                            'Preprocessor',
                            preproc_result.data,
                            deepcopy(trials_preproc)
                    ).result()
                    trials_till_preproc[preproc_name] = trials_preproc
                    preproc_pbar.update(1)

        ttl_trials_till_syn = ttl_trials_till_preproc * syn_trial_max
        ttl_trials_till_postproc = ttl_trials_till_syn
        ttl_trials_till_eval = ttl_trials_till_postproc * eval_trial_evals_sum
        with tqdm(total=ttl_trials_till_syn, desc='Synthesizing: ') as syn_pbar, \
                tqdm(total=ttl_trials_till_postproc, desc='Postprocessing: ') as postproc_pbar, \
                tqdm(total=ttl_trials_till_eval, desc='Evaluating: ') as eval_pbar:
            with ThreadPoolExecutor(max_workers=max_workers) as thread_executor:
                syn_futures = {}
                for trials_name, trials_preproc in trials_till_preproc.items():
                    for syn_trial, (syn_trial_name, syn_para) in \
                            enumerate(self.para['Synthesizer_setting'].items()):
                        trials_preproc['syn'] = {
                            'trial': syn_trial+1,
                            'trial_name': syn_trial_name,
                            'trial_max': syn_trial_max
                        }
                        syn_fullname = trials_name + (syn_trial_name, )
                        # TODO deal work-around:
                        # add random float as filename for avoid same name
                        # but it shouldn't happen
                        syn_future = thread_executor.submit(
                            self._run_single_synthesizer,
                            preproc_result.data,
                            trials_preproc['syn'],
                            syn_para,
                            trial_fullname=syn_fullname+(
                                str(random.uniform(0, 99999999)).zfill(8),
                            )
                        )
                        syn_futures[syn_future] = {
                            'name': syn_fullname,
                            'trials': deepcopy(trials_preproc)
                        }

                for syn_future in as_completed(syn_futures):
                    syn_result = syn_future.result()
                    syn_name = syn_futures[syn_future]['name']
                    trials_syn = syn_futures[syn_future]['trials']
                    self.synthesizer[syn_name] = syn_result
                    trials_syn['syn']['trial_data_key'] = \
                        thread_executor.submit(
                        self._save_in_submodule,
                        'Synthesizer',
                        syn_result.data_syn, deepcopy(trials_syn)).result()

                    syn_pbar.update(1)

                    trials_syn['postproc'] = {
                        'trial_name': preproc_trial_name
                    }
                    # TODO add back missingist when ready
                    # 'missingist' : getattr(
                    #     self.preprocessor[syn_trial_name[0:-1]],
                    #     'missingist',
                    #     None
                    # )
                    postproc_para = {
                        'encoder': getattr(self.preprocessor[syn_name[0:-1]],
                                           'encoder',
                                           None
                                           ),
                        'scaler': getattr(self.preprocessor[syn_name[0:-1]],
                                          'scaler',
                                          None
                                          )
                    }
                    postproc_result = thread_executor.submit(
                        self._run_single_postprocessor,
                        syn_result.data_syn,
                        deepcopy(trials_syn['postproc']),
                        postproc_para
                    ).result()
                    postproc_name = syn_name
                    self.postprocessor[postproc_name] = postproc_result
                    trials_syn['postproc']['trial_data_key'] = \
                        self._save_in_submodule(
                            'Postprocessor',
                            postproc_result.data,
                            deepcopy(trials_syn)
                    )

                    postproc_pbar.update(1)

                    for eval_trial, (eval_trial_name, eval_para) in \
                            enumerate(self.para['Evaluator_setting'].items()):
                        trials_syn['eval'] = {
                            'trial': eval_trial+1,
                            'trial_name': eval_trial_name,
                            'trial_max': eval_trial_max,
                            'trial_evals': eval_trial_evals,
                            'trial_evals_sum': eval_trial_evals_sum
                        }
                        for eval_trial_key in \
                                range(eval_trial_evals[eval_trial]):
                            trials_syn['eval']['eval_trial_key'] = \
                                eval_trial_key+1

                            dict_syn_data_temp = self.splitter[
                                syn_fullname[0:2]].data[syn_fullname[2]
                                                        ]
                            eval_result = thread_executor.submit(
                                self._run_single_evaluator,
                                {'ori': dict_syn_data_temp['train'],
                                 'syn': postproc_result.data,
                                 'control': dict_syn_data_temp['validation']
                                 },
                                deepcopy(trials_syn['eval']),
                                eval_para
                            ).result()

                            eval_name = postproc_name + (
                                eval_trial_name,
                                eval_trial_key+1
                            )
                            # TODO for now trail name execution\
                            #     depends on particular trial name format,
                            #     > preproc_trial_name
                            #     > syn_trial_name
                            #     > eval_trial_evals
                            #     need to be modify for customerized available
                            #     print(preproc_trial_name)
                            eval_fullname = (
                                __version__,
                                self.exectime,
                                load_trial_name,
                                split_trial_name,
                                trials['split']['trial_split'],
                                split_data_key,
                                preproc_trial_name.split('-')[0],
                                preproc_trial_name.split('-')[1],
                                preproc_trial_name.split('-')[2],
                                preproc_trial_name.split('-')[3],
                                syn_trial_name.split('-')[0],
                                '-'.join(syn_trial_name.split('-')[1:]),
                                eval_trial_name.split('-')[0],
                                '-'.join(eval_trial_name.split('-')[1:]),
                                eval_trial_evals[eval_trial],
                                eval_trial_key+1
                            )

                            trials_syn['eval']['trial_data_key'] = \
                                thread_executor.submit(
                                    self._save_in_submodule,
                                    'Evaluator',
                                    (eval_fullname, eval_result),
                                    deepcopy(trials_syn)
                            ).result()
                            self.evaluator[eval_name] = eval_result

                            eval_pbar.update(1)

        # self.monitor_cpu_usage = False
        # monitor_thread.join()

        print(f"====== ====== ====== ====== ====== ======")
        print(
            f"Executor (run - parallel): "
            f"Total execution time: "
            f"{round(time.time()-time_start ,4)} sec."
        )
        print(f"====== ====== ====== ====== ====== ======")

    def _run_single_loader(self, trial, para, **kwargs):
        time_start = time.time()
        loader = Loader(**para)
        print(
            f"Executor - Loader: "
            f"{trial['trial_name']} loading time: "
            f"{round(time.time()-time_start ,4)} sec."
        )
        return loader

    def _run_single_splitter(self, data, trial, para):
        time_start = time.time()
        splitter = Splitter(data=data, **para)
        print(
            f"Executor - Splitter: "
            f"{trial['trial_name']} splitting time: "
            f"{round(time.time()-time_start ,4)} sec."
        )
        return splitter

    def _run_single_preprocessor(self, data, trial, para):
        time_start = time.time()
        preprocessor = Preprocessor(data=data, **para)
        print(
            f"Executor - Preprocessor: "
            f"{trial['trial_name']} preprocessing time: "
            f"{round(time.time()-time_start ,4)} sec."
        )
        return preprocessor

    def _run_single_synthesizer(self, data, trial, para, **kwargs):
        time_start = time.time()
        synthesizer = Synthesizer(data=data, **para)
        trial_fullname = kwargs.get('trial_fullname', None)
        if trial_fullname:
            trial_tempfile = (
                f".sample.csv.temp."
                f"{'-'.join(str(item) for item in trial_fullname)}"
            )
            synthesizer.fit_sample(output_file_path=trial_tempfile)
            if os.path.exists(trial_tempfile):
                os.remove(trial_tempfile)
        else:
            synthesizer.fit_sample()
        print(
            f"Executor - Synthesizer: "
            f"{trial['trial_name']} synthesizing time: "
            f"{round(time.time()-time_start ,4)} sec."
        )
        return synthesizer

    def _run_single_postprocessor(self, data, trial, para):
        time_start = time.time()
        postprocessor = Postprocessor(data=data, **para)
        print(
            f"Executor - Postprocessor: "
            f"postprocessing time: "
            f"{round(time.time()-time_start ,4)} sec."
        )
        return postprocessor

    def _run_single_evaluator(self, data, trial, para):
        time_start = time.time()
        # TODO As AnonymeterMethodMap,
        #     use class define mapping of string and int,
        #     don't use string condition.
        if trial['trial_name'].lower().startswith('anonymeter-inference'):
            _columns = data['syn'].columns
            evaluator = {}
            for _column in _columns:
                para['anonymeter_secret'] = _column
                evaluator[_column] = Evaluator(data=data, **para)
                evaluator[_column].eval()
        else:
            evaluator = Evaluator(data=data, **para)
            evaluator.eval()
        print(
            f"Executor - Evaluator: "
            f"{trial['trial_name']} at {trial['eval_trial_key']} trials "
            f"evaluating time: {round(time.time()-time_start ,4)} sec."
        )
        return evaluator

    # TODO Built a Reporter
    def _save_in_submodule(self, module, data=None, trials=None):
        filename_prog = f"{self.outputname}_Executor.txt"
        existmodule_setting = False
        # TODO As AnonymeterMethodMap,
        #     use class define mapping of string and int,
        #     don't use string condition.
        if not module.startswith('Executor'):
            str_module_setting = f"Module {module} setting:\n"
            with open(filename_prog, 'r') as prog:
                for line in prog:
                    if line == str_module_setting:
                        existmodule_setting = True
                        break
            if not existmodule_setting:
                with open(filename_prog, "a") as prog:
                    prog.write(f"====== ====== ====== ====== ====== ======\n")
                    prog.write(str_module_setting)
                    prog.write(f"====== ====== ====== ====== ====== ======\n")

        if module == 'Executor_Start':
            with open(filename_prog, "w") as prog:
                prog.write(f"{self.outputname}\n")
            return None

        elif module == 'Splitter':
            load_trial = trials['load']['trial']
            split_trial = trials['split']['trial']
            load_trial_name = trials['load']['trial_name']
            split_trial_name = trials['split']['trial_name']
            load_trial_max = trials['load']['trial_max']
            split_trial_max = trials['split']['trial_max']
            split_trial_split = trials['split']['trial_split']
            digit_split_trial_split = len(str(split_trial_split))
            split_trial_splits_sum = trials['split']['trial_split_sum']
            split_trial_splits = trials['split']['trial_splits']
            ttl_trial = \
                load_trial_max * split_trial_max * split_trial_splits_sum
            digit_ttl_trial = len(str(ttl_trial))
            """
            # trial = (# Loading file - 1) * (# TTL Loading x # TTL Splitting)
                    + (Sum of # Splitting setting before this Splitting)
                    + (# Split data key (which add later in loop))
            """
            trial_key = \
                (load_trial - 1) * split_trial_splits_sum + \
                sum(split_trial_splits[:(split_trial-1)])
            trial_data_key = {}
            with open(filename_prog, "a") as prog:
                for data_key, data_value in data.items():
                    trial_key_now = trial_key+data_key
                    str_trial_key_now = \
                        str(trial_key_now).zfill(digit_ttl_trial)
                    str_data_key = \
                        str(data_key).zfill(digit_split_trial_split)
                    str_trial = (
                        f"Load[{load_trial_name}]_"
                        f"Split[{split_trial_name}]"
                        f"[{split_trial_split}-{str_data_key}]"
                    )
                    prog.write(
                        f"Trial {str_trial_key_now} = {str_trial}.\n"
                    )

                    data_value['train'].to_csv(
                        (f"{self.outputname}_"
                         f"Trial[{str_trial_key_now}][Ori].csv"
                         ),
                        index=False
                    )
                    data_value['validation'].to_csv(
                        (f"{self.outputname}_"
                         f"Trial[{str_trial_key_now}][Ctrl].csv"
                         ),
                        index=False
                    )

                    trial_data_key[data_key] = (
                        str_trial_key_now,
                        str_trial
                    )
            return trial_data_key

        elif module == 'Preprocessor':
            split_trial_key_temp = \
                trials['split']['trial_data_key'][trials['split']['data_key']]
            str_split_trial_key = split_trial_key_temp[0]
            str_split_trial = split_trial_key_temp[1]
            preproc_trial_name = trials['preproc']['trial_name']
            preproc_trial = trials['preproc']['trial']
            preproc_trial_max = trials['preproc']['trial_max']
            digit_preproc_trial_max = len(str(preproc_trial_max))
            str_preproc_trial = \
                str(preproc_trial).zfill(digit_preproc_trial_max)

            str_trial_key = f"{str_split_trial_key}-{str_preproc_trial}"
            str_trial = f"{str_split_trial}_Preproc[{preproc_trial_name}]"

            trial_data_key = (str_trial_key, str_trial)
            with open(filename_prog, "a") as prog:
                prog.write(f"Trial {str_trial_key} = {str_trial}.\n")
                data.to_csv(
                    f"{self.outputname}_Trial[{str_trial_key}].csv",
                    index=False
                )
            return trial_data_key

        elif module == 'Synthesizer':
            str_preproc_trial_key = trials['preproc']['trial_data_key'][0]
            preproc_trial = trials['preproc']['trial_data_key'][1]
            syn_trial_name = trials['syn']['trial_name']
            syn_trial = trials['syn']['trial']
            syn_trial_max = trials['syn']['trial_max']
            digit_syn_trial_max = len(str(syn_trial_max))
            str_syn_trial = str(syn_trial).zfill(digit_syn_trial_max)

            str_trial_key = f"{str_preproc_trial_key}-{str_syn_trial}"
            str_trial = f"{preproc_trial}_Syn[{syn_trial_name}]"

            trial_data_key = (str_trial_key, str_trial)
            with open(filename_prog, "a") as prog:
                prog.write(f"Trial {str_trial_key} = {str_trial}.\n")
                data.to_csv(
                    f"{self.outputname}_Trial[{str_trial_key}].csv",
                    index=False
                )
            return trial_data_key

        elif module == 'Postprocessor':
            str_trial_key = trials['syn']['trial_data_key'][0]
            str_trial = trials['syn']['trial_data_key'][1]

            trial_data_key = (str_trial_key, str_trial)
            with open(filename_prog, "a") as prog:
                prog.write(f"Trial {str_trial_key} = {str_trial}.\n")
                data.to_csv(
                    f"{self.outputname}_Trial[{str_trial_key}]Postproc.csv",
                    index=False
                )
            return trial_data_key

        elif module == 'Evaluator':
            str_postproc_trial_key = trials['postproc']['trial_data_key'][0]
            postproc_trial = trials['postproc']['trial_data_key'][1]
            eval_trial_name = trials['eval']['trial_name']
            eval_trial = trials['eval']['trial']
            eval_trial_max = trials['eval']['trial_max']
            digit_eval_trial_max = len(str(eval_trial_max))
            str_eval_trial = str(eval_trial).zfill(digit_eval_trial_max)

            eval_trial_key = trials['eval']['eval_trial_key']
            eval_trial_key_max = max(trials['eval']['trial_evals'])
            digit_eval_trial_key_max = len(str(eval_trial_key_max))
            str_eval_trial_key = \
                str(eval_trial_key).zfill(digit_eval_trial_key_max)

            str_trial_key = (
                f"{str_postproc_trial_key}-"
                f"{str_eval_trial}-{str_eval_trial_key}"
            )
            str_trial = (
                f"{postproc_trial}_"
                f"Eval[{eval_trial_name}-{str_eval_trial_key}]"
            )

            trial_data_key = (str_trial_key, str_trial)
            with open(filename_prog, "a") as prog:
                prog.write(f"Trial {str_trial_key} = {str_trial}.\n")

            rpt_columns = ','.join([
                'PETsARD_version',
                'exec_exectime',
                'exec_trial',
                'load_filename',
                'split_ratio',
                'split_samples',
                'split_Num',
                'preproc_missing_method',
                'preproc_outlier_method',
                'preproc_encoding_method',
                'preproc_scaling_method',
                'syn_method_library',
                'syn_method',
                'eval_method_library',
                'eval_method',
                'eval_samples',
                'eval_num'
            ])
            data_infor = data[0][:2]+(str_trial_key,)+data[0][2:]
            rpt_line = ','.join([str(item) for item in data_infor])
            # TODO As AnonymeterMethodMap,
            #     use class define mapping of string and int,
            #     don't use string condition.
            if eval_trial_name.lower().startswith('anonymeter'):
                eval_module = 'Anonymeter'
                rpt_columns += ','+','.join([
                    'secret',
                    'Risk', 'Risk_CI_btm', 'Risk_CI_top',
                    'Attack_Rate', 'Attack_Rate_err',
                    'Baseline_Rate', 'Baseline_Rate_err',
                    'Control_Rate', 'Control_Rate_err'
                ])
                if eval_trial_name.lower().startswith('anonymeter-inference'):
                    rpt_line_inference = []
                    for data_secret, data_evaluator in data[1].items():
                        data_score = data_evaluator.Evaluator.evaluation
                        data_score = ','.join([
                            f"{item:.16f}" for item in [
                                data_score['Risk'],
                                data_score['Risk_CI_btm'],
                                data_score['Risk_CI_top'],
                                data_score['Attack_Rate'],
                                data_score['Attack_Rate_err'],
                                data_score['Baseline_Rate'],
                                data_score['Baseline_Rate_err'],
                                data_score['Control_Rate'],
                                data_score['Control_Rate_err']
                            ]
                        ])
                        rpt_line_inference.append(
                            rpt_line + f",{data_secret},{data_score}")
                    rpt_line = "\n".join(rpt_line_inference)
                else:
                    data_secret = ''
                    data_score = data[1].Evaluator.evaluation
                    data_score = ','.join([
                        f"{item:.16f}" for item in [
                            data_score['Risk'],
                            data_score['Risk_CI_btm'],
                            data_score['Risk_CI_top'],
                            data_score['Attack_Rate'],
                            data_score['Attack_Rate_err'],
                            data_score['Baseline_Rate'],
                            data_score['Baseline_Rate_err'],
                            data_score['Control_Rate'],
                            data_score['Control_Rate_err']
                        ]
                    ])
                    rpt_line += f",{data_secret},{data_score}"
            else:
                eval_module = 'Unknown'
                rpt_columns += ',Unknown'
                rpt_line += f',{data[1]}'
            filename_rpt = f"{self.outputname}_Report_{eval_module}.csv"

            if not os.path.exists(filename_rpt):
                with open(filename_rpt, "w") as rpt:
                    rpt.write(f"{rpt_columns}\n")

            with open(filename_rpt, "a") as rpt:
                rpt.write(f"{rpt_line}\n")

            return trial_data_key
