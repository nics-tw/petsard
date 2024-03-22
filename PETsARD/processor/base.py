from copy import deepcopy
import logging
from types import NoneType
import warnings

from PETsARD.processor.encoder import *
from PETsARD.processor.missing import *
from PETsARD.processor.outlier import *
from PETsARD.processor.scaler import *
from PETsARD.processor.mediator import *
from PETsARD.processor.discretizing import *
from PETsARD.error import *
from PETsARD.loader.metadata import Metadata


logging.basicConfig(level=logging.INFO, filename='log.txt', filemode='w',
                    format='[%(levelname).1s %(asctime)s] %(message)s',
                    datefmt='%Y%m%d %H:%M:%S')

class Processor:
    """
    Manage the processors. 
    It arrange the execution queue and allocate the tasks 
    to the right processors based on the metadata and the parameters.
    """

    def __init__(self, metadata: Metadata, config: dict = None) -> None:
        """
        Args:
        metadata (Metadata): The metadata class to 
            provide the metadata of the data, which contains the properties
            of the data, including column names, column types, inferred 
            column types, NA percentage per column, total number of rows and 
            columns, NA percentage in the data.
            The structure of metadata is:
                {
                    'col': {
                    col_name: {'type': pd.dtype,
                                'infer_dtype': 
                                'categorical'|'numerical'|'datetime'|'object',
                            'na_percentage': float}, ...
                    }
                },
                'global':{
                    'row_num': int,
                    'col_num': int,
                    'na_percentage': float
                    }
                }
        config (dict): The user-defined config.
        """
        # object datatype indicates the unusual data,
        # passive actions will be taken in processing procedure
        self._default_processor: dict = {
            'missing': {
                'numerical': MissingMean,
                'categorical': MissingDrop,
                'datetime': MissingDrop,
                'object': MissingDrop
            },
            'outlier': {
                'numerical': OutlierIQR,
                'categorical': lambda: None,
                'datetime': OutlierIQR,
                'object': lambda: None
            },
            'encoder': {
                'numerical': lambda: None,
                'categorical': EncoderUniform,
                'datetime': lambda: None,
                'object': EncoderUniform
            },
            'scaler': {
                'numerical': ScalerStandard,
                'categorical': lambda: None,
                'datetime': ScalerStandard,
                'object': lambda: None
            },
            'discretizing': {
                'numerical': DiscretizingKBins,
                'categorical': EncoderLabel,
                'datetime': DiscretizingKBins,
                'object': EncoderLabel
            }
        }

        self._default_sequence: list = [
            'missing',
            'outlier',
            'encoder',
            'scaler'
        ]

        self._processor_map: dict = {
            'encoder_uniform': EncoderUniform,
            'encoder_label': EncoderLabel,
            'encoder_onehot': EncoderOneHot,
            'missing_mean': MissingMean,
            'missing_median': MissingMedian,
            'missing_simple': MissingSimple,
            'missing_drop': MissingDrop,
            'outlier_zscore': OutlierZScore,
            'outlier_iqr': OutlierIQR,
            'outlier_isolationforest': OutlierIsolationForest,
            'outlier_lof': OutlierLOF,
            'scaler_standard': ScalerStandard,
            'scaler_zerocenter': ScalerZeroCenter,
            'scaler_minmax': ScalerMinMax,
            'scaler_log': ScalerLog,
            'discretizing_kbins': DiscretizingKBins,
        }

        self._metadata: dict = metadata.metadata
        logging.debug(f'Metadata loaded.')

        # processing sequence
        self._sequence: list = None
        self._fitting_sequence: list = None
        self._inverse_sequence: list = None
        self._is_fitted: bool = False

        # deal with global transformation of missinghandler and outlierhandler
        self.mediator_missing: MediatorMissing | None = None
        self.mediator_outlier: MediatorOutlier | None = None
        self.mediator_encoder: MediatorEncoder | None = None

        # global NA values imputation
        self._na_percentage_global: float = self._metadata['global'].\
            get('na_percentage', 0.0)
        self.rng = np.random.default_rng()

        self._generate_config()

        if config is not None:
            self.update_config(config=config)

        # the temp config records the config from in-process/expanded column 
        self._working_config: dict = {}

        logging.debug(f'Config loaded.')

    def _generate_config(self) -> None:
        """
        Generate config based on the metadata.
        Metadata is used for inferring the default processor based on
            the column type.

        Config structure: {processor_type: {col_name: processor_obj}}

        Args:
            None: The metadata is stored in the instance itself.

        Return:
            None: The config will be stored in the instance itself.
        """

        self._config: dict = {
            processor: dict.fromkeys(self._metadata['col'].keys())
                for processor in self._default_processor.keys()
        }

        for col, val in self._metadata['col'].items():
            for processor, obj in self._default_processor.items():
                self._config[processor][col] = obj[val['infer_dtype']]()

    def get_config(self, col: list = None, print_config: bool = False) -> dict:
        """
        Get the config from the instance.

        Args:
            col (list): The columns the user want to get the config from. 
            If the list is empty, 
                all columns from the metadata will be selected.
            print_config (bool, default=False): 
                Whether the result should be printed.

        Return:
            (dict): The config with selected columns.
        """
        get_col_list: list = []
        result_dict: dict = {
            processor: {} for processor in self._default_processor.keys()
        }

        if col:
            get_col_list = col
        else:
            get_col_list = list(self._metadata['col'].keys())

        if print_config:
            for processor in self._config.keys():
                print(processor)
                for colname in get_col_list:
                    print(
                        f'    {colname}:',
                        f' {type(self._config[processor][colname]).__name__}')
                    result_dict[processor][colname] = \
                        self._config[processor][colname]
        else:
            for processor in self._config.keys():
                for colname in get_col_list:
                    result_dict[processor][colname] = \
                        self._config[processor][colname]

        return result_dict

    def update_config(self, config: dict) -> None:
        """
        Update part of the config.

        Args:
            config (dict): The dict with the same format as the config class.
        """

        for processor, val in config.items():
            for col, obj in val.items():
                # accept string of processor
                if type(obj) == str:
                    obj = self._processor_map.get(obj, None)()

                self._config[processor][col] = obj

    def fit(self, data: pd.DataFrame, sequence: list = None) -> None:
        """
        Fit the data.

        Args:
            data (pd.DataFrame): The data to be fitted.
            sequence (list): The processing sequence. 
                Avaliable procedures: 'missing', 'outlier', 
                    'encoder', 'scaler', and 'discretizing'.
                    ['missing', 'outlier', 'encoder', 'scaler'] 
                    is the default sequence.
        """

        if sequence is None:
            self._sequence = self._default_sequence
        else:
            self._check_sequence_valid(sequence)
            self._sequence = sequence

        self._fitting_sequence = self._sequence.copy()

        if 'missing' in self._sequence:
            # if missing is in the procedure,
            # MediatorMissing should be in the queue
            # right after the missing
            self.mediator_missing = MediatorMissing(self._config)
            self._fitting_sequence.insert(
                self._fitting_sequence.index('missing') + 1,
                self.mediator_missing)
            logging.info('MediatorMissing is created.')

        if 'outlier' in self._sequence:
            # if outlier is in the procedure,
            # MediatorOutlier should be in the queue
            # right after the outlier
            self.mediator_outlier = MediatorOutlier(self._config)
            self._fitting_sequence.insert(
                self._fitting_sequence.index('outlier') + 1,
                self.mediator_outlier)
            logging.info('MediatorOutlier is created.')

        if 'encoder' in self._sequence:
            # if encoder is in the procedure,
            # MediatorEncoder should be in the queue
            # right after the encoder
            self.mediator_encoder = MediatorEncoder(self._config)
            self._fitting_sequence.insert(
                self._fitting_sequence.index('encoder') + 1,
                self.mediator_encoder)
            logging.info('MediatorEncoder is created.')

        self._detect_edit_global_transformation()

        logging.debug(f'Fitting sequence generation completed.')

        for processor in self._fitting_sequence:
            if type(processor) == str:
                for col, obj in self._config[processor].items():

                    logging.debug(
                        f'{processor}: {obj} from {col} start processing.')

                    if obj is None:
                        continue

                    if processor not in obj.PROC_TYPE:
                        raise ValueError(
                            f'Invalid processor from {col} in {processor}')

                    obj.fit(data[col])

                logging.info(f'{processor} fitting done.')
            else:
                # if the processor is not a string,
                # it should be a mediator, which could be fitted directly.

                logging.debug(f'mediator: {processor} start processing.')
                processor.fit(data)
                logging.info(f'{processor} fitting done.')

        # it is a shallow copy
        self._working_config = self._config.copy()
        
        self._is_fitted = True

    def _check_sequence_valid(self, sequence: list) -> None:
        """
        Check whether the sequence is valid.

        Args:
            sequence (list): The processing sequence.
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
                'There are duplicated procedures in the sequence,',
                ' please remove them.')

        for processor in sequence:
            if processor not in self._default_processor.keys():
                raise ValueError(
                    f'{processor} is invalid, please check it again.')
            
        if 'discretizing' in sequence:
            if 'encoder' in sequence:
                raise ValueError("'discretizing' and 'encoder' processor" + \
                                 " cannot coexist.")
            if sequence[-1] != 'discretizing':
                raise ValueError("'discretizing' processor must be the last processor.")

    def _detect_edit_global_transformation(self) -> None:
        """
        Detect whether a processor in the config conducts global transformation.
        If it does, suppress other processors in the config 
            by replacing them to the global one.
        Only works with Outlier currently.
        """
        is_global_transformation: bool = False
        replaced_class: object = None

        for obj in self._config['outlier'].values():
            if obj is None:
                continue
            if obj.IS_GLOBAL_TRANSFORMATION:
                is_global_transformation = True
                replaced_class = obj.__class__
                logging.info(
                    'Global transformation detected.' +
                    f' All processors will be replaced to {replaced_class}.')
                break

        if is_global_transformation:
            for col, obj in self._config['outlier'].items():
                self._config['outlier'][col] = replaced_class()

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
                self._adjust_working_config(processor, self._fitting_sequence)
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
                                                    data.shape[0] *
                                                    self.
                                                    _na_percentage_global),
                                                replace=False).ravel())

        for col, obj in self._config['missing'].items():
            if obj is None:
                continue
            obj.set_imputation_index(index_list)

            try:
                with warnings.catch_warnings():
                    # ignore the known warning about RuntimeWarning:
                    # invalid value encountered in scalar divide
                    warnings.simplefilter('ignore')
                    # the NA percentage taking global NA percentage
                    # into consideration
                    adjusted_na_percentage: float = \
                        self._metadata['col'][col].\
                        get('na_percentage', 0.0)\
                        / self._na_percentage_global
            # if there is no NA in the original data
            except ZeroDivisionError:
                adjusted_na_percentage: float = 0.0

            obj.set_na_percentage(adjusted_na_percentage)

        # there is no method for restoring outliers
        self._inverse_sequence = self._sequence.copy()
        self._inverse_sequence.reverse()
        if 'outlier' in self._inverse_sequence:
            self._inverse_sequence.remove('outlier')

        if 'encoder' in self._inverse_sequence:
            # if encoder is in the procedure,
            # MediatorEncoder should be in the queue
            # right after the encoder
            self._inverse_sequence.insert(
                self._inverse_sequence.index('encoder'),
                self.mediator_encoder)
            logging.info('MediatorEncoder is created.')

        logging.debug(f'Inverse sequence generation completed.')

        transformed: pd.DataFrame = deepcopy(data)

        for processor in self._inverse_sequence:
            if type(processor) == str:
                for col, obj in self._config[processor].items():

                    logging.debug(
                        f'{processor}: {obj} from {col} start' +\
                        ' inverse transforming.')

                    if obj is None:
                        continue

                    transformed[col] = obj.inverse_transform(transformed[col])

                logging.info(f'{processor} inverse transformation done.')
            else:
                # if the processor is not a string,
                # it should be a mediator, which transforms the data directly.
                logging.debug(
                    f'mediator: {processor} start inverse transforming.'
                )
                logging.debug(
                    f'before transformation: data shape: {transformed.shape}')
                transformed = processor.inverse_transform(transformed)
                logging.debug(
                    f'after transformation: data shape: {transformed.shape}')
                logging.info(f'{processor} transformation done.')  

        return transformed

    # determine whether the processors are not default settings
    def get_changes(self) -> dict:
        """
        Compare the differences between the current config 
            and the default config.

        Return:
            (pd.DataFrame): A dataframe recording the differences 
                bewteen the current config and the default config.
        """
        changes_dict: dict = {
            'processor': [],
            'col': [],
            'current': [],
            'default': []
        }

        for processor, default_class in self._default_processor.items():
            for col in self._metadata['col'].keys():
                obj = self._config[processor][col]
                default_obj = default_class[self._metadata['col']
                                            [col]['infer_dtype']]

                if default_obj() is None:
                    default_obj = NoneType

                if not isinstance(obj, default_obj):
                    changes_dict['processor'].append(processor)
                    changes_dict['col'].append(col)
                    changes_dict['current'].append(type(obj).__name__)
                    changes_dict['default'].append(default_obj.__name__)

        return pd.DataFrame(changes_dict)
    
    def _adjust_working_config(self, mediator: Mediator, 
                               sequence: list) -> None:
        """
        Adjust the working config for the downstream tasks.

        For example, after one-hot encoding, some columns will be created
        and some will be removed. This method aims to correct the config
        to fit the current state and make all tasks done at ease.

        Specifically, it tracks the difference between old and new data through
        Mediator.map, creates the new config for the new data by inheriting
        the old one, and removes the old config. All changes will be applied
        to the procedures after the current one.

        Args:
            mediator (Mediator): The Mediator instance for checking the
                difference.
            sequence (list): Read the fitting sequence to determine the scope
                of the adjustment.

        Return:
            None: It will adjust the working config directly.
        """
        if len(mediator.map) == 0:
            pass
        else:
            # locate the current stage
            current_index = sequence.index(mediator)

            for i in range(current_index + 1, len(sequence)):
                if type(sequence[i]) is not str:
                    # it is a mediator
                    continue
                else:
                    processor = sequence[i]

                    for ori_col, new_col in mediator.map.items():
                        for col in new_col:
                            self._working_config[processor][col] = \
                                deepcopy(self._config[processor][ori_col])
