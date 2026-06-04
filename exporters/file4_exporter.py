import pandas as pd
import openpyxl
from openpyxl.styles import Font
from config import FILE4_PATH, YELLOW_FILL, BLUE_HEADER


def export_file4(df: pd.DataFrame, output_path: str = None):
    # Если путь не передан, берём из конфига (для тестов из консоли)
    if output_path is None:
        output_path = FILE4_PATH

    # 1. Сохраняем DataFrame
    df.to_excel(output_path, index=False, sheet_name="Сравнение")

    # 2. Открываем ИМЕННО ТОТ файл, который сохранили (а не из конфига!)
    wb = openpyxl.load_workbook(output_path)
    ws = wb.active

    # 3. Стилизация заголовка
    for col in range(1, len(df.columns) + 1):
        cell = ws.cell(row=1, column=col)
        cell.font = Font(color="000000", bold=True)
        cell.alignment = openpyxl.styles.Alignment(wrap_text=True)

    # 4. Подсветка строк
    for i, row in df.iterrows():
        # Используем 'in', чтобы поймать статус, даже если там есть лишние пробелы
        status = str(row['Статус'])
        if "Расхождение" in status or "Отсутствует" in status:
            for col in range(1, len(df.columns) + 1):
                ws.cell(row=i + 2, column=col).fill = YELLOW_FILL

    # 5. Сохраняем ИМЕННО в тот файл
    wb.save(output_path)
    wb.close()