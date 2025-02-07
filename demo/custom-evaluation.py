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
