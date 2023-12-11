class Preprocessor:
    """
    Base class for all "Preprocessor".

    The "Preprocessor" class defines the common API
    that all the "Preprocessor" need to implement, as well as common functionality.

    ...

    !!!!!! IMPORTANT !!!!!!
    Missingist -> Outlierist -> Encoder -> Scaler

    ...
    Methods:
        Preprocessor(DataFrame): Preprocessing specified DataFrame.
        Returns:
            DataFrame: A pandas DataFrame that input data after processing
    ...
    
    Args:
        data (pandas.DataFrame):
            The pandas DataFrame format of data.

        missing (bool):
            Should missing be handle or NOT. Default is True.
        missing_method (str ,optional):
            Which method will use to handle missing.
            Default is drop, it means drop every rows if any of columns is missing.
        missing_columns (dict ,optional):
            Specifies the action ('missing'/'ignore') for specific columns.
                Format is {'action': [colnames]}.
                Default is None, meaning all columns will be checked.
                - 'missing' : Columns to be included in missing value check.
                - 'ignore'  : Columns to be excluded from missing value check.

    """
    def __init__(self
                ,data         # : pd.DataFrame
                 ####### ####### ####### ####### ####### ######
                 ####### Missingist
                ,missing         : bool = True
                ,missing_method  : str  = 'drop'
                ,missing_columns : dict = None
                 ####### ####### ####### ####### ####### ######
                 ####### Outlier
                ,outlier         : bool = True
                ):
        _para_Preprocessor = {
            'missing' : missing
        }

        if _para_Preprocessor['missing']:
            ####### ####### ####### ####### ####### ######
            ####### Missing data handle (Factory Design)
            _para_Preprocessor['missing_setting'] = {
                'missing_method'  : missing_method
               ,'missing_columns' : missing_columns
            }

            from .MissingistFactory import MissingistFactory
            data = MissingistFactory(df_data = data
                                    ,**_para_Preprocessor['missing_setting'])\
                                    .handle()

        self.data = data
