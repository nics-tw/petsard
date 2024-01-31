"""
    Top-level package for PETsARD.
    ...

    __init__.py
    TODO replace email from Justyn's personal to team's

    Loader.py
    TODO condition for non-csv and/or too large <-dask ?
    TODO considering stream algorithm
    TODO autocheck if filepath is weblink
    TODO load from boto3
    TODO dtype duplicate function to colnames_discrete, colnames_datetime
    TODO study how to limit read_excel if sheet_name is a list
    TODO 本來有個 Describer 的可選項是 missing_level，應該要編在 Loader 裡的，但目前還沒實作
    TODO .to_datetime()  實作民國年

    Preprocessor.py
    TODO 時間怎麼踢離群值
    TODO 抗偏態的IQR：statsmodels.medcouple

    Processor.py
    TODO convert to Processor

"""

from PETsARD.loader import *
from PETsARD.loader.metadata import Metadata
from PETsARD.processor import *
from PETsARD.synthesizer import *
from PETsARD.evaluator import *
from PETsARD.util import *
from PETsARD.executor import Executor
from PETsARD.Config import *


__all__ = [
    'loader',
    'processor',
    'synthesizer',
    'evaluator',
    'Executor',
    'util',
    'Metadata',
    'Config'
]
