"""
...
TODO:
    LoadingError in Loader_excel_pandas.py
    ResultError  in Anonymeter.py -> or make it as Reporter
    UnfittedError in SDV_SingleTable.py
    SamplingError in Splitter.py
    UnsupportDtypeError in df_cast_check.py
"""


class UnfittedError(Exception):
    pass

class NoConfigError(Exception):
    pass

class ConfigError(Exception):
    pass

class UnsupportedSynMethodError(Exception):
    pass