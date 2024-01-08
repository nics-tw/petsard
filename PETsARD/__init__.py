"""
[UNDO]
__init__.py
        replace email from Justyn's personal to team's
Loader.py
        condition for non-csv and/or too large <-dask ?
        considering stream algorithm
        autocheck if filepath is weblink
        load from boto3
        dtype duplicate function to colnames_discrete, colnames_datetime
        study how to limit read_excel if sheet_name is a list
        本來有個 Describer 的可選項是 missing_level，應該要編在 Loader 裡的，但目前還沒實作
        .to_datetime()  實作民國年
Preprocessor.py
        Outlierist.py
                時間怎麼踢離群值
                抗偏態的IQR：statsmodels.medcouple
"""


"""Top-level package for PETs-Experiment."""

from .Metadata import Metadata
from .Executor import Executor
from .Processor import *
from .util          import *
from .Evaluator     import *
from .Postprocessor import *
from .Synthesizer   import *
from .Preprocessor  import *
from .Loader        import *

__all__ = [
    'Loader',
    'Splitter',
    'Preprocessor',
    'Synthesizer',
    'Postprocessor',
    'Evaluator',
    'Processor',
    'Executor',
    'Splitter',
    'Metadata'
]
