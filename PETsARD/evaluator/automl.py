import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor,\
        RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import KFold, StratifiedKFold
from sklearn.cluster import KMeans
from sklearn.metrics import f1_score, silhouette_score

from PETsARD.error import ConfigError


class AutoML:
    """
    Interface class for AutoML Models.

    AutoML is a class that evaluating dataset utility.

    Args:
        config (dict): A dictionary containing the configuration settings.
            - method (str): The method name of how you evaluating data.
            - task (str): The downstream task of the data.
            - target (str): The target column of the data.
    """

    def __init__(self, config: dict):
        if 'task' not in config:
            raise ConfigError

        self.config: dict = config
        self.data: dict = {}

        self.ml = None

    def create(self, data):
        """
        Create a worker and send the data to the worker.

        Args:
            data (dict): The data to be described. The keys should be 'ori' 
            and 'syn, and the value should be a pandas DataFrame.
        """
        self.data = data
        self.ml = ML(self.config)
        self.ml.create(self.data)

    def eval(self):
        """
        Evaluate the data with the method given in the config.
        """
        self.ml.eval()

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


class ML(AutoML):
    """
    Train and evaluate the models based on the original data and the synthetic 
    data. The worker of AutoML.

    Args:
        config (dict): A dictionary containing the configuration settings.
            - method (str): The method name of how you evaluating data.
            - task (str): The downstream task of the data.
            - target (str): The target column of the data.
    """

    def __init__(self, config: dict):
        super().__init__(config=config)

        self.result_ori: dict = {}
        self.result_syn: dict = {}

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

        data_ori = pd.get_dummies(data_ori, drop_first=True)
        data_syn = pd.get_dummies(data_syn, drop_first=True)

        if self.config['task'] == 'regression':
            self.result_ori, self.result_syn = self._regression(
                data_ori, target_ori, data_syn, target_syn
            )
        elif self.config['task'] == 'classification':
            self.result_ori, self.result_syn = self._classification(
                data_ori, target_ori, data_syn, target_syn
            )
        elif self.config['task'] == 'cluster':
            self.result_ori, self.result_syn = self._cluster(             
                data_ori, data_syn
            )
 

    def _regression(self, data_ori, target_ori, data_syn, target_syn):
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
            target (str): The target column of the data.

        Returns:
            result (dict): The result of the evaluation.
        """ 
        result_ori = {
            'linear_regression': [], 
            'random_forest': [], 
            'gradient_boosting': []
        }

        result_syn = {
            'linear_regression': [], 
            'random_forest': [], 
            'gradient_boosting': []
        }
        
        kf = KFold(n_splits=5, shuffle=True, random_state=42)
        
        for train_index, test_index in kf.split(data_ori, target_ori):
            data_ori_train, data_ori_test = data_ori.iloc[train_index, :], \
                data_ori.iloc[test_index, :]
            target_ori_train, target_ori_test = target_ori[train_index], \
                target_ori[test_index]
            data_syn_train, data_syn_test = data_syn.iloc[train_index, :], \
                data_syn.iloc[test_index, :]
            target_syn_train, target_syn_test = target_syn[train_index], \
                target_syn[test_index]

            ssx_ori = StandardScaler()
            data_ori_train = ssx_ori.fit_transform(data_ori_train)
            data_ori_test = ssx_ori.transform(data_ori_test)

            ssy_ori = StandardScaler()
            target_ori_train = ssy_ori.fit_transform(
                target_ori_train.reshape(-1, 1)
            ).ravel()
            target_ori_test = ssy_ori.transform(
                target_ori_test.reshape(-1, 1)
            ).ravel()

            ssx_syn = StandardScaler()
            data_syn_train = ssx_syn.fit_transform(data_syn_train)
            data_syn_test = ssx_syn.transform(data_syn_test)

            ssy_syn = StandardScaler()
            target_syn_train = ssy_syn.fit_transform(
                target_syn_train.reshape(-1, 1)
            ).ravel()
            target_syn_test = ssy_syn.transform(
                target_syn_test.reshape(-1, 1)
            ).ravel()

            lr_ori = LinearRegression()
            rf_ori = RandomForestRegressor(random_state=42)
            gb_ori = GradientBoostingRegressor(random_state=42)

            lr_syn = LinearRegression()
            rf_syn = RandomForestRegressor(random_state=42)
            gb_syn = GradientBoostingRegressor(random_state=42)

            lr_ori.fit(data_ori_train, target_ori_train)
            rf_ori.fit(data_ori_train, target_ori_train)
            gb_ori.fit(data_ori_train, target_ori_train)

            lr_syn.fit(data_syn_train, target_syn_train)
            rf_syn.fit(data_syn_train, target_syn_train)
            gb_syn.fit(data_syn_train, target_syn_train)

            result_ori['linear_regression'].append(
                lr_ori.score(data_ori_test, target_ori_test)
            )
            result_ori['random_forest'].append(
                rf_ori.score(data_ori_test, target_ori_test)
            )
            result_ori['gradient_boosting'].append(
                gb_ori.score(data_ori_test, target_ori_test)
            )

            result_syn['linear_regression'].append(
                lr_syn.score(data_syn_test, target_syn_test)
            )
            result_syn['random_forest'].append(
                rf_syn.score(data_syn_test, target_syn_test)
            )
            result_syn['gradient_boosting'].append(
                gb_syn.score(data_syn_test, target_syn_test)
            )

        return result_ori, result_syn

    def _classification(self, data_ori, target_ori, data_syn, target_syn):
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
            target (str): The target column of the data.

        Returns:
            result (dict): The result of the evaluation.
        """ 
        result_ori = {
            'logistic_regression': [], 
            'svc': [],
            'random_forest': [], 
            'gradient_boosting': []
        }

        result_syn = {
            'logistic_regression': [], 
            'svc': [],
            'random_forest': [], 
            'gradient_boosting': []
        }
        
        kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        
        for train_index, test_index in kf.split(data_ori, target_ori):
            data_ori_train, data_ori_test = data_ori.iloc[train_index, :], \
                data_ori.iloc[test_index, :]
            target_ori_train, target_ori_test = target_ori[train_index], \
                target_ori[test_index]
            data_syn_train, data_syn_test = data_syn.iloc[train_index, :], \
                data_syn.iloc[test_index, :]
            target_syn_train, target_syn_test = target_syn[train_index], \
                target_syn[test_index]

            ssx_ori = StandardScaler()
            data_ori_train = ssx_ori.fit_transform(data_ori_train)
            data_ori_test = ssx_ori.transform(data_ori_test)

            ssx_syn = StandardScaler()
            data_syn_train = ssx_syn.fit_transform(data_syn_train)
            data_syn_test = ssx_syn.transform(data_syn_test)

            lr_ori = LogisticRegression(random_state=42)
            svc_ori = SVC(random_state=42)
            rf_ori = RandomForestClassifier(random_state=42)
            gb_ori = GradientBoostingClassifier(random_state=42)

            lr_syn = LogisticRegression(random_state=42)
            svc_syn = SVC(random_state=42)
            rf_syn = RandomForestClassifier(random_state=42)
            gb_syn = GradientBoostingClassifier(random_state=42)

            lr_ori.fit(data_ori_train, target_ori_train)
            svc_ori.fit(data_ori_train, target_ori_train)
            rf_ori.fit(data_ori_train, target_ori_train)
            gb_ori.fit(data_ori_train, target_ori_train)

            lr_syn.fit(data_syn_train, target_syn_train)
            svc_syn.fit(data_syn_train, target_syn_train)
            rf_syn.fit(data_syn_train, target_syn_train)
            gb_syn.fit(data_syn_train, target_syn_train)

            result_ori['logistic_regression'].append(
                f1_score(target_ori_test, lr_ori.predict(data_ori_test),
                         average='micro')
            )
            result_ori['svc'].append(
                f1_score(target_ori_test, svc_ori.predict(data_ori_test),
                         average='micro')
            )
            result_ori['random_forest'].append(
                f1_score(target_ori_test, rf_ori.predict(data_ori_test),
                         average='micro')
            )
            result_ori['gradient_boosting'].append(
                f1_score(target_ori_test, gb_ori.predict(data_ori_test),
                         average='micro')
            )

            result_syn['logistic_regression'].append(
                f1_score(target_syn_test, lr_syn.predict(data_syn_test),
                         average='micro')
            )
            result_syn['svc'].append(
                f1_score(target_syn_test, svc_syn.predict(data_syn_test),
                         average='micro')
            )
            result_syn['random_forest'].append(
                f1_score(target_syn_test, rf_syn.predict(data_syn_test),
                         average='micro')
            )
            result_syn['gradient_boosting'].append(
                f1_score(target_syn_test, gb_syn.predict(data_syn_test),
                         average='micro')
            )
            
        return result_ori, result_syn
            
    def _cluster(self, data_ori, data_syn):
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

        Returns:
            result (dict): The result of the evaluation.
        """ 
        result_ori = {
            'KMeans_cluster4': [],
            'KMeans_cluster5': [],
            'KMeans_cluster6': []
        }

        result_syn = {
            'KMeans_cluster4': [],
            'KMeans_cluster5': [],
            'KMeans_cluster6': []
        }
        
        kf = KFold(n_splits=5, shuffle=True, random_state=42)
        
        for train_index, test_index in kf.split(data_ori):
            data_ori_train, data_ori_test = data_ori.iloc[train_index, :], \
                data_ori.iloc[test_index, :]
            data_syn_train, data_syn_test = data_syn.iloc[train_index, :], \
                data_syn.iloc[test_index, :]

            ss_ori = StandardScaler()
            data_ori_train = ss_ori.fit_transform(data_ori_train)
            data_ori_test = ss_ori.transform(data_ori_test)

            ss_syn = StandardScaler()
            data_syn_train = ss_syn.fit_transform(data_syn_train)
            data_syn_test = ss_syn.transform(data_syn_test)

            k4_ori = KMeans(random_state=42, n_clusters=4)
            k5_ori = KMeans(random_state=42, n_clusters=5)
            k6_ori = KMeans(random_state=42, n_clusters=6)

            k4_syn = KMeans(random_state=42, n_clusters=4)
            k5_syn = KMeans(random_state=42, n_clusters=5)
            k6_syn = KMeans(random_state=42, n_clusters=6)

            k4_ori.fit(data_ori_train)
            k5_ori.fit(data_ori_train)
            k6_ori.fit(data_ori_train)

            k4_syn.fit(data_syn_train)
            k5_syn.fit(data_syn_train)
            k6_syn.fit(data_syn_train)

            result_ori['KMeans_cluster4'].append(
                silhouette_score(data_ori_test, k4_ori.predict(data_ori_test))
            )
            result_ori['KMeans_cluster5'].append(
                silhouette_score(data_ori_test, k5_ori.predict(data_ori_test))
            )
            result_ori['KMeans_cluster6'].append(
                silhouette_score(data_ori_test, k6_ori.predict(data_ori_test))
            )

            result_syn['KMeans_cluster4'].append(
                silhouette_score(data_syn_test, k4_syn.predict(data_syn_test))
            )
            result_syn['KMeans_cluster5'].append(
                silhouette_score(data_syn_test, k5_syn.predict(data_syn_test))
            )
            result_syn['KMeans_cluster6'].append(
                silhouette_score(data_syn_test, k6_syn.predict(data_syn_test))
            )

        return result_ori, result_syn

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

        normalise_range = 2 if self.config['task'] == 'cluster' else 1

        compare_df = pd.DataFrame({'Ori_mean': np.mean(ori_value),
                                   'Ori_std': np.std(ori_value), 
                                   'Syn_mean': np.mean(syn_value), 
                                   'Syn_std': np.std(syn_value)}, index=[0])
        
        compare_df['pct_change'] = ((compare_df['Syn_mean'] - 
                                    compare_df['Ori_mean']) / 
                                    normalise_range) * 100
        
        return compare_df

    def get_columnwise(self) -> None:
        """
        Dummy method for the column-wise result of the evaluation.
        """
        raise NotImplementedError

    def get_pairwise(self) -> None:
        """
        Dummy method for the pair-wise result of the evaluation.
        """
        raise NotImplementedError
