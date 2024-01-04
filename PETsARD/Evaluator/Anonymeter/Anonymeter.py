import numpy as np
import time
import warnings


class Anonymeter():

    def __init__(self, **kwargs):
        class_attributes = {
            'data_ori':     ('ori',                    None),
            'data_syn':     ('syn',                    None),
            'data_control': ('control',                None),
            'n_attacks':    ('anonymeter_n_attacks',   2000),
            'n_jobs':       ('anonymeter_n_jobs',      -2),
            'n_neighbors':  ('anonymeter_n_neighbors', 10),
            'aux_cols':     ('anonymeter_aux_cols',    None),
            'secret':       ('anonymeter_secret',      None)
        }

        _data = kwargs.get('data', None)
        for attr, (key, default) in class_attributes.items():
            value = _data.get(key, kwargs.get(key, default))
            setattr(self, attr, value)
        pass

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
                _time_start = time.time()

                self._eval_method = (
                    self._eval_method if hasattr(self, '_eval_method')
                    else 'Unknown'
                )
                print(
                    f"Evaluator (Anonymeter): Evaluating  {self._eval_method}."
                )

                if self._eval_method.startswith('SinglingOut'):
                    _mode = (
                        'univariate' if self._eval_method.endswith('Univariate')
                        else 'multivariate' if self._eval_method.endswith('Multivariate')
                        else 'Unknown'
                    )
                    try:
                        self._Evaluator.evaluate(mode=_mode)
                    except RuntimeError as ex:
                        print(
                            f"Evaluator (Anonymeter): Singling out "
                            f"evaluation failed with {ex}."
                            f"\n                        "
                            f"Please re-run this cell. "
                            f"For more stable results increase `n_attacks`. "
                            f"Note that this will make the evaluation slower."
                        )
                else:
                    self._Evaluator.evaluate(n_jobs=self.n_jobs)
                    print(
                        f"Evaluator (Anonymeter): Evaluating  "
                        f"{self._eval_method} spent "
                        f"{round(time.time()-_time_start ,4)} sec."
                    )
                self.evaluation = self._extract_result()
            else:
                raise ValueError(
                    f"Evaluator (Anonymeter): .eval() "
                    f"while _Evaluator didn't ready."
                )

    def _extract_result(self):
        _Evaluator = self._Evaluator
        _dict_result = {}
        _para_to_handle = [
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

        for _key, _attrs in _para_to_handle:
            try:
                _attr_value = _Evaluator
                for _attr in _attrs:
                    if '()' in _attr:
                        _method_name = _attr.split('(')[0]
                        if hasattr(_attr_value, _method_name):
                            _method = getattr(_attr_value, _method_name)
                            if callable(_method):
                                _attr_value = _method()
                            else:
                                _dict_result[_key] = np.nan
                                break
                        else:
                            _dict_result[_key] = np.nan
                            break
                    elif '[' in _attr:
                        _attr_name = _attr.split('[')[0]
                        _index = int(_attr.split('[')[1].rstrip(']'))
                        if hasattr(_attr_value, _attr_name)\
                                and isinstance(getattr(_attr_value, _attr_name), (list, dict, tuple)):
                            try:
                                _attr_value = getattr(
                                    _attr_value, _attr_name)[_index]
                            except (IndexError, KeyError):
                                _dict_result[_key] = np.nan
                                break
                        else:
                            _dict_result[_key] = np.nan
                            break
                    else:
                        _attr_value = getattr(_attr_value, _attr)
                _dict_result[_key] = _attr_value
            except Exception as e:
                _dict_result[_key] = np.nan
        return _dict_result
