from .PETs_Loader import PETs_Loader
from .PETs_util   import update_nested


class PETs_Describer(PETs_Loader):
    def __init__(self ,loader=None ,params={} ,**kwargs):
        if loader:
            super().__init__(filepath=loader.filepath)

            from datetime import datetime
            import pytz
            self.descctime = datetime.now().astimezone(pytz.timezone('Asia/Taipei'))

            ####### ####### #######
            # init - params       #
            ####### ####### #######
            # input > loader > default
            params = update_nested(loader.params ,params)
            self.params = {'describe'        : 'Y'
                          ,'describe_params' : {'dist_fitting'  : 'N'
                                              ,'correlation'   : 'N'
                                              ,'collinearity'  : 'N'
                                              ,'missing_level' : {'data': {}
                                                                  ,'col' : {}
                                                                  }
                                              }
                          }
            self.params = update_nested(self.params ,params)

            ####### ####### #######
            # init - describe     #
            ####### ####### #######
            if self.params['describe'] == 'Y':
                self.describe(**self.params['describe_params'])
        else:
            import warnings
            raise Exception("Describe should follow loader, please load your data.")



    ####### ####### ####### ####### ####### #######
    # EDA                                         #
    ####### ####### ####### ####### ####### #######
    def describe(self
                ,dist_fitting = 'N'
                ,correlation  = 'N'
                ,collinearity = 'N'
                ,missing_level = {'data': {}
                                 ,'col' : {}
                                 }
                ,**kwargs
                ):
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