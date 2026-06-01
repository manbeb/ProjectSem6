import openpyxl
import re
import os
from typing import Dict, Optional


def parse_file2(filepath: str) -> Optional[Dict]:
    wb = openpyxl.load_workbook(filepath, data_only=True)

    # Ищем лист с итогами
    sheet = None
    for name in wb.sheetnames:
        if 'ИТОГ' in name.upper():
            sheet = wb[name]
            break
    if not sheet:
        wb.close()
        return None

    # Улучшенный поиск ФИО - ищем в первых 15 строках
    fio = "Неизвестный"
    for row_idx in range(2, 15):
        cell_val = str(sheet.cell(row=row_idx, column=1).value or "")
        # Ищем паттерн: "Фамилия И.О." или "Фамилия Имя Отчество, должность"
        if any(x in cell_val for x in ['Заведующий', 'Доцент', 'Старший', 'Профессор', 'Ассистент']):
            # Извлекаем ФИО до запятой или должности
            match = re.match(
                r'^([А-Яа-яЁё\.\s\-]+?)(?:\s{2,}|,|\s+Заведующий|\s+Доцент|\s+Профессор|\s+Старший|\s+Ассистент)',
                cell_val)
            if match:
                fio = match.group(1).strip()
                break

    # Парсим таблицу итогов (ищем по ключевым словам)
    totals = {'План_Учебная': 0, 'План_ВтораяПоловина': 0, 'Факт_Итого': None}

    for row_idx in range(10, 30):
        label_cell = sheet.cell(row=row_idx, column=1)
        val_cell = sheet.cell(row=row_idx, column=3)

        if not label_cell.value:
            continue

        label = str(label_cell.value).strip().lower()
        val = val_cell.value

        if val is None:
            continue

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