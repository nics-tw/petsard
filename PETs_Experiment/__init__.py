"""
[UNDO]
__init__.py
        replace email from Justyn's personal to team's
requirement.txt
        build one of it
        read xlsx require openpyxl
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

__author__  = 'NICS-PETs'
__email__   = 'matheme.justyn@gmail.com'
__version__ = '0.2.0'



from .Loader       import *
from .Preprocessor import *
from .util         import *



__all__ =   ['Loader'
            ,'Preprocessor'
            ]