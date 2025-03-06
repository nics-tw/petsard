from enum import Enum, auto

ALLOWED_COLUMN_TYPES: list = ["category", "datetime"]

OPTIMIZED_DTYPES: dict = {
    "category": "category",
    "datetime": "datetime64[s]",
    "int": "int64",
    "float": "float64",
}


class EvaluationScoreGranularityMap(Enum):
    """
    Mapping of the granularity of evaluation score.
    """

    GLOBAL: int = auto()
    COLUMNWISE: int = auto()
    PAIRWISE: int = auto()

    @classmethod
    def map(cls, granularity: str) -> int:
        """
        Get suffixes mapping int value

        Args:
            granularity (str): The granularity of evaluator score.

        Return:
            (int): The method code.
        """
        return cls.__dict__[granularity.upper()]
