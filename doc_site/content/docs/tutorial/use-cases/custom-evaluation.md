---
title: Custom Evaluation
type: docs
weight: 34
prev: docs/tutorial/use-cases/ml-utility
next: docs/tutorial/use-cases/benchmark-datasets
---


Besides built-in evaluation methods, you can create your own evaluation methods. This is particularly useful when you have specific evaluation needs.

Click the below button to run this example in Colab:

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

## Creating Custom Evaluator

When implementing custom evaluations, you can freely choose whether to inherit from `BaseEvaluator` or not, but the integration of your evaluation program with `PETsARD` primarily relies on these two essential constants:

`self.REQUIRED_INPUT_KEYS` (list[str]): Defines the dictionary keys required in the input data. Standard keys include `ori` (original data), `syn` (synthetic data), and `control` (control data). Whether you provide the control parameter determines if your custom evaluation can be performed without a data splitting process.
`self.AVAILABLE_SCORES_GRANULARITY` (`list[str]`): Defines the granularity options for evaluation results. Available options include `global` (global evaluation), `columnwise` (column-by-column evaluation), `pairwise` (column pair evaluation), and `details` (custom detailed evaluation).

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

## Required Methods

For your own evaluator, you only need to implement one `eval()` method that returns a dictionary containing evaluation results at different granularity levels. The keys of this dictionary must match those defined in `AVAILABLE_SCORES_GRANULARITY`, and each value must be a `pd.DataFrame` that conforms to a specific format.

### Format Requirements for Dictionary Key-Value Pairs

1. `global`：Global Evaluation Results

    - A single-row DataFrame showing overall scores or evaluation summary

2. `columnwise`：Column-level Results

    -  A DataFrame with one row per original data column, using column names as indices

3. `pairwise`：Column-pair Results

    - A DataFrame with one row per column pair, using a MultiIndex to represent column pairs

4. `details`: Custom Details

    - A DataFrame in a custom format that can contain any type of detailed evaluation information
