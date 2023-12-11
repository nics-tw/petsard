class Missingist:
    def __init__(self
                ,df_data       # : pd.DataFrame
                ,missing_columns : dict
                ,**kwargs):
        self.df_data            = df_data
        self.missing_columns    = missing_columns
        self.cols_check_missing = self.__missing_columns_action(cols_check_missing = self.df_data.columns.to_list()
                                                               ,dict_action        = self.missing_columns)

    def handle(self ,**kwargs):
        raise NotImplementedError("This method should be implemented by subclasses.")

    def __missing_columns_action(self
                                ,cols_check_missing : list
                                ,dict_action        : dict):
        """
        Determines the columns to be included or excluded in the missing value check.

        This function adjusts the list of columns to check for missing values based on the specified actions in 'dict_action'.

        Methods:
            __missing_columns_action(col_to_check ,dict_action):
            Adjusts columns for missing value check.
            Returns:
                list: A list of column names after applying the missing handle.
        
        """

        cols_check_missing = set(cols_check_missing)

        if dict_action:
            _action_keys = set(dict_action.keys())

            if   not _action_keys.issubset({'missing', 'ignore'}):
                raise ValueError(f"Missingist: dict_action must be either 'missing' or 'ignore', now is '{_action_keys}'.")
            elif len(_action_keys) >= 2:
                raise ValueError("Missingist: dict_action should not contain both 'missing' and 'ignore'. Only one action will be applied.")
            else:
                _action_key = _action_keys.pop()

            _set_check_missing = cols_check_missing.copy() if _action_key == 'ignore' else {}

            _cols = [dict_action[_action_key]] if isinstance(dict_action[_action_key], str)\
            else  dict_action[_action_key]
            for _col in _cols:
                _col = {_col}
                if not _col.issubset(cols_check_missing):
                    raise ValueError(f"Missingist: Columns '{_col}' not found in columns of DataFrame.")
                
                if   _action_key == 'ignore':
                    _set_check_missing -= _col
                elif _action_key == 'missing':
                    _set_check_missing += _col
        return list(_set_check_missing)