---
title: Custom Evaluation
type: docs
weight: 20
prev: docs/tutorial/special-cases/benchmark-datasets
sidebar:
  open: true
---


Besides built-in evaluation methods, you can create your own evaluation methods. This is particularly useful when you have specific evaluation needs.

Click the below button to run this example in Colab:

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

## Creating Custom Evaluator

Create an evaluator class inheriting from `EvaluatorBase`:

```python
import pandas as pd

from petsard.evaluator.evaluator_base import EvaluatorBase


class MyEvaluator(EvaluatorBase):
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

## Required Methods

Your evaluator class must implement all of the following methods:

  1. `get_global()`：Returns overall evaluation results

    - One row showing overall scores

  2. `get_columnwise()`：Returns per-column evaluation results

    - One row per column
    - Uses original column names as index

  3. `get_pairwise()`：Returns column relationship evaluation results

    - One row per column pair
    - Uses column pairs as index

All three methods must be implemented to ensure evaluation results can be presented at different granularities. Each method should return a DataFrame containing your evaluation metrics.