import time
from typing import Dict, List, Optional, Union
import warnings

import numpy as np
import pandas as pd


class Anonymeter():

    def __init__(self,
                 data: Dict[str, pd.DataFrame],
                 anonymeter_n_attacks:   int = 2000,
                 anonymeter_n_jobs:      int = -2,
                 anonymeter_n_neighbors: int = 10,
                 anonymeter_aux_cols:    Optional[List[List[str]]] = None,
                 anonymeter_secret:      Optional[Union[str,
                                                        List[str]]] = None,
                 **kwargs
                 ):
        # FIXME mileschangmoda:
        # autopep8沒有把空白縮排刪掉嗎?
        # 我的理解應該是不會用空白對齊，我自己會刻意讓變數名稱長度相等
        data_attr = {
            'data_ori':     ('ori',     None),
            'data_syn':     ('syn',     None),
            'data_control': ('control', None)
        }
        # FIXME mileschangmoda:
        # 不要加底線，data只在這個function有用。加強型態
        for attr, (key, default) in data_attr.items():
            value = data.get(key, default)
            setattr(self, attr, value)

        # FIXME mileschangmoda:
        # 我其實不太確定你為什麼要用kwargs.get，有什麼好處嗎？
        # 如果參數固定是不是直接寫在def __init__(self, anonymeter_n_attacks, ...)?這樣可以寫強形態。
        # FIXME mileschangmoda:
        # 這邊也是，用dict[key]跟_data.get(key)的差異?
        self.n_attacks:   int = anonymeter_n_attacks
        self.n_jobs:      int = anonymeter_n_jobs
        self.n_neighbors: int = anonymeter_n_neighbors
        self.aux_cols:    Optional[List[List[str]]] = anonymeter_aux_cols
        self.secret:      Optional[Union[str, List[str]]] = anonymeter_secret

        self.eval_method = 'Unknown'
        # FIXME mileschangmoda:
        # 這個pass是什麼?

    def eval(self):
        """
        ...

        Exception:

            FutureWarning:
                anonymeter\evaluators\singling_out_evaluator.py:97:
                    FutureWarning: is_categorical_dtype is deprecated
                    and will be removed in a future version.
                    Use isinstance(dtype, CategoricalDtype)
                    instead elif is_categorical_dtype(values).

            UserWarning
                anonymeter\stats\confidence.py:215:
                    UserWarning: Attack is as good or worse as baseline model.
                    Estimated rates: attack = 0.30674239114619767,
                    baseline = 0.30773856438771213.
                    Analysis results cannot be trusted. self._sanity_check()

        """
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=FutureWarning)
            warnings.simplefilter("ignore", category=UserWarning)

            if self._Evaluator:
                # FIXME mileschangmoda:
                # 同前
                time_start = time.time()

                print(
                    f"Evaluator (Anonymeter): Evaluating  {self.eval_method}."
                )

                # FIXME mileschangmoda:
                # 在__init__裡直接設Unknown就好?
                # 建議可以再設一個
                # FIXME mileschangmoda:
                # 太多後面我就不一一標了
                # FIXME mileschangmoda:
                # 這些可以用class處理會比字串檢查好很多
                _eval_method_num = AnonymeterMethodMap.map(self.eval_method)
                if _eval_method_num in [0, 1]:
                    _mode = (
                        'univariate' if _eval_method_num == 0
                        else 'multivariate'
                    )
                    try:
                        self._Evaluator.evaluate(mode=_mode)
                    except RuntimeError as ex:
                        print(
                            f"Evaluator (Anonymeter): Singling out "
                            f"evaluation failed with {ex}."
                            f"\n                        "
                            f"Please re-run this cell. "
                            f"For more stable results increase `n_attacks`."
                            f"Note that this will make the evaluation slower."
                        )
                else:
                    self._Evaluator.evaluate(n_jobs=self.n_jobs)
                    print(
                        f"Evaluator (Anonymeter): "
                        f"Evaluating {self.eval_method} spent "
                        f"{round(time.time()-time_start ,4)} sec."
                    )
                self.evaluation = self._extract_result()
            else:
                raise ValueError(
                    f"Evaluator (Anonymeter): .eval() "
                    f"while _Evaluator didn't ready."
                )

    def _extract_result(self) -> dict:
        # TODO Use other method to extract results.
        #      also consider to migrated to Reporter.
        # FIXME mileschangmoda:
        # "不用現在處理"蠻多字串處理的，我知道python字串處理很方便，但用在程式邏輯上會增加偵錯難度不建議。
        dict_result = {}
        para_to_handle = [
            ('Risk',              ['risk()',    'value']),
            ('Risk_CI_btm',       ['risk()',    'ci[0]']),
            ('Risk_CI_top',       ['risk()',    'ci[1]']),
            ('Attack_Rate',       ['results()', 'attack_rate',   'value']),
            ('Attack_Rate_err',   ['results()', 'attack_rate',   'error']),
            ('Baseline_Rate',     ['results()', 'baseline_rate', 'value']),
            ('Baseline_Rate_err', ['results()', 'baseline_rate', 'error']),
            ('Control_Rate',      ['results()', 'control_rate',  'value']),
            ('Control_Rate_err',  ['results()', 'control_rate',  'error'])
        ]

        for key, evals in para_to_handle:
            # FIXME mileschangmoda:
            # 應該是default設成np.nan，不要在except中指定值
            dict_result[key] = np.nan
            try:
                # FIXME mileschangmoda:
                # 前面寫_Evaluator = self._Evaluator，這邊再指一次是不是有點多餘?_Evaluator後面就沒用到了
                eval_instance = self._Evaluator
                for eval_command in evals:
                    if '()' in eval_command:
                        method_name = eval_command.split('(')[0]
                        # FIXME mileschangmoda:
                        # 這裡就體現短變數名稱的意義_attr_value其實算是沒有意義的命名方式
                        # if hasattr(evaluator, name) and isinstance(evaluator[name]), (list, dict, tuple)):
                        if hasattr(eval_instance, method_name):
                            method = getattr(eval_instance, method_name)
                            if callable(method):
                                eval_instance = method()
                            else:
                                break
                        else:
                            break
                    elif '[' in eval_command:
                        attr_name = eval_command.split('[')[0]
                        index = int(eval_command.split('[')[1].rstrip(']'))
                        if hasattr(eval_instance, attr_name):
                            attr = getattr(eval_instance, attr_name)
                            if isinstance(attr, (list, dict, tuple)):
                                try:
                                    eval_instance = attr[index]
                                except (IndexError, KeyError):
                                    break
                        else:
                            break
                    else:
                        eval_instance = getattr(eval_instance, eval_command)
                dict_result[key] = eval_instance
            except Exception as ex:
                pass
        return dict_result


# FIXME mileschangmoda:
# 在__init__裡直接設Unknown就好?
# 建議可以再設一個
class AnonymeterMethodMap():
    method_map = {
        'singlingout - univariate':   0,
        'singlingout - multivariate': 1,
        'linkability':                2,
        'inference':                  3
    }

    @classmethod
    def map(cls, method_name: str) -> int:
        try:
            return cls.method_map[method_name.lower()]
        except KeyError as ex:
            print(
                f"Evaluator (Anonymeter): Method "
                f"{method_name} not recognized.\n"
                f"{ex}"
            )
