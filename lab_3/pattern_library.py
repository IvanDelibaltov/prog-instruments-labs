import re
import calendar
from datetime import datetime
from typing import Dict, List
from pandas import DataFrame
import pandas as pd  # Добавляем импорт


def is_valid_date(date_str: str) -> bool:
    """Проверяет корректность даты (учитывая месяцы и високосные годы)."""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')

        # Проверяем, что день соответствует месяцу
        year, month, day = map(int, date_str.split('-'))

        # Проверяем существующий день в месяце
        last_day = calendar.monthrange(year, month)[1]
        return 1 <= day <= last_day

    except ValueError:
        return False
    except Exception:
        return False


def validate_by_pattern(data: str, pattern: str, column_name: str = None) -> bool:
    """Проверяет строку на соответствие регулярному выражению."""
    # Проверка на NaN (используем pd.isna)
    if isinstance(data, float) and pd.isna(data):
        return False
    if data is None:
        return False

    # Преобразуем в строку
    str_data = str(data).strip()

    # Особый случай для дат
    if column_name == "date":
        return is_valid_date(str_data)

    try:
        return bool(re.fullmatch(pattern, str_data))
    except re.error:
        return False


def find_error_rows(df: DataFrame, patterns_dict: Dict[str, str]) -> List[int]:
    """Находит номера строк с ошибками по всем колонкам."""
    error_rows = set()

    for column_name, pattern in patterns_dict.items():
        if column_name in df.columns:
            column_errors = 0
            for row_index, value in df[column_name].items():
                if not validate_by_pattern(value, pattern, column_name):
                    error_rows.add(row_index)
                    column_errors += 1

            print(f"Колонка '{column_name}': найдено {column_errors} ошибок")

    return sorted(list(error_rows))