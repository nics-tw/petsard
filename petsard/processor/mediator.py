import logging

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor

from petsard.exceptions import UnfittedError
from petsard.processor.encoder import (
    EncoderDateDiff,
    EncoderOneHot,
)
from petsard.processor.missing import MissingDrop
from petsard.processor.outlier import (
    OutlierIQR,
    OutlierIsolationForest,
    OutlierLOF,
    OutlierZScore,
)
from petsard.processor.scaler import ScalerTimeAnchor


class Mediator:
    """
    Deal with the processors with the same type to
    manage (column-wise) global behaviours including dropping the records.
    It is responsible for two actions:
        1. Gather all columns needed to process
        2. Coordinate and perform global behaviours
    """

    def __init__(self) -> None:
        self._process_col: list = []
        self._is_fitted: bool = False

        # for working config adjustment
        self.map: dict = {}

    def fit(self, data: None) -> None:
        """
        Base method of `fit`.

        Args:
            None, the config is read during initialisation.
            data: Redundant input.
        """
        # in most cases, mediator doesn't need data to fit
        # just to keep the interface unified
        self._fit(data)

        self._is_fitted = True

    def _fit():
        """
        _fit method is implemented in subclasses.

        fit method is responsible for general action defined by the base class.
        _fit method is for specific procedure conducted by each subclasses.
        """
        raise NotImplementedError(
            "_fit method should be implemented " + "in subclasses."
        )

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Base method of `transform`.

        Args:
            data (pd.DataFrame): The in-processing data.

        Return:
            (pd.DataFrame): The finished data.
        """
        if not self._is_fitted:
            raise UnfittedError("The object is not fitted. Use .fit() first.")

        if len(self._process_col) == 0:
            return data
        else:
            return self._transform(data)

    def _transform():
        """
        _transform method is implemented in subclasses.

        transform method is responsible for general action
            defined by the base class.
        _transform method is for specific procedure
            conducted by each subclasses.
        """
        raise NotImplementedError(
            "_transform method should be implemented " + "in subclasses."
        )

    def inverse_transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Base method of `inverse_transform`.
        Only for MediatorEncoder currently.

        Args:
            data (pd.DataFrame): The in-processing data.

        Return:
            (pd.DataFrame): The finished data.
        """
        if not self._is_fitted:
            raise UnfittedError("The object is not fitted. Use .fit() first.")

        if len(self._process_col) == 0:
            return data
        else:
            return self._inverse_transform(data)

    def _inverse_transform():
        """
        _inverse_transform method is implemented in subclasses.

        inverse_transform method is responsible for general action
            defined by the base class.
        _inverse_transform method is for specific procedure
            conducted by each subclasses.
        """
        raise NotImplementedError(
            "_inverse_transform method should be implemented " + "in subclasses."
        )


class MediatorMissing(Mediator):
    """
    Deal with global behaviours in MissingHandler.
    """

    def __init__(self, config: dict) -> None:
        """
        Args:
            config (dict): The config related to the processing data
            to cope with global behaviours.
        """
        super().__init__()
        self._config: dict = config["missing"]

    def _fit(self, data: None) -> None:
        """
        Gather information for the columns needing global transformation.

        Args:
            None, the config is read during initialisation.
            data: Redundant input.
        """
        for col, obj in self._config.items():
            if isinstance(obj, MissingDrop):
                self._process_col.append(col)

    def _transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Conduct global transformation.

        Args:
            data (pd.DataFrame): The in-processing data.

        Return:
            transformed (pd.DataFrame): The finished data.
        """
        if len(self._process_col) == 1:
            col_name: str = self._process_col[0]
            process_filter: np.ndarray = data[col_name].values

            transformed: pd.DataFrame = data.loc[~process_filter, :].reset_index(
                drop=True
            )

            # restore the original data from the boolean data
            transformed[col_name] = (
                self._config.get(col_name, None).data_backup[~process_filter].values
            )

            return transformed
        else:
            process_filter: np.ndarray = data[self._process_col].any(axis=1).values

            transformed: pd.DataFrame = data.loc[~process_filter, :].reset_index(
                drop=True
            )

            for col in self._process_col:
                # restore the original data from the boolean data
                transformed[col] = (
                    self._config.get(col, None).data_backup[~process_filter].values
                )

            return transformed

    def _inverse_transform(self, data: pd.DataFrame):
        raise NotImplementedError("_inverse_transform is not supported in this class")


class MediatorOutlier(Mediator):
    """
    Deal with global behaviours in OutlierHandler.
    """

    def __init__(self, config: dict) -> None:
        """
        Args:
            config (dict): The config related to the processing data
            to cope with global behaviours.
        """
        super().__init__()
        self._config: dict = config["outlier"]
        self.model = None

        # indicator for using global outlier methods,
        # such as Isolation Forest and Local Outlier Factor
        self._global_model_indicator: bool = False

        # if any column in the config sets outlier method
        # as isolation forest or local outlier factor
        # it sets the overall transformation as that one
        for col, obj in self._config.items():
            if isinstance(obj, OutlierIsolationForest):
                self.model = IsolationForest()
                self._global_model_indicator = True
                break
            elif isinstance(obj, OutlierLOF):
                self.model = LocalOutlierFactor()
                self._global_model_indicator = True
                break
            else:
                pass

    def _fit(self, data: None) -> None:
        """
        Gather information for the columns needing global transformation.

        Args:
            None, the config is read during initialisation.
            data: Redundant input.
        """
        if self._global_model_indicator:
            # global transformation from sklearn only accepts numeric type data
            self._process_col = list(
                data.columns[data.apply(pd.api.types.is_numeric_dtype, axis=0)]
            )

            if len(self._process_col) < 1:
                raise ValueError(
                    "There should be at least one numerical column \
                        to fit the model."
                )
        else:
            for col, obj in self._config.items():
                if type(obj) in [OutlierIQR, OutlierZScore]:
                    self._process_col.append(col)

    def _transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Conduct global transformation.

        Args:
            data (pd.DataFrame): The in-processing data.

        Return:
            transformed (pd.DataFrame): The finished data.
        """
        if self._global_model_indicator:
            # the model may classify most data as outliers
            # after transformation by other processors
            # so fit_predict will be used in _transform
            predict_result: np.ndarray = self.model.fit_predict(data[self._process_col])
            self.result: np.ndarray = predict_result
            process_filter: np.ndarray = predict_result == -1.0

            transformed: pd.DataFrame = data.loc[~process_filter, :].reset_index(
                drop=True
            )

            return transformed
        elif len(self._process_col) == 1:
            col_name: str = self._process_col[0]
            process_filter: np.ndarray = data[col_name].values

            transformed: pd.DataFrame = data.loc[~process_filter, :].reset_index(
                drop=True
            )

            # restore the original data from the boolean data
            transformed[col_name] = self._config.get(col_name, None).data_backup[
                ~process_filter
            ]

            return transformed
        else:
            process_filter: np.ndarray = data[self._process_col].any(axis=1).values

            transformed: pd.DataFrame = data.loc[~process_filter, :].reset_index(
                drop=True
            )

            for col in self._process_col:
                # restore the original data from the boolean data
                transformed[col] = self._config.get(col, None).data_backup[
                    ~process_filter
                ]

            return transformed

    def _inverse_transform(self, data: pd.DataFrame):
        raise NotImplementedError("_inverse_transform is not supported in this class")


class MediatorEncoder(Mediator):
    """
    Deal with global behaviours in Encoder.
    """

    def __init__(self, config: dict) -> None:
        """
        Args:
            config (dict): The config related to the processing data
            to cope with global behaviours.
        """
        super().__init__()
        self._config: dict = config["encoder"]

        # store the original column order
        self._colname: list = []

    def _fit(self, data: None) -> None:
        """
        Gather information for the columns needing global transformation.

        Args:
            None, the config is read during initialisation.
            data: Redundant input.
        """
        for col, obj in self._config.items():
            if isinstance(obj, (EncoderOneHot, EncoderDateDiff)):
                self._process_col.append(col)

        self._colname = data.columns

    def _transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Conduct global transformation.
        Can be seperated into two steps:
        1. Create propers new column names (to avoid duplicates).
        2. Drop the original columns and insert the new ones to the dataframe.

        Args:
            data (pd.DataFrame): The in-processing data.

        Return:
            transformed (pd.DataFrame): The finished data.
        """
        transformed = data.copy()

        for col in self._process_col:
            label_list = self._config[col].labels[1:]

            # prevent duplicates
            n = 1
            new_labels = [str(col) + "_" + str(label) for label in label_list]

            # check if the new labels and the original columns overlap
            while len(set(new_labels) & set(self._colname)) != 0:
                n = n + 1
                new_labels = [str(col) + "_" * n + str(label) for label in label_list]

            ohe_df = pd.DataFrame(self._config[col]._transform_temp, columns=new_labels)

            self.map[col] = new_labels

            # clear the temp
            self._config[col]._transform_temp = None

            transformed.drop(col, axis=1, inplace=True)
            transformed = pd.concat([transformed, ohe_df], axis=1)

        return transformed

    def _inverse_transform(self, data: pd.DataFrame):
        """
        Conduct global inverse transformation.
        Can be seperated into two steps:
        1. Retrieve new column data and extract values.
        2. Drop the new columns and insert the original ones to the dataframe.

        Args:
            data (pd.DataFrame): The in-processing data.

        Return:
            transformed (pd.DataFrame): The finished data.
        """
        transformed = data.copy()

        for ori_col, new_col in self.map.items():
            transformed.drop(new_col, axis=1, inplace=True)
            transformed[ori_col] = (
                self._config[ori_col].model.inverse_transform(data[new_col]).ravel()
            )

        return transformed.reindex(columns=self._colname)


class MediatorScaler(Mediator):
    """
    Mediator for scaling operations that require global coordination.
    Ensures TimeAnchor transformations are performed before other scaling operations.
    """

    def __init__(self, config: dict) -> None:
        """
        Initialize MediatorScaler.

        Args:
            config (dict): Configuration dictionary containing scaler settings
        """
        super().__init__()
        self.logger = logging.getLogger(f"PETsARD.{self.__class__.__name__}")
        self._config = config["scaler"]

    def _fit(self, data: pd.DataFrame) -> None:
        """
        Find and process TimeAnchor scalers with comprehensive error checking.

        This method validates TimeAnchor scaler configurations by checking:
        - Reference column specification
        - Correct unit setting
        - Reference column existence
        - Reference column datetime type
        """
        self.time_anchor_cols: list[str] = []
        self.reference_cols: dict[str, str] = {}

        for col, processor in self._config.items():
            # Check if it's a TimeAnchor scaler
            if isinstance(processor, ScalerTimeAnchor):
                # Check if reference column is specified
                if not hasattr(processor, "reference"):
                    self.logger.error(
                        f"TimeAnchor scaler {col} has no reference column specified"
                    )
                    raise ValueError(
                        f"TimeAnchor scaler {col} has no reference column specified"
                    )
                ref_col = processor.reference

                # Validate unit, default to 'D'
                unit = processor.unit
                if unit not in ["D", "S"]:
                    self.logger.error(
                        f"TimeAnchor scaler {col} has incorrect unit, must be 'D'(days) or 'S'(seconds)"
                    )
                    raise ValueError(
                        f"TimeAnchor scaler {col} has incorrect unit, must be 'D'(days) or 'S'(seconds)"
                    )

                # Check if reference column exists in dataset
                if ref_col not in data.columns:
                    self.logger.error(
                        f"Reference column {ref_col} does not exist in dataset"
                    )
                    raise ValueError(
                        f"Reference column {ref_col} does not exist in dataset"
                    )

                # Check if reference column is datetime type
                # if not pd.api.types.is_datetime64_any_dtype(data[ref_col]):
                #     self.logger.error(
                #         f"Reference column {ref_col} must be datetime type"
                #     )
                #     raise ValueError(
                #         f"Reference column {ref_col} must be datetime type"
                #     )

                self.time_anchor_cols.append(col)
                self.reference_cols[col] = ref_col

                processor.set_reference_time(data[ref_col])

    def _transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform data, ensuring TimeAnchor operations are done first"""
        # Set reference time series for each TimeAnchor scaler
        for col in self.time_anchor_cols:
            ref_col = self.reference_cols[col]
            self._config[col].set_reference_time(data[ref_col])

        result = data.copy()
        self.original_dtypes = result.dtypes.to_dict()

        # First transform TimeAnchor columns
        for col, processor in self._config.items():
            if isinstance(processor, ScalerTimeAnchor):
                result[col] = processor.transform(data[col])

        # Then transform other columns
        for col, processor in self._config.items():
            if processor is not None and not isinstance(processor, ScalerTimeAnchor):
                result[col] = processor.transform(data[col])

        return result

    def _inverse_transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Inverse transform data in the correct order"""
        result = data.copy()

        # First inverse transform non-TimeAnchor columns
        for col, processor in self._config.items():
            if processor is not None and not isinstance(processor, ScalerTimeAnchor):
                result[col] = processor.inverse_transform(data[col])

        # Then inverse transform TimeAnchor columns
        for col, processor in self._config.items():
            if isinstance(processor, ScalerTimeAnchor):
                result[col] = processor.inverse_transform(data[col])
                if hasattr(self, "original_dtypes"):
                    result[col] = result[col].astype(self.original_dtypes[col])

        return result
