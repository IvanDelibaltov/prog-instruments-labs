import hashlib
import json
from typing import List

"""
В этом модуле обитают функции, необходимые для автоматизированной проверки результатов ваших трудов.
"""


def calculate_checksum(row_numbers: List[int]) -> str:
    """Вычисляет MD5 хеш отсортированного списка чисел."""
    sorted_numbers = sorted(row_numbers)  # Исправлено: не изменяем исходный список
    return hashlib.md5(json.dumps(sorted_numbers).encode('utf-8')).hexdigest()


def serialize_result(variant: int, checksum: str) -> None:
    """Сохраняет результат в JSON файл."""
    result_data = {
        "variant": variant,
        "checksum": checksum
    }

    try:
        with open("result.json", "w", encoding="utf-8") as file:
            json.dump(result_data, file, ensure_ascii=False, indent=2)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Файл не найден: {e}")
    except Exception as e:
        raise Exception(f"Неизвестная ошибка: {e}")


if __name__ == "__main__":
    print(calculate_checksum([1, 2, 3]))
    print(calculate_checksum([3, 2, 1]))