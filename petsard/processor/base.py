import logging
import warnings
from copy import deepcopy
from types import NoneType

import numpy as np
import pandas as pd

from petsard.error import ConfigError, UnfittedError
from petsard.loader.metadata import Metadata
from petsard.processor.discretizing import DiscretizingKBins
from petsard.processor.encoder import EncoderLabel, EncoderOneHot, EncoderUniform
from petsard.processor.mediator import (
    Mediator,
    MediatorEncoder,
    MediatorMissing,
    MediatorOutlier,
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
    ScalerZeroCenter,
)
from petsard.util import (
    optimize_dtype,
    safe_astype,
    safe_dtype,
    safe_infer_dtype,
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
        return cls.PROCESSOR_MAP.get(processor_type, {}).get(data_type)


class ProcessorClassMap:
    """Mapping of processor names to their corresponding classes."""

    CLASS_MAP: dict[str, str] = {
        # encoder
        "encoder_uniform": EncoderUniform,
        "encoder_label": EncoderLabel,
        "encoder_onehot": EncoderOneHot,
        # missing
        "missing_mean": MissingMean,
        "missing_median": MissingMedian,
        "missing_simple": MissingSimple,
        "missing_drop": MissingDrop,
        "missing_mode": MissingMode,
        # outlier
        "outlier_zscore": OutlierZScore,
        "outlier_iqr": OutlierIQR,
        "outlier_isolationforest": OutlierIsolationForest,
        "outlier_lof": OutlierLOF,
        # scaler
        "scaler_standard": ScalerStandard,
        "scaler_zerocenter": ScalerZeroCenter,
        "scaler_minmax": ScalerMinMax,
        "scaler_log": ScalerLog,
        # discretizing
        "discretizing_kbins": DiscretizingKBins,
    }

    VALID_NAMES: frozenset = frozenset(CLASS_MAP.keys())

    @classmethod
    def get_class(cls, processor_name: str):
        return cls.CLASS_MAP.get(processor_name, lambda: None)


class Processor:
    """
    Manage the processors.
    It arrange the execution queue and allocate the tasks
    to the right processors based on the metadata and the parameters.
    """

    MAX_SEQUENCE_LENGTH: int = 4  # Maximum number of procedures allowed in sequence
    DEFAULT_SEQUENCE: list[str] = ["missing", "outlier", "encoder", "scaler"]

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
        self.logger = logging.getLogger(f"PETsARD.{self.__class__.__name__}")
        self.logger.debug("Initializing Processor")
        self.logger.debug(
            f"Loaded metadata contains {len(metadata.metadata['col'])} columns, "
            f"with {metadata.metadata['global']['row_num']} rows"
        )

        self._metadata: Metadata = metadata
        self.logger.debug("Metadata loaded.")

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
        self._na_percentage_global: float = self._metadata.metadata["global"].get(
            "na_percentage", 0.0
        )
        self.rng = np.random.default_rng()

        self._generate_config()

        if config is not None:
            self.update_config(config=config)

        # the temp config records the config from in-process/expanded column
        self._working_config: dict = {}

        self.logger.debug("Config loaded.")

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
        self.logger.debug("Starting config generation")

        self._config: dict = {
            processor: dict.fromkeys(self._metadata.metadata["col"].keys())
            for processor in DefaultProcessorMap.VALID_TYPES
        }

        for col, val in self._metadata.metadata["col"].items():
            self.logger.debug(
                f"Processing column '{col}': inferred type {val['infer_dtype']}"
            )
            for processor, obj in DefaultProcessorMap.PROCESSOR_MAP.items():
                processor_class = obj[val["infer_dtype"]]
                self.logger.debug(
                    f"  > Setting {processor} processor: {processor_class.__name__}"
                )
                self._config[processor][col] = processor_class()

        self.logger.debug("Config generation completed")

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
            processor: {} for processor in DefaultProcessorMap.VALID_TYPES
        }

        if col:
            get_col_list = col
        else:
            get_col_list = list(self._metadata.metadata["col"].keys())

        if print_config:
            for processor in self._config.keys():
                print(processor)
                for colname in get_col_list:
                    print(
                        f"    {colname}:",
                        f" {type(self._config[processor][colname]).__name__}",
                    )
                    result_dict[processor][colname] = self._config[processor][colname]
        else:
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
                # accept string of processor
                obj = (
                    ProcessorClassMap.get_class(processor_spec)()
                    if isinstance(processor_spec, str)
                    else processor_spec
                )

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

        if "missing" in self._sequence:
            # if missing is in the procedure,
            # MediatorMissing should be in the queue
            # right after the missing
            self.mediator_missing = MediatorMissing(self._config)
            self._fitting_sequence.insert(
                self._fitting_sequence.index("missing") + 1, self.mediator_missing
            )
            self.logger.info("MediatorMissing is created.")

        if "outlier" in self._sequence:
            # if outlier is in the procedure,
            # MediatorOutlier should be in the queue
            # right after the outlier
            self.mediator_outlier = MediatorOutlier(self._config)
            self._fitting_sequence.insert(
                self._fitting_sequence.index("outlier") + 1, self.mediator_outlier
            )
            self.logger.info("MediatorOutlier is created.")

        if "encoder" in self._sequence:
            # if encoder is in the procedure,
            # MediatorEncoder should be in the queue
            # right after the encoder
            self.mediator_encoder = MediatorEncoder(self._config)
            self._fitting_sequence.insert(
                self._fitting_sequence.index("encoder") + 1, self.mediator_encoder
            )
            self.logger.info("MediatorEncoder is created.")

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

                self.logger.debug(f"mediator: {type(obj).__name__} start processing.")
                processor.fit(data)
                self.logger.info(f"{type(obj).__name__} fitting done.")

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

        transformed: pd.DataFrame = data.copy()

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
                    if transformed[col].dtype.kind in "biufc":  # numeric columns
                        self.logger.debug(
                            f"  > Pre-transform stats: "
                            f"mean={transformed[col].mean():.4f}, "
                            f"std={transformed[col].std():.4f}, "
                            f"na_cnt={transformed[col].isna().sum()}"
                        )

                    transformed[col] = obj.transform(transformed[col])

                    col_metadata: dict = self._metadata.metadata["col"][col]
                    if col_metadata["infer_dtype"] == "datetime":
                        # it is fine to re-adjust mulitple times
                        #   for get the final dtype,
                        # and it is impossible for re-adjust under current logic
                        if isinstance(
                            obj,
                            (
                                EncoderUniform,
                                EncoderLabel,
                                EncoderOneHot,
                                ScalerStandard,
                                ScalerZeroCenter,
                                ScalerMinMax,
                                ScalerLog,
                            ),
                        ):
                            self._adjust_metadata(
                                mode="columnwise",
                                data=transformed[col],
                                col=col,
                            )

                    # Log post-transformation statistics
                    if transformed[col].dtype.kind in "biufc":
                        self.logger.debug(
                            f"  > Post-transform stats: "
                            f"mean={transformed[col].mean():.4f}, "
                            f"std={transformed[col].std():.4f}, "
                            f"na_cnt={transformed[col].isna().sum()}"
                        )

                self.logger.info(f"{processor} transformation done.")
            else:
                # if the processor is not a string,
                # it should be a mediator, which transforms the data directly.

                self.logger.debug(
                    f"mediator: {type(processor).__name__} start transforming."
                )
                self.logger.debug(
                    f"before transformation: data shape: {transformed.shape}"
                )

                transformed = processor.transform(transformed)
                if isinstance(processor, MediatorEncoder):
                    self._adjust_metadata(
                        mode="global",
                        data=transformed,
                    )
                self._adjust_working_config(processor, self._fitting_sequence)

                self.logger.debug(
                    f"after transformation: data shape: {transformed.shape}"
                )
                self.logger.info(f"{type(processor).__name__} transformation done.")

        self._metadata.metadata["global"]["row_num_after_preproc"] = transformed.shape[
            0
        ]

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
            self.rng.choice(
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
                    adjusted_na_percentage: float = (
                        self._metadata.metadata["col"][col].get("na_percentage", 0.0)
                        / self._na_percentage_global
                    )
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
                self._inverse_sequence.index("encoder"), self.mediator_encoder
            )
            self.logger.info("MediatorEncoder is created.")

        if "discretizing" in self._inverse_sequence:
            # if discretizing is in the procedure,
            # remove all of NA values in the data
            # See #440
            data = data.dropna()

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
                        and safe_dtype(transformed[col].dtype).startswith("float")
                    ):
                        transformed[col] = transformed[col].round().astype(int)
                    transformed[col] = obj.inverse_transform(transformed[col])

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

        return self._align_dtypes(transformed)

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
            for col in self._metadata.metadata["col"].keys():
                obj = self._config[processor][col]
                default_obj = default_class[
                    self._metadata.metadata["col"][col]["infer_dtype"]
                ]

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
        for col, val in self._metadata.metadata["col"].items():
            data[col] = safe_astype(data[col], val["dtype"])

        return data

    def _adjust_metadata(
        self,
        mode: str,
        data: pd.Series | pd.DataFrame,
        col: str = None,
    ) -> None:
        """
        Adjusts the metadata for a given column based on the processed data.

        Args:
            mode (str): The mode of adjustment.
                'columnwise': Adjust the metadata based on the column.
                'global': Adjust the metadata based on the whole data.
            data (pd.Series | pd.DataFrame): The processed data for the column.
            col (str): The name of the column. Default is None.
                No need to specifiy when mode is 'global'.

        Raises:
            ConfigError: If the specified column is not found in the metadata.

        Returns:
            None
        """
        self.logger.debug(f"Starting metadata adjustment, mode: {mode}")

        try:
            if mode == "columnwise":
                if not isinstance(data, pd.Series):
                    self.logger.warning(
                        "Input data must be pd.Series for columnwise mode"
                    )
                    raise ConfigError("data should be pd.Series in columnwise mode.")
                if col is None:
                    self.logger.warning("Column name not specified")
                    raise ConfigError("col is not specified.")
                if col not in self._metadata.metadata["col"]:
                    raise ConfigError(f"{col} is not in the metadata.")

                self.logger.debug(f"Adjusting metadata for column '{col}'")

                dtype_after_preproc: str = optimize_dtype(data)
                infer_dtype_after_preproc: str = safe_infer_dtype(
                    safe_dtype(dtype_after_preproc)
                )
                self._metadata.metadata["col"][col]["dtype_after_preproc"] = (
                    dtype_after_preproc
                )
                self._metadata.metadata["col"][col]["infer_dtype_after_preproc"] = (
                    infer_dtype_after_preproc
                )

                if "col_after_preproc" in self._metadata.metadata:
                    self._metadata.metadata["col_after_preproc"][col][
                        "dtype_after_preproc"
                    ] = dtype_after_preproc
                    self._metadata.metadata["col_after_preproc"][col][
                        "infer_dtype_after_preproc"
                    ] = infer_dtype_after_preproc
            elif mode == "global":
                if not isinstance(data, pd.DataFrame):
                    raise ConfigError("data should be pd.DataFrame in global mode.")

                self.logger.debug("Performing global metadata adjustment")

                new_metadata = Metadata()
                new_metadata.build_metadata(data=data)
                self._metadata.metadata["col_after_preproc"] = deepcopy(
                    new_metadata.metadata["col"]
                )
            else:
                raise ConfigError("Invalid mode.")

        except Exception as e:
            self.logger.error(f"Metadata adjustment failed: {str(e)}")
            raise
