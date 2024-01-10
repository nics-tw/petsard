from copy import deepcopy
import logging
import warnings

from .Encoder import *
from .Missingist import *
from .Outlierist import *
from .Scaler import *
from .Mediator import *
from ..Error import *
from ..Metadata import Metadata


logging.basicConfig(level=logging.INFO, filename='log.txt', filemode='w',
                    format='[%(levelname).1s %(asctime)s] %(message)s',
                    datefmt='%Y%m%d %H:%M:%S')


class Processor:
    """
    Manage the processors. It arrange the execution queue and allocate the tasks to the right processors based on the metadata and the parameters.

    Args:
        metadata (Metadata): The metadata class to provide the metadata of the data.
        config (dict): The user-defined config.

    Return:
        None
    """

    # object datatype indicates the unusual data,
    # passive actions will be taken in processing procedure

    _DEFAULT_MISSINGIST: dict = {'numerical': Missingist_Mean,
                                 'categorical': Missingist_Drop,
                                 'datetime': Missingist_Drop,
                                 'object': Missingist_Drop}

    _DEFAULT_OUTLIERIST: dict = {'numerical': Outlierist_IQR,
                                 'categorical': None,
                                 'datatime': Outlierist_IQR,
                                 'object': None}

    _DEFAULT_ENCODER: dict = {'numerical': None,
                              'categorical': Encoder_Uniform,
                              'datetime': None,
                              'object': Encoder_Uniform}

    _DEFAULT_SCALER: dict = {'numerical': Scaler_Standard,
                             'categorical': None,
                             'datetime': Scaler_Standard,
                             'object': None}

    _DEFAULT_SEQUENCE: list = ['missingist', 'outlierist', 'encoder', 'scaler']

    _PROCESSOR_MAP: dict = {'encoder_uniform': Encoder_Uniform,
                            'encoder_label': Encoder_Label,
                            'missingist_mean': Missingist_Mean,
                            'missingist_median': Missingist_Median,
                            'missingist_simple': Missingist_Simple,
                            'missingist_drop': Missingist_Drop,
                            'outlierist_zscore': Outlierist_ZScore,
                            'outlierist_iqr': Outlierist_IQR,
                            'outlierist_isolationforest': Outlierist_IsolationForest,
                            'outlierist_lof': Outlierist_LOF,
                            'scaler_standard': Scaler_Standard,
                            'scaler_zerocenter': Scaler_ZeroCenter,
                            'scaler_minmax': Scaler_MinMax,
                            'scaler_log': Scaler_Log}

    def __init__(self, metadata: Metadata, config: dict = None) -> None:
        metadata: dict = metadata.metadata
        self._check_metadata_valid(metadata=metadata)
        self._metadata: dict = metadata
        logging.debug(f'Metadata loaded.')

        # processing sequence
        self._sequence: list = None
        self._fitting_sequence: list = None
        self._inverse_sequence: list = None
        self._is_fitted: bool = False

        # deal with global transformation of missingist and outlierist
        self.mediator_missingist: Mediator_Missingist | None = None
        self.mediator_outlierist: Mediator_Outlierist | None = None

        # global NA values imputation
        self._na_percentage_global: float = metadata['metadata_global'].get('na_percentage',
                                                                            0.0)
        self.rng = np.random.default_rng()

        self._config: dict = dict()

        if config is None:
            self._generate_config()
        else:
            self.set_config(config=config)

        logging.debug(f'Config loaded.')

    def _check_metadata_valid(self, metadata: dict) -> None:
        """
        Check whether the metadata contains the proper keys (metadata_col and metadata_global) for generating config.

        Args:
            metadata (dict): Metadata from the class Metadata or with the same format.

        Return:
            None
        """
        # check the structure of metadata
        if type(metadata) != dict:
            raise TypeError('Metadata should be a dict.')

        if not ('metadata_col' in metadata and 'metadata_global' in metadata):
            raise ValueError(
                "'metadata_col' and 'metadata_global' should be in the metadata.")

        if type(metadata['metadata_col']) != dict:
            raise TypeError('metadata_col should be a dict.')

        if type(metadata['metadata_global']) != dict:
            raise TypeError('metadata_global should be a dict.')

        for v in metadata['metadata_col'].values():
            if type(v) != dict:
                raise TypeError(
                    'The elements in metadata_col should be a dict.')

    def _check_config_valid(self, config_to_check: dict = None) -> None:
        """
        Check whether the config contains valid preprocessors. It checks the validity of column names, the validity of processor types (i.e., dict keys), and the validity of processor objects (i.e., dict values).

        Args:
            config (dict, default=None): Config generated by the class or with the same format.

        Return:
            None
        """
        if config_to_check is None:
            raise ValueError('A config should be passed.')

        # check the structure of config
        if type(config_to_check) != dict:
            raise TypeError('Config should be a dict.')

        # check the validity of processor types
        if not set(config_to_check.keys()).issubset({'missingist', 'outlierist', 'encoder', 'scaler'}):
            raise ValueError(
                f'Invalid config processor type in the input dict, please check the dict keys of processor types.')

        for processor, processor_class in {'missingist': Missingist, 'outlierist': Outlierist, 'encoder': Encoder, 'scaler': Scaler}.items():

            if config_to_check.get(processor, None) is None:
                continue

            if type(config_to_check[processor]) != dict:
                raise TypeError(
                    'The config in each processor should be a dict.')

            # check the validity of column names (keys)
            if not set(config_to_check[processor].keys()).issubset(set(self._metadata['metadata_col'].keys())):
                raise ValueError(
                    f'Some columns in the input config {processor} are not in the metadata. Please check the config or metadata again.')

            for col in config_to_check[processor].keys():
                # check the validity of processor objects (values)
                obj = config_to_check[processor].get(col, None)

                if not (isinstance(obj, processor_class) or isinstance(obj, str) or obj is None):
                    raise ValueError(
                        f'{col} from {processor} contain(s) invalid processor object(s), please check them again.')

    def _generate_config(self) -> None:
        """
        Generate config based on the metadata.

        Config structure: {processor_type: {col_name: processor_obj}}

        Args:
            None: The metadata is stored in the instance itself.

        Return:
            None: The config will be stored in the instance itself.
        """
        self._config: dict = None  # initialise the dict
        self._config = {'missingist': {},
                        'outlierist': {},
                        'encoder': {},
                        'scaler': {}}

        for col, val in self._metadata['metadata_col'].items():

            processor_dict: dict = {'missingist': self._DEFAULT_MISSINGIST[val['infer_dtype']]()
                                    if self._DEFAULT_MISSINGIST[val['infer_dtype']] is not None else None,
                                    'outlierist': self._DEFAULT_OUTLIERIST[val['infer_dtype']]()
                                    if self._DEFAULT_OUTLIERIST[val['infer_dtype']] is not None else None,
                                    'encoder': self._DEFAULT_ENCODER[val['infer_dtype']]()
                                    if self._DEFAULT_ENCODER[val['infer_dtype']] is not None else None,
                                    'scaler': self._DEFAULT_SCALER[val['infer_dtype']]()
                                    if self._DEFAULT_SCALER[val['infer_dtype']] is not None else None}

            for processor, obj in processor_dict.items():
                self._config[processor][col] = obj

    def get_config(self, col: list = None, print_config: bool = False) -> dict:
        """
        Get the config from the instance.

        Args:
            col (list): The columns the user want to get the config from. If the list is empty, all columns from the metadata will be selected.
            print_config (bool, default=False): Whether the result should be printed.

        Return:
            (dict): The config with selected columns.
        """
        get_col_list: list = []
        result_dict: dict = {'missingist': {},
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
                    print(
                        f'    {colname}: {type(self._config[processor][colname]).__name__}')
                    result_dict[processor][colname] = self._config[processor][colname]
        else:
            for processor in self._config.keys():
                for colname in get_col_list:
                    result_dict[processor][colname] = self._config[processor][colname]

        return result_dict

    def set_config(self, config: dict) -> None:
        """
        Edit the whole config. To keep the structure of the config, it fills the unspecified preprocessors with None. To prevent from this, use update_config() instead.

        Args:
            config (dict): The dict with the same format as the config class.

        Return:
            None
        """
        self._check_config_valid(config_to_check=config)

        for processor, val in self._config.items():
            if processor not in config.keys():
                config[processor] = {}
            for col in val.keys():
                obj = config[processor].get(col, None)
                
                # accept string of processor
                if type(obj) == str:
                    obj_convert = self._PROCESSOR_MAP.get(obj, None)
                    if obj_convert is None:
                        raise ValueError(f'Invalid processor name {obj}.')
                    else:
                        self._config[processor][col] = obj_convert()
                else:
                    self._config[processor][col] = obj

    def update_config(self, config: dict) -> None:
        """
        Update part of the config.

        Args:
            config (dict): The dict with the same format as the config class.

        Return:
            None
        """
        self._check_config_valid(config_to_check=config)

        for processor, val in config.items():
            for col, obj in val.items():
                # accept string of processor
                if type(obj) == str:
                    obj_convert = self._PROCESSOR_MAP.get(obj, None)
                    if obj_convert is None:
                        raise ValueError(f'Invalid processor name {obj}.')
                    else:
                        self._config[processor][col] = obj_convert()
                else:
                    self._config[processor][col] = obj

    def fit(self, data: pd.DataFrame, sequence: list = None) -> None:
        """
        Fit the data.

        Args:
            data (pd.DataFrame): The data to be fitted.
            sequence (list): The processing sequence. 
                Avaliable procedures: 'missingist', 'outlierist', 'encoder', 'scaler'.
                This is the default sequence.

        Return:
            None
        """

        if sequence is None:
            self._sequence = self._DEFAULT_SEQUENCE
        else:
            self._check_sequence_valid(sequence)
            self._sequence = sequence

        self._fitting_sequence = self._sequence.copy()

        if 'missingist' in self._sequence:
            # if missingist is in the procedure, Mediator_Missingist should be in the queue right after the missingist
            self.mediator_missingist = Mediator_Missingist(self._config)
            self._fitting_sequence.insert(self._fitting_sequence.index('missingist')+1,
                                          self.mediator_missingist)
            logging.info('Mediator_Missingist is created.')

        if 'outlierist' in self._sequence:
            # if outlierist is in the procedure, Mediator_Outlierist should be in the queue right after the outlierist
            self.mediator_outlierist = Mediator_Outlierist(self._config)
            self._fitting_sequence.insert(self._fitting_sequence.index('outlierist')+1,
                                          self.mediator_outlierist)
            logging.info('Mediator_Outlierist is created.')

        self._detect_edit_global_transformation()

        logging.debug(f'Fitting sequence generation completed.')

        for processor in self._fitting_sequence:
            if type(processor) == str:
                for col, obj in self._config[processor].items():

                    logging.debug(
                        f'{processor}: {obj} from {col} start processing.')

                    if obj is None:
                        continue

                    obj.fit(data[col])

                logging.info(f'{processor} fitting done.')
            else:
                # if the processor is not a string,
                # it should be a mediator, which could be fitted directly.

                logging.debug(f'mediator: {processor} start processing.')
                processor.fit(data)
                logging.info(f'{processor} fitting done.')

        self._is_fitted = True

    def _check_sequence_valid(self, sequence: list) -> None:
        """
        Check whether the sequence is valid.

        Args:
            sequence (list): The processing sequence.

        Return:
            None
        """
        if type(sequence) != list:
            raise TypeError('Sequence should be a list.')

        if len(sequence) == 0:
            raise ValueError(
                'There should be at least one procedure in the sequence.')

        if len(sequence) > 4:
            raise ValueError('Too many procedures!')

        if len(list(set(sequence))) != len(sequence):
            raise ValueError(
                'There are duplicated procedures in the sequence, please remove them.')

        for processor in sequence:
            if processor not in ['missingist', 'outlierist', 'encoder', 'scaler']:
                raise ValueError(
                    f'{processor} is invalid, please check it again.')

    def _detect_edit_global_transformation(self) -> None:
        """
        Detect whether a processor in the config conducts global transformation.
        If it does, suppress other processors in the config by replacing them to the global one.
        Only works with Outlierist currently.

        Args:
            None

        Return:
            None
        """
        is_global_transformation: bool = False
        replaced_class: object = None

        for obj in self._config['outlierist'].values():
            if obj is None:
                continue
            if obj.IS_GLOBAL_TRANSFORMATION:
                is_global_transformation = True
                replaced_class = obj.__class__
                logging.info(
                    f'Global transformation detected. All processors will be replaced to {replaced_class}.')
                break

        if is_global_transformation:
            for col, obj in self._config['outlierist'].items():
                self._config['outlierist'][col] = replaced_class()

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transform the data through a series of procedures.

        Args:
            data (pd.DataFrame): The data to be transformed.

        Return:
            transformed (pd.DataFrame): The transformed data.
        """
        if not self._is_fitted:
            raise UnfittedError('The object is not fitted. Use .fit() first.')

        transformed: pd.DataFrame = deepcopy(data)

        for processor in self._fitting_sequence:
            if type(processor) == str:
                for col, obj in self._config[processor].items():

                    logging.debug(
                        f'{processor}: {obj} from {col} start transforming.')

                    if obj is None:
                        continue

                    transformed[col] = obj.transform(transformed[col])

                logging.info(f'{processor} transformation done.')
            else:
                # if the processor is not a string,
                # it should be a mediator, which transforms the data directly.

                logging.debug(f'mediator: {processor} start transforming.')
                logging.debug(
                    f'before transformation: data shape: {transformed.shape}')
                transformed = processor.transform(transformed)
                logging.debug(
                    f'after transformation: data shape: {transformed.shape}')
                logging.info(f'{processor} transformation done.')

        return transformed

    def inverse_transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Inverse transform the data through a series of procedures.

        Args:
            data (pd.DataFrame): The data to be inverse transformed.

        Return:
            transformed (pd.DataFrame): The inverse transformed data.
        """
        if not self._is_fitted:
            raise UnfittedError('The object is not fitted. Use .fit() first.')

        # set NA percentage in Missingist
        index_list: list = list(self.rng.choice(data.index,
                                                size=int(
                                                    data.shape[0]*self._na_percentage_global),
                                                replace=False).ravel())

        for col, obj in self._config['missingist'].items():
            if obj is None:
                continue
            obj.set_imputation_index(index_list)

            try:
                with warnings.catch_warnings():
                    # ignore the known warning about RuntimeWarning: invalid value encountered in scalar divide
                    warnings.simplefilter('ignore')
                    # the NA percentage taking global NA percentage into consideration
                    adjusted_na_percentage: float = self._metadata['metadata_col'][col].get('na_percentage', 0.0)\
                        / self._na_percentage_global
            # if there is no NA in the original data
            except ZeroDivisionError:
                adjusted_na_percentage: float = 0.0

            obj.set_na_percentage(adjusted_na_percentage)

        # there is no method for restoring outliers
        self._inverse_sequence = self._sequence.copy()
        if 'outlierist' in self._inverse_sequence:
            self._inverse_sequence.remove('outlierist')

        logging.debug(f'Inverse sequence generation completed.')

        transformed: pd.DataFrame = deepcopy(data)

        # mediators are not involved in the inverse_transform process.
        for processor in self._inverse_sequence:
            for col, obj in self._config[processor].items():

                logging.debug(
                    f'{processor}: {obj} from {col} start inverse transforming.')

                if obj is None:
                    continue

                transformed[col] = obj.inverse_transform(transformed[col])

            logging.info(f'{processor} inverse transformation done.')

        return transformed

    # determine whether the processors are not default settings

    def get_changes(self) -> dict:
        """
        Compare the differences between the current config and the default config.

        Args:
            None

        Return:
            (pd.DataFrame): A dataframe recording the differences bewteen the current config and the default config.
        """
        changes_dict: dict = {'processor': [], 'col': [],
                              'current': [], 'default': []}

        for processor, default_class in {'missingist': self._DEFAULT_MISSINGIST, 'outlierist': self._DEFAULT_OUTLIERIST, 'encoder': self._DEFAULT_ENCODER, 'scaler': self._DEFAULT_SCALER}.items():
            for col, obj in self._config[processor].items():
                if default_class[self._metadata['metadata_col'][col]['infer_dtype']] is None:
                    if obj is not None:
                        changes_dict['processor'].append(processor)
                        changes_dict['col'].append(col)
                        changes_dict['current'].append(type(obj).__name__)
                        changes_dict['default'].append('NoneType')
                elif not isinstance(obj, default_class[self._metadata['metadata_col'][col]['infer_dtype']]):
                    changes_dict['processor'].append(processor)
                    changes_dict['col'].append(col)
                    changes_dict['current'].append(type(obj).__name__)
                    changes_dict['default'].append(
                        default_class[self._metadata['metadata_col'][col]['infer_dtype']].__name__)

        return pd.DataFrame(changes_dict)
