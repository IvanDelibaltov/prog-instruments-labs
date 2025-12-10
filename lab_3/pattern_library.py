import re

from typing import Dict, List
from pandas import DataFrame


def validate_by_pattern(data: str, pattern: str) -> bool:

    if data is None or data != data:
        return False

    try:
        if re.fullmatch(pattern, str(data)):
            return True
        return False
    except re.error:
        return False


def find_error_rows(df: DataFrame, patterns_dict: Dict[str, str]) -> List[int]:

    error_rows = set()

    for column_name, pattern in patterns_dict.items():
        if column_name in df.columns:
            for row_index, value in df[column_name].items():
                if not validate_by_pattern(value, pattern):
                    error_rows.add(row_index)

    return sorted(list(error_rows))