import openpyxl
import re
import os
from typing import Dict, Optional


def parse_file2(filepath: str) -> Optional[Dict]:
    wb = openpyxl.load_workbook(filepath, data_only=True)

    # 1. Ищем лист с ИТОГАМИ
    sheet = None
    for name in wb.sheetnames:
        if 'ИТОГ' in name.upper():
            sheet = wb[name]
            break

    if not sheet:
        wb.close()
        return None

    # 2. Извлекаем ФИО из шапки (ищем строку с должностью)
    fio = "Неизвестный"
    for row_idx in range(1, 20):
        cell_val = str(sheet.cell(row=row_idx, column=1).value or "")
        # Паттерн: "Шумик Е.Г.    Заведующий кафедрой, 1 ст."
        if any(pos in cell_val for pos in ['Заведующий', 'Доцент', 'Профессор', 'Старший', 'Ассистент']):
            # Берем часть до должности
            match = re.match(
                r'^([А-Яа-яЁё\.\s\-]+?)(?:\s{2,}|,|\s+Заведующий|\s+Доцент|\s+Профессор|\s+Старший|\s+Ассистент)',
                cell_val)
            if match:
                fio = match.group(1).strip()
            else:
                fio = cell_val.split('Заведующий')[0].split('Доцент')[0].split('Профессор')[0].strip()
            break

    # 3. Парсим таблицу ИТОГОВ (структура: Col B = Название, Col C = Значение)
    totals = {}
    fact_hours = None

    for row_idx in range(1, sheet.max_row + 1):
        cell_b = str(sheet.cell(row=row_idx, column=2).value or "")
        cell_c = sheet.cell(row=row_idx, column=3).value

        # Ищем фактические часы
        if 'Фактическое кол-во часов' in cell_b or 'Фактическое кол-во' in cell_b:
            fact_hours = float(cell_c) if cell_c is not None else None

        # Ищем плановые значения по категориям
        if cell_c is not None:
            if 'Учебная нагрузка' in cell_b:
                totals['Учебная'] = float(cell_c)
            elif 'Неконтактная работа' in cell_b:
                totals['Неконтактная'] = float(cell_c)
            elif 'Метод. работа' in cell_b or 'Метод.' in cell_b:
                totals['Метод'] = float(cell_c)
            elif 'Электр. обучение' in cell_b:
                totals['Электр'] = float(cell_c)
            elif 'Научная работа' in cell_b:
                totals['Научная'] = float(cell_c)
            elif 'Орг. работа' in cell_b:
                totals['Орг'] = float(cell_c)
            elif 'Повыш. квалификации' in cell_b:
                totals['Повыш'] = float(cell_c)
            elif 'Поручения рук. напр.' in cell_b:
                totals['Поручения'] = float(cell_c)

    # 4. Считаем общий план
    plan_total = sum(v for v in totals.values() if v is not None)

    wb.close()

    return {
        'ФИО': fio,
        'План_Из_Файла2': plan_total if plan_total > 0 else totals.get('Учебная', 0),
        'Факт_Из_Файла2': fact_hours,
        'Источник': os.path.basename(filepath),
        'Детали': totals
    }