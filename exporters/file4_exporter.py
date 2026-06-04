import pandas as pd
import os
import re
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment

YELLOW_FILL = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
BLUE_HEADER = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")


def _apply_formatting(filepath: str, df: pd.DataFrame):
    """Применяет стилизацию к уже сохранённому Excel-файлу."""
    wb = openpyxl.load_workbook(filepath)
    ws = wb.active

    # Стилизация шапки
    for col in range(1, len(df.columns) + 1):
        cell = ws.cell(row=1, column=col)
        cell.font = Font(color="000000", bold=True)
        cell.alignment = Alignment(wrap_text=True)

    # 🔑 КРИТИЧНО: сбрасываем индекс, чтобы он шёл строго 0, 1, 2...
    # Это исправляет "съехавшую" подсветку в отчётах по кафедрам
    df = df.reset_index(drop=True)

    # Подсветка строк с расхождениями
    for row_idx, row in df.iterrows():
        status = str(row.get('Статус', ''))
        if 'Расхождение' in status or 'Отсутствует' in status:
            # row_idx начинается с 0, +2 т.к. 1-я строка Excel = заголовок
            excel_row = row_idx + 2
            for col in range(1, len(df.columns) + 1):
                ws.cell(row=excel_row, column=col).fill = YELLOW_FILL

    wb.save(filepath)
    wb.close()


def export_reports(result_df: pd.DataFrame, output_dir: str) -> dict:
    """
    Экспортирует общий отчёт и отдельные отчёты по кафедрам.
    Возвращает словарь с путями: {'general': ..., 'departments': {кафедра: путь}}
    """
    os.makedirs(output_dir, exist_ok=True)
    paths = {'general': '', 'departments': {}}

    # 1. Общий отчёт
    general_path = os.path.join(output_dir, "Отчёт_общий.xlsx")
    result_df.to_excel(general_path, index=False, sheet_name="Сравнение")
    _apply_formatting(general_path, result_df)
    paths['general'] = general_path

    # 2. Отчёты по кафедрам
    df_clean = result_df.copy()
    df_clean['Кафедра'] = df_clean['Кафедра'].fillna("Не указана").astype(str).str.strip()

    grouped = df_clean.groupby('Кафедра')
    for dept, group_df in grouped:
        # Очищаем название от недопустимых символов для имён файлов
        clean_dept = re.sub(r'[\\/*?:"<>|]', "_", dept)
        if not clean_dept:
            clean_dept = "Без_кафедры"

        dept_path = os.path.join(output_dir, f"Отчёт_{clean_dept}.xlsx")
        group_df.to_excel(dept_path, index=False, sheet_name="Сравнение")
        _apply_formatting(dept_path, group_df)  # Теперь индекс сбросится внутри функции
        paths['departments'][dept] = dept_path

    return paths