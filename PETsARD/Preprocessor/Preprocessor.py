from PETsARD.Preprocessor.MissingistFactory import MissingistFactory
from PETsARD.Preprocessor.OutlieristFactory import OutlieristFactory
from PETsARD.Preprocessor.EncoderFactory import EncoderFactory
from PETsARD.Preprocessor.ScalerFactory import ScalerFactory


class Preprocessor:
    """
    Base class for all "Preprocessor".

    The "Preprocessor" class defines the common API
        that all the "Preprocessor" need to implement,
        as well as common functionality.

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


        every sub-module follows same args format:
            sub-module, sub-module_method, and sub-module_columns.
            There're 4 sub-module as {'missing','outlier','encoding','scaling'}.

        sub-module (bool):
            Should sub-module be handle or NOT. Default is True.
        sub-module_method (str ,optional):
            Which method will use to handle sub-module.
        sub-module_columns (dict ,optional):
            Specifies the action ('focus'/'ignore') for specific columns.
                Format is {'action': [colnames]}.
                Default is None, meaning all columns will be checked.
                - 'focus'  : Columns to be included in sub-module action.
                - 'ignore' : Columns to be excluded from sub-module action.
    """

    def __init__(
            self,
            data,
            missing:         bool = True,
            missing_method:  str = 'drop',
            missing_columns: dict = None,
            outlier:         bool = True,
            outlier_method:  str = 'iqr',
            outlier_columns: dict = None,
            encoding:         bool = True,
            encoding_method:  str = 'label',
            encoding_columns: dict = None,
            scaling:         bool = False,
            scaling_method:  str = 'standard',
            scaling_columns: dict = None
    ):
        para_preprocessor = {
            'missing': missing,
            'outlier': outlier,
            'encoding': encoding,
            'scaling': scaling
        }

        if para_preprocessor['missing']:
            para_preprocessor['missing_setting'] = {
                'missing_method': missing_method,
                'missing_columns': missing_columns,
                'missing_columns_action': self._handlecols_action(
                    'missing', data.columns,
                    missing_columns
                )
            }
            data, missingist = MissingistFactory(
                df_data=data,
                **para_preprocessor['missing_setting']
            ).handle()
        else:
            missingist = None

        if para_preprocessor['outlier']:
            para_preprocessor['outlier_setting'] = {
                'outlier_method': outlier_method,
                'outlier_columns': outlier_columns,
                'outlier_columns_action': self._handlecols_action(
                    'outlier',
                    data.columns,
                    outlier_columns
                )
            }
            data = OutlieristFactory(
                df_data=data,
                **para_preprocessor['outlier_setting']
            ).handle()

        if para_preprocessor['encoding']:
            para_preprocessor['encoding_setting'] = {
                'encoding_method': encoding_method,
                'encoding_columns': encoding_columns,
                'encoding_columns_action': self._handlecols_action(
                    'encoding',
                    data.columns,
                    encoding_columns
                )
            }
            data, encoder = EncoderFactory(
                df_data=data,
                **para_preprocessor['encoding_setting']
            ).handle()
        else:
            encoder = None

        if para_preprocessor['scaling']:
            para_preprocessor['scaling_setting'] = {
                'scaling_method': scaling_method,
                'scaling_columns': scaling_columns,
                'scaling_columns_action': self._handlecols_action(
                    'scaling',
                    data.columns,
                    scaling_columns
                )
            }
            data, scaler = ScalerFactory(df_data=data, **para_preprocessor['scaling_setting'])\
                .handle()
        else:
            scaler = None

        self.data = data
        if encoder:
            self.encoder = encoder
        if scaler:
            self.scaler = scaler
        if missingist:
            self.missingist = missingist
        self.para = {}
        self.para['Preprocessor'] = para_preprocessor

    def _handlecols_action(
            self,
            submodule: str,
            cols: list,
            dict_action: dict
    ) -> list:
        """
        Determines the columns to be focus
            or ignore/excluded in the sub-function action.

        This function adjusts the list of columns to check for sub-function
            based on the specified actions in 'dict_action'.
        Only allow 'focus' or 'ignore' action.

        Methods:
            _handle_cols_action(cols ,dict_action):
            Adjusts columns for action.
            Returns:
                list: A list of column names after applying the action.

        """
        allow_action = {'focus', 'ignore'}

        cols = set(cols)
        cols_action = cols.copy()
        if dict_action:
            action_key = set(dict_action.keys())

            if not action_key.issubset(allow_action):
                raise ValueError(
                    f"Preprocessor: {submodule} columns "
                    f"must be either 'focus' or 'ignore', "
                    f"now is "
                    f"'{_ for _ in action_key if _ not in allow_action}'."
                )
            elif len(action_key) >= 2:
                raise ValueError(
                    f"Preprocessor: "
                    f"{submodule} columns should not contain "
                    f"both 'focus' and 'ignore'. "
                    f"Only one action will be applied."
                )
            else:
                action = action_key.pop()

            cols_action = cols_action if action == 'ignore' else set()

            cols_for_action = (
                [dict_action[action]] if isinstance(dict_action[action], str)
                else dict_action[action]
            )
            for col_for_action in cols_for_action:
                col_for_action = {col_for_action}
                if not col_for_action.issubset(cols):
                    raise ValueError(
                        f"Preprocessor: "
                        f"{submodule} column '{col_for_action}' "
                        f"not found in columns of DataFrame."
                    )

                if action == 'ignore':
                    cols_action -= col_for_action
                elif action == 'focus':
                    cols_action.update(col_for_action)

        return list(cols_action)
