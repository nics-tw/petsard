---
title: "Evaluator"
draft: false
weight: 21
toc: true
math: true
---

The `Evalutor` module is responsible for evaluting the quality of synthetic data. You can specify evaluation method in `Evaluator` class and use it to examine the synthetic data.

```Python
from PETsARD import Evaluator


eval = Evaluator(
    method='anonymeter-singlingout',
    n_attacks=2000
)
eval.create(
    data={
        'ori': split.data[1]['train'],
        'syn': inverse_transformed_data,
        'control': split.data[1]['validation']
    }
)
eval.eval()
print(eval.get_global())
```

## `Evaluator`

To initialise an `Evaluator`, you need to specify the evaluation method to assess the data. It is important to note that for each evaluation method, a separate `Evaluator` needs to be created. In other words, if you need to evaluate a dataset with five different methods, there will be five corresponding `Evaluator` instances.

```Python
eval = Evaluator(
    method,
    **kwargs
)
```

**Parameters**

`method` (`str`): The evaluation method. Case insensitive. The format should be: `{library name}-{function name}`. For example, `'anonymeter-singlingout'`

- `method = 'default'` will use `PETsARD` default evaluation: SDMetrics - QualityReport (`'sdmetrics-single_table-qualityreport'`).
- `method = 'custom_method'` support users in evaluating with custom Python functions.
  - For custom Python functions, we recommend directly inheriting from the `EvaluatorBase` class and implementing its methods to meet the requirements. You can import from here:

```Python
from PETsARD.evaluator.evaluator_base import EvaluatorBase
```

`custom_method` (`dict`, default=`None`, optional): The dictionary contains the custom method information. It should include: - `filepath` (`str`): The path to the custom method file. - `method` (`str`): The method name in the custom method file.

`**kwargs` (`dict`, optional): The parameters defined by each evaluation methods. See the following sections.

### `create()`

Create an `Evaluator` object with the given data. There are three types of data that may be required: the original data utilised for synthesis (referred to as "ori"), the synthetic data generated from "ori" (referred to as "syn"), and the original data that was not employed for synthesis (referred to as "control"). Different evaluation methods have different requirements, see the following section for details. Fortunately, if you are utilizing our pipeline, there is no need to concern yourself with this requirement; you are ready to proceed without any additional steps.

Create an `Evaluator` object with the given data.

- `Anonymeter` and `MLUtility` required three types of data:
  - The original data utilised for synthesis (referred to as `'ori'`)
  - The synthetic data generated from `'ori'` (referred to as `'syn'`)
  - The original data that was not employed for synthesis (referred to as `'control'`).
- `SDMetrics` required two types of data:
  - The original data utilised for synthesis (referred to as `'ori'`)
  - The synthetic data generated from `'ori'` (referred to as `'syn'`)
- Fortunately, if you are utilizing our `Executor` (see [Executor page](PETsARD/docs/usage/01_executor/)), there is no need to concern yourself with this requirement; you are ready to proceed without any additional steps.

```Python
eval.create(
    data = {
      'ori': df_ori,
      'syn': df_syn,
      'control': df_control
    }
)
```

**Parameters**

`data` (`dict`): The dictionary contains 3 types of data, in the forms of `pd.DataFrame`s. The `keys` of `data` are specified above.

### `eval()`

Evaluate the synthetic dataset.

### `get_global()`

Returns the global evaluation result.

**Output**

(`pandas.DataFrame`): A dataFrame with the global evaluation result. One row only for representing the whole data result.

### `get_columnwise()`

Returns the column-wise evaluation result.

**Output**

(`pandas.DataFrame`): A dataFrame with the column-wise evaluation result. Each row contains one column in original data.

### `get_pairwise()`

Retrieves the pairwise evaluation result.

**Output**

(`pandas.DataFrame`): A dataFrame with the pairwise evaluation result. Each row contains the pairwise relationship between two columns (column x column) in original data.

### `self.config`

The configuration of `Evaluator` module:

- In standard usage, it includes the `method`, `method_code` from the input parameters, along with other parameters (`kwargs`).
- When `method` is set to `'default'`, the `method` will be replaced by the default evaluation method of `PETsARD`: SDMetrics - QualityReport (`'sdmetrics-single_table-qualityreport'`).
- When `method` is set to `'custom_method'`, it encompasses `method`, `custom_method`.
  - The `custom_method` dictionary further contains `filepath` and `method` as parameters.

### `self.evaluator`

The instantiated evaluator itself.

### `self.data`

Stored the `data` input from `.create()` function. See the [`create()`](PETsARD/docs/usage/10_evaluator/#create) documentation for more information.

### `self.result`

A dictionary storing evaluator results. The format varies with different modules.

## Available Evaluator Types

In this section, we provide a comprehensive list of supported evaluator types, their `method` name, and their data requirements.

<div class="table-wrapper" markdown="block">

|  Submodule   |    Class     |    Alias (`method` name)     | `'ori'` needed | `'syn'` needed | `'control'` needed |
| :----------: | :----------: | :--------------------------: | :------------: | :------------: | :----------------: |
| `anonymeter` | `Anonymeter` |   'anonymeter-singlingout'   |       ✅       |       ✅       |         ✅         |
| `anonymeter` | `Anonymeter` |   'anonymeter-linkability'   |       ✅       |       ✅       |         ✅         |
| `anonymeter` | `Anonymeter` |    'anonymeter-inference'    |       ✅       |       ✅       |         ✅         |
| `sdmetrics`  | `SDMetrics`  | 'sdmetrics-diagnosticreport' |       ✅       |       ✅       |                    |
| `sdmetrics`  | `SDMetrics`  |  'sdmetrics-qualityreport'   |       ✅       |       ✅       |                    |
| `mlutility`  |  `MLWorker`  |    'mlutility-regression'    |       ✅       |       ✅       |         ✅         |
| `mlutility`  |  `MLWorker`  |  'mlutility-classification'  |       ✅       |       ✅       |         ✅         |
| `mlutility`  |  `MLWorker`  |     'mlutility-cluster'      |       ✅       |       ✅       |         ✅         |

</div>

### Anonymeter

`anonymeter` is a comprehensive Python library that evaluates various aspects of privacy risks in synthetic tabular data, including Singling Out, Linkability, and Inference risks.

These three points are based on the criteria established by [Article 29 Data Protection Working Party (WP29)](https://ec.europa.eu/justice/article-29/documentation/opinion-recommendation/files/2014/wp216_en.pdf) under the Data Protection Directive (Directive 95/46), as outlined in their written guidance published in 2014, for evaluating the effectiveness standards of anonymization techniques. `anonymeter` received positively reviewed from the [Commission Nationale de l’Informatique et des Libertés (CNIL)](https://www.cnil.fr/en/home) on February 13, 2023, acknowledging its ability to effectively evaluate the three standards of anonymization effectiveness in synthetic data. CNIL recommends using this library to evaluate the risk of re-identification.

Therefore, `PETsARD` includes built-in calls to `anonymeter`. For more details, please refer to its official GitHub: [statice/anonymeter](https://github.com/statice/anonymeter)

#### `'anonymeter-singlingout'`

Singling Out risk represents the possibility of still being able to identify a particular individual, their part, or complete records, even after any Privacy-Enhancing Techniques have been applied. In the example from the `anonymeter`, it refers to the scenario where "there is only one person with attributes X, Y, and Z". In other words, attackers may attempt to identify specific individuals.

The paper on `anonymeter` specifically mentions: "It's important to note that singling out does not imply re-identification. Yet the ability to isolate an individual is often enough to exert control on that individual, or to mount other privacy attacks."

**Parameters**

`n_attacks` (`int`, default=`2000`): Number of times this particular attack will be executed. In this case, it is the number of distinct `queries`. A `query` is a specific condition-based searching command matching only one record in a certain field, achieving Singling Out. A higher number will reduce the statistical uncertainties on the results, at the expense of a longer computation time.

`n_cols` (`int`, default=`3`): The number of columns used for generating Singling Out `queries`.

`max_attempts` (`int`, default=`500000`): The maximum number of attempts to find a successful attack.

#### `'anonymeter-linkability'`

Linkability risk represents the possibility that, even after Privacy-Enhancing Techniques have been applied, or when records exist in different databases, at least two records about the same individual or group of individuals can still be linked together. In the example from the `anonymeter`, it refers to the scenario where "records A and B belong to the same person". In particular, even if attackers cannot single out the specific individual's identity, they may still attempt to establish links between records through shared features or information.

**Parameters**

`n_attacks` (`int`, default=`2000`): Number of times this particular attack will be executed. In this case, it is the number of rows in the training dataset. A higher number will reduce the statistical uncertainties on the results, at the expense of a longer computation time.

`max_n_attacks` (`bool`, default=`False`): Determines whether to enforce the maximum number of attacks. Support only for Linkability and Inference. If True, the input for `n_attacks` is forcibly set to the theoretical maximum number of attacks.

`aux_cols` (`Tuple[List[str], List[str]]`): Columns of the auxiliary information.

> The pattern of Linkability attacks assumes that attackers, whether malicious or honest-but-curious users, possesses two sets of non-overlapping original train data columns. When composite synthesized data involving these two sets of data columns is released, the attacker can use the synthetic data to link to their own original data, to determine whether the data from one dataset belongs to certain records in another dataset. In this context, the auxiliary data columns `aux_cols` are the two pieces of information the attackers own.
> For example, a medical center intends to release synthesized data from their heart disease research, which includes age, gender, postal code, and the number of heart attacks. Meanwhile, the attacker may have obtained real population data, such as gender and postal codes, from public sources or data leaks, along with real epidemiological data, such as age and the frequency of heart attacks, in their original form or in proportion. In this case, `aux_cols` is shown below.
> The potential linkage attack method in this case may be that "due to the close similarity between the real population data and real epidemiological data with the values in this synthesized data, it is possible to link the age and the frequency of heart attacks of a certain group of people from the population data, or link the gender and place of residence of a certain group of people from the epidemiological data."
> `aux_cols` involves domain-specific knowledge about the dataset, so neither `PETsARD` nor `anonymeter` provide default values for it. Users need to configure it themselves based on their understanding of the dataset. In future updates, following the experimental approach outlined in the `anonymeter` paper, different amounts of auxiliary information will be considered. The attacker's auxiliary information will be sampled from "only two columns" to "the maximum number of columns in the dataset," and these options will be provided as default values.

```Python
aux_cols = [
    ['sex', 'zip_code'], # public
    ['age', 'heart_attack_times'] # private
]
```

`n_neighbors` (`int`, default=`10`): The N closest neighbors considered for the link search.

> To handle mixed data types, `anonymeter` uses Gower's Distance/Similarity:
>
> - Numeric variables: Gower's Distance is the absolute difference between the normalized values.
> - Categorical variables: Gower's Distance is 1 if the values are not equal.
>   After combining all attributes, the Manhattan Distance is calculated, and return the nearest N neighbors. So, in the context of Linkability risk, `n_neighbors` represents how close the two sets of data from the same person need to be linked to be considered a successful linkability attack.

#### `'anonymeter-inference'`

Inference risk represents the possibility that, even after Privacy-Enhancing Techniques have been applied, there is still a significant chance of deducing the value of an attribute from the values of a set of other attributes. In the example from the `anonymeter`, it refers to the scenario where "a person with attributes X and Y also have Z". To phrase it differently, even if attackers cannot single out individual identities or cannot link different records, they may still be able to deduce specific information via statistical analysis or other methods.

**Parameters**

`n_attacks` (`int`, default=`2000`): Number of times this particular attack will be executed. In this case, it is the number of rows in the training dataset. A higher number will reduce the statistical uncertainties on the results, at the expense of a longer computation time.

`max_n_attacks` (`bool`, default=`False`): Determines whether to enforce the maximum number of attacks. Support only for Linkability and Inference. If True, the input for `n_attacks` is forcibly set to the theoretical maximum number of attacks.

`secret` (`str`): Column(s) of secret information.

`aux_cols` (`List[str]`, default=None): Columns of auxiliary information. The default value consists of a list of columns excluding those that contain the keyword `secret`. In other words, if `aux_cols` is not specifically designated, this parameter will include all columns except those with `secret`.

> In the context of Inference risk, the parameters `secret` and `aux_cols` go hand in hand. `secret` represents the attribute that is kept confidential, and in this scenario, `aux_cols` are the attributes other than secret that are considered to provide auxiliary information to the attacker.
> The example provided by `anonymeter` suggests the following configuration:

```Python
columns = ori_data.columns

for secret in columns:
    aux_cols = [col for col in columns if col != secret]
    evaluator = InferenceEvaluator(
        aux_cols=aux_cols,
        secret=secret,
        ...
    )
```

> This approach allows us to iterate through each column considered as a `secret`. And following the method outlined in the `anonymeter` paper, averaging all the risk results for the `secret` attributes results in the dataset's overall inference risk.

#### `get_global()`

Retrieve the evaluation results from `anonymeter` methods.

**Outputs**

(`pd.DataFrame`): The evaluation results. Below is an example:

<div class="table-wrapper" markdown="block">

|        |   risk   | risk_CI_btm | risk_CI_top | attack_rate | attack_rate_err | baseline_rate | baseline_rate_err | control_rate | control_rate_err |
| :----: | :------: | :---------: | :---------: | :---------: | :-------------: | :-----------: | :---------------: | :----------: | :--------------: |
| result | 0.998962 |  0.997923   |     1.0     |  0.999041   |    0.000959     |   0.024413    |     0.006695      |   0.076813   |     0.011631     |

</div>

<div class="table-wrapper" markdown="block">

|        Key        |                    Definition                     |
| :---------------: | :-----------------------------------------------: |
|       Risk        |                   Privacy Risk                    |
|    risk_CI_btm    | The bottom of confidence interval of Privacy Risk |
|    risk_CI_top    |  The top of confidence interval of Privacy Risk   |
|    attack_rate    |           The Main Privacy Attack rate            |
|  attack_rate_err  |         Error of Main Privacy Attack rate         |
|   baseline_rate   |         The Baseline Privacy Attack rate          |
| baseline_rate_err |     Error of the Baseline Privacy Attack rate     |
|   control_rate    |          The Control Privacy Attack rate          |
| control_rate_err  |     Error of the Control Privacy Attack rate      |

</div>

- Privacy Risk is a high level estimation of specific privacy risk obtained from the attack rates mentioned below. Its formula is as follows.
  - The numerator represents the attacker's exploitation of synthetic data, as the Main Attack to excess of the Control Attack success rate.
  - The denominator is the normalization factor by 1 minus Control Attack, representing the signifying the effectiveness of Main Attack relative to the Perfect Attacker (100%), to calculate the difference in the numerator.
  - Perfect Attacker is a concept that represents an all-knowing, all-powerful attacker. In our evaluating, this means they have a 100% chance of a successful attack. Therefore, the underlying idea behind this score is that Main Attack, due to their access to synthesized data, have a higher success rate compared to Control Attack. However, the proportion of this success rate increase relative to the Perfect Attacker's perfect success rate is what matters.
  - Ranging from zero to one, with higher numbers indicating higher privacy risk, the information provided by synthetic data brings attackers closer to that of a perfect attacker.

$$
    Privacy Risk =
        \frac{
            Attack Rate_{Main} - Attack Rate_{Control}
        }{
            1 - Attack Rate_{Control}
        }
$$

- Attack Rate refers to the proportion of successful executions of a specific attack, whether by malicious or honest-but-curious users. Also called Success Attack Rate.
  - Since it is assumed that each attack is independent, and attacks are only concerned with either success or failure, they can be modeled as Bernoulli trials. The Wilson Score Interval can be used to estimate the binomial success rate and adjusted confidence interval as below. The default of confidence level is 95%.
  - From zero to one, a higher number indicates a higher success rate for that specific attack.

$$
    {Attack Rate} =
        \frac{
            N_{Success} + \frac{ {Z}^{2} }{2}
        }{
            N_{Total}+{Z}^{2}
        }
$$

N Success means numbers of Success Attacks，N Total means numbers of Total Attacks, and Z means Z score under confidence level.

- Main Attack Rate refers to the attack rate inferred from the training data records using synthetic data.

- Baseline Attack Rate or Naive Attack Rate is the success rate inferred from the training data records using random guessing.

  - The Baseline Attack Rate provides a benchmark for measuring the strength of attacks. If the Main Attack Rate is less than or equal to the Baseline Attack Rate, it indicates the Main Attack modeling is less effective than random guessing. In this case, the result is meaningless, and the `anonymeter` library will issue a warning, suggesting that users should exclude such results from their analysis to avoid incorrectly reporting a "no risk" outcome. `PETsARD` will directly return the result, and users are responsible for their own filtering.
    - The possibility of the Main Attack being inferior to random includes scenarios with insufficient attack occurrences (`n_attacks`), attackers having too little auxiliary information (e.g., misconfigured `aux_cols` in the inference function), or issues with the data itself (e.g., too few columns, too few records, or too few combinations of categorical variables).

- Control Attack Rate is the attack rate inferred from the control data records using synthetic data.

### SDMetrics

The Python library `sdmetrics`, which is developed by [datacebo](https://docs.sdv.dev/sdmetrics/) evaluates the synthetic data in two perspectives: data validity (`'sdmetrics-diagnosticreport'`) and data quality (`'sdmetrics-qualityreport'`).

#### `'sdmetrics-diagnosticreport'`

It evaluates whether the data structure of the synthetic data is similar to that of the original data. Given that these two datasets are expected to exhibit similarity in basic properties, such as identical column names and comparable column ranges, the evaluation score should ideally approach 100%.

##### `get_global()`

Retrieve the global evaluation results from `'sdmetrics-diagnosticreport'` methods.

**Outputs**

(`pd.DataFrame`): The evaluation results. Below is an example.

<div class="table-wrapper" markdown="block">

|        | Score | Data Validity | Data Structure |
| :----: | :---: | :-----------: | :------------: |
| result |  1.0  |      1.0      |      1.0       |

</div>

The `Score` is calculated as the average of two properties: `Data Validity` and `Data Structure`. The former metrics is the average of the data validity score across all columns. The data validity score for each column is the average of the following metrics: `KeyUniqueness` (ensuring uniqueness of primary keys), `BoundaryAdherence` or `CategoryAdherence` (verifying that the synthetic data's range or categories conform to those of the original data). On the other hand, `Data Structure` checks whether the synthetic data shares identical column names with the original data. See [SDMetrics website](https://docs.sdv.dev/sdmetrics/reports/diagnostic-report/whats-included) for more information.

##### `get_columnwise()`

Retrieve the column-wise evaluation results from `'sdmetrics-diagnosticreport'` methods. Only `Data Validity` metric is provided. See the above section for further information about `Data Validity`.

**Outputs**

(`pd.DataFrame`): The evaluation results. Below is an example.

<div class="table-wrapper" markdown="block">

|     |   Property    |      Metric       | Score |
| :-: | :-----------: | :---------------: | :---: |
| age | Data Validity | BoundaryAdherence |  1.0  |

</div>

#### `'sdmetrics-qualityreport'`

It evaluates whether the synthetic data is similar to the original data in the respect to statistics. The higher the score, the better the quality.

##### `get_global()`

Retrieve the global evaluation results from `'sdmetrics-qualityreport'` methods.

**Outputs**

(`pd.DataFrame`): The evaluation results. Below is an example:

<div class="table-wrapper" markdown="block">

| Score  | Column Shapes | Column Pair Trends |
| :----: | :-----------: | :----------------: | :-: |
| result |      1.0      |        1.0         | 1.0 |

</div>

The `Score` is calculated as the average of two properties: `Column Shapes` and `Column Pair Trends`. The former metrics is the average of the KSComplement/TVComplement across all columns. The latter metrics is the average of Correlation Similarity/Contingency Similarity across all columns pairs. See [SDMetrics website](https://docs.sdv.dev/sdmetrics/reports/quality-report/whats-included) for more information.

##### `get_columnwise()`

Retrieve the column-wise evaluation results from `'sdmetrics-qualityreport'` methods. Only `Column Shapes` metric is provided. See the above section for further information about `Column Shapes`.

**Outputs**

(`pd.DataFrame`): The evaluation results. Below is an example:

<div class="table-wrapper" markdown="block">

|     |   Property    |    Metric    | Score |
| :-: | :-----------: | :----------: | :---: |
| age | Column Shapes | KSComplement |  1.0  |

</div>

##### `get_pairwise()`

Retrieve the pairwise evaluation results from `'sdmetrics-qualityreport'` methods. Only `Column Pair Trends` metric is provided. See the above section for further information about `Column Pair Trends`.

**Outputs**

(`pd.DataFrame`): The evaluation results. Below is an example.

<div class="table-wrapper" markdown="block">

|                  |      Property      |        Metric         | Score | Real Correlation | Synthetic Correlation |
| :--------------: | :----------------: | :-------------------: | :---: | :--------------: | :-------------------: |
| (age, workclass) | Column Pair Trends | ContingencySimilarity |  1.0  |       NaN        |          NaN          |

</div>

### MLUtility

To assess the utility of synthetic datasets, one may train the same machine learning models on original and synthetic datasets and compare the test results on control dataset. If the score from the synthetic one closely approximate or even surpass that from the original one, it suggests that the synthetic datasets are suitable for utilisation. To ensure the robustness of the results, several kinds of model will be trained, and the average of the results will be computed to derive the final result. Only basic data preprocessing steps will be applied, such as removing missing values and normalization.

#### `'mlutility-regression'`

Evaluate the utility based on regression tasks, where the data will undergo training on linear regression, random forest regression, and gradient boosting regression using default hyper-parameters. The evaluation metric employed will be the coefficient of determination ($R^2$).

**Parameters**

`target` (`str`): The target column of the data. Should be a numerical column.

#### `'mlutility-classification'`

Evaluate the utility based on classification tasks, where the data will undergo training on logistic regression, SVC, random forest, and gradient boosting classification using default hyper-parameters. The evaluation metric employed will be the F1-score.

**Parameters**

`target` (`str`): The target column of the data.

#### `'mlutility-cluster'`

Evaluate the utility based on clustering tasks, where the data will undergo training on k-means with different cluster numbers: 4, 5, and 6 (can be changed via `n_clusters`). Other hyper-parameters are the same. The evaluation metric employed will be the silhouette score.

**Parameters**

`n_clusters` (`list`, default=`[4, 5, 6]`): A list of numbers of clusters.

#### `get_global()`

Retrieve the evaluation results from MLUtility methods.

**Outputs**

(`pd.DataFrame`): The evaluation results. Below is an example:

| ori_mean | ori_std  | syn_mean | syn_std  |   diff    |
| :------: | :------: | :------: | :------: | :-------: |
| 0.413081 | 0.084311 | 0.034577 | 0.519624 | -0.378504 |

In the table provided, `ori_mean` and `syn_mean` represent the average scores across all runs and models obtained from the original dataset and the synthetic dataset, respectively. Correspondingly, `ori_std` and `syn_std` denote the respective standard deviations. The `diff` column signifies the difference in performance observed on the synthetic dataset compared to the original dataset. A positive value in this column indicates that the performance of the synthetic dataset surpasses that of the original dataset, while a negative value suggests the opposite.

## Refenece

For explanations of the library in this paper and translations of terminologies between Chinese and English, please refer to the following references:

- Giomi, M., Boenisch, F., Wehmeyer, C., & Tasnádi, B. (2023). A Unified Framework for Quantifying Privacy Risk in Synthetic Data. _Proceedings of Privacy Enhancing Technologies Symposium_, 2023(2), 312–328. https://doi.org/10.56553/popets-2023-0055
- 蔡柏毅（2021）。淺談個資「去識別化」與「合理利用」間的平衡。《金融聯合徵信》，第三十九期，2021年12月。
