# The Synthetic Data Vault
# https://sdv.dev/
# https://github.com/sdv-dev/SDV
# https://docs.sdv.dev/sdv/
from .PETs_Loader import PETs_Loader
from .PETs_util   import df_downcast ,label_encoding ,update_append_nested
# 231103, Justyn: if you failed when you run on VSCode, check if you can "import torch"
#                 if not, you should install Microsoft Visual C++ Redistributable
#                 and you can download it on Microsoft official website
# [TODO] Conditional Sampling

class PETs_SD_SDV(PETs_Loader):

    def __init__(self
                ,loader = None
                ,params = {}
                ,**kwargs):

        if loader:
            ####### ####### #######
            # init - params       #
            ####### ####### #######
            # input > loader > default
            # inherit here
            params = update_append_nested(loader.params ,params)
            # default here
            default_params = {'sd_params': {'library'  : 'SDV'
                                           ,'train_model' : 'Y'
                                           ,'metadata'    : 'SingleTable'
                                           ,'model'       : 'GaussianCoupula'
                                           ,'save_model'    : 'Y'
                                           ,'save_filename' : ''
                                           ,'save_folder'   : '.\\model_dpsd'
                                           }
                             ,'sample'        : 'N'
                             ,'sample_params' : {'reset_sample'       : 'N'
                                                ,'sample_rows'        : 100
                                                ,'sample_rows_as_raw' : 'N'
                                                ,'save_data'   : 'Y'
                                                ,'save_method' : 'csv'
                                                ,'save_folder' : '.\\data_dpsd'
                                                }
                             }
            params = update_append_nested(default_params ,params)
            ####### ####### #######
            # init - inherit      #
            ####### ####### #######
            super().__init__(params=params ,filepath=loader.filepath)

            ####### ####### #######
            # init - synthesizer or not #
            ####### ####### #######
            self.params['sd_params']['save_filename'] = self.params['filename' ]\
                                                     if self.params['sd_params']['save_filename'] == ''\
                                                   else self.params['sd_params']['save_filename']
            if hasattr(loader, 'synthesizer'):
                self.synthesizer = loader.synthesizer
            else:
                self.synthesize(**self.params['sd_params'])

            ####### ####### #######
            # init - sample or not #
            ####### ####### #######
            if self.params['sample'] == 'Y':
                self.sample(**self.params['sample_params'])



    ####### ####### #######
    # synthesize for synthesizer #
    ####### ####### #######
    def synthesize(self ,library  = 'SDV'
                        ,train_model = 'Y'
                        ,metadata    = 'SingleTable'
                        ,model       = 'GaussianCoupula'
                        ,save_model    = 'Y'
                        ,save_filename = 'Unknown'
                        ,save_folder   = '.\\model_dpsd'
                  ,**kwargs):
        from datetime import datetime
        import pytz
        sdtime = datetime.now().astimezone(pytz.timezone('Asia/Taipei'))
        self.sdtime = sdtime
        output_filename = f"{save_filename}_[{library}]_[{model}]_{sdtime.strftime('%Y%m%d_%H%M%S')}_{sdtime.tzinfo.zone.replace('/' ,'_')}"
        self.params['sd_params']['output_filename'] = output_filename

        if train_model == 'Y':
            self.__metadata_model(metadata ,model)
        if save_model == 'Y':
            import os
            self.synthesizer.save(os.path.join(save_folder ,output_filename+".pkl"))




    ####### ####### #######
    # metadata            #
    ####### ####### #######
    def __metadata_model(self ,metadata
                              ,model
                        ,**kwargs):
        import time
        __dict_metadata_model = {'SingleTable': {'GaussianCoupula': self.__singletable_GaussianCoupula
                                                ,'CTGAN'          : self.__singletable_CTGAN
                                                ,'TVAE'           : self.__singletable_TVAE
                                                ,'CoupulaGAN'     : self.__singletable_CoupulaGAN
                                                }
                                }

        if metadata in __dict_metadata_model:
            if model in __dict_metadata_model[metadata]:
                self.__data_prepare()
                self.__singletable()
                
                __time_start = time.time()
                print(f"We are execute {metadata} - {model}.")
                __dict_metadata_model[metadata][model]()
                self.synthesizer.fit(self.sd_sdv_data)
                print(f"Model training time: {round(time.time()-__time_start ,4)} sec.")
            else:
                raise Exception(f"Model not supported in {metadata}: {model}")
        else:
            import warnings
            raise Exception(f"Metadata not support: only SingleTable, now is {metadata}.")



    ####### ####### #######
    # data_prepare        #
    ####### ####### #######
    def __data_prepare(self):
        # get setting or set N
        __downcast       = self.params.get('read_params' ,{}).get('downcast'       ,'N')
        __label_encoding = self.params.get('read_params' ,{}).get('label_encoding' ,'N')
        __model          = self.params.get('sd_params'   ,{}).get('model'          ,'' )

        __map_data = {# GaussianCoupula: use downcast data, if didn't create it, downcast it.
                      ('GaussianCoupula' ,'Y'): self.data
                     ,('GaussianCoupula' ,'N'): df_downcast(self.data)
                      # CTGAN: use original data, if oricast didn't exist, trust self.data.
                     ,('CTGAN' ,'Y'): getattr(self ,'data_oricast' ,self.data)
                     ,('CTGAN' ,'N'): self.data
                      # TVAE/CoupulaGAN, use label encoding, if label encoding didn't exist, calculate one.
                     ,('TVAE' ,'Y'): getattr(self ,'data_label_encoding' ,label_encoding(self.data))
                     ,('TVAE' ,'N'): label_encoding(self.data)
                     ,('CoupulaGAN' ,'Y'): getattr(self ,'data_label_encoding' ,label_encoding(self.data))
                     ,('CoupulaGAN' ,'N'): label_encoding(self.data)
                     }

        self.sd_sdv_data = __map_data.get((__model
                                          ,__downcast if __model in ['GaussianCoupula','CTGAN'] else __label_encoding
                                          )
                                         ,None)
        if self.sd_sdv_data is None:
            import warnings
            raise Exception(f"Model not support: In SingleTable, only GaussianCoupula/CTGAN/TVAE/CoupulaGAN, now is {__model}.")



    ####### ####### #######
    # metadata            #
    ####### ####### #######
    def __singletable(self):
        import time
        from sdv.metadata import SingleTableMetadata
        __time_start = time.time()
        self.sd_sdv_metadata = SingleTableMetadata()
        self.sd_sdv_metadata.detect_from_dataframe(self.sd_sdv_data)
        print(f"Metafile loading time: {round(time.time()-__time_start ,4)} sec.")



    ####### ####### #######
    # Synthesizer - SingleTable #
    ####### ####### #######
    def __singletable_GaussianCoupula(self):
        from sdv.single_table import GaussianCopulaSynthesizer
        self.synthesizer = GaussianCopulaSynthesizer(self.sd_sdv_metadata)


    def __singletable_CTGAN(self):
        from sdv.single_table import CTGANSynthesizer
        self.synthesizer = CTGANSynthesizer(self.sd_sdv_metadata)


    def __singletable_TVAE(self):
        from sdv.single_table import TVAESynthesizer
        self.synthesizer = TVAESynthesizer(self.sd_sdv_metadata)


    def __singletable_CoupulaGAN(self):
        from sdv.single_table import CopulaGANSynthesizer
        self.synthesizer = CopulaGANSynthesizer(self.sd_sdv_metadata)



    ####### ####### #######
    # Sample              #
    ####### ####### #######
    def sample(self
              ,reset_sample       = 'N'
              ,sample_rows        = 100
              ,sample_rows_as_raw = 'N'
              ,save_data   = 'Y'
              ,save_method = 'csv'
              ,save_folder = '.\\data_dpsd'
              ,**kwargs):
        import time
        import os

        # sample_rows_as_raw for as same rows
        sample_rows = self.data.shape[0] if sample_rows_as_raw == 'Y' else sample_rows

        __metadata           = self.params.get('sd_params' ,{}).get('metadata'        ,'SingleTable')
        __model              = self.params.get('sd_params' ,{}).get('model'           ,'Unknown'    )
        __sd_output_filename = self.params.get('sd_params' ,{}).get('output_filename' ,'PETs_SD_SDV')

        from datetime import datetime
        import pytz
        sdsampletime = datetime.now().astimezone(pytz.timezone('Asia/Taipei'))
        self.sdsampletime = sdsampletime
        output_filename = f"{__sd_output_filename}_{sample_rows}_{sdsampletime.strftime('%Y%m%d_%H%M%S')}_{sdsampletime.tzinfo.zone.replace('/' ,'_')}"
        self.params['sample_params']['output_filename'] = output_filename

        time_start = time.time()

        if reset_sample == 'Y':
            self.synthesizer.reset_sampling()
        
        if __metadata == 'SingleTable':
            self.__singletable_sample(reset_sample = reset_sample
                                     ,sample_rows  = sample_rows
                                     )
        else:
            import warnings
            raise Exception(f"Metadata not support: only SingleTable, now is {__metadata}.")
        __sample_rows_as_raw = 'as same as raw data: ' if sample_rows_as_raw == 'Y' else ''
        print(f"Sample {__sample_rows_as_raw}# {sample_rows} rows data by {__model} in {round(time.time()-time_start ,4)} 秒")

        if save_data == 'Y':
            ####### ####### #######
            # Sample: .sample.csv.temp permission denied #
            ####### ####### #######
            timeout = 100 # 100 sec.
            csv_temp_filepath = ".sample.csv.temp"
            interval_wait_sec = 3 # every 3 sec.
            time_start = time.time()
            while True:
                if time.time() - time_start > timeout:
                    print(f"{csv_temp_filepath} Timeout: couldn't access after {timeout} sec.")
                    return False
                if not os.path.exists(csv_temp_filepath):
                    return True
                try:
                    with open(csv_temp_filepath, 'r+'):
                        return True
                except IOError:
                    time.sleep(interval_wait_sec)
                    print(f"{csv_temp_filepath} been occupied, wait for {interval_wait_sec} sec.")
                    print(f"{csv_temp_filepath} been occupied, wait for {interval_wait_sec} sec..")
                    print(f"{csv_temp_filepath} been occupied, wait for {interval_wait_sec} sec...")

            self.__sample_save(**{'save_method'     : save_method
                                 ,'save_folder'     : save_folder
                                 ,'output_filename' : output_filename
                                 }
                              )



    def __sample_save(self ,save_method
                           ,save_folder
                           ,output_filename
                     ,**kwargs):
        if save_method == 'csv':
            self.synthetic_data.to_csv(f"{save_folder}\\{output_filename}.csv")
        else:
            import warnings
            raise Exception(f"Sample save not support: only csv, now is {save_method}.")
        print(f"SD data as {save_method} save in {save_folder}\\{output_filename}.{save_method}.")



    def __singletable_sample(self ,reset_sample
                                  ,sample_rows
                            ):
        batch_rows = 10000 if sample_rows >= 100000 else sample_rows
        self.synthetic_data = self.synthesizer.sample(num_rows   = sample_rows
                                                     ,batch_size = batch_rows
                                                     )