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

    # Сбрасываем индекс для корректной подсветки
    df = df.reset_index(drop=True)

    # Подсветка строк с расхождениями
    for row_idx, row in df.iterrows():
        status = str(row.get('Статус', ''))
        if 'Расхождение' in status or 'Отсутствует' in status:
            excel_row = row_idx + 2
            for col in range(1, len(df.columns) + 1):
                ws.cell(row=excel_row, column=col).fill = YELLOW_FILL

    wb.save(filepath)
    wb.close()


def export_reports(
        result_df: pd.DataFrame,
        general_dir: str,  # ← папка для общего отчёта
        departments_dir: str  # ← папка для отчётов по кафедрам
) -> dict:
    """
    Экспортирует общий отчёт и отдельные отчёты по кафедрам.

    Args:
        result_df: DataFrame с результатами сравнения
        general_dir: Путь к папке для общего отчёта
        departments_dir: Путь к папке для отчётов по кафедрам

    Returns:
        Словарь с путями: {'general': ..., 'departments': {кафедра: путь}}
    """
    os.makedirs(general_dir, exist_ok=True)
    os.makedirs(departments_dir, exist_ok=True)

    paths = {'general': '', 'departments': {}}

    # 1. Общий отчёт (сохраняем в general_dir)
    general_path = os.path.join(general_dir, "Отчёт_общий.xlsx")
    result_df.to_excel(general_path, index=False, sheet_name="Сравнение")
    _apply_formatting(general_path, result_df)
    paths['general'] = general_path

    # 2. Отчёты по кафедрам (сохраняем в departments_dir)
    df_clean = result_df.copy()
    df_clean['Кафедра'] = df_clean['Кафедра'].fillna("Не указана").astype(str).str.strip()

    grouped = df_clean.groupby('Кафедра')
    for dept, group_df in grouped:
        # Очищаем название от недопустимых символов
        clean_dept = re.sub(r'[\\/*?:"<>|]', "_", dept)
        if not clean_dept:
            clean_dept = "Без_кафедры"

        dept_path = os.path.join(departments_dir, f"Отчёт_{clean_dept}.xlsx")
        group_df.to_excel(dept_path, index=False, sheet_name="Сравнение")
        _apply_formatting(dept_path, group_df)
        paths['departments'][dept] = dept_path

    return paths