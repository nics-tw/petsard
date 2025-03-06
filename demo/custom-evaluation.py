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
