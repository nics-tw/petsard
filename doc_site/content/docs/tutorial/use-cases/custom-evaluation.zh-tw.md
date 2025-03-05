---
title: 自定義評測
type: docs
weight: 33
prev: docs/tutorial/use-cases/data-constraining
next: docs/tutorial/use-cases/benchmark-datasets
---


除了使用內建的評測方法外，您也可以建立自己的評測方法。這在您有特定的評估需求時特別有用。

請點擊下方按鈕在 Colab 中執行範例：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/custom-evaluation.ipynb)

```yaml
---
Loader:
  data:
    filepath: 'benchmark/adult-income.csv'
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
    custom_method:
      filepath: 'custom-evaluation.py'  # Path to your custom evaluator
      method: 'MyEvaluator'        # Evaluator class name
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

建立評測類別，繼承 `BaseEvaluator`：

```python
import pandas as pd

from petsard.evaluator.evaluator_base import BaseEvaluator


class MyEvaluator(BaseEvaluator):
    def __init__(self, config: dict):
        super().__init__(config=config)
        self.result = None
        self.columns = None

    def _create(self, data: dict) -> None:
        # Get column names for columnwise and pairwise analysis
        self.columns = data["ori"].columns

    def eval(self) -> None:
        # Implement your evaluation logic
        self.result = {"score": 100}

    def get_global(self) -> pd.DataFrame:
        # Return overall evaluation results
        return pd.DataFrame(self.result, index=["result"])

    def get_columnwise(self) -> pd.DataFrame:
        # Return per-column evaluation results
        # Must use original column names
        return pd.DataFrame(self.result, index=self.columns)

    def get_pairwise(self) -> pd.DataFrame:
        # Return column relationship evaluation results
        # Generate all possible column pairs
        pairs = [
            (col1, col2)
            for i, col1 in enumerate(self.columns)
            for j, col2 in enumerate(self.columns)
            if j <= i
        ]
        return pd.DataFrame(self.result, index=pd.MultiIndex.from_tuples(pairs))
```

## 必要實作方法

您的評測類別必須實作以下所有方法：

1. `get_global()`：回傳整體評估結果

    - 一列資料顯示整體評分

2. `get_columnwise()`：回傳各欄位的評估結果

    - 每個欄位一列資料
    - 使用原始資料的欄位名稱作為索引

3. `get_pairwise()`：回傳欄位間關係的評估結果

    - 每對欄位組合一列資料
    - 使用欄位配對作為索引

這三個方法都必須實作，以確保評測結果能在不同的顆粒度下呈現。每個方法都應該回傳一個包含您評測指標的 DataFrame。