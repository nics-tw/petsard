# read xlsx require openpyxl
# [TODO] condition for non-csv and/or too large <-dask, stream algorithm
from .PETs_util import df_downcast ,update_nested

class PETs_Loader():

    def __init__(self ,filepath ,params={}):
        ####### ####### ####### ####### ####### ######
        # check file exist                           #
        ####### ####### ####### ####### ####### ######
        import os
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"The file is not exist: {filepath}")
        self.filepath = filepath
 
        ####### ####### ####### ####### ####### ######
        # exectime                                   #
        ####### ####### ####### ####### ####### ######
        from datetime import datetime
        import pytz
        self.exectime = datetime.now().astimezone(pytz.timezone('Asia/Taipei'))

        ####### ####### #######
        # init - params       #
        ####### ####### #######
        self.params = {'read_method' : 'pandas_csv'
                      ,'read_params' : {'downcast'       : 'Y'
                                       ,'label_encoding' : 'N'
                                       ,'str_col'        : []
                                        # pandas_csv
                                       ,'header_exist'   : 'Y'
                                       ,'header'         : []
                                        # pandas_xlsx
                                       ,'sheet_name'     : ''
                                       }
                      }
        self.params = update_nested(self.params ,params)

        ####### ####### #######
        # init - read         #
        ####### ####### #######
        if   self.params['read_method'] == 'pandas_csv':
            self.read_csv(**self.params['read_params'])
        elif self.params['read_method'] == 'pandas_xlsx':
            self.read_xlsx(**self.params['read_params'])
        else:
            import warnings
            raise Exception("Read method is NOT support (e.g. pandas_csv, pandas_xlsx).")



    ####### ####### ####### ####### ####### ######
    # read_csv                                   #
    ####### ####### ####### ####### ####### ######
    def read_csv(self
                ,header_exist   = 'Y'
                ,header         = []
                ,str_col        = []
                ,downcast       = 'Y'
                ,label_encoding = 'N'
                ,**kwargs
                ):
        import pandas as pd

        if len(str_col) >= 1:
            __dict_str_col = dict.fromkeys(str_col, str)
        else:
            __dict_str_col = {}

        if   header_exist == 'Y':
            self.data = pd.read_csv(self.filepath ,dtype=__dict_str_col)
        elif header_exist == 'N':
            self.data = pd.read_csv(self.filepath ,dtype=__dict_str_col
                                   ,header=None ,names=header)
        else:
            import warnings
            raise Exception("'csv_header_exist' should be either 'Y' or 'N'.")

        if downcast == 'Y':
            self.data_oricast = self.data.copy()
            self.data         = df_downcast(self.data)
        self.columns = self.data.columns.tolist()
        self.dtypes  = dict(map(lambda k ,v : (k ,str(v))
                               ,self.columns
                               ,self.data.dtypes.tolist()
                               )
                           )
        if label_encoding == 'Y':
            self.label_encoding()



    ####### ####### ####### ####### ####### ######
    # read_xlsx                                  #
    ####### ####### ####### ####### ####### ######
    # require openpyxl
    def read_xlsx(self
                 ,sheet_name = ''
                 ,str_col    = []
                 ,downcast       = 'Y'
                 ,label_encoding = 'N'
                ,**kwargs
                 ):
        import pandas as pd

        if len(str_col) >= 1:
            __dict_str_col = dict.fromkeys(str_col, str)
        else:
            __dict_str_col = {}

        if sheet_name == '':
            self.data     = pd.read_excel(self.filepath ,dtype=__dict_str_col)
        else:
            try:
                self.data = pd.read_excel(self.filepath ,dtype=__dict_str_col
                                         ,sheet_name=sheet_name)
            except ValueError as e:
                if "Worksheet named" in str(e) and "not found" in str(e):
                    print(f"Sheet name {sheet_name} does NOT exist.")
                else:
                    print("An unknown ValueError occurred:", e)

        if downcast == 'Y':
            self.data_oricast = self.data.copy()
            self.data         = df_downcast(self.data)
        self.columns = self.data.columns.tolist()
        self.dtypes  = dict(map(lambda k ,v : (k ,str(v))
                                ,self.columns
                                ,self.data.dtypes.tolist()
                                )
                            )
        if label_encoding == 'Y':
            self.label_encoding()



    ####### ####### ####### ####### ####### ######
    # label_encoding                             #
    ####### ####### ####### ####### ####### ######
    def label_encoding(self):
        self.data_label_encoding = self.data.copy()
        for col in self.data.select_dtypes(['category']).columns:
            self.data_label_encoding[col] = self.data_label_encoding[col].cat.codes