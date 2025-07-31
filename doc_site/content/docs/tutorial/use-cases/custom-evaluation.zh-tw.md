---
title: 自定義評測
type: docs
weight: 34
prev: docs/tutorial/use-cases/ml-utility
next: docs/tutorial/use-cases/benchmark-datasets
---


除了使用內建的評測方法外，您也可以建立自己的評測方法。這在您有特定的評估需求時特別有用。

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/use-cases/custom-evaluation.ipynb)

```yaml
---
Loader:
  data:
    filepath: 'benchmark/adult-income.csv'
Splitter:
  demo:
    num_samples: 1
    train_split_ratio: 0.8
Preprocessor:
  demo:
    method: 'default'
Synthesizer:
  demo:
    method: 'default'
Postprocessor:
  demo:
    method: 'default'
Evaluator:
  custom:
    method: 'custom_method'
    module_path: 'custom-evaluation.py'  # Path to your custom synthesizer
    class_name: 'MyEvaluator_Pushover'  # Synthesizer class name
Reporter:
  save_report_global:
    method: 'save_report'
    granularity: 'global'
  save_report_columnwise:
    method: 'save_report'
    granularity: 'columnwise'
  save_report_pairwise:
    method: 'save_report'
    granularity: 'pairwise'
...
```

## 建立自定義評測

實現自訂評測時，你可以自由選擇是否要繼承 `BaseEvaluator`，但評測程式跟 `PETsARD` 的整合主要基於以下兩個關鍵常數：

- `self.REQUIRED_INPUT_KEYS` (`list[str]`)：定義輸入資料必須包含的字典鍵值。標準鍵值包含 `ori`（原始資料）、`syn`（合成資料）和 `control`（控制資料）。提供 `control` 參數與否決定了您的自訂評測是否能在不進行資料分割的情況下進行評估。
- `self.AVAILABLE_SCORES_GRANULARITY` (`list[str]`)：定義評估結果的顆粒度選項。可選值包括 `global`（全域評測）、`columnwise`（逐欄位評測）、`pairwise`（逐欄位對評測）以及 `details`（自訂細節評測）。

```python
import pandas as pd


class MyEvaluator_Pushover:
    REQUIRED_INPUT_KEYS: list[str] = ["ori", "syn", "control"]
    AVAILABLE_SCORES_GRANULARITY: list[str] = [
        "global",
        "columnwise",
        "pairwise",
        "details",
    ]

    def __init__(self, config: dict):
        """
        Args:
            config (dict): The configuration assign by Synthesizer
        """
        self.config: dict = config

    def eval(self, data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        # Implement your evaluation logic
        eval_result: dict[str, int] = {"score": 100}
        colnames: list[str] = data["ori"].columns
        pairs: list[tuple[str, str]] = [
            (col1, col2)
            for i, col1 in enumerate(colnames)
            for j, col2 in enumerate(colnames)
            if j <= i
        ]
        lorem_text: str = (
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
            "sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
            "Ut enim ad minim veniam, "
            "quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. "
            "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. "
            "Excepteur sint occaecat cupidatat non proident, "
            "sunt in culpa qui officia deserunt mollit anim id est laborum."
        )

        return {
            # Return overall evaluation results
            "global": pd.DataFrame(eval_result, index=["result"]),
            # Return per-column evaluation results. Must contains all column names
            "columnwise": pd.DataFrame(eval_result, index=colnames),
            # Return column relationship evaluation results. Must contains all column pairs
            "pairwise": pd.DataFrame(
                eval_result, index=pd.MultiIndex.from_tuples(pairs)
            ),
            # Return detailed evaluation results, not specified the format
            "details": pd.DataFrame({"lorem_text": lorem_text.split(". ")}),
        }
```

## 必要實作方法

您的評測類別需要實作一個 `eval()` 方法，該方法返回一個字典，其中包含不同顆粒度的評估結果。該字典的鍵必須與 `AVAILABLE_SCORES_GRANULARITY` 中定義的一致，而每個值都必須是符合特定格式的 `pandas.DataFrame`。主要如下：

### 字典鍵值對應的格式要求

1. `global`：全域評估結果

    - 單行的 DataFrame，顯示整體評分或評估摘要

2. `columnwise`：欄位級評估結果

    - 每個原始資料欄位一行的 DataFrame，使用欄位名稱作為索引

3. `pairwise`：欄位對評估結果

    - 每對欄位組合一行的 DataFrame，使用 `MultiIndex` 表示欄位對

4. `details`：自定義細節

    - 自定義格式的 DataFrame，可包含任何類型的詳細評估資訊
