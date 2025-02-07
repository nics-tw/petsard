"""
Top-level package for petsard.
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

from petsard.config import Config, Status
from petsard.constrainer import Constrainer
from petsard.evaluator import Describer, Evaluator
from petsard.executor import Executor
from petsard.loader import Loader, Metadata, Splitter
from petsard.processor import Processor
from petsard.reporter import Reporter
from petsard.synthesizer import Synthesizer

__all__ = [
    "Loader",
    "Metadata",
    "Splitter",
    "Processor",
    "Synthesizer",
    "Constrainer",
    "Evaluator",
    "Describer",
    "Reporter",
    "Config",
    "Status",
    "Executor",
]
