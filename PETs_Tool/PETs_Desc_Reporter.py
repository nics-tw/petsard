from .PETs_Describer import PETs_Describer
from .PETs_util      import update_nested


class PETs_Desc_Reporter(PETs_Describer):
    def __init__(self ,describer=None ,params={} ,**kwargs):
        if describer:
            super().__init__(filepath=describer.filepath)

            ####### ####### #######
            # init - params       #
            ####### ####### #######
            # input > loader > default
            params = update_nested(describer.params ,params)
            self.params = {'report'          : 'N'
                          ,'report_params'   : {'print_report'  : 'Y'
                                               ,'save_report'   : 'N'
                                               ,'save_filename' : ''
                                               }
                          }
            self.params = update_nested(self.params ,params)

            ####### ####### #######
            # init - report       #
            ####### ####### #######
            if self.params['report'] == 'Y':
                if self.params['describe'] == 'Y':
                    self.save_filename = f"{self.filename}_{self.exectime}_{self.desctime}.txt"\
                                         if self.params.report_params.save_filename == ''\
                                       else f"{self.params.report_params.save_filename}_{self.desctime}.txt"
                    self.report(**self.params['report_params'])
                else:
                    import warnings
                    raise Exception("Report should follow describer, please set your describe to 'Y'.")
        else:
            import warnings
            raise Exception("Report should follow describer, please describe your data.")




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
                __report += self.__report_describe(self.__transform_nested_dict({k: v for k ,v in self.describe.items()
                                                                                 if k in [col for col ,dtype in self.dtypes.items() if dtype != 'category']})
                                                  ,'Continue'
                                                  )

                __report += self.__report_describe(self.__transform_nested_dict({k: v for k ,v in self.describe.items()
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
            with open(self.save_filename ,'w') as f:
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
    


    @staticmethod
    def __transform_nested_dict(dict_input):
        def __transform_dict(dict_sub ,parent_key=''):
            dict_item = {}
            for k ,v in dict_sub.items():
                new_key = f'{parent_key}_{k}' if parent_key else k
                if isinstance(v ,dict):
                    dict_item.update(__transform_dict(v ,new_key))
                else:
                    dict_item[new_key] = v
            return dict_item
        return {k: __transform_dict(v) for k ,v in dict_input.items()}

