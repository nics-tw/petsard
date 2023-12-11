class Loader_excel_pandas:
    def __init__(self):
        pass

    def load(self ,para_Loader):
        __dict_setting = {}
        __dict_setting['io'] = para_Loader['filepath']

        __list_setting = ['sheet_name' ,'dtype' ,'na_values']
        __dict_setting.update({k: para_Loader[k] for k in __list_setting})

        if para_Loader['header_exist']:
            __dict_setting['header'] = 0
        else:
            __dict_setting.update({'header' : None
                                  ,'names'  : para_Loader['header_names']
                                  })

        import pandas as pd
        try:
            return pd.read_excel(**__dict_setting)
        except ValueError as e:
            if "Worksheet named" in str(e) and "not found" in str(e):
                print(f"Sheet name {__dict_setting['sheet_name']} does NOT exist.")
            else:
                print("An unknown ValueError occurred:", e)
