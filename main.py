# ... внутри main() после чтения file2_paths ...

# Пример маппинга: имя файла -> кафедра (можно вынести в config.py)
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
# ... далее вызов compare_data(file1_df, file2_records) ...