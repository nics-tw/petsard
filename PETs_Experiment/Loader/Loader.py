class Loader:
    """
    Base class for all "Loader".

    The "Loader" class defines the common API
    that all the "Loader" need to implement, as well as common functionality.

    ...
    Methods:
        Loader(filepath)
        Returns:
            pandas.DataFrame: A pandas DataFrame
                containing the loaded data which already casting
    ...
    
    Args:
        filepath (str):
            The fullpath of dataset.

        header_exist (bool ,optional):
            Is header as 1st row of data or NOT. Default is True.
        header_names (list ,optional):
            Header list of data.
            It will be replacement if header_exist is True,
            and generating if header_exist is False. Default is empty list [].
        sep (str ,optional):
            Character or regex pattern to treat as the delimiter. Default is comma ",". 

        sheet_name (str | int ,optional):
            Strings are used for sheet names.
            Integers are used in zero-indexed sheet positions (chart sheets do not count as a sheet position).
            Specify None to get all worksheets.

        colnames_discrete (list ,optional):
            List of column names that are discrete. They will be forcibly treated as strings,
            and convert to categorical later. Default is empty list [].
        colnames_datetime (list ,optional):
            List of column names that are date/datetime. They will be forcibly treated as strings,
            and convert to date or datetime later. Default is empty list [].

        dtype (dict ,optional):
            Dictionary of columns data type force assignment.
            Format as {colname: col_dtype}. Default is None, means no se empty dict {}.

        na_values (str | list | dict ,optional):
            Extra string to recognized as NA/NaN.
            If dictionary passed, value will be specific per-column NA values.
            Format as {colname: na_values}.
            Default is None, means no extra. Check pandas document for Default NA string list.

    """
    def __init__(self
                ,filepath          : str
                ,header_exist      : bool     = True
                ,header_names      : list     = None
                ,sep               : str      = ','
                ,sheet_name                   = 0   # : str ,int
                 ####### ####### ####### ####### ####### ######
                 ####### [TODO] dtype 跟 colnames_xxx 重複功能
                ,colnames_discrete : list     = None     ######
                ,colnames_datetime : list     = None     ######
                ,dtype             : dict     = None     ######
                 ####### ####### ####### ####### ####### ######
                ,na_values                    = None
                ):
        _para_Loader = {}
        
        ####### ####### ####### ####### ####### ######
        ####### Check filepath exist
        _para_Loader = self._check_filepath_exist(_para_Loader ,filepath)

        ####### ####### ####### ####### ####### ######
        ####### Specified Data Types
        _para_Loader = self._specifying_dtype(_para_Loader ,colnames_discrete ,colnames_datetime)

        ####### ####### ####### ####### ####### ######
        ####### General Setting                      #
        _para_Loader.update({'header_exist' : header_exist
                            ,'header_names' : header_names
                            ,'sep'          : sep
                            ,'sheet_name'   : sheet_name
                            ,'na_values'    : na_values
                            })

        ####### ####### ####### ####### ####### ######
        ####### Delegate and Load Data (Factory Design)
        from .LoaderFactory import LoaderFactory
        self.data = LoaderFactory(_para_Loader).load()
        ####### ####### ####### ####### ####### ######
        ####### Optimized dtype
        if not dtype:
            dtype = {}
        ####### ####### ####### ####### ####### ###### ######
        ####### [TODO] 我還在思考這裡要怎麼直接接收 pd.dateframe 的 dtype
        from ..util import df_cast_check        ###### ######
        dtype.update(df_cast_check(self.data ,dtype))  ######
        self.dtype = dtype                      ###### ######
        ####### ####### ####### ####### ####### ###### ######
        from ..util import df_casting
        self.data = df_casting(self.data ,dtype)

        ####### ####### ####### ####### ####### ######
        ####### Recode parameter
        self.para = {}
        self.para['Loader'] = _para_Loader



    def _check_filepath_exist(self ,para_Loader ,filepath):
        import os
        if os.path.exists(filepath):
            para_Loader.update({'filepath' : filepath
                               ,'file_ext' : os.path.splitext(filepath)[1].lstrip('.').lower()
                               })
        else:
            raise FileNotFoundError(f"Loader - _check_filepath_exist: The file is not exist: {filepath}")
        return para_Loader



    def _specifying_dtype(self ,para_Loader ,colnames_discrete ,colnames_datetime):
        colnames_discrete = [] if colnames_discrete is None else colnames_discrete
        colnames_datetime = [] if colnames_datetime is None else colnames_datetime
        __dict_colnames_string = dict.fromkeys([*colnames_discrete
                                               ,*colnames_datetime]
                                              ,str)
        para_Loader.update({'colnames_discrete' : colnames_discrete
                           ,'colnames_datetime' : colnames_datetime
                           ,'dtype'             : __dict_colnames_string
                           })
        return para_Loader