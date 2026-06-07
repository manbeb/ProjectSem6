import pandas as pd
import os
import re
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.utils import get_column_letter

YELLOW_FILL = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
BLUE_HEADER = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")


def _apply_formatting(filepath: str, df: pd.DataFrame):
    wb = openpyxl.load_workbook(filepath)
    ws = wb.active
    df = df.reset_index(drop=True)

    for col_idx, col_name in enumerate(df.columns, start=1):
        cell = ws.cell(row=1, column=col_idx)
        cell.font = Font(color="000000", bold=True)
        cell.alignment = Alignment(wrap_text=True, vertical="center")

        max_length = len(str(col_name))
        for val in df.iloc[:, col_idx - 1]:
            val_str = str(val) if pd.notna(val) else ""
            if len(val_str) > max_length:
                max_length = len(val_str)

        new_width = min(max_length + 2, 60)
        ws.column_dimensions[get_column_letter(col_idx)].width = new_width

    for row_idx, row in df.iterrows():
        status = str(row.get('Статус', ''))
        if 'Расхождение' in status or 'Отсутствует' in status:
            excel_row = row_idx + 2
            for col in range(1, len(df.columns) + 1):
                ws.cell(row=excel_row, column=col).fill = YELLOW_FILL

    wb.save(filepath)
    wb.close()


def export_reports(result_df: pd.DataFrame, general_dir: str, departments_dir: str) -> dict:
    os.makedirs(general_dir, exist_ok=True)
    os.makedirs(departments_dir, exist_ok=True)

    paths = {'general': '', 'departments': {}}

    # 1. Общий отчёт
    general_path = os.path.join(general_dir, "Отчёт_общий.xlsx")
    result_df.to_excel(general_path, index=False, sheet_name="Сравнение")
    _apply_formatting(general_path, result_df)
    paths['general'] = general_path

    # 2. Отчёты по кафедрам с АГРЕГАЦИЕЙ
    df_clean = result_df.copy()
    df_clean['Кафедра'] = df_clean['Кафедра'].fillna("Не указана").astype(str).str.strip()

    # ОБНОВЛЁННЫЙ список: только итоговые значения и разницы. Колонок "Факт_..." больше нет.
    numeric_cols = [
        'План (ИС ВВГУ)', 'Факт (Отчёт кафедры)', 'Разница (План - Факт)',
        'Разница_Учебная', 'Разница_Неконтактная', 'Разница_Метод',
        'Разница_Электр', 'Разница_Научная', 'Разница_Орг',
        'Разница_Повыш', 'Разница_Поручения'
    ]

    grouped = df_clean.groupby('Кафедра')
    for dept, group_df in grouped:
        clean_dept = re.sub(r'[\\/*?:"<>|]', "_", dept)
        if not clean_dept:
            clean_dept = "Без_кафедры"

        agg_dict = {col: 'sum' for col in numeric_cols if col in group_df.columns}

        agg_dict['Статус'] = lambda x: 'Расхождение' if any(
            'Расхождение' in str(v) or 'Отсутствует' in str(v) for v in x) else '✓ Совпадает'
        agg_dict['Файлы-источники'] = lambda x: ', '.join(
            sorted(list(set(y.strip() for val in x for y in str(val).split(',')))))

        # АГРЕГИРУЕМ данные СТРОГО по ФИО ППС
        agg_df = group_df.groupby(['ФИО ППС'], as_index=False).agg(agg_dict)

        for col in numeric_cols:
            if col in agg_df.columns:
                agg_df[col] = agg_df[col].round(2)

        # Удаляем колонку 'Кафедра' и 'Должность' для отчёта по кафедре
        agg_df = agg_df.drop(columns=['Кафедра', 'Должность'], errors='ignore')

        dept_path = os.path.join(departments_dir, f"Отчёт_{clean_dept}.xlsx")
        agg_df.to_excel(dept_path, index=False, sheet_name="Сравнение")
        _apply_formatting(dept_path, agg_df)
        paths['departments'][dept] = dept_path

    return paths