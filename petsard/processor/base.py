import logging
import warnings
from copy import deepcopy
from types import NoneType

import numpy as np
import pandas as pd
from pandas.api.types import is_datetime64_any_dtype

from petsard.exceptions import ConfigError, UnfittedError
from petsard.metadater import Metadater, SchemaMetadata
from petsard.processor.discretizing import DiscretizingKBins
from petsard.processor.encoder import (
    EncoderDateDiff,
    EncoderLabel,
    EncoderMinguoDate,
    EncoderOneHot,
    EncoderUniform,
)
from petsard.processor.mediator import (
    Mediator,
    MediatorEncoder,
    MediatorMissing,
    MediatorOutlier,
    MediatorScaler,
)
from petsard.processor.missing import (
    MissingDrop,
    MissingMean,
    MissingMedian,
    MissingMode,
    MissingSimple,
)
from petsard.processor.outlier import (
    OutlierIQR,
    OutlierIsolationForest,
    OutlierLOF,
    OutlierZScore,
)
from petsard.processor.scaler import (
    ScalerLog,
    ScalerMinMax,
    ScalerStandard,
    ScalerTimeAnchor,
    ScalerZeroCenter,
)


class DefaultProcessorMap:
    """
    Mapping of default processors for different data types.

    object datatype indicates the unusual data,
        passive actions will be taken in processing procedure
    """

    PROCESSOR_MAP: dict[str, dict[str, str]] = {
        "missing": {
            "numerical": MissingMean,
            "categorical": MissingDrop,
            "datetime": MissingDrop,
            "object": MissingDrop,
        },
        "outlier": {
            "numerical": OutlierIQR,
            "categorical": lambda: None,
            "datetime": OutlierIQR,
            "object": lambda: None,
        },
        "encoder": {
            "numerical": lambda: None,
            "categorical": EncoderUniform,
            "datetime": lambda: None,
            "object": EncoderUniform,
        },
        "scaler": {
            "numerical": ScalerStandard,
            "categorical": lambda: None,
            "datetime": ScalerStandard,
            "object": lambda: None,
        },
        "discretizing": {
            "numerical": DiscretizingKBins,
            "categorical": EncoderLabel,
            "datetime": DiscretizingKBins,
            "object": EncoderLabel,
        },
    }

    VALID_TYPES: frozenset = frozenset(PROCESSOR_MAP.keys())

    @classmethod
    def get_processor(cls, processor_type: str, data_type: str):
        processor_class = cls.CLASS_MAP.get(processor_type, lambda: None)
        if processor_class is None:
            raise ConfigError(f"Invalid sub-processor type: {processor_type}")
        return processor_class


class ProcessorClassMap:
    """Mapping of processor names to their corresponding classes."""

    CLASS_MAP: dict[str, str] = {
        # encoder
        "encoder_label": EncoderLabel,
        "encoder_onehot": EncoderOneHot,
        "encoder_uniform": EncoderUniform,
        "encoder_minguodate": EncoderMinguoDate,
        "encoder_datediff": EncoderDateDiff,
        # missing
        "missing_drop": MissingDrop,
        "missing_mean": MissingMean,
        "missing_median": MissingMedian,
        "missing_mode": MissingMode,
        "missing_simple": MissingSimple,
        # outlier
        "outlier_lof": OutlierLOF,
        "outlier_iqr": OutlierIQR,
        "outlier_isolationforest": OutlierIsolationForest,
        "outlier_zscore": OutlierZScore,
        # scaler
        "scaler_log": ScalerLog,
        "scaler_minmax": ScalerMinMax,
        "scaler_standard": ScalerStandard,
        "scaler_timeanchor": ScalerTimeAnchor,
        "scaler_zerocenter": ScalerZeroCenter,
        # discretizing
        "discretizing_kbins": DiscretizingKBins,
    }

    VALID_NAMES: frozenset = frozenset(CLASS_MAP.keys())

    @classmethod
    def get_class(cls, processor_name: str):
        subprocessor_class = cls.CLASS_MAP.get(processor_name, lambda: None)
        if subprocessor_class is None:
            raise ConfigError(f"Invalid sub-processor name: {processor_name}")
        return subprocessor_class


class MediatorMap:  # pragma: no cover
    """
    Mapping of mediator classes to their corresponding processors.
    """

    MEDIATOR_MAP = {
        "missing": {"class": MediatorMissing, "attr_name": "mediator_missing"},
        "outlier": {"class": MediatorOutlier, "attr_name": "mediator_outlier"},
        "encoder": {"class": MediatorEncoder, "attr_name": "mediator_encoder"},
        "scaler": {"class": MediatorScaler, "attr_name": "mediator_scaler"},
    }

    @classmethod
    def get_class_info(cls, processor_type: str):
        mediator_class = cls.MEDIATOR_MAP.get(processor_type)
        if mediator_class is None:
            raise ConfigError(f"Invalid processor type of mediator: {processor_type}")
        return mediator_class


class Processor:
    """
    Manage the processors.
    It arrange the execution queue and allocate the tasks
    to the right processors based on the metadata and the parameters.
    """

    MAX_SEQUENCE_LENGTH: int = 4  # Maximum number of procedures allowed in sequence
    DEFAULT_SEQUENCE: list[str] = ["missing", "outlier", "encoder", "scaler"]

    def __init__(self, metadata: SchemaMetadata, config: dict = None) -> None:
        """
        Args:
            metadata (SchemaMetadata):
                The schema metadata class to provide the metadata of the data,
                which contains the properties of the data,
                including column names, column types, inferred column types,
                NA percentage per column, total number of rows and columns, NA percentage in the data.

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

        Attr.
            logger (logging.Logger): The logger for the processor.
            _metadata (SchemaMetadata): The schema metadata of the data.
            _is_fitted (bool): Whether the processor is fitted.
            _config (dict): The config of the processor.
            _working_config (dict): The temporary config for in-process columns.
            _sequence (list): The user-defined sequence.
            _fitting_sequence (list): The actual fitting sequence with mediators.
            _inverse_sequence (list): The sequence for inverse transformation.
            _na_percentage_global (float): The global NA percentage.
            _rng (np.random.Generator): The random number generator for NA imputation.
        """

        # Setup logging
        self.logger = logging.getLogger(f"PETsARD.{self.__class__.__name__}")
        self.logger.debug("Initializing Processor")
        self.logger.debug(f"Loaded metadata contains {len(metadata.fields)} fields")

        self.logger.debug("config is provided:")
        self.logger.debug(f"config is provided: {config}")

        # Initialize metadata
        self._metadata: SchemaMetadata = metadata
        self.logger.debug("Schema metadata loaded.")

        # Initialize processing state
        self._is_fitted: bool = False
        self._config: dict = {}  # Will be set in _generate_config()
        self._working_config: dict = {}  # Temporary config for in-process columns

        # Initialize sequence tracking
        self._sequence: list = None  # User-defined sequence
        self._fitting_sequence: list = None  # Actual fitting sequence with mediators
        self._inverse_sequence: list = None  # Sequence for inverse transformation

        # setup mediators
        self._mediator: dict[str, Mediator] = {}

        # Setup NA handling
        self._na_percentage_global: float = self._get_global_na_percentage()
        self._rng = np.random.default_rng()  # Random number generator for NA imputation

        self._generate_config()

        if config is not None:
            self.update_config(config=config)

        self.logger.debug("Config loaded.")

    def _get_field_names(self) -> list[str]:
        """Get all field names from schema metadata"""
        return [field.name for field in self._metadata.fields]

    def _get_field_infer_dtype(self, field_name: str) -> str:
        """Get inferred data type for a field"""
        field = self._metadata.get_field(field_name)
        if not field:
            raise ValueError(f"Field {field_name} not found in metadata")

        # Map DataType to legacy string format
        if hasattr(field.data_type, "value"):
            data_type_str = field.data_type.value.lower()
        else:
            data_type_str = str(field.data_type).lower()

        # Map specific DataType values to legacy categories
        if data_type_str in [
            "int8",
            "int16",
            "int32",
            "int64",
            "float32",
            "float64",
            "decimal",
        ]:
            return "numerical"
        elif data_type_str in ["string", "binary"]:
            return "categorical"
        elif data_type_str == "boolean":
            return "categorical"
        elif data_type_str in ["date", "time", "timestamp", "timestamp_tz"]:
            return "datetime"
        else:
            return "object"

    def _get_field_dtype(self, field_name: str) -> str:
        """Get source dtype for a field"""
        field = self._metadata.get_field(field_name)
        if not field:
            raise ValueError(f"Field {field_name} not found in metadata")
        return field.source_dtype

    def _get_field_na_percentage(self, field_name: str) -> float:
        """Get NA percentage for a field"""
        field = self._metadata.get_field(field_name)
        if not field or not field.stats:
            return 0.0
        return field.stats.na_percentage

    def _get_global_na_percentage(self) -> float:
        """Calculate global NA percentage from all fields"""
        if not self._metadata.fields:
            return 0.0

        total_na = sum(
            field.stats.na_count if field.stats else 0
            for field in self._metadata.fields
        )
        total_rows = max(
            field.stats.row_count if field.stats else 0
            for field in self._metadata.fields
        )
        total_cells = total_rows * len(self._metadata.fields)

        return (total_na / total_cells) if total_cells > 0 else 0.0

    def _generate_config(self) -> None:
        """
        Generate config based on the metadata.
        Metadata is used for inferring the default processor based on
            the column type.

        Config structure: {
            processor_type: {
                col_name: processor_obj
            }
        }

        Return:
            None: The config will be stored in the instance itself.
        """
        self.logger.debug("Starting config generation")

        field_names = self._get_field_names()
        self._config: dict = {
            processor: dict.fromkeys(field_names)
            for processor in DefaultProcessorMap.VALID_TYPES
        }

        for col in field_names:
            infer_dtype = self._get_field_infer_dtype(col)
            self.logger.debug(f"Processing column '{col}': inferred type {infer_dtype}")
            for processor, obj in DefaultProcessorMap.PROCESSOR_MAP.items():
                processor_class = obj[infer_dtype]
                self.logger.debug(
                    f"  > Setting {processor} processor: {processor_class.__name__}"
                )
                self._config[processor][col] = processor_class()

        self.logger.debug("Config generation completed")

    def get_config(self, col: list = None) -> dict:
        """
        Get the config from the instance.

        Args:
            col (list): The columns the user want to get the config from.
            If the list is empty,
                all columns from the metadata will be selected.

        Return:
            (dict): The config with selected columns.
        """
        get_col_list: list = []
        result_dict: dict = {
            processor: {} for processor in DefaultProcessorMap.VALID_TYPES
        }

        if col:
            get_col_list = col
        else:
            get_col_list = self._get_field_names()

        for processor in self._config.keys():
            for colname in get_col_list:
                result_dict[processor][colname] = self._config[processor][colname]

        return result_dict

    def update_config(self, config: dict) -> None:
        """
        Update part of the config.

        Args:
            config (dict): The dict with the same format as the config class.
        """

        for processor, val in config.items():
            for col, processor_spec in val.items():
                # convert sub-processor name to class
                if processor_spec is None or (
                    isinstance(processor_spec, str) and processor_spec.lower() == "none"
                ):
                    obj = None
                elif isinstance(processor_spec, str):
                    processor_code = processor_spec
                    obj = ProcessorClassMap.get_class(processor_code)()
                elif isinstance(processor_spec, dict):
                    processor_code = processor_spec.pop("method")
                    self.logger.debug(f"{processor} config: {processor_spec}")
                    obj = ProcessorClassMap.get_class(processor_code)(**processor_spec)
                else:
                    self.logger.error(f"Invalid processor spec: {processor_spec}")
                    raise ConfigError(f"Invalid processor spec: {processor_spec}")

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
            self._sequence = self.DEFAULT_SEQUENCE
        else:
            self._check_sequence_valid(sequence)
            self._sequence = sequence

        self._fitting_sequence = self._sequence.copy()

        # Mediator creation
        for proc_name in self._sequence:
            mediator_info = MediatorMap.get_class_info(proc_name)
            if mediator_info:
                mediator = mediator_info["class"](self._config)
                self._mediator[proc_name] = mediator
                # MediatorScaler for TimeAnchor should .set_reference_time() before Scaler in transform()
                if isinstance(mediator, MediatorScaler):
                    self._fitting_sequence.insert(
                        self._fitting_sequence.index(proc_name), mediator
                    )
                # Other Mediator is modified after the processor
                else:
                    self._fitting_sequence.insert(
                        self._fitting_sequence.index(proc_name) + 1, mediator
                    )
                self.logger.info(f"{mediator_info['class'].__name__} is created.")

        self._detect_edit_global_transformation()

        self.logger.debug("Fitting sequence generation completed.")

        for processor in self._fitting_sequence:
            if isinstance(processor, str):
                for col, obj in self._config[processor].items():
                    self.logger.debug(
                        f"{processor}: {type(obj).__name__} from {col} start processing."
                    )

                    if obj is None:
                        continue

                    if processor not in obj.PROC_TYPE:
                        raise ValueError(f"Invalid processor from {col} in {processor}")

                    obj.fit(data[col])

                self.logger.info(f"{processor} fitting done.")
            else:
                # if the processor is not a string,
                # it should be a mediator, which could be fitted directly.

                # Skip fit() for MediatorScaler
                if not isinstance(processor, MediatorScaler):
                    self.logger.debug(
                        f"mediator: {type(processor).__name__} start processing."
                    )
                    processor.fit(data)
                    self.logger.info(f"{type(processor).__name__} fitting done.")

        # it is a shallow copy
        self._working_config = self._config.copy()

        self._is_fitted = True

    def _check_sequence_valid(self, sequence: list) -> None:
        """
        Check whether the sequence is valid.

        Args:
            sequence (list[str]): The processing sequence.


        Raises:
            TypeError: If sequence is not a list.
            ValueError: If sequence is empty, contains duplicates,
                    exceeds max length, or contains invalid processors.
        """
        self.logger.debug(f"Validating sequence: {sequence}")
        error_msg: str = None

        # Check type
        if not isinstance(sequence, list):
            error_msg = (
                "Sequence must be a list of processing steps, "
                f"got {type(sequence).__name__} instead"
            )
            self.logger.error(error_msg)
            raise TypeError(error_msg)

        # Check empty
        if len(sequence) == 0:
            error_msg = (
                "Sequence cannot be empty. Must contain at least one processing step"
            )
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        # Check length
        if len(sequence) > self.MAX_SEQUENCE_LENGTH:
            error_msg = (
                f"Sequence length {len(sequence)} exceeds maximum allowed length "
                f"({self.MAX_SEQUENCE_LENGTH})"
            )
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        # Check duplicates
        if len(set(sequence)) != len(sequence):
            # Find the duplicated items for better error message
            duplicates = [item for item in sequence if sequence.count(item) > 1]
            error_msg = (
                "Duplicate processors found in sequence. "
                f"Duplicated items: {', '.join(duplicates)}"
            )
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        invalid_processors: set = set(sequence) - DefaultProcessorMap.VALID_TYPES
        if invalid_processors:
            error_msg = f"Invalid processors found: {', '.join(invalid_processors)}."
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        if "discretizing" in sequence:
            if "encoder" in sequence:
                error_msg = (
                    "'discretizing' and 'encoder' processors cannot be used together. "
                    "Please choose only one of them"
                )
                self.logger.error(error_msg)
                raise ValueError(error_msg)
            if sequence[-1] != "discretizing":
                error_msg = (
                    "'discretizing' processor must be the last step in the sequence. "
                    f"Current sequence: {' -> '.join(sequence)}"
                )
                self.logger.error(error_msg)
                raise ValueError(error_msg)

        self.logger.debug("Sequence validation completed successfully")

    def _detect_edit_global_transformation(self) -> None:
        """
        Detect whether a processor in the config conducts global transformation.
        If it does, suppress other processors in the config
            by replacing them to the global one.
        Only works with Outlier currently.
        """
        is_global_transformation: bool = False
        replaced_class: object = None

        for obj in self._config["outlier"].values():
            if obj is None:
                continue
            if obj.IS_GLOBAL_TRANSFORMATION:
                is_global_transformation = True
                replaced_class = obj.__class__
                self.logger.info(
                    "Global transformation detected."
                    + f" All processors will be replaced to {replaced_class}."
                )
                break

        if is_global_transformation:
            for col, obj in self._config["outlier"].items():
                self._config["outlier"][col] = replaced_class()

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transform the data through a series of procedures.

        Args:
            data (pd.DataFrame): The data to be transformed.

        Return:
            transformed (pd.DataFrame): The transformed data.
        """
        if not self._is_fitted:
            raise UnfittedError("The object is not fitted. Use .fit() first.")

        self.logger.debug(f"Starting data transformation, input shape: {data.shape}")

        self.transformed: pd.DataFrame = data.copy()

        for processor in self._fitting_sequence:
            if isinstance(processor, str):
                self.logger.debug(f"Executing {processor} processing")

                for col, obj in self._config[processor].items():
                    self.logger.debug(
                        f"{processor}: {type(obj).__name__} from {col} start transforming."
                    )

                    if obj is None:
                        self.logger.debug(
                            f"  > Skipping column '{col}': no processing needed"
                        )
                        continue

                    # Log pre-transformation statistics
                    if self.transformed[col].dtype.kind in "biufc":  # numeric columns
                        self.logger.debug(
                            f"  > Pre-transform stats: "
                            f"mean={self.transformed[col].mean():.4f}, "
                            f"std={self.transformed[col].std():.4f}, "
                            f"na_cnt={self.transformed[col].isna().sum()}"
                        )

                    self.transformed[col] = obj.transform(self.transformed[col])

                    infer_dtype = self._get_field_infer_dtype(col)
                    if infer_dtype == "datetime":
                        # it is fine to re-adjust mulitple times
                        #   for get the final dtype,
                        # and it is impossible for re-adjust under current logic
                        if isinstance(
                            obj,
                            (
                                EncoderLabel,
                                EncoderOneHot,
                                EncoderUniform,
                                EncoderMinguoDate,
                                EncoderDateDiff,
                                ScalerLog,
                                ScalerMinMax,
                                ScalerStandard,
                                ScalerZeroCenter,
                            ),
                        ):
                            Metadater.adjust_metadata_after_processing(
                                mode="columnwise",
                                data=self.transformed[col],
                                original_metadata=self._metadata,
                                col=col,
                            )

                    # Log post-transformation statistics
                    if self.transformed[col].dtype.kind in "biufc":
                        self.logger.debug(
                            f"  > Post-transform stats: "
                            f"mean={self.transformed[col].mean():.4f}, "
                            f"std={self.transformed[col].std():.4f}, "
                            f"na_cnt={self.transformed[col].isna().sum()}"
                        )

                self.logger.info(f"{processor} transformation done.")
            else:
                # if the processor is not a string,
                # it should be a mediator, which transforms the data directly.

                self.logger.debug(
                    f"mediator: {type(processor).__name__} start transforming."
                )
                self.logger.debug(
                    f"before transformation: data shape: {self.transformed.shape}"
                )

                # MediatorScaler for TimeAnchor should use Encoder transformed results sometimes.\
                if isinstance(processor, MediatorScaler):
                    processor.fit(self.transformed)

                self.transformed = processor.transform(self.transformed)
                if isinstance(processor, MediatorEncoder) or isinstance(
                    processor, MediatorScaler
                ):
                    Metadater.adjust_metadata_after_processing(
                        mode="global",
                        data=self.transformed,
                        original_metadata=self._metadata,
                    )
                self._adjust_working_config(processor, self._fitting_sequence)

                self.logger.debug(
                    f"after transformation: data shape: {self.transformed.shape}"
                )
                self.logger.info(f"{type(processor).__name__} transformation done.")

        # Update global row count after preprocessing
        # Note: SchemaMetadata doesn't have mutable global stats like old Metadata
        # This information can be tracked separately if needed
        pass

        transformed: pd.DataFrame = self.transformed.copy()
        delattr(self, "transformed")

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
            raise UnfittedError("The object is not fitted. Use .fit() first.")

        # set NA percentage in Missingist
        index_list: list = list(
            self._rng.choice(
                data.index,
                size=int(data.shape[0] * self._na_percentage_global),
                replace=False,
            ).ravel()
        )

        for col, obj in self._config["missing"].items():
            if obj is None:
                continue
            obj.set_imputation_index(index_list)

            try:
                with warnings.catch_warnings():
                    # ignore the known warning about RuntimeWarning:
                    # invalid value encountered in scalar divide
                    warnings.simplefilter("ignore")
                    # the NA percentage taking global NA percentage
                    # into consideration
                    field_na_percentage = self._get_field_na_percentage(col)
                    adjusted_na_percentage: float = (
                        field_na_percentage / self._na_percentage_global
                    )
                    # Ensure adjusted_na_percentage is within valid range [0.0, 1.0]
                    adjusted_na_percentage = max(0.0, min(1.0, adjusted_na_percentage))
            # if there is no NA in the original data
            except ZeroDivisionError:
                adjusted_na_percentage: float = 0.0

            obj.set_na_percentage(adjusted_na_percentage)

        # there is no method for restoring outliers
        self._inverse_sequence = self._sequence.copy()
        self._inverse_sequence.reverse()
        if "outlier" in self._inverse_sequence:
            self._inverse_sequence.remove("outlier")

        if "encoder" in self._inverse_sequence:
            # if encoder is in the procedure,
            # MediatorEncoder should be in the queue
            # right after the encoder
            self._inverse_sequence.insert(
                self._inverse_sequence.index("encoder"), self._mediator["encoder"]
            )
            self.logger.info("MediatorEncoder is created.")

        if "discretizing" in self._inverse_sequence:
            # if discretizing is in the procedure,
            # remove all of NA values in the data
            # See #440
            data = data.dropna()

        if "scaler" in self._inverse_sequence:
            # if scaler is in the procedure,
            # MediatorScaler should be in the queue
            # right after the scaler
            self._inverse_sequence.insert(
                self._inverse_sequence.index("scaler"), self._mediator["scaler"]
            )
            self.logger.info("MediatorScaler is created.")

        self.logger.debug("Inverse sequence generation completed.")

        transformed: pd.DataFrame = data.copy()

        for processor in self._inverse_sequence:
            if isinstance(processor, str):
                for col, obj in self._config[processor].items():
                    self.logger.debug(
                        f"{processor}: {type(obj).__name__} from {col} start"
                        + " inverse transforming."
                    )

                    if obj is None:
                        continue

                    # Some of Synthesizer will produce float type data
                    #   (e.g. PAC-Synth, DPCTGAN),
                    #   which will cause EncoderLabel in discretizing error.
                    # Here we figure out if we are
                    #    in discretizing inverse transform process,
                    #   and object PROC_TYPE is ('encoder', 'discretizing'),
                    #   then we will force convert the data type to int.
                    # (See #440, also #550 for Encoder sequence error.)
                    if (
                        processor == "discretizing"
                        and obj.PROC_TYPE == ("encoder", "discretizing")
                    ) or (
                        processor == "encoder"
                        and isinstance(obj, EncoderLabel)
                        and str(transformed[col].dtype).startswith("float")
                    ):
                        transformed[col] = transformed[col].round().astype(int)

                    transformed[col] = obj.inverse_transform(transformed[col])

                    # For Datetime after Scaler but not the target of ScalerAnchor (even reference will be affect)
                    if (
                        not is_datetime64_any_dtype(transformed[col])
                        and self._get_field_infer_dtype(col) == "datetime"
                    ):
                        # TODO: here we assume every datetime should output as date...
                        # It should be control on meteadata level
                        transformed[col] = pd.to_datetime(transformed[col]).dt.date

                self.logger.info(
                    f"{type(processor).__name__} inverse transformation done."
                )
            else:
                # if the processor is not a string,
                # it should be a mediator, which transforms the data directly.
                self.logger.debug(
                    f"mediator: {type(processor).__name__} start inverse transforming."
                )
                self.logger.debug(
                    f"before transformation: data shape: {transformed.shape}"
                )
                transformed = processor.inverse_transform(transformed)
                self.logger.debug(
                    f"after transformation: data shape: {transformed.shape}"
                )
                self.logger.info(f"{type(processor).__name__} transformation done.")

        return transformed  # self._align_dtypes(transformed)

    # determine whether the processors are not default settings
    def get_changes(self) -> dict:
        """
        Compare the differences between the current config
            and the default config.

        Return:
            (pd.DataFrame): A dataframe recording the differences
                bewteen the current config and the default config.
        """
        changes_dict: dict = {"processor": [], "col": [], "current": [], "default": []}

        for processor, default_class in DefaultProcessorMap.PROCESSOR_MAP.items():
            for col in self._get_field_names():
                obj = self._config[processor][col]
                infer_dtype = self._get_field_infer_dtype(col)
                default_obj = default_class[infer_dtype]

                if default_obj() is None:
                    default_obj = NoneType

                if not isinstance(obj, default_obj):
                    changes_dict["processor"].append(processor)
                    changes_dict["col"].append(col)
                    changes_dict["current"].append(type(obj).__name__)
                    changes_dict["default"].append(default_obj.__name__)

        return pd.DataFrame(changes_dict)

    def _adjust_working_config(self, mediator: Mediator, sequence: list) -> None:
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
                            self._working_config[processor][col] = deepcopy(
                                self._config[processor][ori_col]
                            )

    def _align_dtypes(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Align the data types between the data and the metadata
            by the rules in util.safe_astypes, see it for more details.

        Args:
            data (pd.DataFrame): The data to be aligned.

        Return:
            (pd.DataFrame): The aligned data.
        """
        for col in self._get_field_names():
            dtype = self._get_field_dtype(col)
            data[col] = Metadater.apply_dtype_conversion(
                data[col], dtype, cast_error="coerce"
            )

        return data
