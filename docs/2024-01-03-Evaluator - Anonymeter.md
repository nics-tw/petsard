# Anonymeter

`Anonymeter` is a comprehensive Python library that evaluates various aspects of privacy risks in synthetic tabular data, including **Singling Out**, **Linkability**, and **Inference** risks.

These three points are based on the criteria established by [Article 29 Data Protection Working Party (WP29)](https://ec.europa.eu/justice/article-29/documentation/opinion-recommendation/files/2014/wp216_en.pdf) under the Data Protection Directive (Directive 95/46), as outlined in their written guidance published in 2014, for evaluating the effectiveness standards of anonymization techniques. `Anonymeter`` received positively reviewed from the [Commission Nationale de l’Informatique et des Libertés (CNIL)](https://www.cnil.fr/en/home) on February 13, 2023, acknowledging its ability to effectively evaluate the three standards of anonymization effectiveness in synthetic data. CNIL recommends using this library to evaluate the risk of re-identification.

Therefore, `PETsARD` includes built-in calls to `Anonymeter`. For more details, please refer to its official GitHub: [statice/anonymeter](https://github.com/statice/anonymeter)

`Anonymeter` 是一個全面評估合成表格資料中不同層面隱私風險的 Python 函式庫，包括**指認性**(**Singling Out**)、**連結性**(**Linkability**)、和**推斷性**(**Inference**)風險。

此三點是根據歐盟個人資料保護指令第29條設立之[個資保護工作小組](https://ec.europa.eu/justice/article-29/documentation/opinion-recommendation/files/2014/wp216_en.pdf)(WP29)，於 2014 年發布的書面指引中所列出，用於評估匿名化技術的有效性標準。而 `Anonymeter` 於 2023 年 02 月 13 日受到[法國國家資訊自由委員會](https://www.cnil.fr/en/home)(CNIL)的正面評價，認為此工具能有效評估合成資料的匿名化有效性三個標準，並建議使用本函式庫來評估資料被重新識別的風險。

因此 `PETsARD`整合了對 `Anonymeter` 的使用。更多詳情請參閱其官方 GitHub：[statice/anonymeter](https://github.com/statice/anonymeter)


```python
from PETsARD import Evaluator
eval = Evaluator(
    evaluating_method='anonymeter-singlingout-univariate',
    data={'ori': train_data,
          'syn': synethsizing_data,
          'control': validation_data
    }
)
eval.eval()
print(eval.Evaluator.evaluation)
```

```plaintext
{'Risk': 0.0,
 'Risk_CI_btm': 0.0,
 'Risk_CI_top': 0.0013568577126237004,
 'Attack_Rate': 0.0009585236406264672,
 'Attack_Rate_err': 0.0009585236406264671,
 'Baseline_Rate': 0.0009585236406264672,
 'Baseline_Rate_err': 0.0009585236406264671,
 'Control_Rate': 0.0009585236406264672,
 'Control_Rate_err': 0.0009585236406264671}
```

---

## Common: Inherited from Evaluator

In the `Anonymeter` module, which is embedded within the `Evaluator` module and inherits parameters from it. Additionally, "Anonymeter" follows a standardized output format.

`Anonymeter` 內嵌在 `Evaluator` 模組、並繼承其參數。同時 `Anonymeter` 也有統一的輸出格式。

---

### evaluating_method

`evaluating_method` (`str`): evaluating method 評估方法

The parameter `evaluating_method`, which is inherited from Evaluator, determines which evaluation module to invoke. Input values starting with 'anonymeter-' can call the following methods of `Anonymeter` (case-insensitive):

繼承自 `Evaluator` 的參數評估方法 (**`evaluating_method`**) 能決定呼叫哪種評估模組，其中以 **'anonymeter-'** 開頭的輸入值便能調用 `Anonymeter`，有以下方法（大小寫不分）：

- **'anonymeter-singlingout-univariate'**: Singling Out risk - Univariate mode
    指認性風險 - 單變數模式
- **'anonymeter-linkability'**: Linkability risk 連結性風險
- **'anonymeter-inference'**: Inference risks 推斷性風險

```python
evaluating_method='anonymeter-singlingout-univariate' # Singling Out risk
evaluating_method='anonymeter-linkability'            # Linkability risk
evaluating_method='anonymeter-inference'              # Inference risk
```

---

### data

`data` (`Dict[str, pd.DataFrame]`): input data 輸入資料

`data` is a dictionary with a specific format, containing specific keys, and each value is a Pandas DataFrame.

`data` 是具特定格式的字典，有特定的鍵，並且每個值都是一個 Pandas DataFrame。

- `ori`: `Original Train data`. A portion of the original data used to generate synthetic data (`syn`).
- `syn`: `Synethsizing data`. Synthetic data generated from `ori`.
- `control`: `Validation data`. Another portion of the original data not used for generating synthetic data and kept confidential.

- `ori`：`原始訓練資料`。被用於生成合成資料 (`syn` )的原始資料部份。
- `syn`：`合成資料`。是用 `ori` 生成得來。
- `control`：`驗證資料`。控制未用於生成合成資料、訊息未洩漏的原始資料部份。

---

### n_attacks

`n_attacks` (`int`, default=2000): Number of target records for specific attack 特定攻擊的攻擊目標數

`n_attacks` is the parameter in `Anonymeter` that specifies how many times this particular attack will be executed. A higher number will reduce the statistical uncertainties on the results, at the expense of a longer computation time. In fact, each type of attack has a potential maximum limit on number of attacks:

- `Singling Out`: Number of distinct `queries`. A `query` is a specific condition-based searching command matching only one record in a certain field, achieving `Singling Out`.
- `Linkability` and `Inference`: Number of rows in the training dataset. The implementation of these two attack methods is to sample from the `Original Train data`.

If a value exceeding the potential maximum attack count is set, `Anonymeter` will issue a warning and disregard the remaining counts.

Therefore, we plan to set the default value to automatically determine this upper limit in future release, to ensure comprehensive testing for `PETsARD`. If users find that the computation time is too long during trial, you can reduce it to the attack numbers provided in the official `Anonymeter` examples: 500 for `Singling Out`, and 2,000 for `Linkability` and `Inference`.

`n_attacks` 即 `Anonymeter` 將執行這種攻擊多少次的參數，較高的數量會降低結果的統計不確定性，但會增加運算時間。事實上各種攻擊方式都存在有潛在的攻擊次數上限：

- `Singling Out`：不重複`搜索語句`的數量。`搜索語句`是特定的條件查詢式，使得該語句能在某欄位中僅對應到一筆資料，達到`指認性`。
- `Linkability` 跟 `Inference`：訓練資料集行數。這兩種攻擊方式背後實現的原理，是對`原始訓練資料進行抽樣。

如果設定了超過潛在上限攻擊次數的值，則 `Anonymeter` 將回傳警告，並忽略剩下的次數。

因此，在未來的更新中，我們計劃將預設值設定為自動判斷上限，以確保 `PETsARD` 的測試足夠全面。如果使用者在試用中發現運算時間過長，可以暫時將攻擊數調低，而 `Anonymeter` 官方範例中設定的值為：`Singling Out` 為 500，`Linkability` 跟 `Inference` 為 2,000。

---

### .eval()

Execute the evaluation. This method is inherited from `Evaluator`, and does not require nor accept any parameters."

執行評估。繼承自 `Evaluator` 的方法，不需也不接受任何參數。

```python
eval = Evaluator(...)
eval.eval()
```

---

#### output

`self.Evaluator.evaluation` (`Dict[str, float]`): evaluation 評估結果

The evaluation results are stored directly as a dictionary in `self.Evaluator.evaluation`, following a specific format, and all values are floating-point numbers within the range of 0.0 to 1.0:

評估結果直接作為字典儲存在 `self.Evaluator.evaluation` 內，具有特定格式，且值都是範圍為 0.0 ~ 1.0 的浮點數：

```plaintext
{'Risk': 0.0,
 'Risk_CI_btm': 0.0,
 'Risk_CI_top': 0.0,
 'Attack_Rate': 0.0,
 'Attack_Rate_err': 0.0,
 'Baseline_Rate': 0.0,
 'Baseline_Rate_err': 0.0,
 'Control_Rate': 0.0,
 'Control_Rate_err': 0.0}
```

| key                | Definition                                            | 定義                    |
|--------------------|-------------------------------------------------------|-------------------------|
| Risk               | **Privacy Risk**                                      | **隱私風險**            |
| Risk_CI_btm        | The **bottom** of confidence interval of Privacy Risk | 隱私風險信賴區間**下界** |
| Risk_CI_top        | The **top** of confidence interval of Privacy Risk    | 隱私風險信賴區間**上界** |
| Attack_Rate        | The Main Privacy **Attack** rate                      | 主要隱私**攻擊**率       |
| Attack_Rate_err    | Error of Main Privacy Attack rate                     | 主要隱私**攻擊**率誤差   |
| Baseline_Rate      | The **Baseline** Privacy Attack rate                  | **基線**隱私攻擊率       |
| Baseline_Rate_err  | Error of the Baseline Privacy Attack rate             | **基線**隱私攻擊率誤差   |
| Control_Rate       | The **Control** Privacy Attack rate                   | **控制**隱私攻擊率       |
| Control_Rate_err   | Error of the Control Privacy Attack rate              | **控制**隱私攻擊率誤差   |

- **Privacy Risk** is a high level estimation of specific privacy risk obtained from the attack rates mentioned below. Its formula is as follows.
    - The numerator represents the attacker's exploitation of synthetic data, as the **Main Attack** to excess of the **Control Attack** success rate.
    - The denominator is the normalization factor by **1 minus Control Attack**, representing the perfect attacker's effectiveness, to calculate the difference in the numerator.
    - From zero to one, with higher numbers indicating higher privacy risk, the information provided by synthetic data brings attackers closer to that of a perfect attacker.

- **隱私風險**是綜合下述攻擊率而得到的對特定隱私風險的評估，其公式如下。
  - 分子代表攻擊者利用合成資料的攻擊、也就是**主要攻擊**對**控制攻擊**成功率的改進。
  - 分母則以 **1 減 控制攻擊** 代表完美攻擊者效果，作為歸一化因子計算分子的差異。
  - 零到一，數字越大代表隱私的風險越高，合成資料提供的資訊能使攻擊者越接近完美攻擊者。

$$PrivacyRisk = \frac{AttackRate_{Main}-AttackRate_{Control}}{1-AttackRate_{Control}}$$

- **Attack Rate** refers to the proportion of **successful** executions of a specific attack, whether by malicious or honest-but-curious users. Also called **Success Attack Rate**.
  - Since it is assumed that each attack is independent, and attacks are only concerned with either success or failure, they can be modeled as Bernoulli trials. The **Wilson Score Interval** can be used to estimate the binomial success rate and adjusted confidence interval as below.The default of confidence level is 95%.
  - From zero to one, a higher number indicates a higher success rate for that specific attack.

- **攻擊率**意指無論是由惡意還是誠實但好奇的使用者**成功**執行特定攻擊的比例。又被稱為**成功攻擊率**。
  - 由於假設每次攻擊都是獨立的，而攻擊只關心成功或失敗兩種結果，因此它們可以被建模為伯努利試驗。可以使用**威爾遜分數區間**來估算二項式成功率與調整後的信賴區間如下。預設信賴分數為 95%。
  - 零到一，數字越大代表該特定攻擊的成功率越高。

$$AttackRate = \frac{N_{Success}+\frac{{Z}^{2}}{2}}{N_{Total}+{Z}^{2}}\quad
\left\{\begin{matrix}
N_{Success} & Number\;of\;Success\;Attack\\
N_{Total} & Number\;of\;Total\;Attack\\
Z & Z\;score\;of\;confidence\;level
\end{matrix}\right.$$

- **Main Attack Rate** refers to the attack rate inferred from the training data records using synthetic data.
- **Baseline Attack Rate** or **Naive Attack Rate** is the success rate inferred from the training data records using random guessing.
  - The Baseline Attack Rate provides a benchmark for measuring the strength of attacks. If the **Main Attack Rate is less than or equal to the Baseline Attack Rate**, it indicates the Main Attack  modeling is less effective than random guessing. In this case, the result is meaningless, and the `Anonymeter` library will issue a warning, suggesting that users should exclude such results from their analysis to avoid incorrectly reporting a "no risk" outcome. `PETsARD` will directly return the result, and users are responsible for their own filtering.
    - The possibility of the Main Attack being inferior to random includes scenarios with insufficient attack occurrences (`n_attacks`), attackers having too little auxiliary information (e.g., misconfigured `aux_cols` in the `Inference` function), or issues with the data itself (e.g., too few columns, too few records, or too few combinations of categorical variables).
- **Control Attack Rate** is the attack rate inferred from the control data records using synthetic data.

- **主要攻擊率**是指使用合成資料來推斷訓練資料紀錄的攻擊率
- **基線攻擊率**或是**天真攻擊率**則是使用隨機猜測來推斷訓練資料紀錄的成功率
  - 基線攻擊率提供了衡量攻擊強度的基準值，如果**主要攻擊率小於等於基線攻擊率**，則代表主要攻擊的建模、其效果還不如隨機猜測，此時結果沒有意義，`Anonymeter`函式庫會在回傳結果的同時。警告用戶應該從分析中加以排除，避免錯誤的報告成『沒有風險』的結果。`PETsARD` 會直接回傳結果，請用戶自行篩選。
  - 導致主要攻擊率不如隨機猜測的可能性，包括攻擊次數過少 (`n_attacks`)，攻擊者可獲得的輔助資訊過少（例如 `Inference` 功能中 `aux_cols` 設定錯誤），或者資料本身存在問題（例如欄位數量不足、記錄太少、或者類別變數的排列組合過於有限等情況）。
- **控制攻擊率**則是使用合成資料來推斷控制資料紀錄的攻擊率

---

## evaluating_method='anonymeter-singlingout-univariate'

**Singling Out risk** represents the possibility of still being able to identify a particular individual, their part, or complete records, even after any Privacy-Enhancing Techniques have been applied. In the example from the `Anonymeter`, it refers to the scenario where "there is only one person with attributes X, Y, and Z". In other words, attackers may attempt to identify specific individuals.

In the example provided by `Anonymeter`, there is exactly one individual in the original dataset with the attributes: `gender`: male, `age`: 65, `ZIP code`: 30305, and `the number of heart attacks`: 4, and this individual can **be singled out**.

The paper on `Anonymeter` specifically mentions: "It's important to note that singling out does not imply re-identification. Yet the ability to isolate an
individual is often enough to exert control on that individual, or to
mount other privacy attacks."

Currently, only single variable mode Singling Out evaluating (`univariate`) are implemented. In future updates, multi variables mode (`multivariate`) will be included to support singling out attacks by multiple attributes combination.

**指認性風險**表示即便經過隱私強化技術處理，仍有多大的可能性去識別出來**特定個體**，其部分或完整記錄的可能性。以 `Anonymeter` 的舉例，就是「只有一個人同時擁有著 X、Y、與 Z 特徵」。換句話說，攻擊者可以嘗試辨識出特定的個體。

`Anonymeter` 的舉例是，原始資料中，`性別`為男性、`年齡`65歲、`郵遞區號`是30305、`心臟病發次數`為4次的個體恰好只有一個，便能**被指認**出來。

`Anonymeter` 的論文有特別提到：「值得注意的是，指認不等於重新識別。然而，能夠單獨辨識一個體通常足以對該個體施加控制，或者進行其他隱私攻擊。」

目前僅實作單變數指認性驗測 (`univariate`)，未來更新將納入指認性驗測的多變數模式 (`multivariate`)，支援結合多種屬性的指認攻擊。

---

### n_cols

`n_cols` (`int`): Number of attributes used in the attacker queries 攻擊中所使用的屬性數量

Only applicable to multi-variable mode (`multivariate`), not implemented

僅適用於多變數模式 (`multivariate`)，未實作。

---

## evaluating_method='anonymeter-linkability'

**Linkability risk** represents the possibility that, even after Privacy-Enhancing Techniques have been applied, or when records exist in different databases, at least two records about the same individual or group of individuals can still be **linked** together. In the example from the `Anonymeter`, it refers to the scenario where "records A and B belong to the same person". In particular, even if attackers **cannot single out** the specific individual's identity, they may still attempt to establish links between records through shared features or information.

**連結性風險**表示即使經過隱私強化技術處理、或是存在不同的資料庫中，仍有多大的可能，將至少兩條關於同一個人或一組人的記錄**連結**在一起。以 `Anonymeter` 的舉例，就是「紀錄 A 與紀錄 B 屬於同一個人」。具體來說，即使攻擊者**無法指認**具體的個體身份，他們仍可能嘗試透過某些共同特徵或資訊，來建立記錄之間的關聯。

---

### aux_cols

`aux_cols` (`Tuple[List[str], List[str]]`) Columns of auxiliary information 輔助資訊欄位

The pattern of Linkability attacks assumes that attackers, whether malicious or honest-but-curious users, can obtain some of the data columns. They use this information to infer the linkability of the other confidential and unreleased data columns. In this context, the auxiliary data columns `aux_cols` are the data columns included in each of these two sets of data.

For example, if we will public tax records at a village level, the released data may only include annual income, tax amount, and tax deductions, while the unreleased data may contain names, gender, and addresses. In this case, `aux_cols` may look like this:

連結性攻擊的攻擊樣態，是假定攻擊者，無論惡意還是誠實但好奇的使用者，能夠取得其中一部分資料欄位，依此推斷出與另一部分保密的、未釋出的資料欄位的連結性。此時輔助資料欄位 `aux_cols` 便是這兩批資料所各自包含的資料欄位。

舉例來說，某個村里層級的個人繳稅紀錄要做公開資料應用，那釋出的資料可能僅包含了年收入、所得稅額、稅務抵免，未釋出的資料則可能包含了姓名、性別、地址。那 `aux_cols` 便如下所示：

```python
aux_cols = [
    ['annual_income', 'tax_amount', 'tax_deduction_amount'], # public
    [ 'name', 'gender', 'address'] # private
]
```

The potential linkability attack method could be something like, "Since we know the name of the richest person and that they live in this village, we can deduce that the person with the highest annual income in the released data is the tax record of the richest individual."

`aux_cols` involves domain-specific knowledge about the dataset, so neither `PETsARD` nor `Anonymeter` provide default values for it. Users need to configure it themselves based on their understanding of the dataset. In future updates, following the experimental approach outlined in the `Anonymeter` paper, different amounts of auxiliary information will be considered. The attacker's auxiliary information will be sampled from "only two columns" to "the maximum number of columns in the dataset," and these options will be provided as default values.

而此時潛在的連結性攻擊方式，便可能是『由於知道首富姓名、且知道首富居住在這個村里，則知道釋出資料中年收入最高的便是首富繳稅紀錄』。

`aux_cols` 涉及對資料集的專業知識，故 `PETsARD`  跟 `Anonymeter` 均不設預設值，須由使用者自行設定。在未來更新中，也將依照 `Anonymeter` 論文的實驗方式，考量不同數量的輔助資訊，將攻擊者的輔助資訊從『僅有兩列』到『資料集的最大列數』所有抽樣方式都遍歷考慮一次，提供這樣的預設值。

---

### n_neighbors

`n_neighbors` (`int`, default=10): Number of neighbors considered for the link search 連結搜索時考慮的鄰居數量

To handle mixed data types, `Anonymeter` uses Gower's Distance/Similarity:

- Numeric  variables: Gower's Distance is the absolute difference between the normalized values.
- Categorical variables: Gower's Distance is 1 if the values are not equal.

After combining all attributes, the Manhattan Distance is calculated, and return the nearest N neighbors. So, in the context of `Linkability risk`, `n_neighbors` represents how close the two sets of data from the same person need to be linked to be considered a successful linkability attack.

`Anonymeter` does not provide a recommended value for `n_neighbors`. In the example, a value of 10 is used, but the default value in the code is 1. `PETsARD` uses 10 as the default value.

為了處理混合資料類型的資料，`Anonymeter` 使用的是高爾距離/高爾相似性：

- 數值型變數：高爾距離為歸一化後兩者相差的絕對值
- 類別型變數：只要不相等，高爾距離即為 1

綜合所有屬性之後計算其曼哈頓距離，最後返回最近的 N 個鄰居。於是 `n_neighbors` 在 `連結性風險` 上的意思，是指同一個人的兩批資料，要在多近的距離內被連結到，才算是連結性攻擊成功。

`Anonymeter` 並沒有給出 `n_neighbors` 的建議值，在範例中使用 10、但在程式裡預設值是 1，`PETsARD` 使用 10 作為預設值。

---

## evaluating_method='anonymeter-inference'

**Inference risk** represents the possibility that, even after Privacy-Enhancing Techniques have been applied, there is still a significant chance of deducing the value of an attribute from the values of a set of other attributes. In the example from the `Anonymeter`, it refers to the scenario where "a person with attributes X and Y also have Z". To phrase it differently, even if attackers **cannot single out** individual identities or **cannot link** different records, they may still be able to deduce specific information via statistical analysis or other methods.

An example provided by `Anonymeter`  is that when in the original data, the `gender` is male, the `age` is 65, and the `ZIP code` is 30305, the attacker can easily **infer** that the secret attribute `number of heart attacks` is 4.

**推斷性風險**代表的是即使經過隱私強化技術處理，仍有多大的可能，從一組其他的特徵中推斷出某個特徵的值。以 `Anonymeter` 的舉例，就是「擁有特徵 X 和特徵 Y 的人也擁有特徵 Z」。也就是說，即使攻擊者**無法指認**個體身分、也無法**連結**不同紀錄，攻擊者仍可以透過統計分析或其他方法來推斷出特定的資訊。

`Anonymeter` 的舉例是，當原始資料中，`性別`為男性、`年齡`65歲、且`郵遞區號`是30305，則攻擊者很容易就能**推斷**出秘密屬性`心臟病發次數`為4次。

---

### secret and aux_cols

`secret` (`str`) Column(s) of secret information 秘密資訊欄位

`aux_cols` (`List[str]`) Columns of auxiliary information 輔助資訊欄位

In the context of Inference risk, the parameters `secret` and `aux_cols` go hand in hand. `secret` represents the attribute that is kept confidential, and in this scenario, `aux_cols` are the attributes other than secret that are considered to provide auxiliary information to the attacker.

The example provided by `Anonymeter` suggests the following configuration:

在推斷性風險中，`secret` 與 `aux_cols` 參數是一體兩面的，secret 代表被保密的屬性 (attribute)，此時 `aux_cols` 則是除了 `secret` 以外的屬性、都被認為可以提供攻擊者輔助資訊。

`Anonymeter` 的範例建議了以下的設定方法：

```python
columns = ori.columns

for secret in columns:
    aux_cols = [col for col in columns if col != secret]
    evaluator = InferenceEvaluator(
        aux_cols=aux_cols,
        secret=secret,
        ...
    )
```

This approach allows us to iterate through each column considered as a `secret`. And following the method outlined in the `Anonymeter` paper, averaging all the risk results for the `secret` attributes results in the dataset's overall inference risk (not detailed in the paper, but calculated as the arithmetic mean by `PETsARD`).

Currently, both `secret` and `aux_cols` have no default values, and it is recommended for users to manually set `aux_cols` as all attributes except for the `secret`. In future updates, following the experimental approach outlined in the `Anonymeter` paper, the attacker's auxiliary information will be considered in a range from "only one column other than secret" to "all columns other than secret," and these options will be provided as default values.

這樣能遍歷每個欄位被視作 `secret`。然後參考 `Anonymeter` 論文的方法，對所有 `secret` 的風險結果取平均、則為資料集整體的 **推論性風險**（論文中沒詳細描述，但 `PETsARD` 使用算術平均）。

目前 `secret` 跟 `aux_cols` 都沒有預設值，建議使用者手動設定為 `aux_cols` 統一為 `secret` 以外的所有屬性。在未來更新中，將依照 `Anonymeter` 論文的實驗方式，將攻擊者的輔助資訊從『除 `secret` 以外僅有一列』到『除 `secret` 以外所有列』所有抽樣方式都遍歷考慮一次，提供這樣的預設值。

## Refenece

For explanations of the library in this paper and translations of terminologies between Chinese and English, please refer to the following references:

本文之函式庫解釋與中英用詞翻譯，請參閱以下文獻：

- Giomi, M., Boenisch, F., Wehmeyer, C., & Tasnádi, B. (2023). A Unified Framework for Quantifying Privacy Risk in Synthetic Data. *Proceedings of Privacy Enhancing Technologies Symposium*, 2023(2), 312–328. https://doi.org/10.56553/popets-2023-0055
- 蔡柏毅（2021）。淺談個資「去識別化」與「合理利用」間的平衡。《金融聯合徵信》，第三十九期，2021年12月。
