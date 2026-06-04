import os
import glob
import pandas as pd
from config import FILE1_PATH, FILE2_DIR, OUTPUT_DIR

from parsers.file1_parser import parse_file1
from parsers.file2_parser import parse_file2
from core.comparator import compare_data
from exporters.file4_exporter import export_file4


def run_pipeline(file1_path: str, dir2_path: str, output_dir: str):
    """
    Основная логика обработки. Принимает пути из GUI.
    Возвращает кортеж (result_df, file4_path) или (None, None) при ошибке.
    """
    print("🚀 Запуск процедуры сравнения нагрузки ППС ВВГУ...")
    os.makedirs(output_dir, exist_ok=True)

    # Формируем пути сохранения внутри выбранной папки
    file3_path = os.path.join(output_dir, "Файл 3_Агрегированный.xlsx")
    file4_path = os.path.join(output_dir, "Файл 4_Сравнение.xlsx")

    # === Шаг 1: Чтение Файла 1 ===
    print("📖 Шаг 1: Чтение и агрегация Файла 1 (ИС ВВГУ)...")
    file1_df = parse_file1(file1_path)  # ← передаём путь
    file1_df.to_excel(file3_path, index=False)
    print(f"   ✅ Файл 3 сохранён: {file3_path}")

    # === Шаг 2: Чтение Файлов 2 ===
    print("📂 Шаг 2: Поиск и парсинг индивидуальных планов (Файлы 2)...")
    file2_paths = glob.glob(os.path.join(dir2_path, "*.xlsx"))
    if not file2_paths:
        print("   ⚠️ В выбранной папке не найдено Excel-файлов.")
        return None, None

    file2_records = []
    for path in file2_paths:
        rec = parse_file2(path)
        if rec:
            file2_records.append(rec)
    print(f"   ✅ Обработано планов: {len(file2_records)}")

    # === Шаг 3: Сравнение ===
    print("️ Шаг 3: Сравнение нагрузок и расчёт разницы...")
    result_df = compare_data(file1_df, file2_records)

    # === Шаг 4: Экспорт ===
    print(" Шаг 4: Формирование Файла 4 с подсветкой расхождений...")
    export_file4(result_df, file4_path)  # ← передаём путь
    print(f"   ✅ Готово! Результат: {file4_path}")

    # Итоговая статистика
    mismatches = result_df[result_df['Статус'].str.contains('Расхождение|Отсутствует', na=False)].shape[0]
    print(f"\n ОТЧЁТ: Всего проверено {len(result_df)} ППС. Требуют внимания: {mismatches}")

    return result_df, file4_path


# Точка входа для консольного запуска
if __name__ == "__main__":
    run_pipeline(
        file1_path=FILE1_PATH,
        dir2_path=FILE2_DIR,
        output_dir=OUTPUT_DIR
    )