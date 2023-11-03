class load_data():

    def __init__(self ,filepath ,params={}):
        # [TODO] verify filepath exist, readable
        # [TODO] condition for non-csv and/or too large <-dask, stream algorithm

        self.filepath = filepath
 
        from datetime import datetime
        import pytz
        self.exectime = datetime.now().astimezone(pytz.timezone('Asia/Taipei'))

        ####### ####### #######
        # init - params       #
        ####### ####### #######
        self.params = {'read_method'     : 'pandas_csv'
                      ,'read_params'     : {'label_encoding' : 'N'}
                      ,'describe'        : 'N'
                      ,'describe_params' : {'dist_fitting'  : 'N'
                                           ,'correlation'   : 'N'
                                           ,'collinearity'  : 'N'
                                           ,'missing_level' : {'data': {}
                                                              ,'col' : {}
                                                              }
                                           }
                      ,'report'          : 'N'
                      ,'report_params'   : {'print_report'  : 'Y'
                                           ,'save_report'   : 'N'
                                           ,'save_filename' : ''
                                           }
                      }
        self.params.update(params)
        if   self.params['read_method'] in ['pandas_csv','pandas_xlsx']:
            if 'str_col' not in self.params['read_params']:
                self.params['read_params']['str_col'] = []

            if   self.params['read_method'] == 'pandas_csv':
                if 'header_exist' not in self.params['read_params']:
                    self.params['read_params']['header_exist'] = 'Y'
                if 'header'       not in self.params['read_params']:
                    self.params['read_params']['header'      ] = []

            elif self.params['read_method'] == 'pandas_xlsx':
                if 'sheet_name' not in self.params['read_params']:
                    self.params['read_params']['sheet_name'] = ''

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

        ####### ####### #######
        # init - describe     #
        ####### ####### #######
        if self.params['describe'] == 'Y':
            self.describe(**self.params['describe_params'])

        ####### ####### #######
        # init - report       #
        ####### ####### #######
        if self.params['report'] == 'Y':
            if self.params['describe'] == 'Y':
                self.report(**self.params['report_params'])
            else:
                import warnings
                raise Exception("Report should follow describe, please set your describe to 'Y'.")



    ####### ####### ####### ####### ####### #######
    # Load data                                   #
    ####### ####### ####### ####### ####### ######

    def read_csv(self
                ,header_exist   = 'Y'
                ,header         = []
                ,str_col        = []
                ,label_encoding = 'N'
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

        self.data    = self.df_downcast(self.data)
        self.columns = self.data.columns.tolist()
        self.dtypes  = dict(map(lambda k ,v : (k ,str(v))
                                ,self.columns
                                ,self.data.dtypes.tolist()
                                )
                            )
        if label_encoding == 'Y':
            self.label_encoding()



    # require openpyxl
    def read_xlsx(self
                 ,sheet_name = ''
                 ,str_col    = []
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

        self.data    = self.df_downcast(self.data)
        self.columns = self.data.columns.tolist()
        self.dtypes  = dict(map(lambda k ,v : (k ,str(v))
                                ,self.columns
                                ,self.data.dtypes.tolist()
                                )
                            )



    def label_encoding(self):
        self.data_label_encoding = self.data.copy()
        for col in self.data.select_dtypes(['category']).columns:
            self.data_label_encoding[col] = self.data_label_encoding[col].cat.codes



    ####### ####### ####### ####### ####### #######
    # EDA                                         #
    ####### ####### ####### ####### ####### #######
    
    def describe(self
                ,dist_fitting = 'N'
                ,correlation  = 'N'
                ,collinearity = 'N'
                ,missing_level = {'data': {}
                                 ,'col' : {}
                                 }):
        self.missing_level = missing_level

        __describe = {}
        __missing  = {}
        for __col ,__col_dtype in self.dtypes.items():
            __col_value = self.data[__col].values

            __col_describe = {}
            __col_describe['nobs'] = len(__col_value)

            if __col_describe['nobs'] >= 1:
                __col_missing = {}

                # [UNDO] datetime?
                if __col_dtype == 'category':
                    __col_describe = self.__describe_category(__col_describe ,__col_value)
                    __col_missing  = self.__missing_category(                 __col_value ,__col_describe['nobs'] ,__col ,self.missing_level)
                else:
                    __col_describe = self.__describe_continue(__col_describe ,__col_value ,dist_fitting)
                    __col_missing  = self.__missing_continue(                 __col_value ,__col_describe['nobs']                          )

                __describe.update({__col: __col_describe})
                __missing.update( {__col: __col_missing })

        self.describe = __describe
        self.missing  = __missing
        
        if correlation == 'Y' or collinearity == 'Y':
            if correlation == 'Y':
                self.correlation  = self.__correlation(  self.data_label_encoding)
            if collinearity == 'Y':
                self.collinearity = self.__collinearnity(self.data_label_encoding)



    ####### ####### #######
    # EDA - Describe      #
    ####### ####### #######

    @staticmethod
    def __describe_category(__col_describe ,__col_value):
        __col_describe['unique'] = len(__col_value.unique())
        __col_value_cnt = __col_value.value_counts(dropna=False)
        __col_describe['top'   ] = {k: {'freq': v
                                    ,'per' : v/__col_describe['nobs'] 
                                    } for k ,v in __col_value_cnt[__col_value_cnt == __col_value_cnt.max()].to_dict().items()}
        return __col_describe



    @staticmethod
    def __describe_continue(__col_describe ,__col_value ,dist_fitting='N'
                           # from fitter import get_common_distributions
                           # __get_common_distributions = get_common_distributions()
                           ,__get_common_distributions = ['cauchy'
                                                         ,'chi2'
                                                         ,'expon'
                                                         ,'exponpow'
                                                         ,'gamma'
                                                         ,'lognorm'
                                                         ,'norm'
                                                         ,'powerlaw'
                                                         ,'rayleigh'
                                                         ,'uniform']
                           ):
        import numpy as np
        from scipy import stats

        # for np.round vs. round, see np.round doc
        __col_describe['mean' ] = np.nanmean(__col_value ,dtype=np.float64)
        # [UNDO] age std differ to pd.describe result
        __col_describe['std'  ] = np.nanstd( __col_value ,dtype=np.float64)
        __col_describe['min'  ] = np.nanmin( __col_value                  )
        # [TODO] dtype 會變
        __col_describe['25%'  ] = np.nanquantile(__col_value ,0.25)
        __col_describe['50%'  ] = np.nanquantile(__col_value ,0.5 )
        __col_describe['75%'  ] = np.nanquantile(__col_value ,0.75)
        __col_describe['max'  ] = np.nanmax(     __col_value      )
        __col_describe['range'] = __col_describe['max'] - __col_describe['min']

        __col_mode = stats.mode(__col_value ,nan_policy='omit')
        __col_describe['mode'] = {__col_mode[0]: {'cnt': __col_mode[1]
                                                 ,'per': __col_mode[1]/__col_describe['nobs'] 
                                                 }
                                 }

        __col_describe['skew'    ] = stats.skew(    __col_value ,nan_policy='omit')
        __col_describe['kurtosis'] = stats.kurtosis(__col_value ,nan_policy='omit')
        # [UNDO] skew/kurtosis test?

        __col_describe['normal_p'] = stats.normaltest(__col_value ,nan_policy='omit').pvalue
        # [UNDO] Shaprio-Wilk?

        if dist_fitting == 'Y':
            from fitter import Fitter
            __best_fit_dist = Fitter(__col_value ,distributions = __get_common_distributions)
            __best_fit_dist.fit()
            __col_describe['best_fit_dist'] = __best_fit_dist.get_best(method = 'sumsquare_error')

        return __col_describe



    ####### ####### #######
    # EDA - Missing       #
    ####### ####### #######

    # Little test 不夠好
    @staticmethod
    def __missing_category(__col_value ,__nobs ,__col
                          ,missing_level = {'data': {}
                                           ,'col' : {}
                                           }
                          ):
        import numpy as np

        if 'data' not in missing_level:
            missing_level.update({'data': {}})
        if 'col'  not in missing_level:
            missing_level.update({'col' : {}})

        __set_missing = {np.nan}
        if len(missing_level['data']) >= 1:
            __set_missing.update(missing_level['data'])
        if __col in missing_level['col']:
            __set_missing.update(missing_level['col'][__col])

        __col_missing = {'cnt': np.count_nonzero([x for x in __col_value if x in __set_missing])}
        __col_missing.update({'per': __col_missing['cnt']/__nobs })
        return(__col_missing)



    @staticmethod
    def __missing_continue(__col_value ,__nobs):
        import numpy as np
        __col_missing = {'cnt': np.count_nonzero(np.isnan(__col_value))}
        __col_missing.update({'per': __col_missing['cnt']/__nobs })
        return(__col_missing)



    ####### ####### #######
    # EDA - Corrleation   #
    ####### ####### #######

    @staticmethod
    def __correlation(__value):
        import numpy as np
        __corr = {}
        __corr['correlation_matrix'] = __value.corr()
        return __corr



    ####### ####### #######
    # EDA - Multicollinearity #
    ####### ####### #######
    @staticmethod
    def __collinearnity(__value):
        from statsmodels.stats.outliers_influence import variance_inflation_factor
        from statsmodels.tools.tools              import add_constant

        __coliner = {}
        __value   = add_constant(__value)

        __coliner['VIF'] = {col: variance_inflation_factor(__value ,i)
                            for col ,i in zip(__value.columns 
                                             ,range(len(__value.columns))
                                             ) if col != 'const'
                           }
        return __coliner



    ####### ####### ####### ####### ####### #######
    # Report                                      #
    ####### ####### ####### ####### ####### #######

    def report(self ,print_report='Y' ,save_report='N' ,save_filename=''):
        from pprint import pformat
        __report = ''

        ####### ####### #######
        # Report - filepath   #
        ####### ####### #######
        __filename = ''
        if hasattr(self, 'filepath'):
            import os
            __report += f'Filepath: {self.filepath}\n\n'
            __filename = os.path.splitext(os.path.basename(self.filepath))[0]

        ####### ####### #######
        # Report - Exectime   #
        ####### ####### #######
        __exectime = ''
        if hasattr(self, 'exectime'):
            __report += f'Execute time: {self.exectime}\n\n'
            __exectime = f"{self.exectime.strftime('%Y%m%d_%H%M%S')}_{self.exectime.tzinfo.zone.replace('/' ,'_')}"

        ####### ####### #######
        # Report - dtype      #
        ####### ####### #######
        if hasattr(self, 'dtypes'):
            __report += f"Columns: {len(self.dtypes)}\ndtypes dict as below:\n"
            __report += f"{pformat(self.dtypes)}\n\n\n\n"

        ####### ####### #######
        # Report - Describe   #
        ####### ####### #######
        if hasattr(self ,'describe'):
            __row_num = next(iter(self.describe.values()))['nobs']
            __report += 'Rows: '+str(__row_num)+'\n\n'
            if __row_num == 0:
                __report += f"There\'s no records in dataset.\n\n\n\n"
            elif __row_num >= 1:
                __report += self.__report_describe(self.transform_nested_dict({k: v for k ,v in self.describe.items()
                                                                               if k in [col for col ,dtype in self.dtypes.items() if dtype != 'category']})
                                                  ,'Continue'
                                                  )

                __report += self.__report_describe(self.transform_nested_dict({k: v for k ,v in self.describe.items()
                                                                               if k in [col for col ,dtype in self.dtypes.items() if dtype == 'category']})
                                                  ,'Discrete'
                                                  )

        ####### ####### #######
        # Report - Missing    #
        ####### ####### #######
        if hasattr(self ,'missing'):
            __report += self.__report_missing({k: v for k ,v in self.missing.items()
                                               if k in [col for col ,dtype in self.dtypes.items() if dtype != 'category']}
                                             ,'Continue'
                                             )
            __report += self.__report_missing({k: v for k ,v in self.missing.items()
                                               if k in [col for col ,dtype in self.dtypes.items() if dtype == 'category']}
                                             ,'Discrete'
                                             )

        ####### ####### #######
        # Report - Correlation #
        ####### ####### #######
        if hasattr(self ,'correlation'):
            if 'correlation_matrix' in self.correlation:
                import numpy as np
                # [TODO] add max, min, stat. test?
                __report += f"Correlation Matrix:\n"
                # tril
                __corr_mat  = self.correlation['correlation_matrix']
                __corr_mat  = __corr_mat.where(np.tril(np.ones(__corr_mat.shape)).astype(bool))
                __report   += f"{pformat(__corr_mat)}\n\n\n\n"

        ####### ####### #######
        # Report - Multicollinearity #
        ####### ####### #######
        if hasattr(self ,'collinearity'):
            if 'VIF' in self.collinearity:
                import pandas as pd
                __report += f"Collinearity - VIF:\n"
                __df_VIF = pd.DataFrame.from_dict(self.collinearity['VIF'] ,orient='index').rename(columns={0: 'VIF'})
                __report += f"{__df_VIF}\n\n\n\n"

        ####### ####### #######
        # Report - print      #
        ####### ####### #######
        if print_report == 'Y':
            print(__report)

        ####### ####### #######
        # Report - save       #
        ####### ####### #######
        if save_report == 'Y':
            save_filename = f"{__filename}_{__exectime}.txt" if save_filename == '' else f"{save_filename}.txt"
            with open(save_filename ,'w') as f:
                f.write(__report)



    @staticmethod
    def __report_describe(__dict ,__tag = 'Unidentified'):
        import pandas as pd
        from pprint import pformat
        __str = ''
        if len(__dict) >= 1:
            __str += f"# {__tag} variable: {len(__dict)}\n\n"
            __str += f"{pformat(pd.DataFrame.from_dict(__dict ,orient='columns'))}\n\n\n\n"
        return __str
    


    @staticmethod
    def __report_missing(__dict ,__tag = 'Unidentified'):
        import pandas as pd
        from pprint import pformat
        __str = ''
        if len(__dict) >= 1:
            __df = pd.DataFrame.from_dict(__dict ,orient='columns')
            __col = __df.loc['per'].idxmax() # max missing
            __cnt = __df.loc['cnt' ,__col]
            __per = __df.loc['per' ,__col]
            if __per == 0.0:
                __str += f"There's no missing in {__tag} variable.\n\n\n\n"
            else:
                __str += f"Most missing {__tag} variable is {__col} , # {__cnt:.0f} ({__per:.4%})\n"
                __str += f"{pformat(__df)}\n\n\n\n"
        return __str



    ####### ####### ####### ####### ####### #######
    # Toolbox                                     #
    ####### ####### ####### ####### ####### #######

    # [TODO] add determine of date
    # [TODO] avoid already have a category as ''
    @staticmethod
    def df_downcast(df):
        import numpy  as np
        import pandas as pd
        list_col       = df.dtypes.index.tolist()
        list_col_dtype = df.dtypes.values.tolist()
        for idx ,col_dtype in enumerate(list_col_dtype):
            col_name  = list_col[idx]
            col_dtype = str(col_dtype)
            if   col_dtype == 'object':
                if col_name == 'date':
                    df[col_name] = pd.to_datetime(df[col_name], format='%Y-%m-%d')
                else:
                    df[col_name] = df[col_name].fillna('').astype('category')
            elif 'int' in col_dtype or 'float' in col_dtype:
                col_min = df[col_name].min()
                col_max = df[col_name].max()
                if   'int' in col_dtype:
                    if   col_min > np.iinfo(np.int8 ).min and col_max < np.iinfo(np.int8 ).max:
                        df[col_name] = df[col_name].astype(np.int8 )
                    elif col_min > np.iinfo(np.int16).min and col_max < np.iinfo(np.int16).max:
                        df[col_name] = df[col_name].astype(np.int16)
                    elif col_min > np.iinfo(np.int32).min and col_max < np.iinfo(np.int32).max:
                        df[col_name] = df[col_name].astype(np.int32)
                    else:
                        df[col_name] = df[col_name].astype(np.int64)
                elif 'float' in col_dtype:
                    if   col_min > np.finfo(np.float16).min and col_max < np.finfo(np.float16).max:
                        df[col_name] = df[col_name].astype(np.float16)
                    elif col_min > np.finfo(np.float32).min and col_max < np.finfo(np.float32).max:
                        df[col_name] = df[col_name].astype(np.float32)
                    else:
                        df[col_name] = df[col_name].astype(np.float64)
        return df
    


    @staticmethod
    def transform_nested_dict(input_dict):
        # 定義一個函數來轉換單一字典
        def transform_dict(sub_dict):
            items_list = list(sub_dict.items())
            new_items_list = []
            
            for key, value in items_list:
                # 如果值是字典，則處理巢狀字典
                if isinstance(value, dict):
                    nested_dict = value
                    new_key_values = {}
                    main_key_value = None
                    
                    # 遍歷巢狀字典
                    for nested_key, nested_value in nested_dict.items():
                        if isinstance(nested_value, dict):
                            main_key_value = (f"{key}", nested_key)
                            for sub_key, sub_value in nested_value.items():
                                new_key = f"{key}_{sub_key}"
                                new_key_values[new_key] = sub_value
                        else:
                            new_key = f"{key}_{nested_key}"
                            new_key_values[new_key] = nested_value
                    
                    # 插入新的 key-value 對
                    if main_key_value:
                        new_items_list.append(main_key_value)
                    
                    for new_key, new_value in new_key_values.items():
                        new_items_list.append((new_key, new_value))
                else:
                    # 如果不是巢狀字典，則直接添加
                    new_items_list.append((key, value))
                    
            # 轉回字典
            new_dict = dict(new_items_list)
            return new_dict



        transformed_dict = {}
        
        for main_key, sub_dict in input_dict.items():
            transformed_sub_dict = transform_dict(sub_dict)
            transformed_dict[main_key] = transformed_sub_dict
        
        return transformed_dict






# [TODO] add main module
# if __name__ = "__main__":
