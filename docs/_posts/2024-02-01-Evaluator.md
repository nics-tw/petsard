The `Evalutor` module is responsible for evaluting the quality of synthetic data. You can specify evaluation method in `Evaluator` class and use it to examine the synthetic data.

`Evaluator` 模組負責評估合成資料的品質。您可以在 `Evaluator` 類別中指定評估方式並檢驗合成資料。

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


# `Evaluator`


To initialise an `Evaluator`, you need to specify the evaluation method to assess the data. It is important to note that for each evaluation method, a separate `Evaluator` needs to be created. In other words, if you need to evaluate a dataset with five different methods, there will be five corresponding `Evaluator` instances.

使用 `Evaluator` 類別的物件之前，您需要指定資料評估方法。需要注意的是，針對每一個評估方法，需要建立各自獨立的 `Evaluator`，亦即如果您要使用五種方法評估資料集，則會需要五個 `Evaluator` 物件。


```Python
eval = Evaluator(
    method,
    **kwargs
)
```


**Parameters**


`method` (`str`): The evaluation method. Case insensitive. The format should be: `{library name}-{function name}`. For example, `'anonymeter-singlingout'`. 評估方法，字串不區分大小寫。格式須為 `{套件名}-{函式名}`，例如：`'anonymeter-singlingout'`
- `method = 'default'` will use `PETsARD` default evaluation: SDMetrics - QualityReport (`'sdmetrics-single_table-qualityreport'`). `method = 'default'` 將使用 `PETsARD` 預設的評測方式：SDMetrics - QualityReport (`'sdmetrics-single_table-qualityreport'`).
- `method = 'custom_method'` support users in evaluating with custom Python functions. `method = 'custom_method'` 支援使用者使用自定義 Python 函式做評測。
  - For custom Python functions, we recommend directly inheriting from the `EvaluatorBase` class and implementing its methods to meet the requirements. You can import from here: 對於自定義函式，我們建議直接繼承 `EvaluatorBase` 類別並對其方法加以實現來滿足要求。您可以從這裡導入：

```Python
from PETsARD.evaluator.evaluator_base import EvaluatorBase
```

`custom_method` (`dict`, default=`None`, optional): The dictionary contains the custom method information. It should include: 此字典包含自定義方法的資訊。它應該包括：
    - `filepath` (`str`): The path to the custom method file. 自定義方法檔案的路徑。
    - `method` (`str`): The method name in the custom method file. 自定義方法檔案中的方法名稱。

`**kwargs` (`dict`, optional): The parameters defined by each evaluation methods. See the following sections. 評估方法的自定義參數。詳見後續章節。


## `create()`

Create an `Evaluator` object with the given data. There are three types of data that may be required: the original data utilised for synthesis (referred to as "ori"), the synthetic data generated from "ori" (referred to as "syn"), and the original data that was not employed for synthesis (referred to as "control"). Different evaluation methods have different requirements, see the following section for details. Fortunately, if you are utilizing our pipeline, there is no need to concern yourself with this requirement; you are ready to proceed without any additional steps.

利用資料創建 `Evaluator`。有 3 種類型的資料可能會被用到：用於合成資料的原始資料（"ori"），利用原始資料（"ori"）合成的合成資料（"syn"），以及沒有用於訓練合成資料模型的資料（"control"），不同的評估方法需要有不同的資料種類要求（詳見後續章節）。如果您使用此套件提供的執行流程，則已經符合使用條件，可直接進行下一步，因為系統會自動區分這三類資料。


Create an `Evaluator` object with the given data.
- `Anonymeter` and `MLUtility` required three types of data:
    - The original data utilised for synthesis (referred to as `'ori'`)
    - The synthetic data generated from `'ori'` (referred to as `'syn'`)
    - The original data that was not employed for synthesis (referred to as `'control'`).
- `SDMetrics` required two types of data:
    - The original data utilised for synthesis (referred to as `'ori'`)
    - The synthetic data generated from `'ori'` (referred to as `'syn'`)
- Fortunately, if you are utilizing our `Executor` (see [Executor page](https://nics-tw.github.io/PETsARD/Executor.html)), there is no need to concern yourself with this requirement; you are ready to proceed without any additional steps.

利用資料創建 `Evaluator`。
- `Anonymeter` 與 `MLUtility` 需要三種類型的資料：
    - 用於合成資料的原始資料（`'ori'`）
    - 利用原始資料合成的合成資料（`'syn'`）
    - 沒有用於訓練合成資料模型的資料（`'control'`）
- `SDMetrics` 需要兩種類型的資料：
    - 用於合成資料的原始資料（`'ori'`）
    - 利用原始資料合成的合成資料（`'syn'`）
- 如果您使用此套件提供的 `Executor` （見 [Executor 頁面](https://nics-tw.github.io/PETsARD/Executor.html)），則已經符合使用條件，可直接進行下一步，因為系統會自動區分這三類資料。


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


`data` (`dict`): The dictionary contains 3 types of data, in the forms of `pd.DataFrame`s. The `keys` of `data` are specified above. 包含三種類型資料，需要是 `pd.DataFrame` 的格式。`data` 的 `keys` 可見上述程式碼。


## `eval()`


Evaluate the synthetic dataset.

評估資料集。


## `get_global()`


Returns the global evaluation result. 返回全資料集評估結果。


**Output**


(`pandas.DataFrame`): A dataFrame with the global evaluation result. One row only for representing the whole data result. 一個包含全資料集評估結果的 DataFrame，只用一行來代表整體資料結果。


## `get_columnwise()`


Returns the column-wise evaluation result. 返回逐欄位評估結果。


**Output**


(`pandas.DataFrame`): A dataFrame with the column-wise evaluation result. Each row contains one column in original data. 一個包含逐欄位評估結果的 DataFrame。每一行包含原始數據中的一個欄位。


## `get_pairwise()`


Retrieves the pairwise evaluation result. 返回欄位成對的評估結果。


**Output**


(`pandas.DataFrame`): A dataFrame with the pairwise evaluation result. Each row contains the pairwise relationship between two columns (column x column) in original data. 一個包含欄位成對評估結果的 DataFrame。每一行包含原始數據中的欄位與欄位之間的關係。


## `self.config`


The configuration of `Evaluator` module:

`Evaluator` 模組的參數：

- In standard usage, it includes the `method`, `method_code` from the input parameters, along with other parameters (`kwargs`). 在標準使用情況下，它包括來自輸入參數的 `method`（評測方法）、`method_code`（評測方法代號）、以及其他參數 (`kwargs`)。
- When `method` is set to `'default'`, the `method` will be replaced by the default evaluation method of `PETsARD`: SDMetrics - QualityReport (`'sdmetrics-single_table-qualityreport'`). 當 `method` 設為 `'default'` 時，`method` 將會被 `PETsARD` 預設的評測方法取代：SDMetrics - QualityReport (`'sdmetrics-single_table-qualityreport'`)。
- When `method` is set to `'custom_method'`, it encompasses `method`, `custom_method`. 當 `method` 設為 `'custom_method'` 時，它包含 `method`、`custom_method`（自訂方法）。
    - The `custom_method` dictionary further contains `filepath` and `method` as parameters. 在 `custom_method` 這個字典下又有 `filepath`（自訂方法檔案路徑）與 `method`（自訂方法名稱）兩個參數。


## `self.evaluator`

The instantiated evaluator itself.

被實例化的評估器本身。


## `self.data`

Stored the `data` input from `.create()` function. See the [`create()`](https://nics-tw.github.io/PETsARD/Evaluator.html#create) documentation for more information.

按照 `.create()` 時所輸入的 `data` 加以保存。見 [`create()`](https://nics-tw.github.io/PETsARD/Evaluator.html#create) 說明。


## `self.result`

A dictionary storing evaluator results. The format varies with different modules.

儲存評估器結果的字典。格式隨不同模組而有所不同。


# Available Evaluator Types

In this section, we provide a comprehensive list of supported evaluator types, their `method` name, and their data requirements.

在此章節我們列出所有目前支援的評估類型及其對應的 `method` 名稱與所需資料種類。


<div class="table-wrapper" markdown="block">

| Submodule | Class | Alias (`method` name) | `'ori'` needed | `'syn'` needed | `'control'` needed |
|---|:---:|:---:|:---:|:---:|:---:|
| `anonymeter` | `Anonymeter` | 'anonymeter-singlingout' | ✅ | ✅ | ✅ |
| `anonymeter` | `Anonymeter` | 'anonymeter-linkability' | ✅ | ✅ | ✅ |
| `anonymeter` | `Anonymeter` | 'anonymeter-inference' | ✅ | ✅ | ✅ |
| `sdmetrics` | `SDMetrics` | 'sdmetrics-diagnosticreport' | ✅ | ✅ |  |
| `sdmetrics` | `SDMetrics` | 'sdmetrics-qualityreport' | ✅ | ✅ |  |
| `mlutility` | `MLWorker` | 'mlutility-regression' | ✅ | ✅ | ✅ |
| `mlutility` | `MLWorker` | 'mlutility-classification' | ✅ | ✅ | ✅ |
| `mlutility` | `MLWorker` | 'mlutility-cluster' | ✅ | ✅ | ✅ |

</div>


## Anonymeter


`anonymeter` is a comprehensive Python library that evaluates various aspects of privacy risks in synthetic tabular data, including Singling Out, Linkability, and Inference risks.

These three points are based on the criteria established by [Article 29 Data Protection Working Party (WP29)](https://ec.europa.eu/justice/article-29/documentation/opinion-recommendation/files/2014/wp216_en.pdf) under the Data Protection Directive (Directive 95/46), as outlined in their written guidance published in 2014, for evaluating the effectiveness standards of anonymization techniques. `anonymeter` received positively reviewed from the [Commission Nationale de l’Informatique et des Libertés (CNIL)](https://www.cnil.fr/en/home) on February 13, 2023, acknowledging its ability to effectively evaluate the three standards of anonymization effectiveness in synthetic data. CNIL recommends using this library to evaluate the risk of re-identification.

Therefore, `PETsARD` includes built-in calls to `anonymeter`. For more details, please refer to its official GitHub: [statice/anonymeter](https://github.com/statice/anonymeter)

`anonymeter` 是一個全面評估合成表格資料中不同層面隱私風險的 Python 函式庫，包括指認性 (Singling Out)、連結性 (Linkability)、和推斷性(Inference)風險。

此三點是根據歐盟個人資料保護指令第29條設立之[個資保護工作小組](https://ec.europa.eu/justice/article-29/documentation/opinion-recommendation/files/2014/wp216_en.pdf) (WP29)，於 2014 年發布的書面指引中所列出，用於評估匿名化技術的有效性標準。而 `anonymeter` 於 2023 年 02 月 13 日受到[法國國家資訊自由委員會](https://www.cnil.fr/en/home) (CNIL)的正面評價，認為此工具能有效評估合成資料的匿名化有效性三個標準，並建議使用本函式庫來評估資料被重新識別的風險。

因此 `PETsARD` 整合了對 `anonymeter` 的使用。更多詳情請參閱其官方 GitHub：[statice/anonymeter](https://github.com/statice/anonymeter)


### `'anonymeter-singlingout'`


Singling Out risk represents the possibility of still being able to identify a particular individual, their part, or complete records, even after any Privacy-Enhancing Techniques have been applied. In the example from the `anonymeter`, it refers to the scenario where "there is only one person with attributes X, Y, and Z". In other words, attackers may attempt to identify specific individuals.

The paper on `anonymeter` specifically mentions: "It's important to note that singling out does not imply re-identification. Yet the ability to isolate an individual is often enough to exert control on that individual, or to mount other privacy attacks."

指認性風險表示即便經過隱私強化技術處理，仍有多大的可能性去識別出來特定個體，其部分或完整記錄的可能性。以 `anonymeter` 的舉例，就是「只有一個人同時擁有著 X、Y、與 Z 特徵」。換句話說，攻擊者可以嘗試辨識出特定的個體。

`anonymeter` 的論文有特別提到：「值得注意的是，指認不等於重新識別。然而，能夠單獨辨識一個體通常足以對該個體施加控制，或者進行其他隱私攻擊。」


**Parameters**


`n_attacks` (`int`, default=`2000`): Number of times this particular attack will be executed. In this case, it is the number of distinct `queries`. A `query` is a specific condition-based searching command matching only one record in a certain field, achieving Singling Out. A higher number will reduce the statistical uncertainties on the results, at the expense of a longer computation time. 攻擊執行次數，在此是指不重複搜索語句 (`queries`)的數量。搜索語句是特定的條件查詢式，使得該語句能在某欄位中僅對應到一筆資料，達到指認性。較高的數量會降低結果的統計不確定性，但會增加運算時間。

`n_cols` (`int`, default=`3`): The number of columns used for generating Singling Out `queries`. 用於產生一個搜索語句的欄位數目。

`max_attempts` (`int`, default=`500000`): The maximum number of attempts to find a successful attack. 找到成功攻擊的最大嘗試次數。


### `'anonymeter-linkability'`


Linkability risk represents the possibility that, even after Privacy-Enhancing Techniques have been applied, or when records exist in different databases, at least two records about the same individual or group of individuals can still be linked together. In the example from the `anonymeter`, it refers to the scenario where "records A and B belong to the same person". In particular, even if attackers cannot single out the specific individual's identity, they may still attempt to establish links between records through shared features or information.

連結性風險表示即使經過隱私強化技術處理、或是存在不同的資料庫中，仍有多大的可能，將至少兩條關於同一個人或一組人的記錄連結在一起。以 `anonymeter` 的舉例，就是「紀錄 A 與紀錄 B 屬於同一個人」。具體來說，即使攻擊者無法指認具體的個體身份，他們仍可能嘗試透過某些共同特徵或資訊，來建立記錄之間的關聯。


**Parameters**


`n_attacks` (`int`, default=`2000`): Number of times this particular attack will be executed. In this case, it is the number of rows in the training dataset. A higher number will reduce the statistical uncertainties on the results, at the expense of a longer computation time. 攻擊執行次數，在此是指訓練資料集行數。較高的數量會降低結果的統計不確定性，但會增加運算時間。

`max_n_attacks` (`bool`, default=`False`): Determines whether to enforce the maximum number of attacks. Support only for Linkability and Inference. If True, the input for `n_attacks` is forcibly set to the theoretical maximum number of attacks. 決定是否強制使用最大攻擊次數。此選項僅支援連結性和推斷性攻擊。當設定為 True 時，`n_attacks` 的輸入將被強制設定為理論上的最大攻擊次數。

`aux_cols` (`Tuple[List[str], List[str]]`): Columns of the auxiliary information. 輔助資訊欄位。

> The pattern of Linkability attacks assumes that attackers, whether malicious or honest-but-curious users, possesses two sets of non-overlapping original train data columns. When composite synthesized data involving these two sets of data columns is released, the attacker can use the synthetic data to link to their own original data, to determine whether the data from one dataset belongs to certain records in another dataset. In this context, the auxiliary data columns `aux_cols` are the two pieces of information the attackers own.
> For example, a medical center intends to release synthesized data from their heart disease research, which includes age, gender, postal code, and the number of heart attacks. Meanwhile, the attacker may have obtained real population data, such as gender and postal codes, from public sources or data leaks, along with real epidemiological data, such as age and the frequency of heart attacks, in their original form or in proportion. In this case, `aux_cols` is shown below.
> The potential linkage attack method in this case may be that "due to the close similarity between the real population data and real epidemiological data with the values in this synthesized data, it is possible to link the age and the frequency of heart attacks of a certain group of people from the population data, or link the gender and place of residence of a certain group of people from the epidemiological data."
> `aux_cols` involves domain-specific knowledge about the dataset, so neither `PETsARD` nor `anonymeter` provide default values for it. Users need to configure it themselves based on their understanding of the dataset. In future updates, following the experimental approach outlined in the `anonymeter` paper, different amounts of auxiliary information will be considered. The attacker's auxiliary information will be sampled from "only two columns" to "the maximum number of columns in the dataset," and these options will be provided as default values.

> 連結性攻擊的攻擊樣態，是假定攻擊者，無論惡意還是誠實但好奇的使用者，擁有兩部分不重疊的原始訓練資料欄位，而當涉及這兩份資料欄位的綜合性合成資料被釋出，攻擊者便可以用合成資料連結到自己手中的原始資料，來推測哪些資料是互相對應的。此時輔助資料欄位 `aux_cols` 便是這兩批資料所各自包含的資料欄位。
> 舉例來說，某間醫學中心要釋出自己心臟病研究的合成資料，其中包括了年齡、性別、郵遞區號、心臟病發次數，而攻擊者可能已經從公開資料或資料洩漏中，得知了真實的戶政資料：性別與郵遞區號、以及真實的流行病學資料：年紀與心臟病發次數，兩種資料的比例或原始資料。那 `aux_cols` 便如下方程式碼。
> 而此時潛在的連結性攻擊方式，便可能是「由於真實戶政資料跟真實流行病學資料，都跟此合成資料的數值差異足夠接近，於是可以由戶政資料連結出某群人的年紀與心臟病發次數，或是由流行病學資料連結出某群人的性別與居住地」。
> `aux_cols` 涉及對資料集的專業知識，故 `PETsARD`  跟 `anonymeter` 均不設預設值，須由使用者自行設定。在未來更新中，也將依照 `anonymeter` 論文的實驗方式，考量不同數量的輔助資訊，將攻擊者的輔助資訊從「僅有兩列」到「資料集的最大列數」所有抽樣方式都遍歷考慮一次，提供這樣的預設值。


```Python
aux_cols = [
    ['sex', 'zip_code'], # public
    ['age', 'heart_attack_times'] # private
]
```

`n_neighbors` (`int`, default=`10`): The N closest neighbors considered for the link search. 連結搜索時考慮的前 N 個最近鄰居數量。

> To handle mixed data types, `anonymeter` uses Gower's Distance/Similarity:
> - Numeric  variables: Gower's Distance is the absolute difference between the normalized values.
> - Categorical variables: Gower's Distance is 1 if the values are not equal.
> After combining all attributes, the Manhattan Distance is calculated, and return the nearest N neighbors. So, in the context of Linkability risk, `n_neighbors` represents how close the two sets of data from the same person need to be linked to be considered a successful linkability attack.

> 為了處理混合資料類型的資料，`anonymeter` 使用的是高爾距離/高爾相似性 (Gower's Distance/Similarity)：
> - 數值型變數：高爾距離為歸一化後兩者相差的絕對值
> - 類別型變數：只要不相等，高爾距離即為 1
> 綜合所有屬性之後計算其曼哈頓距離，最後返回最近的 N 個鄰居。於是 `n_neighbors` 在連結性風險上的意思，是指同一個人的兩批資料，要在多近的距離內被連結到，才算是連結性攻擊成功。


### `'anonymeter-inference'`


Inference risk represents the possibility that, even after Privacy-Enhancing Techniques have been applied, there is still a significant chance of deducing the value of an attribute from the values of a set of other attributes. In the example from the `anonymeter`, it refers to the scenario where "a person with attributes X and Y also have Z". To phrase it differently, even if attackers cannot single out individual identities or cannot link different records, they may still be able to deduce specific information via statistical analysis or other methods.

推斷性風險代表的是即使經過隱私強化技術處理，仍有多大的可能，從一組其他的特徵中推斷出某個特徵的值。以 `anonymeter` 的舉例，就是「擁有特徵 X 和特徵 Y 的人也擁有特徵 Z」。也就是說，即使攻擊者無法指認個體身分、也無法連結不同紀錄，攻擊者仍可以透過統計分析或其他方法來推斷出特定的資訊。


**Parameters**


`n_attacks` (`int`, default=`2000`): Number of times this particular attack will be executed. In this case, it is the number of rows in the training dataset. A higher number will reduce the statistical uncertainties on the results, at the expense of a longer computation time. 攻擊執行次數，在此是指訓練資料集行數。較高的數量會降低結果的統計不確定性，但會增加運算時間。

`max_n_attacks` (`bool`, default=`False`): Determines whether to enforce the maximum number of attacks. Support only for Linkability and Inference. If True, the input for `n_attacks` is forcibly set to the theoretical maximum number of attacks. 決定是否強制使用最大攻擊次數。此選項僅支援連結性和推斷性攻擊。當設定為 True 時，`n_attacks` 的輸入將被強制設定為理論上的最大攻擊次數。

`secret` (`str`) Column(s) of secret information. 秘密資訊欄位。

`aux_cols` (`List[str]`, default=None) Columns of auxiliary information. The default value consists of a list of columns excluding those that contain the keyword `secret`. In other words, if `aux_cols` is not specifically designated, this parameter will include all columns except those with `secret`. 輔助資訊欄位。預設值為排除包含 `secret` 關鍵字的所有欄位後的欄位列表。換句話說，如果不特別指定 `aux_cols`，則該參數會包含所有非 `secret` 欄位。

> In the context of Inference risk, the parameters `secret` and `aux_cols` go hand in hand. `secret` represents the attribute that is kept confidential, and in this scenario, `aux_cols` are the attributes other than secret that are considered to provide auxiliary information to the attacker.
>The example provided by `anonymeter` suggests the following configuration:

> 在推斷性風險中，`secret` 與 `aux_cols` 參數是一體兩面的，secret 代表被保密的屬性 (attribute)，此時 `aux_cols` 則是除了 `secret` 以外的屬性、都被認為可以提供攻擊者輔助資訊。
> `anonymeter` 的範例建議了以下的設定方法：

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

> 這樣能遍歷每個欄位被視作 `secret`。然後參考 `anonymeter` 論文的方法，對所有 `secret` 的風險結果取平均、則為資料集整體的推論性風險。


### `get_global()`


Retrieve the evaluation results from `anonymeter` methods.

獲取 `anonymeter` 方法的評估結果。


**Outputs**

(`pd.DataFrame`): The evaluation results. Below is an example. 評估結果，範例如下。


<div class="table-wrapper" markdown="block">

| | risk | risk_CI_btm | risk_CI_top | attack_rate | attack_rate_err | baseline_rate | baseline_rate_err | control_rate | control_rate_err |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| result | 0.998962 | 0.997923 | 1.0 | 0.999041 | 0.000959 | 0.024413 | 0.006695 | 0.076813 | 0.011631 |

</div>


<div class="table-wrapper" markdown="block">

| Key | Definition | 定義 |
|:---:|:---:|:---:|
| Risk | Privacy Risk | 隱私風險 |
| risk_CI_btm | The bottom of confidence interval of Privacy Risk | 隱私風險信賴區間下界 |
| risk_CI_top | The top of confidence interval of Privacy Risk | 隱私風險信賴區間上界 |
| attack_rate | The Main Privacy Attack rate | 主要隱私攻擊率 |
| attack_rate_err | Error of Main Privacy Attack rate | 主要隱私攻擊率誤差 |
| baseline_rate | The Baseline Privacy Attack rate | 基線隱私攻擊率 |
| baseline_rate_err | Error of the Baseline Privacy Attack rate | 基線隱私攻擊率誤差 |
| control_rate | The Control Privacy Attack rate | 控制隱私攻擊率 |
| control_rate_err | Error of the Control Privacy Attack rate | 控制隱私攻擊率誤差 |

</div>


- Privacy Risk is a high level estimation of specific privacy risk obtained from the attack rates mentioned below. Its formula is as follows.
    - The numerator represents the attacker's exploitation of synthetic data, as the Main Attack to excess of the Control Attack success rate.
    - The denominator is the normalization factor by 1 minus Control Attack, representing the signifying the effectiveness of Main Attack relative to the Perfect Attacker (100%), to calculate the difference in the numerator.
    - Perfect Attacker is a concept that represents an all-knowing, all-powerful attacker. In our evaluating, this means they have a 100% chance of a successful attack. Therefore, the underlying idea behind this score is that Main Attack, due to their access to synthesized data, have a higher success rate compared to Control Attack. However, the proportion of this success rate increase relative to the Perfect Attacker's perfect success rate is what matters.
    - Ranging from zero to one, with higher numbers indicating higher privacy risk, the information provided by synthetic data brings attackers closer to that of a perfect attacker.

- 隱私風險是綜合下述攻擊率而得到的對特定隱私風險的評估，其公式如下。
  - 分子代表攻擊者利用合成資料的攻擊、也就是主要攻擊對控制攻擊成功率的改進。
  - 分母則以 1 - 控制攻擊 代表主要攻擊相對於完美攻擊者 (100%) 的效果，作為歸一化因子計算分子的差異。
  - 完美攻擊者是一個概念，代表著一個全知全能的攻擊者，在我們的驗測中，這表示他有 100% 的成功攻擊機會。因此，這個分數背後的思想是，主要攻擊因為取得合成資料，因此相對於控制攻擊有更高的成功率，但這個成功率提升，相對於完美攻擊者完美的成功率提升，所佔的比例有多少。
  - 0 到 1，數字越大代表隱私的風險越高，合成資料提供的資訊能使攻擊者越接近完美攻擊者。


$$\text{PrivacyRisk} = \frac{\text{AttackRate}_{\text{Main}}-\text{AttackRate}_{\text{Control}}}{1-\text{AttackRate}_{\text{Control}}}$$


- Attack Rate refers to the proportion of successful executions of a specific attack, whether by malicious or honest-but-curious users. Also called Success Attack Rate.
  - Since it is assumed that each attack is independent, and attacks are only concerned with either success or failure, they can be modeled as Bernoulli trials. The Wilson Score Interval can be used to estimate the binomial success rate and adjusted confidence interval as below. The default of confidence level is 95%.
  - From zero to one, a higher number indicates a higher success rate for that specific attack.

- 攻擊率意指無論是由惡意還是誠實但好奇的使用者成功執行特定攻擊的比例。又被稱為成功攻擊率。
  - 由於假設每次攻擊都是獨立的，而攻擊只關心成功或失敗兩種結果，因此它們可以被建模為伯努利試驗。可以使用威爾遜分數區間來估算二項式成功率與調整後的信賴區間如下。預設信心水準為 95%。
  - 0 到 1，數字越大代表該特定攻擊的成功率越高。


$$
\text{AttackRate} =
\frac{N_{\text{Success}}+\frac{ {Z}^{2} }{2} }{ N_{\text{Total}}+{Z}^{2} }\quad\left
\{\begin{matrix}
N_{\text{Success}} & \text{Number of Success Attacks}\\
N_{\text{Total}} & \text{Number of Total Attacks}\\
Z & Z\text{ score of confidence level}
\end{matrix}
\right.
$$


- Main Attack Rate refers to the attack rate inferred from the training data records using synthetic data.
- 主要攻擊率 (Main Attack Rate) 是指使用合成資料來推斷訓練資料紀錄的攻擊率。


- Baseline Attack Rate or Naive Attack Rate is the success rate inferred from the training data records using random guessing.
  - The Baseline Attack Rate provides a benchmark for measuring the strength of attacks. If the Main Attack Rate is less than or equal to the Baseline Attack Rate, it indicates the Main Attack modeling is less effective than random guessing. In this case, the result is meaningless, and the `anonymeter` library will issue a warning, suggesting that users should exclude such results from their analysis to avoid incorrectly reporting a "no risk" outcome. `PETsARD` will directly return the result, and users are responsible for their own filtering.
    - The possibility of the Main Attack being inferior to random includes scenarios with insufficient attack occurrences (`n_attacks`), attackers having too little auxiliary information (e.g., misconfigured `aux_cols` in the inference function), or issues with the data itself (e.g., too few columns, too few records, or too few combinations of categorical variables).
- 基線攻擊率 (Baseline Attack Rate) 或是天真攻擊率 (Naive Attack Rate) 則是使用隨機猜測來推斷訓練資料紀錄的成功率。
  - 基線攻擊率提供了衡量攻擊強度的基準值，如果主要攻擊率小於等於基線攻擊率，則代表主要攻擊的建模、其效果還不如隨機猜測，此時結果沒有意義，`anonymeter`函式庫會在回傳結果的同時。警告用戶應該從分析中加以排除，避免錯誤的報告成「沒有風險」的結果。`PETsARD` 會直接回傳結果，請用戶自行篩選。
  - 導致主要攻擊率不如隨機猜測的可能性，包括攻擊次數過少 (`n_attacks`)，攻擊者可獲得的輔助資訊過少（例如 inference 功能中 `aux_cols` 設定錯誤），或者資料本身存在問題（例如欄位數量不足、記錄太少、或者類別變數的排列組合過於有限等情況）。


- Control Attack Rate is the attack rate inferred from the control data records using synthetic data.
- 控制攻擊率 (Control Attack Rate) 則是使用合成資料來推斷控制資料紀錄的攻擊率。


## SDMetrics


The Python library `sdmetrics`, which is developed by [datacebo](https://docs.sdv.dev/sdmetrics/) evaluates the synthetic data in two perspectives: data validity (`'sdmetrics-diagnosticreport'`) and data quality (`'sdmetrics-qualityreport'`).

由 [datacebo](https://docs.sdv.dev/sdmetrics/) 開發的 Python 套件 `sdmetrics` 從以下兩個面向評估合成資料：資料效度 (data validity) (`'sdmetrics-diagnosticreport'`)及資料品質 (data quality) (`'sdmetrics-qualityreport'`)。


### `'sdmetrics-diagnosticreport'`


It evaluates whether the data structure of the synthetic data is similar to that of the original data. Given that these two datasets are expected to exhibit similarity in basic properties, such as identical column names and comparable column ranges, the evaluation score should ideally approach 100%.

此指標衡量合成資料的資料結構是否與原始資料相似。由於兩資料集在基本性質上（如欄位名稱應一致、欄位的值域應相似）必須有高度相似性，因此此分數應盡可能接近 100%。


#### `get_global()`


Retrieve the global evaluation results from `'sdmetrics-diagnosticreport'` methods.

獲取 `'sdmetrics-diagnosticreport'` 方法的全域評估結果。


**Outputs**


(`pd.DataFrame`): The evaluation results. Below is an example. 評估結果，範例如下。


<div class="table-wrapper" markdown="block">

| | Score | Data Validity | Data Structure |
|:---:|:---:|:---:|:---:|
| result | 1.0 | 1.0 | 1.0 |

</div>


The `Score` is calculated as the average of two properties: `Data Validity` and `Data Structure`. The former metrics is the average of the data validity score across all columns. The data validity score for each column is the average of the following metrics: `KeyUniqueness` (ensuring uniqueness of primary keys), `BoundaryAdherence` or `CategoryAdherence` (verifying that the synthetic data's range or categories conform to those of the original data). On the other hand, `Data Structure` checks whether the synthetic data shares identical column names with the original data. See [SDMetrics website](https://docs.sdv.dev/sdmetrics/reports/diagnostic-report/whats-included) for more information.

`Score` 為兩指標 `Data Validity` 及 `Data Structure` 的平均。前者是資料效度分數在各欄位的平均。每個欄位的資料效度分數由以下指標組成：`KeyUniqueness` （確保資料主鍵 (primary keys) 的唯一性）, `BoundaryAdherence` or `CategoryAdherence` (確保合成資料的值域或類別與原始資料一致). 而 `Data Structure` 則是檢查合成資料與原始資料的欄位名稱是否相同。詳見 [SDMetrics website](https://docs.sdv.dev/sdmetrics/reports/diagnostic-report/whats-included).


#### `get_columnwise()`


Retrieve the column-wise evaluation results from `'sdmetrics-diagnosticreport'` methods. Only `Data Validity` metric is provided. See the above section for further information about `Data Validity`.

獲取 `'sdmetrics-diagnosticreport'` 方法的各欄位評估結果。僅提供 `Data Validity` 指標的結果。關於 `Data Validity` 的細節，詳見上方章節。


**Outputs**


(`pd.DataFrame`): The evaluation results. Below is an example. 評估結果，範例如下。


<div class="table-wrapper" markdown="block">

| | Property | Metric | Score |
|:---:|:---:|:---:|:---:|
| age | Data Validity | BoundaryAdherence | 1.0 |

</div>


### `'sdmetrics-qualityreport'`


It evaluates whether the synthetic data is similar to the original data in the respect to statistics. The higher the score, the better the quality.

此指標衡量合成資料是否與原始資料在統計指標上相似。分數越高代表合成資料品質越好。


#### `get_global()`


Retrieve the global evaluation results from `'sdmetrics-qualityreport'` methods.

獲取 `'sdmetrics-qualityreport'` 方法的全域評估結果。


**Outputs**


(`pd.DataFrame`): The evaluation results. Below is an example. 評估結果，範例如下。


<div class="table-wrapper" markdown="block">

| | Score | Column Shapes | Column Pair Trends |
|:---:|:---:|:---:|:---:|
| result | 1.0 | 1.0 | 1.0 |

</div>


The `Score` is calculated as the average of two properties: `Column Shapes` and `Column Pair Trends`. The former metrics is the average of the KSComplement/TVComplement across all columns. The latter metrics is the average of Correlation Similarity/Contingency Similarity across all columns pairs. See [SDMetrics website](https://docs.sdv.dev/sdmetrics/reports/quality-report/whats-included) for more information.

`Score` 為兩指標 `Column Shapes` 及 `Column Pair Trends` 的平均。前者是每個欄位 KSComplement/TVComplement 值的平均。後者每個欄位組（column pair，兩個欄位即為一個欄位組）的 Correlation Similarity/Contingency Similarity 的平均。詳見 [SDMetrics website](https://docs.sdv.dev/sdmetrics/reports/quality-report/whats-included).


#### `get_columnwise()`


Retrieve the column-wise evaluation results from `'sdmetrics-qualityreport'` methods. Only `Column Shapes` metric is provided. See the above section for further information about `Column Shapes`.

獲取 `'sdmetrics-qualityreport'` 方法的各欄位評估結果。僅提供 `Column Shapes` 指標的結果。關於 `Column Shapes` 的細節，詳見上方章節。


**Outputs**


(`pd.DataFrame`): The evaluation results. Below is an example. 評估結果，範例如下。


<div class="table-wrapper" markdown="block">

| | Property | Metric | Score |
|:---:|:---:|:---:|:---:|
| age | Column Shapes | KSComplement | 1.0 |

</div>


#### `get_pairwise()`

Retrieve the pairwise evaluation results from `'sdmetrics-qualityreport'` methods. Only `Column Pair Trends` metric is provided. See the above section for further information about `Column Pair Trends`.

獲取 `'sdmetrics-qualityreport'` 方法的欄位組合評估結果。僅提供 `Column Pair Trends` 指標的結果。關於 `Column Pair Trends` 的細節，詳見上方章節。

**Outputs**

(`pd.DataFrame`): The evaluation results. Below is an example. 評估結果，範例如下。


<div class="table-wrapper" markdown="block">

| | Property | Metric | Score | Real Correlation | Synthetic Correlation |
|:---:|:---:|:---:|:---:|:---:|:---:|
| (age, workclass) | Column Pair Trends | ContingencySimilarity | 1.0 | NaN | NaN |

</div>

## MLUtility

To assess the utility of synthetic datasets, one may train the same machine learning models on original and synthetic datasets and compare the test results on control dataset. If the score from the synthetic one closely approximate or even surpass that from the original one, it suggests that the synthetic datasets are suitable for utilisation. To ensure the robustness of the results, several kinds of model will be trained, and the average of the results will be computed to derive the final result. Only basic data preprocessing steps will be applied, such as removing missing values and normalization.

使用者可以利用原始資料與合成資料分別訓練相同的機器學習模型，並利用控制組的資料進行結果預測。若兩個模型的表現分數接近，甚至合成資料模型超過原始資料模型的表現，代表合成資料具有高度的實用性。實驗中會使用不同的機器學習模型進行訓練，並回傳算數平均數作為結果，以提升結果的可靠性。在過程中只會進行基本的資料前處理，如移除遺失值與標準化。

### `'mlutility-regression'`

Evaluate the utility based on regression tasks, where the data will undergo training on linear regression, random forest regression, and gradient boosting regression using default hyper-parameters. The evaluation metric employed will be the coefficient of determination ($R^2$).

用迴歸任務衡量實用性。使用的機器學習模型包含：線性迴歸、隨機森林迴歸、梯度提升迴歸，三者皆以預設超參數進行訓練。使用的衡量指標為 $R^2$。

**Parameters**

`target` (`str`): The target column of the data. Should be a numerical column. 資料集中用於預測的目標欄位，需為數值欄位。

### `'mlutility-classification'`

Evaluate the utility based on classification tasks, where the data will undergo training on logistic regression, SVC, random forest, and gradient boosting classification using default hyper-parameters. The evaluation metric employed will be the F1-score.

用分類任務衡量實用性。使用的機器學習模型包含：羅吉斯迴歸、支援向量機、隨機森林、梯度提升分類，四者皆以預設超參數進行訓練。使用的衡量指標為 F1 分數。

**Parameters**

`target` (`str`): The target column of the data. 資料集中用於預測的目標欄位。

### `'mlutility-cluster'`

Evaluate the utility based on clustering tasks, where the data will undergo training on k-means with different cluster numbers: 4, 5, and 6 (can be changed via `n_clusters`). Other hyper-parameters are the same. The evaluation metric employed will be the silhouette score.

用聚類任務衡量實用性。使用的機器學習模型包含：不同類別數（4、5、6，可藉由 `n_clusters` 調整）的 k-平均演算法，三者皆以預設超參數進行訓練。使用的衡量指標為輪廓係數。

**Parameters**

`n_clusters` (`list`, default=`[4, 5, 6]`): A list of numbers of clusters.

### `get_global()`

Retrieve the evaluation results from AutoML methods.

獲取 AutoML 方法的評估結果。

**Outputs**

(`pd.DataFrame`): The evaluation results. Below is an example. 評估結果，範例如下。

| ori_mean | ori_std | syn_mean | syn_std | diff |
|:---:|:---:|:---:|:---:|:---:|
| 0.413081 | 0.084311 | 0.034577 | 0.519624 | -0.378504 |

In the table provided, `ori_mean` and `syn_mean` represent the average scores across all runs and models obtained from the original dataset and the synthetic dataset, respectively. Correspondingly, `ori_std` and `syn_std` denote the respective standard deviations. The `diff` column signifies the difference in performance observed on the synthetic dataset compared to the original dataset. A positive value in this column indicates that the performance of the synthetic dataset surpasses that of the original dataset, while a negative value suggests the opposite.

在上述表格中，`ori_mean` 和 `syn_mean` 分別代表原始資料與合成資料在各次執行與各模型的分數平均。同樣的，`ori_std` 和 `syn_std` 分別代表相對應的標準差。而 `diff` 代表合成資料相比於原始資料上的進步差異值。正值代表合成資料上的表現優於原始資料上的表現；負值則代表原始資料上的表現優於合成資料上的表現。

## AutoML

> FutureWarning: `automl` will be deprecated soon. Please use `mlutility` instead.
> 警告：`automl` 即將被汰換，請改用 `mlutility`。

To assess the utility of synthetic datasets, one may conduct machine learning model training on these datasets and compare the results with those obtained from training on original datasets. If the scores closely approximate or even surpass those achieved with original datasets, it suggests that the synthetic datasets are suitable for utilisation. To ensure the robustness of the results, the model will be trained and evaluated five times (in default, can be changed via the parameter `n_splits`), and the average of the results will be computed to derive the final result. Only basic data preprocessing steps will be applied, such as removing missing values and normalization.

使用者可以透過利用合成資料訓練機器學習模型，並將結果與利用原始資料訓練的模型結果比較，來得知合成資料的實用性。若兩者分數接近，甚至是超過原始資料的表現，代表合成資料具有高度的實用性。每個模型會用不同的資料切分訓練、衡量五次（次數為預設值，可藉由 `n_splits` 調整），並回傳算數平均數作為結果，以提升結果的可靠性。在過程中只會進行基本的資料前處理，如移除遺失值與標準化。

### `'automl-regression'`

Evaluate the utility based on regression tasks, where the data will undergo training on linear regression, random forest regression, and gradient boosting regression using default hyper-parameters. The evaluation metric employed will be the coefficient of determination ($R^2$).

用迴歸任務衡量實用性。使用的機器學習模型包含：線性迴歸、隨機森林迴歸、梯度提升迴歸，三者皆以預設超參數進行訓練。使用的衡量指標為 $R^2$。

**Parameters**

`target` (`str`): The target column of the data. Should be a numerical column. 資料集中用於預測的目標欄位，需為數值欄位。

`n_splits` (`int`, default=`5`): The parameter for k-fold cross validation. Should be greater than 1. 在 k-fold 交叉驗證時的 k 值。需大於 1。

### `'automl-classification'`

Evaluate the utility based on classification tasks, where the data will undergo training on logistic regression, SVC, random forest, and gradient boosting classification using default hyper-parameters. The evaluation metric employed will be the F1-score.

用分類任務衡量實用性。使用的機器學習模型包含：羅吉斯迴歸、支援向量機、隨機森林、梯度提升分類，四者皆以預設超參數進行訓練。使用的衡量指標為 F1 分數。

**Parameters**

`target` (`str`): The target column of the data. 資料集中用於預測的目標欄位。

`n_splits` (`int`, default=`5`): The parameter for k-fold cross validation. Should be greater than 1. 在 k-fold 交叉驗證時的 k 值。需大於 1。

### `'automl-cluster'`

Evaluate the utility based on clustering tasks, where the data will undergo training on k-means with different cluster numbers: 4, 5, and 6 (can be changed via `n_clusters`). Other hyper-parameters are the same. The evaluation metric employed will be the silhouette score.

用聚類任務衡量實用性。使用的機器學習模型包含：不同類別數（4、5、6，可藉由 `n_clusters` 調整）的 k-平均演算法，三者皆以預設超參數進行訓練。使用的衡量指標為輪廓係數。

**Parameters**

`n_clusters` (`list`, default=`[4, 5, 6]`): A list of numbers of clusters.

`n_splits` (`int`, default=`5`): The parameter for k-fold cross validation. Should be greater than 1. 在 k-fold 交叉驗證時的 k 值。需大於 1。

### `get_global()`

Retrieve the evaluation results from AutoML methods.

獲取 AutoML 方法的評估結果。

**Outputs**

(`pd.DataFrame`): The evaluation results. Below is an example. 評估結果，範例如下。

| ori_mean | ori_std | syn_mean | syn_std | diff |
|:---:|:---:|:---:|:---:|:---:|
| 0.413081 | 0.084311 | 0.034577 | 0.519624 | -0.378504 |

In the table provided, `ori_mean` and `syn_mean` represent the average scores across all runs and models obtained from the original dataset and the synthetic dataset, respectively. Correspondingly, `ori_std` and `syn_std` denote the respective standard deviations. The `diff` column signifies the difference in performance observed on the synthetic dataset compared to the original dataset. A positive value in this column indicates that the performance of the synthetic dataset surpasses that of the original dataset, while a negative value suggests the opposite.

在上述表格中，`ori_mean` 和 `syn_mean` 分別代表原始資料與合成資料在各次執行與各模型的分數平均。同樣的，`ori_std` 和 `syn_std` 分別代表相對應的標準差。而 `diff` 代表合成資料相比於原始資料上的進步差異值。正值代表合成資料上的表現優於原始資料上的表現；負值則代表原始資料上的表現優於合成資料上的表現。

# Refenece


For explanations of the library in this paper and translations of terminologies between Chinese and English, please refer to the following references:

本文之函式庫解釋與中英用詞翻譯，請參閱以下文獻：

- Giomi, M., Boenisch, F., Wehmeyer, C., & Tasnádi, B. (2023). A Unified Framework for Quantifying Privacy Risk in Synthetic Data. *Proceedings of Privacy Enhancing Technologies Symposium*, 2023(2), 312–328. https://doi.org/10.56553/popets-2023-0055
- 蔡柏毅（2021）。淺談個資「去識別化」與「合理利用」間的平衡。《金融聯合徵信》，第三十九期，2021年12月。