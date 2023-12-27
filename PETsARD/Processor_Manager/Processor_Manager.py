from ..Preprocessor import Missingist, Outlierist, Encoder, Scaler

from ..Preprocessor.Missingist_Drop import Missingist_Drop
from ..Preprocessor.Missingist_Mean import Missingist_Mean
from ..Preprocessor.Missingist_Median import Missingist_Median
from ..Preprocessor.Missingist_Simple import Missingist_Simple

from ..Preprocessor.Outlierist_IQR import Outlierist_IQR
from ..Preprocessor.Outlierist_IsolationForest import Outlierist_IsolationForest
from ..Preprocessor.Outlierist_LOF import Outlierist_LOF
from ..Preprocessor.Outlierist_Zscore import Outlierist_Zscore

from ..Preprocessor.Encoder_Label import Encoder_Label
from ..Preprocessor.Encoder_Uniform import Encoder_Uniform

from ..Preprocessor.Scaler_MinMax import Scaler_MinMax
from ..Preprocessor.Scaler_Standard import Scaler_Standard
from ..Preprocessor.Scaler_ZeroCenter import Scaler_ZeroCenter

# TODO - edit type in metadata to meet the standard of pandas
# TODO - add input and output types to all functions

class Processor_Manager:

    # object datatype indicates the unusual data,
    # passive actions will be taken in processing procedure

    _DEFAULT_MISSINGIST = {'numerical': Missingist_Mean, 
                           'categorical': Missingist_Drop,
                           'datetime': Missingist_Drop,
                           'object': Missingist_Drop}
    
    # TODO - add LOF and Isolation Forest as global config to outlierist
    
    _DEFAULT_OUTLIERIST = {'numerical': Outlierist_IQR,
                           'categorical': None,
                           'datatime': Outlierist_IQR,
                           'object': None}
    
    _DEFAULT_ENCODER = {'numerical': None,
                        'categorical': Encoder_Uniform,
                        'datetime': None,
                        'object': Encoder_Uniform}
    
    _DEFAULT_SCALER = {'numerical': Scaler_Standard,
                       'categorical': None,
                       'datetime': Scaler_Standard,
                       'object': None}
    


    def __init__(self, metadata, config=None) -> None:
        self._check_metadata_valid(metadata=metadata)
        self._metadata = metadata

        self._config = dict()

        if config is None:
            self._generate_config()
        else:
            self.set_config(config=config)

    def _check_metadata_valid(self, metadata):
        """
        Check whether the metadata contains the proper keys (metadata_col and metadata_global) for generating config.

        Input:
            metadata (dict): Metadata from the class Metadata or with the same format.

        Output:
            None
        """
        if not ('metadata_col' in metadata and 'metadata_global' in metadata):
            raise ValueError("'metadata_col' and 'metadata_global' should be in the metadata.")

    def _check_config_valid(self, config=None):
        """
        Check whether the config contains valid preprocessors. It checks the validity of column names, the validity of processor types (i.e., dict keys), and the validity of processor objects (i.e., dict values).

        Input:
            config (dict, default=None): Config generated by the class or with the same format.

        Output:
            None
        """
        config_to_check = self._config if config is None else config

        # check the validity of processor types
        if not set(config_to_check.keys()).issubset({'missingist', 'outlierist', 'encoder', 'scaler'}):
            raise ValueError(f'Invalid config processor type in the input dict, please check the dict keys of processor types.')

        for processor, processor_class in {'missingist': Missingist, 'outlierist': Outlierist, 'encoder': Encoder, 'scaler': Scaler}.items():
            
            # check the validity of column names (keys)
            if not set(config_to_check[processor].keys()).issubset(set(self._metadata['metadata_col'].keys())):
                raise ValueError(f'Some columns in the input config {processor} are not in the metadata. Please check the config or metadata again.')

            for col in config_to_check[processor].keys():
                # check the validity of processor objects (values)
                if not(isinstance(config_to_check[processor].get(col, None), processor_class) or config_to_check[processor].get(col, None) is None):
                    raise ValueError(f'{col} from {processor} contain(s) invalid processor object(s), please check them again.')
                    

    # FIXME - should pass the object here, however, due to the current design,
    # users need to pass the data when initialise the object, which causes an error
    # when generating config
    def _generate_config(self):
        """
        Generate config based on the metadata.

        Config structure: {processor_type: {col_name: processor_obj}}

        Input:
            None: The metadata is stored in the instance itself.

        Output:
            None: The config will be stored in the instance itself.
        """
        self._config = None # initialise the dict
        self._config = {'missingist': {},
                        'outlierist': {},
                        'encoder': {},
                        'scaler': {}}

        for col, val in self._metadata['metadata_col'].items():

            processor_dict = {'missingist': self._DEFAULT_MISSINGIST[val['type']],
                            'outlierist': self._DEFAULT_OUTLIERIST[val['type']],
                            'encoder': self._DEFAULT_ENCODER[val['type']],
                            'scaler': self._DEFAULT_SCALER[val['type']]}
            
            for processor, obj in processor_dict.items():
                self._config[processor][col] = obj


    def get_config(self, col=[], print_config=False):
        """
        Get the config from the instance.

        Input:
            col (list): The columns the user want to get the config from. If the list is empty, all columns from the metadata will be selected.
            print_config (bool, default=False): Whether the result should be printed.

        Output:
            (dict): The config with selected columns.
        """
        get_col_list = []
        result_dict = {'missingist': {},
                       'outlierist': {},
                       'encoder': {},
                       'scaler': {}}

        if col:
            get_col_list = col
        else:
            get_col_list = list(self._metadata['metadata_col'].keys())

        if print_config:
            for processor in self._config.keys():
                print(processor)
                for colname in get_col_list:
                    print(f'    {colname}: {self._config[processor][colname]}')
                    result_dict[processor][colname] = self._config[processor][colname]
        else:
            for processor in self._config.keys():
                for colname in get_col_list:
                    result_dict[processor][colname] = self._config[processor][colname]


        return result_dict

    def set_config(self, config):
        """
        Edit the whole config. To keep the structure of the config, it fills the unspecified preprocessors with None. To prevent from this, use update_config() instead.

        Input:
            config (dict): The dict with the same format as the config class.

        Output:
            None
        """
        self._check_config_valid(config=config)

        for processor, val in self._config.items():
            if processor not in config.keys():
                config[processor] = {}
            for col in val.keys():
                self._config[processor][col] = config[processor].get(col, None)

    def update_config(self, config):
        """
        Update part of the config.

        Input:
            config (dict): The dict with the same format as the config class.

        Output:
            None
        """
        self._check_config_valid(config=config)

        for processor, val in config.items():
            for col, obj in val.items():
                self._config[processor][col] = obj

    # should be able to select certain processor(s) to execute
    # TODO - need more step to drop outlierist selected from IQR and ZScore
    # TODO - need Outlierist manager and Missingist manager to collect all the output from the instances and decide what records should be dropped
    # TODO - check the object of outlierist before start fitting (e.g., if one of them is global transformation then suppress other transformation)
    def fit(self):
        pass

    def transform(self):
        pass

    def inverse_transform(self):
        pass

    def get_processor(self):
        pass

    
    # determine whether the processors are not default settings
    def get_changes(self):
        pass

