import pandas as pd
import re


def clean_name(name: str) -> str:
    """Убирает ID в скобках и лишние пробелы"""
    if pd.isna(name):
        return ""
    return re.sub(r'\s*\(\d+\)', '', str(name).strip())


def parse_file1(file_path: str = None) -> pd.DataFrame:
    if file_path is None:
        from config import FILE1_PATH
        file_path = FILE1_PATH

    # 1. Читаем "сырой" файл без шапки
    df_raw = pd.read_excel(file_path, header=None)

    # 2. Динамический поиск строки заголовка
    header_idx = None
    for i, row in df_raw.iterrows():
        if any('Преподаватель' in str(cell) for cell in row.dropna()):
            header_idx = i
            break

    if header_idx is None:
        raise ValueError("❌ Не найдена строка заголовка 'Преподаватель'.")

    print(f"✅ Заголовок найден в строке (0-index): {header_idx}")

    # 3. Восстанавливаем объединённые ячейки шапки
    header_block = df_raw.iloc[header_idx:header_idx + 4].reset_index(drop=True).ffill(axis=0)
    col_names = header_block.iloc[-1].astype(str).str.strip().tolist()

    # Читаем данные со строки после найденного заголовка
    df = df_raw.iloc[header_idx + 1:].copy()
    df.columns = col_names

    # 4. Ищем индексы базовых колонок
    def get_col_index(keyword):
        for i, name in enumerate(df.columns):
            if keyword in str(name):
                return i
        return None

    idx_fio = get_col_index('Преподаватель')
    idx_dep = get_col_index('Кафедра')
    idx_position = get_col_index('Должность')

    if idx_fio is None or idx_dep is None:
        raise ValueError("❌ Не найдены индексы колонок ФИО или Кафедра")

    # 5. Формируем базовый DataFrame
    df_clean = df.iloc[:, [idx_fio, idx_dep]].copy()
    df_clean.columns = ['Преподаватель', 'Кафедра']

    if idx_position is not None:
        df_clean['Должность'] = df.iloc[:, idx_position].copy()
    else:
        df_clean['Должность'] = 'Не указана'

    # 6. Извлекаем 8 детализированных колонок по ЖЁСТКИМ индексам (8-15)
    # 8: часов, план (Учебная), 9: 1 Неконтактная, ..., 15: 7 Поруч.отв
    detail_mapping = {
        'План_Учебная': 8,
        'План_Неконтактная': 9,
        'План_Метод': 10,
        'План_Электр': 11,
        'План_Научная': 12,
        'План_Орг': 13,
        'План_Повыш': 14,
        'План_Поручения': 15
    }

    for col_name, idx in detail_mapping.items():
        if idx < len(df.columns):
            df_clean[col_name] = pd.to_numeric(df.iloc[:, idx], errors='coerce').fillna(0)
        else:
            df_clean[col_name] = 0.0

    # 7. Очистка и фильтрация пустых строк
    df_clean = df_clean[df_clean['Преподаватель'].astype(str).str.strip() != '']
    df_clean['Кафедра'] = df_clean['Кафедра'].astype(str).str.strip()
    df_clean['Должность'] = df_clean['Должность'].astype(str).str.strip()

    # 8. Агрегация СТРОГО по составному ключу: ФИ + Кафедра + Должность
    df_clean['ФИ'] = df_clean['Преподаватель'].apply(clean_name)

    detail_cols = list(detail_mapping.keys())
    agg = df_clean.groupby(['ФИ', 'Кафедра', 'Должность'], as_index=False)[detail_cols].sum()

    # 9. КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Считаем общий план как сумму детализированных полей.
    # Это исключает ошибки парсинга общей ячейки "План" и гарантирует математическую точность.
    agg['План_ИС_ВВГУ'] = agg[detail_cols].sum(axis=1)

    return agg