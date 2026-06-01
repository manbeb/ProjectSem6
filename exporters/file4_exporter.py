import pandas as pd
import openpyxl
from openpyxl.styles import Font
from config import FILE4_PATH, YELLOW_FILL, BLUE_HEADER

def export_file4(df: pd.DataFrame):
    # 1. Сохраняем данные
    df.to_excel(FILE4_PATH, index=False, sheet_name="Сравнение")
    wb = openpyxl.load_workbook(FILE4_PATH)
    ws = wb.active

    # 2. Стилизация заголовка
    for col in range(1, len(df.columns) + 1):
        cell = ws.cell(row=1, column=col)
        cell.fill = BLUE_HEADER
        cell.font = Font(color="FFFFFF", bold=True)
        cell.alignment = openpyxl.styles.Alignment(wrap_text=True)

    # 3. Подсветка строк по ТЗ (разница != 0 или отсутствует в ИС)
    for i, row in df.iterrows():
        # Проверяем флаг подсветки через статус
        if row['Статус'] in ["Расхождение", "❌ Отсутствует в ИС ВВГУ"]:
            for col in range(1, len(df.columns) + 1):
                ws.cell(row=i + 2, column=col).fill = YELLOW_FILL

    wb.save(FILE4_PATH)