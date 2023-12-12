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

    def __init__(self, data
                ,missing: bool = True
                    ,missing_method: str = 'drop'
                    ,missing_columns: dict = None
                ,outlier: bool = True
                    ,outlier_method: str   = 'iqr'
                    ,outlier_columns: dict = None
                ,encoding: bool = True
                    ,encoding_method: str = 'label'
                    ,encoding_columns: dict = None
                ,scaling: bool = False
                    ,scaling_method:  str = 'standard'
                    ,scaling_columns: dict = None
                 ):
        _para_Preprocessor = {
            'missing': missing, 'outlier': outlier, 'encoding': encoding, 'scaling': scaling
        }

        if _para_Preprocessor['missing']:
            ####### ####### ####### ####### ####### ######
            # Missing data handle (Factory Design)
            _para_Preprocessor['missing_setting'] = {
                'missing_method': missing_method ,'missing_columns': missing_columns, 'missing_columns_action': self._handle_cols_action('missing', data.columns, missing_columns)
            }
            from .MissingistFactory import MissingistFactory
            data = MissingistFactory(df_data=data, **_para_Preprocessor['missing_setting'])\
                .handle()

        if _para_Preprocessor['outlier']:
            ####### ####### ####### ####### ####### ######
            # Outlier data handle (Factory Design)
            _para_Preprocessor['outlier_setting'] = {
                'outlier_method': outlier_method ,'outlier_columns': outlier_columns, 'outlier_columns_action': self._handle_cols_action('outlier', data.columns, outlier_columns)
            }
            from .OutlieristFactory import OutlieristFactory
            data = OutlieristFactory(df_data=data, **_para_Preprocessor['outlier_setting'])\
                .handle()

        if _para_Preprocessor['encoding']:
            ####### ####### ####### ####### ####### ######
            # Encoding data (Factory Design)
            _para_Preprocessor['encoding_setting'] = {
                'encoding_method': encoding_method ,'encoding_columns': encoding_columns, 'encoding_columns_action': self._handle_cols_action('encoding', data.columns, encoding_columns)
            }
            from .EncoderFactory import EncoderFactory
            data ,encoder = EncoderFactory(df_data=data, **_para_Preprocessor['encoding_setting'])\
                .handle()

        if _para_Preprocessor['scaling']:
            ####### ####### ####### ####### ####### ######
            # Scaling data (Factory Design)
            _para_Preprocessor['scaling_setting'] = {
                'scaling_method': scaling_method ,'scaling_columns': scaling_columns, 'scaling_columns_action': self._handle_cols_action('scaling', data.columns, scaling_columns)
            }
            from .ScalerFactory import ScalerFactory
            data ,scaler = ScalerFactory(df_data=data, **_para_Preprocessor['scaling_setting'])\
                .handle()

        self.data    = data
        self.encoder = encoder
        self.scaler  = scaler


    def _handle_cols_action(self ,submodule: str, cols: list, dict_action: dict) -> list:
        """
        Determines the columns to be focus or ignore/excluded in the sub-function action.

        This function adjusts the list of columns to check for sub-function based on the specified actions in 'dict_action'.
        Only allow 'focus' or 'ignore' action.

        Methods:
            _handle_cols_action(cols ,dict_action):
            Adjusts columns for action.
            Returns:
                list: A list of column names after applying the action.

        """
        _allow_action = {'focus', 'ignore'}

        cols = set(cols)
        _cols_action = cols.copy()
        if dict_action:
            _action_key = set(dict_action.keys())

            if not _action_key.issubset(_allow_action):
                raise ValueError(
                    f"Preprocessor: {submodule} columns must be either 'focus' or 'ignore', now is '{_ for _ in _action_key if _ not in _allow_action}'.")
            elif len(_action_key) >= 2:
                raise ValueError(
                    f"Preprocessor: {submodule} columns should not contain both 'focus' and 'ignore'. Only one action will be applied.")
            else:
                _action = _action_key.pop()

            _cols_action = _cols_action if _action == 'ignore' else {}

            _cols_for_action = [dict_action[_action]] if isinstance(dict_action[_action], str)\
                else dict_action[_action]
            for _col_for_action in _cols_for_action:
                _col_for_action = {_col_for_action}
                if not _col_for_action.issubset(cols):
                    raise ValueError(
                        f"Preprocessor: {submodule} column '{_col_for_action}' not found in columns of DataFrame.")

                if _action == 'ignore':
                    _cols_action -= _col_for_action
                elif _action == 'focus':
                    _cols_action += _col_for_action

        return list(_cols_action)
