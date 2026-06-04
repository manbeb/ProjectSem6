import pandas as pd
import re


def clean_name(name: str) -> str:
    """Убирает ID в скобках и лишние пробелы"""
    if pd.isna(name): return ""
    return re.sub(r'\s*\(\d+\)', '', str(name).strip())


def parse_file1(file_path: str = None) -> pd.DataFrame:
    # 1. Читаем "сырой" файл без шапки
    if file_path is None:
        from config import FILE1_PATH
        file_path = FILE1_PATH

    df_raw = pd.read_excel(file_path, header=None)

    # Динамический поиск строки, где есть "Преподаватель"
    header_idx = None
    for i, row in df_raw.iterrows():
        if any('Преподаватель' in str(cell) for cell in row.dropna()):
            header_idx = i
            break

    if header_idx is None:
        raise ValueError("❌ Не найдена строка заголовка 'Преподаватель'.")
    print(f"✅ Заголовок найден в строке (0-index): {header_idx}")

    # 2. Восстанавливаем объединённые ячейки шапки
    header_block = df_raw.iloc[header_idx:header_idx + 4].reset_index(drop=True).ffill(axis=0)
    col_names = header_block.iloc[-1].astype(str).str.strip().tolist()

    # Читаем данные со строки после найденного заголовка
    df = df_raw.iloc[header_idx + 1:].copy()
    df.columns = col_names

    # 🔑 КРИТИЧНОЕ ИСПРАВЛЕНИЕ: Ищем колонки по ИНДЕКСАМ, чтобы обойти дубликаты имён
    def get_col_index(keyword):
        for i, name in enumerate(df.columns):
            if keyword in str(name):
                return i
        return None

    idx_fio = get_col_index('Преподаватель')
    idx_dep = get_col_index('Кафедра')
    idx_plan = get_col_index('План')

    # Fallback для Плана, если не нашли по тексту (обычно одна из последних колонок)
    if idx_plan is None:
        idx_plan = len(df.columns) - 3
        print(f"⚠️ Колонка 'План' не найдена по тексту. Используем позиционный индекс: {idx_plan}")

    if idx_fio is None or idx_dep is None:
        raise ValueError("❌ Не найдены индексы колонок ФИО или Кафедра")

    # Выбираем данные строго по позициям. Теперь у нас ровно 3 колонки с уникальными именами.
    df_clean = df.iloc[:, [idx_fio, idx_dep, idx_plan]].copy()
    df_clean.columns = ['Преподаватель', 'Кафедра', 'План']

    # 3. Очистка и фильтрация пустых строк
    df_clean = df_clean[df_clean['Преподаватель'].astype(str).str.strip() != '']
    df_clean['Кафедра'] = df_clean['Кафедра'].astype(str).str.strip()

    # 4. Безопасная конвертация 'План' в числа
    plan_s = df_clean['План'].astype(str)
    plan_s = plan_s.str.replace(',', '.', regex=False).str.replace(r'[^\d.]', '', regex=True)
    df_clean['План'] = pd.to_numeric(plan_s, errors='coerce').fillna(0)

    # 5. Агрегация по ФИО + Кафедра (Формирование Файла 3)
    df_clean['ФИО_очищенное'] = df_clean['Преподаватель'].apply(clean_name)
    agg = df_clean.groupby(['ФИО_очищенное', 'Кафедра'], as_index=False)['План'].sum()
    agg.rename(columns={'План': 'План_ИС_ВВГУ'}, inplace=True)

    return agg