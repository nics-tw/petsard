"""
    Top-level package for PETsARD.
    ...

    __init__.py
    TODO replace email from Justyn's personal to team's

    Loader.py
    TODO condition for non-csv and/or too large <-dask ?
    TODO considering stream algorithm
    TODO dtype duplicate function to colnames_discrete, colnames_datetime
    TODO study how to limit read_excel if sheet_name is a list
    TODO 本來有個 Describer 的可選項是 missing_level，應該要編在 Loader 裡的，但目前還沒實作
    TODO .to_datetime()  實作民國年

    Preprocessor.py
    TODO 時間怎麼踢離群值
    TODO 抗偏態的IQR：statsmodels.medcouple
"""

from PETsARD.loader import Loader, Metadata, Splitter
from PETsARD.processor import Processor
from PETsARD.synthesizer import Synthesizer
from PETsARD.evaluator import Evaluator, Describer, AutoML
from PETsARD.reporter import Reporter
from PETsARD.util import *
from PETsARD.config import Config, Status
from PETsARD.executor import Executor


__all__ = [
    'Loader',
    'Metadata',
    'Splitter',
    'Processor',
    'Synthesizer',
    'Evaluator',
    'Describer',
    'Reporter',
    'Config',
    'Status',
    'Executor',
]
