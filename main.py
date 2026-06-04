import os
import glob
import pandas as pd
from config import FILE2_DIR, FILE3_PATH, FILE4_PATH
from parsers.file1_parser import parse_file1
from parsers.file2_parser import parse_file2
from core.comparator import compare_data
from exporters.file4_exporter import export_file4

def main():
    print("🚀 Запуск процедуры сравнения нагрузки ППС ВВГУ...")
    os.makedirs(os.path.dirname(FILE3_PATH), exist_ok=True)

    # 1. Формируем Файл 3
    print("📖 Шаг 1: Чтение и агрегация Файла 1 (ИС ВВГУ)...")
    file1_df = parse_file1()
    file1_df.to_excel(FILE3_PATH, index=False)
    print(f"   ✅ Файл 3 сохранён: {FILE3_PATH}")

    # 2. Читаем все Файлы 2
    print("📂 Шаг 2: Поиск и парсинг индивидуальных планов (Файлы 2)...")
    os.makedirs(FILE2_DIR, exist_ok=True)
    file2_paths = glob.glob(os.path.join(FILE2_DIR, "*.xlsx"))
    if not file2_paths:
        print("   ⚠️ В папке input_files не найдено Excel-файлов. Поместите туда Файлы 2.")
        return

    DEPT_MAPPING = {
        "Шумик_КафедраИБ.xlsx": "Кафедра ИБ",
        "Шумик_КафедраПО.xlsx": "Кафедра ПО",
        # Добавьте остальные файлы
    }

    file2_records = []
    for path in file2_paths:
        filename = os.path.basename(path)
        # Берём кафедру из маппинга или пытаемся автоопределить
        dept = DEPT_MAPPING.get(filename)

        rec = parse_file2(path, department_override=dept)
        if rec:
            file2_records.append(rec)

    print(f"   ✅ Обработано планов: {len(file2_records)}")

    # 3. Сравнение
    print("⚖️ Шаг 3: Сравнение нагрузок и расчёт разницы...")
    result_df = compare_data(file1_df, file2_records)

    # 4. Экспорт в Файл 4
    print("💾 Шаг 4: Формирование Файла 4 с подсветкой расхождений...")
    export_file4(result_df)
    print(f"   ✅ Готово! Результат: {FILE4_PATH}")

    # Итоговая статистика
    mismatches = result_df[result_df['Статус'].str.contains('Расхождение|Отсутствует', na=False)].shape[0]
    print(f"\n📊 ОТЧЁТ: Всего проверено {len(result_df)} ППС. Требуют внимания: {mismatches}")

if __name__ == "__main__":
    main()