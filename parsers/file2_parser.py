import openpyxl
import re
import os
from typing import Dict, Optional


def parse_file2(filepath: str, department_override: str = None) -> Optional[Dict]:
    wb = openpyxl.load_workbook(filepath, data_only=True)
    sheet = None
    for name in wb.sheetnames:
        if 'ИТОГ' in name.upper():
            sheet = wb[name]
            break
    if not sheet:
        wb.close()
        return None

    fio = "Неизвестный"
    for row_idx in range(1, 15):
        cell_val = str(sheet.cell(row=row_idx, column=1).value or "")
        if any(x in cell_val for x in ['Заведующий', 'Доцент', 'Старший', 'Профессор', 'Ассистент']):
            match = re.match(
                r'^([А-Яа-яЁё\.\s\-]+?)(?:\s{2,}|,|\s+Заведующий|\s+Доцент|\s+Профессор|\s+Старший|\s+Ассистент)',
                cell_val)
            if match:
                fio = match.group(1).strip()
            else:
                fio = cell_val.split('Заведующий')[0].split('Доцент')[0].split('Профессор')[0].strip()
            break

    department = department_override
    if not department:
        # Автоизвлечение из имени файла: Иванов_КафедраИБ.xlsx -> КафедраИБ
        dept_match = re.search(r'[_\-]([А-Яа-яЁё\s]+)\.xlsx', os.path.basename(filepath), re.IGNORECASE)
        department = dept_match.group(1).strip() if dept_match else "Не указана"

    totals = {}
    fact_hours = None
    for row_idx in range(1, sheet.max_row + 1):
        cell_b = str(sheet.cell(row=row_idx, column=2).value or "")
        cell_c = sheet.cell(row=row_idx, column=3).value

        if 'Фактическое кол-во часов' in cell_b or 'Фактическое кол-во' in cell_b:
            fact_hours = float(cell_c) if cell_c is not None else None

        if cell_c is not None:
            if 'Учебная нагрузка' in cell_b:
                totals['Учебная'] = float(cell_c)
            elif 'Неконтактная' in cell_b:
                totals['Неконтактная'] = float(cell_c)
            elif 'Метод.' in cell_b:
                totals['Метод'] = float(cell_c)
            elif 'Электр.' in cell_b:
                totals['Электр'] = float(cell_c)
            elif 'Научная' in cell_b:
                totals['Научная'] = float(cell_c)
            elif 'Орг.' in cell_b:
                totals['Орг'] = float(cell_c)
            elif 'Повыш.' in cell_b:
                totals['Повыш'] = float(cell_c)
            elif 'Поручения' in cell_b:
                totals['Поручения'] = float(cell_c)

    plan_total = sum(v for v in totals.values() if v is not None)
    wb.close()

    return {
        'ФИО': fio,
        'Кафедра': department,
        'План_Из_Файла2': plan_total if plan_total > 0 else totals.get('Учебная', 0),
        'Факт_Из_Файла2': fact_hours,
        'Источник': os.path.basename(filepath)
    }