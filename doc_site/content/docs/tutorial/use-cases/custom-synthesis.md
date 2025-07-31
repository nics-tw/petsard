---
title: Custom Synthesis
type: docs
weight: 31
prev: docs/tutorial/use-cases/comparing-synthesizers
next: docs/tutorial/use-cases/data-constraining
---


Besides built-in synthesis methods, you can create your own synthesis methods. This is particularly useful when you have specific synthesis needs.

Click the below button to run this example in Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nics-tw/petsard/blob/main/demo/use-cases/custom-synthesis.ipynb)

```yaml
---
Loader:
  data:
    filepath: 'benchmark://adult-income'
Preprocessor:
  demo:
    method: 'default'
Synthesizer:
  custom:
    method: 'custom_method'
    module_path: 'custom-synthesis.py'  # Path to your custom synthesizer
    class_name: 'MySynthesizer_Shuffle'  # Synthesizer class name
Postprocessor:
  demo:
    method: 'default'
Evaluator:
  demo:
    method: 'default'
Reporter:
  save_report_global:
    method: 'save_report'
    granularity: 'global'
...
```

## Creating Custom Synthesizer

Create a synthesizer class that implements the required methods:

```python
import numpy as np
import pandas as pd

from petsard.metadater import SchemaMetadata


class MySynthesizer_Shuffle:
    """
    A simple synthesizer that shuffles each column independently.

    This synthesizer preserves the distribution of each column while breaking
    the relationships between columns. It can be useful for simple anonymization
    or as a baseline synthetic data generation method.
    """

    def __init__(self, config: dict, metadata: SchemaMetadata):
        """
        Initialize the synthesizer.

        In this demo we don't use metadata, but please keep it in the signature,
        and feel free to prepare your synthesizer to use it.

        Args:
            metadata (SchemaMetadata): The metadata object.
        """
        self.config: dict = config
        self.result: pd.DataFrame = None

        if "random_seed" in self.config:
            np.random.seed(self.config["random_seed"])

    def fit(self, data: pd.DataFrame) -> None:
        """
        Shuffle Algorithm
        """
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Data must be a pandas DataFrame")

        if data.empty:
            raise ValueError("Cannot fit on empty data")

        columns: list[str] = data.columns.tolist()
        synthetic_data: pd.DataFrame = pd.DataFrame()

        values: np.ndarray = None
        for col in columns:
            # Get the column data and handle different types appropriately
            original_series: pd.Series = data[col]

            if pd.api.types.is_categorical_dtype(original_series):
                # For categorical data, convert to codes, shuffle, then map back
                codes = original_series.cat.codes.values.copy()
                np.random.shuffle(codes)
                # Convert shuffled codes back to categorical values
                synthetic_data[col] = pd.Categorical.from_codes(
                    codes,
                    categories=original_series.cat.categories,
                    ordered=original_series.cat.ordered,
                )
            else:
                # For non-categorical data, create a copy of values and shuffle
                values = original_series.values.copy()
                np.random.shuffle(values)
                synthetic_data[col] = values

        self.result = synthetic_data

    def sample(self) -> pd.DataFrame:
        return self.result
```

## Required Methods

Your synthesizer class must implement all of the following methods:

1. `__init__(config: dict, metadata: SchemaMetadata)`：Initialize the synthesizer

    - Takes configuration dictionary and metadata object
    - Sets up any necessary parameters or internal state

2. `fit(data: pd.DataFrame)`：Train the synthesizer on input data

    - Processes input data and prepares for synthesis
    - Learns patterns, distributions, or relationships

3. `sample()`：Generate synthetic data

    - Returns a pandas DataFrame with synthetic data
    - Should maintain the same structure as the original data

All three methods must be implemented for the custom synthesizer to work correctly with PETsARD. The synthesizer is expected to produce synthetic data that maintains the structure of the original data while applying your custom synthesis algorithm.
