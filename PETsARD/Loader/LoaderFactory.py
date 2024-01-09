import pandas as pd

from .Loader_csv_pandas import Loader_csv_pandas
from .Loader_excel_pandas import Loader_excel_pandas


class LoaderFactory:
    def __init__(self
                ,para_Loader : dict
                ):
        _file_ext = para_Loader['file_ext']
        if _file_ext == 'csv':
            self.Loader = Loader_csv_pandas()
        elif _file_ext in ['xls' ,'xlsx' ,'xlsm' ,'xlsb'
                          ,'odf' ,'ods'  ,'odt']:
            self.Loader = Loader_excel_pandas()
        else:
            raise ValueError(
                f"Loader - LoaderFactory: "
                f"Unsupported file type, now is {_file_ext}."
            )

        self.para_Loader = para_Loader

    def load(self) -> pd.DataFrame:
        return self.Loader.load(self.para_Loader)