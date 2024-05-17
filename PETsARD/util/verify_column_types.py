from typing import Dict

from PETsARD.util.params import ALLOWED_COLUMN_TYPES


def verify_column_types(column_types: Dict[str, list] = None) -> bool:
    """
    Verify the column types setting is valid or not.

    Args:
        column_types (dict):
            The dictionary of column names and their types.
            Format as {type: [colname]}
            Only below types are supported (case-insensitive):
            - 'category': The column will be treated as categorical.
            - 'datetime': The column will be treated as datetime.
    """
    return all(
        coltype.lower() in ALLOWED_COLUMN_TYPES
        for coltype in column_types.keys()
    )