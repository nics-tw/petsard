import re
import warnings

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor,
    RandomForestClassifier,
    GradientBoostingClassifier
)
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import f1_score, silhouette_score
from sklearn.model_selection import KFold, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from tqdm import tqdm

from PETsARD.error import ConfigError, UnsupportedMethodError
from PETsARD.evaluator.evaluator_base import EvaluatorBase
from PETsARD.util.safe_round import safe_round


class AutoMLMap():
    """
    map of AutoML
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
                re.sub(r"^automl-", "", method).upper()
            ]
        except KeyError:
            raise UnsupportedMethodError


class AutoML(EvaluatorBase):
    """
    Interface class for AutoML Models.

    AutoML is a class that evaluating dataset utility.

    Args:
        config (dict): A dictionary containing the configuration settings.
            - method (str): The method name of how you evaluating data, which
            is downstream task of the data.
            - target (str): The target column of the data. Required for
            regression and classification. Ignored for clustering. Should be
            a numerical column for regression.
            - n_splits (int, default=5): The parameter for k-fold cross validation. Should
            be greater than 1.
            - n_clusters (list, default=[4, 5, 6]): A list of numbers of
            clusters for clustering. Required for clustering.
            Ignored for regression and classification.
    """

    def __init__(self, config: dict):
        if 'method' not in config:
            raise ConfigError

        super().__init__(config=config)
        self.data: dict = {}

        self.ml = ML(self.config)

    def _create(self, data):
        """
        Create a worker and send the data to the worker.

        Args:
            data (dict): The data to be described. The keys should be 'ori'
            and 'syn, and the value should be a pandas DataFrame.
        """
        if not set(data.keys()) == set(['ori', 'syn']):
            raise ConfigError
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


class ML:
    """
    Train and evaluate the models based on the original data and the synthetic
    data. The worker of AutoML.

    Args:
        config (dict): A dictionary containing the configuration settings.
            - method (str): The method name of how you evaluating data, which
            is downstream task of the data.
            - target (str): The target column of the data. Required for
            regression and classification. Ignored for clustering. Should be
            a numerical column for regression.
            - n_splits (int, default=5): The parameter for k-fold cross
            validation. Should be greater than 1.
            - n_clusters (list, default=[4, 5, 6]): A list of numbers of
            clusters for clustering. Required for clustering. Ignored for
            regression and classification.
    """

    def __init__(self, config: dict):
        self.config: dict = config
        self.config['method_code'] = AutoMLMap.map(config['method'])

        self.result_ori: dict = {}
        self.result_syn: dict = {}

        # store the aggregated result
        self.result: dict = {}

        self.n_splits = self.config.get('n_splits', 5)
        self.n_clusters = self.config.get('n_clusters', [4, 5, 6])

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

        # Data preprocessing
        data_ori = data_ori.dropna()
        data_syn = data_syn.dropna()

        if 'target' in self.config:
            target = self.config['target']
            target_ori = data_ori[target].values
            data_ori = data_ori.drop(columns=[target])
            target_syn = data_syn[target].values
            data_syn = data_syn.drop(columns=[target])
        else:
            if self.config['method_code'] != AutoMLMap.CLUSTER:
                raise ConfigError

        data_ori = pd.get_dummies(data_ori, drop_first=True)
        data_syn = pd.get_dummies(data_syn, drop_first=True)

        if self.config['method_code'] == AutoMLMap.REGRESSION:
            self.result_ori = self._regression(data_ori, target_ori,
                                               self.n_splits)
            self.result_syn = self._regression(data_syn, target_syn,
                                               self.n_splits)
        elif self.config['method_code'] == AutoMLMap.CLASSIFICATION:
            self.result_ori = self._classification(data_ori, target_ori,
                                                   self.n_splits)
            self.result_syn = self._classification(data_syn, target_syn,
                                                   self.n_splits)
        elif self.config['method_code'] == AutoMLMap.CLUSTER:
            self.result_ori = self._cluster(data_ori, self.n_splits,
                                            self.n_clusters)
            self.result_syn = self._cluster(data_syn, self.n_splits,
                                            self.n_clusters)

        self.result = {'ori': self.result_ori, 'syn': self.result_syn}

    def _regression(self, data, target, n_splits):
        """
        Regression model fitting and evaluation.
        The models used are linear regression, random forest,
        and gradient boosting.

        For the robustness of the results, the model is trained
        and evaluated 5 times, and the average of the results
        is used as the final result.

        To prevent the data leakage, the normalisation is done inside the loop.

        The metric used for evaluation is R^2.

        Args:
            data (pd.DataFrame): The data to be fitted.
            target (pd.DataFrame): The target column of the data.
            n_splits (int): The parameter for k-fold cross validation. Should
            be greater than 1.

        Returns:
            result (dict): The result of the evaluation.
        """
        result = {
            'linear_regression': [],
            'random_forest': [],
            'gradient_boosting': []
        }

        kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)

        for train_index, test_index in tqdm(kf.split(data, target),
                                            desc='Regression',
                                            total=n_splits):
            data_train, data_test = data.iloc[train_index, :], \
                data.iloc[test_index, :]
            target_train, target_test = target[train_index], \
                target[test_index]

            ssx = StandardScaler()
            data_train = ssx.fit_transform(data_train)
            data_test = ssx.transform(data_test)

            ssy = StandardScaler()
            target_train = ssy.fit_transform(
                target_train.reshape(-1, 1)).ravel()
            target_test = ssy.transform(target_test.reshape(-1, 1)).ravel()

            lr = LinearRegression()
            rf = RandomForestRegressor(random_state=42)
            gb = GradientBoostingRegressor(random_state=42)

            lr.fit(data_train, target_train)
            rf.fit(data_train, target_train)
            gb.fit(data_train, target_train)

            result['linear_regression'].append(
                self._lower_bound_check(lr.score(data_test, target_test),
                                        'regression'),
            )
            result['random_forest'].append(
                self._lower_bound_check(rf.score(data_test, target_test),
                                        'regression'),
            )
            result['gradient_boosting'].append(
                self._lower_bound_check(gb.score(data_test, target_test),
                                        'regression'),
            )

        return result

    def _classification(self, data, target, n_splits):
        """
        Classification model fitting and evaluation.
        The models used are logistic regression, SVC, random forest,
        and gradient boosting.

        For the robustness of the results, the model is trained
        and evaluated 5 times, and the average of the results
        is used as the final result.

        To prevent the data leakage, the normalisation is done inside the loop.

        The metric used for evaluation is f1 score.

        Args:
            data (pd.DataFrame): The data to be fitted.
            target (pd.DataFrame): The target column of the data.
            n_splits (int): The parameter for k-fold cross validation. Should
            be greater than 1.

        Returns:
            result (dict): The result of the evaluation.
        """
        result = {
            'logistic_regression': [],
            'svc': [],
            'random_forest': [],
            'gradient_boosting': []
        }

        kf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)

        for train_index, test_index in tqdm(kf.split(data, target),
                                            desc='Classification',
                                            total=n_splits):
            data_train, data_test = data.iloc[train_index, :], \
                data.iloc[test_index, :]
            target_train, target_test = target[train_index], \
                target[test_index]

            if len(np.unique(target_train)) == 1:
                # indicates that there is only one class in the target
                # which makes the model training impossible
                result['logistic_regression'].append(np.nan)
                result['svc'].append(np.nan)
                result['random_forest'].append(np.nan)
                result['gradient_boosting'].append(np.nan)

                warnings.warn('Only one class in the target, ' +
                              'the model training is impossible. ' +
                              'The score is set to NaN.')
                continue

            ss = StandardScaler()
            data_train = ss.fit_transform(data_train)
            data_test = ss.transform(data_test)

            lr = LogisticRegression(random_state=42)
            svc = SVC(random_state=42)
            rf = RandomForestClassifier(random_state=42)
            gb = GradientBoostingClassifier(random_state=42)

            lr.fit(data_train, target_train)
            svc.fit(data_train, target_train)
            rf.fit(data_train, target_train)
            gb.fit(data_train, target_train)

            result['logistic_regression'].append(
                self._lower_bound_check(
                    f1_score(target_test, lr.predict(data_test),
                             average='micro'),
                    'classification'
                )
            )
            result['svc'].append(
                self._lower_bound_check(
                    f1_score(target_test, svc.predict(data_test),
                             average='micro'),
                    'classification'
                )
            )
            result['random_forest'].append(
                self._lower_bound_check(
                    f1_score(target_test, rf.predict(data_test),
                             average='micro'),
                    'classification'
                )
            )
            result['gradient_boosting'].append(
                self._lower_bound_check(
                    f1_score(target_test, gb.predict(data_test),
                             average='micro'),
                    'classification'
                )
            )

        return result

    def _cluster(self, data, n_splits, n_clusters):
        """
        Clustering model fitting and evaluation.
        The models used are KMeans with different number of clusters.

        For the robustness of the results, the model is trained
        and evaluated 5 times, and the average of the results
        is used as the final result.

        To prevent the data leakage, the normalisation is done inside the loop.

        The metric used for evaluation is silhouette score.

        Args:
            data (pd.DataFrame): The data to be fitted.
            n_splits (int): The parameter for k-fold cross validation. Should
            be greater than 1.
            n_clusters (list): A list of numbers of clusters for clustering.

        Returns:
            result (dict): The result of the evaluation.
        """
        result = {
            f'KMeans_cluster{k}': [] for k in n_clusters
        }

        kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)

        for train_index, test_index in tqdm(kf.split(data),
                                            desc='Cluster',
                                            total=n_splits):
            data_train, data_test = data.iloc[train_index, :], \
                data.iloc[test_index, :]

            ss = StandardScaler()
            data_train = ss.fit_transform(data_train)
            data_test = ss.transform(data_test)

            for k in n_clusters:
                k_model = KMeans(random_state=42, n_clusters=k, n_init='auto')

                k_model.fit(data_train)

                result[f'KMeans_cluster{k}'].append(
                    self._lower_bound_check(
                        silhouette_score(
                            data_test, k_model.predict(data_test)),
                        'cluster'
                    )
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
        syn_value = []

        for i in self.result_syn.values():
            syn_value += i

        ori_value = []

        for i in self.result_ori.values():
            ori_value += i

        normalise_range = 2 if self.config['method_code'] == \
            AutoMLMap.CLUSTER else 1

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
