import re
import warnings

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, \
    RandomForestClassifier, GradientBoostingClassifier
from sklearn.cluster import KMeans
from sklearn.metrics import f1_score, silhouette_score

from PETsARD.error import ConfigError, UnsupportedMethodError
from PETsARD.evaluator.evaluator_base import EvaluatorBase
from PETsARD.util.safe_round import safe_round


class MLUtilityMap():
    """
    map of MLUtility
    """
    REGRESSION:   int = 1
    CLASSIFICATION: int = 2
    CLUSTER: int = 3

    @classmethod
    def map(cls, method: str) -> int:
        """
        Get suffixes mapping int value

        Args:
            method (str): evaluating method

        Return:
            (int): The method code.
        """
        try:
            return cls.__dict__[
                re.sub(r"^mlutility-", "", method).upper()
            ]
        except KeyError:
            raise UnsupportedMethodError


class MLUtility(EvaluatorBase):
    """
    Interface class for MLWorker Models.

    MLWorker is a class that evaluating dataset utility.

    Args:
        config (dict): A dictionary containing the configuration settings.
            - method (str): The method name of how you evaluating data, which
            is downstream task of the data.
            - target (str): The target column of the data. Required for
            regression and classification. Ignored for clustering. Should be
            a numerical column for regression.
            - n_clusters (list, default=[4, 5, 6]): A list of numbers of 
            clusters for clustering. Required for clustering. 
            Ignored for regression and classification.
    """

    def __init__(self, config: dict):
        if 'method' not in config:
            raise ConfigError

        super().__init__(config=config)
        self.data: dict = {}

        self.ml = MLWorker(self.config)

    def create(self, data):
        """
        Create a worker and send the data to the worker.

        Args:
            data (dict): The data to be described. The keys should be 'ori'
            'syn, and 'control', and the value should be a pandas DataFrame.
        """
        self.data = data

        self.ml.create(self.data)

    def eval(self):
        """
        Evaluate the data with the method given in the config.
        """
        self.ml.eval()

        self.result = self.ml.result

    def get_global(self):
        """
        Get the global result of the evaluation.
        """
        return self.ml.get_global()

    def get_columnwise(self):
        """
        Get the column-wise result of the evaluation. Dummy method.
        """
        return self.ml.get_columnwise()

    def get_pairwise(self):
        """
        Get the pair-wise result of the evaluation. Dummy method.
        """
        return self.ml.get_pairwise()


class MLWorker:
    """
    Train and evaluate the models based on the original data and the synthetic
    data. The worker of MLUtility.

    Args:
        config (dict): A dictionary containing the configuration settings.
            - method (str): The method name of how you evaluating data, which
            is downstream task of the data.
            - target (str): The target column of the data. Required for
            regression and classification. Ignored for clustering. Should be
            a numerical column for regression.
            - n_clusters (list, default=[4, 5, 6]): A list of numbers of 
            clusters for clustering. Required for clustering. Ignored for 
            regression and classification.
    """

    def __init__(self, config: dict):
        self.config: dict = config
        self.config['method_code'] = MLUtilityMap.map(config['method'])

        self.result_ori: dict = {}
        self.result_syn: dict = {}

        # store the aggregated result
        self.result: dict = {}

        self.n_clusters = self.config.get('n_clusters', [4, 5, 6])
        if not isinstance(self.n_clusters, list):
            raise ConfigError
        if not all(isinstance(x, int) for x in self.n_clusters):
            raise ConfigError

        self.data_content: pd.DataFrame = None

    def create(self, data):
        """
        Store the data in the instance.

        Args:
            data (pd.DataFrame): The data to be trained on.
        """
        self.data_content = data

    def eval(self):
        """
        Data preprocessing and model fitting and evaluation.

        Data preprocessing process: remove missing values, one-hot encoding for
        categorical variables, and normalisation.
        """

        data_ori = self.data_content['ori']
        data_syn = self.data_content['syn']
        data_test = self.data_content['control']

        # Data preprocessing
        data_ori = data_ori.dropna()
        data_syn = data_syn.dropna()
        data_test = data_test.dropna()

        # Check if there is dataframe is not empty
        if data_ori.shape[0] == 0 or data_syn.shape[0] == 0 or \
                data_test.shape[0] == 0:
            warnings.warn('The data is empty after removing missing values.')
            self.result = {'ori': {'error': np.nan}, 'syn': {'error': np.nan}}
            return

        if self.config['method_code'] == MLUtilityMap.CLUSTER:
            pass
        elif self.config['method_code'] in [
            MLUtilityMap.CLASSIFICATION, MLUtilityMap.REGRESSION
        ]:
            if 'target' not in self.config:
                raise ConfigError
            target = self.config['target']
            target_ori = data_ori[target].values
            data_ori = data_ori.drop(columns=[target])
            target_syn = data_syn[target].values
            data_syn = data_syn.drop(columns=[target])
            target_test = data_test[target].values
            data_test = data_test.drop(columns=[target])
        else:
            raise ConfigError

        # One-hot encoding

        cat_col = (data_ori.dtypes == 'category')\
            .reset_index(name='is_cat').query('is_cat == True')['index'].values

        if len(cat_col) != 0:
            ohe = OneHotEncoder(drop='first', sparse_output=False,
                                handle_unknown='infrequent_if_exist')
            ohe.fit(data_ori[cat_col])
            data_ori_cat = ohe.transform(data_ori[cat_col])
            data_syn_cat = ohe.transform(data_syn[cat_col])
            data_test_cat = ohe.transform(data_test[cat_col])

            data_ori = data_ori.drop(columns=cat_col)
            data_syn = data_syn.drop(columns=cat_col)
            data_test = data_test.drop(columns=cat_col)

            data_ori = np.concatenate([data_ori, data_ori_cat], axis=1)
            data_syn = np.concatenate([data_syn, data_syn_cat], axis=1)
            data_test = np.concatenate([data_test, data_test_cat], axis=1)

        if self.config['method_code'] == MLUtilityMap.REGRESSION:
            self.result_ori = self._regression(data_ori, target_ori,
                                               data_test, target_test)
            self.result_syn = self._regression(data_syn, target_syn,
                                               data_test, target_test)
        elif self.config['method_code'] == MLUtilityMap.CLASSIFICATION:
            self.result_ori = self._classification(data_ori, target_ori,
                                                   data_test, target_test)
            self.result_syn = self._classification(data_syn, target_syn,
                                                   data_test, target_test)
        elif self.config['method_code'] == MLUtilityMap.CLUSTER:
            self.result_ori = self._cluster(data_ori, data_test,
                                            self.n_clusters)
            self.result_syn = self._cluster(data_syn, data_test,
                                            self.n_clusters)

        self.result = {'ori': self.result_ori, 'syn': self.result_syn}

    def _regression(self, X_train, y_train, X_test, y_test):
        """
        Regression model fitting, evaluation, and testing.
        The models used are linear regression, random forest,
        and gradient boosting.

        To prevent the data leakage, the normalisation is done inside the loop.

        The metric used for evaluation is R^2.

        Args:
            X_train (pd.DataFrame): The data to be fitted.
            y_train (pd.DataFrame): The target column of the training data.
            X_test (pd.DataFrame): The data to be tested.
            y_test (pd.DataFrame): The target column of the testing data.

        Returns:
            result (dict): The result of the evaluation.
        """
        result = {}

        ssx = StandardScaler()
        X_train = ssx.fit_transform(X_train)
        X_test = ssx.transform(X_test)

        ssy = StandardScaler()
        y_train = ssy.fit_transform(y_train.reshape(-1, 1)).ravel()
        y_test = ssy.transform(y_test.reshape(-1, 1)).ravel()

        lr = LinearRegression()
        rf = RandomForestRegressor(random_state=42)
        gb = GradientBoostingRegressor(random_state=42)

        lr.fit(X_train, y_train)
        rf.fit(X_train, y_train)
        gb.fit(X_train, y_train)

        result['linear_regression'] = self._lower_bound_check(
            lr.score(X_test, y_test), 'regression'
        )
        result['random_forest'] = self._lower_bound_check(
            rf.score(X_test, y_test), 'regression'
        )
        result['gradient_boosting'] = self._lower_bound_check(
            gb.score(X_test, y_test), 'regression'
        )

        return result

    def _classification(self, X_train, y_train, X_test, y_test):
        """
        Classification model fitting, evaluation, and testing.
        The models used are logistic regression, SVC, random forest,
        and gradient boosting.

        To prevent the data leakage, the normalisation is done inside the loop.

        The metric used for evaluation is f1 score.

        Args:
            X_train (pd.DataFrame): The data to be fitted.
            y_train (pd.DataFrame): The target column of the training data.
            X_test (pd.DataFrame): The data to be tested.
            y_test (pd.DataFrame): The target column of the testing data.

        Returns:
            result (dict): The result of the evaluation.
        """
        result = {}

        # check if the target is constant
        if len(np.unique(y_train)) == 1:
            warnings.warn('The target column is constant, ' +
                          'indicating the performance is not reliable.')
            return {'error': np.nan}

        ss = StandardScaler()
        X_train = ss.fit_transform(X_train)
        X_test = ss.transform(X_test)

        lr = LogisticRegression(random_state=42)
        svc = SVC(random_state=42)
        rf = RandomForestClassifier(random_state=42)
        gb = GradientBoostingClassifier(random_state=42)

        lr.fit(X_train, y_train)
        svc.fit(X_train, y_train)
        rf.fit(X_train, y_train)
        gb.fit(X_train, y_train)

        result['logistic_regression'] = self._lower_bound_check(
            f1_score(y_test, lr.predict(X_test),
                     average='micro'),
            'classification'
        )
        result['svc'] = self._lower_bound_check(
            f1_score(y_test, svc.predict(X_test),
                     average='micro'),
            'classification'
        )
        result['random_forest'] = self._lower_bound_check(
            f1_score(y_test, rf.predict(X_test),
                     average='micro'),
            'classification'
        )
        result['gradient_boosting'] = self._lower_bound_check(
            f1_score(y_test, gb.predict(X_test),
                     average='micro'),
            'classification'
        )

        return result

    def _cluster(self, X_train, X_test, n_clusters):
        """
        Clustering model fitting, evaluation, and testing.
        The models used are KMeans with different number of clusters.

        For the robustness of the results, the model is trained
        and evaluated 5 times, and the average of the results
        is used as the final result.

        To prevent the data leakage, the normalisation is done inside the loop.

        The metric used for evaluation is silhouette score.

        Args:
            X_train (pd.DataFrame): The data to be fitted.
            X_test (pd.DataFrame): The data to be tested.
            n_clusters (list): A list of numbers of clusters for clustering.

        Returns:
            result (dict): The result of the evaluation.
        """
        result = {}

        ss = StandardScaler()
        X_train = ss.fit_transform(X_train)
        X_test = ss.transform(X_test)

        for k in n_clusters:
            k_model = KMeans(random_state=42, n_clusters=k, n_init='auto')

            k_model.fit(X_train)

            try:
                silhouette_score_value: float = \
                    silhouette_score(X_test, k_model.predict(X_test))
            except ValueError as e:
                warnings.warn('There is only one cluster in the prediction, ' +
                              'or the valid data samples are too few, ' +
                              'indicating the performance is arbitrarily poor.' +
                              ' The score is set to the lower bound.' + 
                              ' Error message: ' + str(e))
                silhouette_score_value = -1

            result[f'KMeans_cluster{k}'] = self._lower_bound_check(
                silhouette_score_value,
                'cluster'
            )

        return result

    def _lower_bound_check(self, value: float, type: 'str') -> float:
        """
        Check if the score is beyond the lower bound.
        For regression and classification, the lower bound is 0.
        For clustering, the lower bound is -1.

        If the value is less than the lower bound, return the lower bound and
        raise a warning.
        Otherwise, return the value.

        Args:
            value (float): The value to be checked.
            type (str): The type of the evaluation.

        Returns:
            (float): The value in the range.
        """
        if type == 'cluster':
            lower_bound = -1
        else:
            lower_bound = 0

        if value < lower_bound:
            warnings.warn('The score is less than the lower bound,' +
                          ' indicating the performance is arbitrarily poor.' +
                          ' The score is set to the lower bound.')
            return lower_bound
        else:
            return value

    def get_global(self) -> pd.DataFrame:
        """
        Get the global result of the evaluation.

        Returns:
            (pd.DataFrame): The global result of the evaluation.
        """
        syn_value = list(self.result_syn.values())

        ori_value = list(self.result_ori.values())

        normalise_range = 2 if self.config['method_code'] == \
            MLUtilityMap.CLUSTER else 1

        compare_df = pd.DataFrame({'ori_mean': safe_round(np.mean(ori_value)),
                                   'ori_std': safe_round(np.std(ori_value)),
                                   'syn_mean': safe_round(np.mean(syn_value)),
                                   'syn_std': safe_round(np.std(syn_value))},
                                  index=[0])

        compare_df['diff'] = safe_round(
             compare_df['syn_mean'] - compare_df['ori_mean'])

        return compare_df

    def get_columnwise(self) -> None:
        """
        Dummy method for the column-wise result of the evaluation.

        Returns:
            None: None for ML didn't have columnwise result.
        """
        return None

    def get_pairwise(self) -> None:
        """
        Dummy method for the pair-wise result of the evaluation.

        Returns:
            None: None for ML didn't have pairwise result.
        """
        return None
