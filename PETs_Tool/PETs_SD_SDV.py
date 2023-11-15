# The Synthetic Data Vault
# https://sdv.dev/
# https://github.com/sdv-dev/SDV
# https://docs.sdv.dev/sdv/
from .PETs_Loader import PETs_Loader
from .PETs_util   import df_downcast ,label_encoding ,update_append_nested
# 231103, Justyn: if you failed when you run on VSCode, check if you can "import torch"
#                 if not, you should install Microsoft Visual C++ Redistributable
#                 and you can download it on Microsoft official website



class PETs_SD_SDV(PETs_Loader):

    def __init__(self ,loader=None ,params={} ,filename='' ,**kwargs):
        if loader:
            ####### ####### #######
            # init - params       #
            ####### ####### #######
            # input > loader > default
            # inherit here
            params = update_append_nested(loader.params ,params)
            # default here
            default_params = {'sd_method': 'SDV'
                             ,'sd_params': {'metadata' : 'SingleTable'
                                           ,'model'    : 'GaussianCoupula'
                                           ,'sampling'      : 'N'
                                           ,'sampling_rows' : 10000
                                           }
                             }
            params = update_append_nested(default_params ,params)
            ####### ####### #######
            # init - filename     #
            ####### ####### #######
            filename = loader.filename if filename == '' else filename
            ####### ####### #######
            # init - inherit      #
            ####### ####### #######
            super().__init__(params=params
                            ,filepath=loader.filepath ,filename=filename)

            from datetime import datetime
            import pytz
            self.sdtime = datetime.now().astimezone(pytz.timezone('Asia/Taipei'))
            ####### ####### #######
            # init - output filename #
            ####### ####### #######
            self.output_filename = f"{self.filename}_[{self.params['sd_method']}]_[{self.params['sd_params']['model']}]_{self.sdtime.strftime('%Y%m%d_%H%M%S')}_{self.sdtime.tzinfo.zone.replace('/' ,'_')}"

            self.__metadata_model(**self.params['sd_params'])


    ####### ####### #######
    # metadata            #
    ####### ####### #######
    def __metadata_model(self
                        ,metadata = 'SingleTable'
                        ,model    = 'GaussianCoupula'
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
                self.synthesizer.save(f".\model_dpsd\{self.output_filename}.pkl")

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
        