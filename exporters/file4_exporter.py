import pandas as pd
import openpyxl
from openpyxl.styles import Font
from config import FILE4_PATH, YELLOW_FILL, BLUE_HEADER


def export_file4(df: pd.DataFrame, output_path: str = None):
    """
    Создаёт Файл 4: Excel с результатами сравнения и условным форматированием.
    """
    if output_path is None:
        output_path = FILE4_PATH

    # 1. Сохраняем DataFrame
    df.to_excel(output_path, index=False, sheet_name="Сравнение")

    # 2. Открываем ИМЕННО тот файл, который сохранили
    wb = openpyxl.load_workbook(output_path)  # ← было FILE4_PATH (баг!)
    ws = wb.active

    # 3. Стилизация заголовка
    for col in range(1, len(df.columns) + 1):
        cell = ws.cell(row=1, column=col)
        cell.fill = BLUE_HEADER
        cell.font = Font(color="FFFFFF", bold=True)
        cell.alignment = openpyxl.styles.Alignment(wrap_text=True)

    # 4. Подсветка строк
    for i, row in df.iterrows():
        status = str(row['Статус']).strip()  # ← strip() убирает пробелы из comparator.py
        if "Расхождение" in status or "Отсутствует" in status:
            for col in range(1, len(df.columns) + 1):
                ws.cell(row=i + 2, column=col).fill = YELLOW_FILL

    # 5. Сохраняем ИМЕННО в тот файл
    wb.save(output_path)  # ← было FILE4_PATH (баг!)
    wb.close()