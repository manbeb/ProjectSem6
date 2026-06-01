import openpyxl
import re
import os
from typing import Dict, Optional


def parse_file2(filepath: str) -> Optional[Dict]:
    wb = openpyxl.load_workbook(filepath, data_only=True)

    # 1. Ищем лист с итогами
    sheet = None
    for name in wb.sheetnames:
        if 'ИТОГ' in name.upper():
            sheet = wb[name]
            break
    if not sheet: return None

    # 2. Извлекаем ФИО из шапки (строки 2-4)
    fio = "Неизвестный"
    for row in sheet.iter_rows(min_row=2, max_row=4, max_col=1):
        cell_val = str(row[0].value or "")
        if any(x in cell_val for x in ['Заведующий', 'Доцент', 'Старший', 'Профессор', 'Ассистент']):
            fio = re.split(r'\s*(Заведующий|Доцент|Старший|Профессор|Ассистент)', cell_val)[0].strip()
            break

    # 3. Парсим таблицу итогов
    totals = {'План_Учебная': 0, 'План_ВтораяПоловина': 0, 'Факт_Итого': None}
    for row in sheet.iter_rows(min_row=10, max_row=25, values_only=True):
        if not row[0]: continue
        label = str(row[0]).strip().lower()
        val = row[2]  # Колонка C с часами

        if val is None: continue
        if 'учебная нагрузка' in label:
            totals['План_Учебная'] = float(val)
        elif 'неконтактная' in label or 'вторая половина' in label:
            totals['План_ВтораяПоловина'] = float(val)
        elif 'фактическое кол-во' in label:
            totals['Факт_Итого'] = float(val)

    plan_total = totals['План_Учебная'] + totals['План_ВтораяПоловина']

    wb.close()
    return {
        'ФИО': fio,
        'План_Из_Файла2': plan_total,
        'Факт_Из_Файла2': totals['Факт_Итого'],
        'Источник': os.path.basename(filepath)
    }