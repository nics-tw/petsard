from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor

from PETsARD.Processor.Missingist import MissingistDrop
from PETsARD.Processor.Encoder import EncoderOneHot
from PETsARD.Processor.Outlierist import *


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

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Base method of `transform`.

        Args:
            data (pd.DataFrame): The in-processing data.

        Return:
            (pd.DataFrame): The finished data.
        """
        if not self._is_fitted:
            raise UnfittedError('The object is not fitted. Use .fit() first.')

        if len(self._process_col) == 0:
            return data
        else:
            return self._transform(data)


class MediatorMissingist(Mediator):
    """
    Deal with global behaviours in Missingist.
    """

    def __init__(self, config: dict) -> None:
        """
        Args:
            config (dict): The config related to the processing data 
            to cope with global behaviours.
        """
        super().__init__()
        self._config: dict = config['missingist']

    def _fit(self, data: None) -> None:
        """
        Gather information for the columns needing global transformation.

        Args:
            None, the config is read during initialisation.
            data: Redundant input.
        """
        for col, obj in self._config.items():
            if type(obj) == MissingistDrop:
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

            transformed: pd.DataFrame = data.loc[~process_filter, :].\
                reset_index(drop=True)

            # restore the original data from the boolean data
            transformed.loc[:, col_name] = self._config.get(col_name,
                                                            None).\
                                            data_backup[~process_filter].values

            return transformed
        else:
            process_filter: np.ndarray = data[self._process_col].any(
                axis=1).values

            transformed: pd.DataFrame = data.loc[~process_filter, :].\
                reset_index(drop=True)

            for col in self._process_col:
                # restore the original data from the boolean data
                transformed.loc[:, col] = self._config.get(col,
                                                           None).\
                                            data_backup[~process_filter].values

            return transformed


class MediatorOutlierist(Mediator):
    """
    Deal with global behaviours in Outlierist.
    """

    def __init__(self, config: dict) -> None:
        """
        Args:
            config (dict): The config related to the processing data 
            to cope with global behaviours.
        """
        super().__init__()
        self._config: dict = config['outlierist']
        self.model = None

        # indicator for using global outlier methods, 
        # such as Isolation Forest and Local Outlier Factor
        self._global_model_indicator: bool = False

        # if any column in the config sets outlierist method 
        # as isolation forest or local outlier factor
        # it sets the overall transformation as that one
        for col, obj in self._config.items():
            if type(obj) == OutlieristIsolationForest:
                self.model = IsolationForest()
                self._global_model_indicator = True
                break
            elif type(obj) == OutlieristLOF:
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
                data.columns[data.apply(pd.api.types.is_numeric_dtype, axis=0)])

            if len(self._process_col) < 1:
                raise ValueError(
                    'There should be at least one numerical column \
                        to fit the model.')
        else:
            for col, obj in self._config.items():
                if type(obj) in [OutlieristIQR, OutlieristZScore]:
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
            predict_result: np.ndarray = self.model.fit_predict(
                data[self._process_col])
            self.result: np.ndarray = predict_result
            process_filter: np.ndarray = predict_result == -1.0

            transformed: pd.DataFrame = data.loc[~process_filter, :].\
                reset_index(drop=True)

            return transformed
        elif len(self._process_col) == 1:
            col_name: str = self._process_col[0]
            process_filter: np.ndarray = data[col_name].values

            transformed: pd.DataFrame = data.loc[~process_filter, :].\
                reset_index(drop=True)

            # restore the original data from the boolean data
            transformed.loc[:, col_name] = self._config.get(col_name,
                                                            None).\
                                                data_backup[~process_filter]

            return transformed
        else:
            process_filter: np.ndarray = data[self._process_col].any(
                axis=1).values

            transformed: pd.DataFrame = data.loc[~process_filter, :].\
                reset_index(drop=True)

            for col in self._process_col:
                # restore the original data from the boolean data
                transformed.loc[:, col] = self._config.get(col,
                                                           None).\
                                                data_backup[~process_filter]

            return transformed

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
        self._config: dict = config['encoder']

    def _fit(self, data: None) -> None:
        """
        Gather information for the columns needing global transformation.

        Args:
            None, the config is read during initialisation.
            data: Redundant input.
        """
        for col, obj in self._config.items():
            if type(obj) == EncoderOneHot:
                self._process_col.append(col)

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
            label_list = self._config[col].labels

            # prevent duplicates
            n = 1
            new_labels = [str(col) + '_' + str(l) for l in label_list]

            # check if the new labels and the original columns overlap
            while len(set(new_labels) & set(data.columns)) != 0:
                n = n + 1
                new_labels = [str(col) + '_' * n + str(l) for l in label_list]

            ohe_df = pd.DataFrame(self._config[col]._transform_temp, 
                                  columns=new_labels)
            
            # clear the temp
            self._config[col]._transform_temp = None

            transformed.drop(col, axis=1, inplace=True)
            transformed = pd.concat([transformed, ohe_df], axis=1)
            
        return transformed