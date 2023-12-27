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

from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor

class Mediator:
    """
    Deal with the processors with the same type to manage (column-wise) global behaviours including dropping the records.
    It is responsible for three actions:
        1. Gather all columns needed to process
        2. Coordinate and perform global behaviours
    """
    def __init__(self):
        self._process_col = []

    def fit(self, data=None):
        # in most cases, mediator doesn't need data to fit
        # just to keep the interface unified
        self._fit(data)

    def transform(self, data):
        if len(self._process_col) == 0:
            return data
        else:
            return self._transform(data)


class Mediator_Missingist(Mediator):
    def __init__(self, config):
        super().__init__()
        self._config = config['missingist']

    def _fit(self, data):
        """
        Gather information for the columns needing global transformation.

        Input:
            None, the config is read during initialisation.

        Output:
            None
        """
        for col, obj in self._config.items():
            if type(obj) == Missingist_Drop:
                self._process_col.append(col)

    def _transform(self, data):
        """
        Conduct global transformation.

        Input:
            data (pd.DataFrame): The in-processing data.

        Output:
            (pd.DataFrame): The finished data.
        """
        if len(self._process_col) == 1:
            col_name = self._process_col[0]
            process_filter = data[col_name].values

            transformed = data.loc[process_filter, :].reset_index(drop=True)

            # restore the original data from the boolean data
            transformed.loc[:, col_name] = self._config.get(col_name, None).data_backup[process_filter]

            return transformed
        else:
            process_filter = data[self._process_col].any(axis=1).values

            transformed = data.loc[process_filter, :].reset_index(drop=True)

            for col in self._process_col:
                # restore the original data from the boolean data
                transformed.loc[:, col] = self._config.get(col, None).data_backup[process_filter]

            return transformed

class Mediator_Outlierist(Mediator):
    def __init__(self, config):
        super().__init__()
        self._config = config['outlierist']
        self.model = None

        # indicator for using global outlier methods, such as Isolation Forest and Local Outlier Factor
        self._global_model_indicator = False

        # if any column in the config sets outlierist method as isolation forest or local outlier factor
        # it sets the overall transformation as that one
        for col, obj in self._config.items():
            if type(obj) == Outlierist_IsolationForest:
                self.model = IsolationForest()
                self._global_model_indicator = True
                self._process_col.append(col)
                break
            elif type(obj) == Outlierist_LOF:
                self.model = LocalOutlierFactor()
                self._global_model_indicator = True
                self._process_col.append(col)
                break
            else:
                pass


    def _fit(self, data):
        """
        Gather information for the columns needing global transformation.

        Input:
            None, the config is read during initialisation.

        Output:
            None
        """
        if self._global_model_indicator:
            self.model.fit(data)
        else:
            for col, obj in self._config.items():
                if type(obj) in [Outlierist_IQR, Outlierist_Zscore]:
                    self._process_col.append(col)

    def _transform(self, data):
        """
        Conduct global transformation.

        Input:
            data (pd.DataFrame): The in-processing data.

        Output:
            (pd.DataFrame): The finished data.
        """
        if self._global_model_indicator:
            predict_result = self.model.predict(data)
            process_filter = predict_result == -1.0

            transformed = data.loc[process_filter, :].reset_index(drop=True)

            return transformed
        elif len(self._process_col) == 1:
            col_name = self._process_col[0]
            process_filter = data[col_name].values

            transformed = data.loc[process_filter, :].reset_index(drop=True)

            # restore the original data from the boolean data
            transformed.loc[:, col_name] = self._config.get(col_name, None).data_backup[process_filter]

            return transformed
        else:
            process_filter = data[self._process_col].any(axis=1).values

            transformed = data.loc[process_filter, :].reset_index(drop=True)

            for col in self._process_col:
                # restore the original data from the boolean data
                transformed.loc[:, col] = self._config.get(col, None).data_backup[process_filter]

            return transformed