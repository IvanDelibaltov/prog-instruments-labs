from checksum import calculate_checksum, serialize_result
from file_manager import read_csv, read_json
from pattern_library import find_error_rows


def main():
    try:
        # Читаем настройки
        settings = read_json('settings.json')

        # Читаем данные
        df = read_csv(settings['data'])
        print(f"Всего строк в CSV: {len(df)}")
        print()

        # Читаем паттерны
        patterns_dict = read_json(settings['patterns'])

        # Находим строки с ошибками
        print("Поиск строк с ошибками...")
        error_rows = find_error_rows(df, patterns_dict)
        print(f"\nВсего строк с ошибками: {len(error_rows)}")

        # Покажем только первые 5 ошибок для примера
        if error_rows and len(error_rows) > 0:
            print(f"Первые 5 ошибочных строк: {error_rows[:5]}")

        # Вычисляем контрольную сумму
        checksum = calculate_checksum(error_rows)
        print(f"\nКонтрольная сумма: {checksum}")
        print(f"Ожидаемая сумма: 9165dfabdf1a692ca00fec953a587722")
        print(f"Совпадает: {'ДА' if checksum == '9165dfabdf1a692ca00fec953a587722' else 'НЕТ'}")

        # Сохраняем результат
        serialize_result(int(settings['var']), checksum)
        print(f"Результат сохранен в result.json")

    except FileNotFoundError as e:
        print(f"Ошибка: Файл не найден: {e}")
    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()