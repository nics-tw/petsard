ALLOWED_COLUMN_TYPES: list = ["category", "datetime"]

OPTIMIZED_DTYPES: dict = {
    "category": "category",
    "datetime": "datetime64[s]",
    "int": "int64",
    "float": "float64",
}
