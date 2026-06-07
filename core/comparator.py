import pandas as pd
from config import TOLERANCE_HOURS
from core.name_utils import names_match


def compare_data(file1_df: pd.DataFrame, file2_records: list) -> pd.DataFrame:
    """
    file1_df: DataFrame с колонками ['ФИ', 'Кафедра', 'Должность', 'План_ИС_ВВГУ']
    file2_records: список словарей из парсера Файла 2
    """
    grouped_data = {}

    # 1. Группируем записи из Файлов 2 по паре (ФИО, Кафедра)
    for rec in file2_records:
        fio_2 = rec['ФИО']
        pos_2 = rec.get('Должность', '')

        # Находим Кафедру в Файле 1 по совпадению ФИ и Должности
        found_dept = None
        for _, row1 in file1_df.iterrows():
            if names_match(fio_2, row1['ФИ']):
                if pos_2 in str(row1['Должность']) or str(row1['Должность']) in pos_2:
                    found_dept = row1['Кафедра']
                    break

        if found_dept is None:
            found_dept = "Не указана"

        # Ключ группировки: (ФИО, Кафедра)
        key = (fio_2, found_dept)

        if key not in grouped_data:
            grouped_data[key] = {
                'ФИО': fio_2,
                'Кафедра': found_dept,
                'План_Сумма': 0.0,
                'Факт_Сумма': 0.0,
                'Есть_Факт': False,
                'Источники': []
            }

        grouped_data[key]['План_Сумма'] += rec['План_Из_Файла2']
        if rec.get('Факт_Из_Файла2') is not None:
            grouped_data[key]['Факт_Сумма'] += rec['Факт_Из_Файла2']
            grouped_data[key]['Есть_Факт'] = True
        grouped_data[key]['Источники'].append(rec['Источник'])

    results = []

    # 2. Формируем итоговые строки
    for key, data in grouped_data.items():
        fio, dept = key
        plan_f2 = data['План_Сумма']
        fact_f2 = data['Факт_Сумма'] if data['Есть_Факт'] else None

        # 3. Считаем общий план из ИС ВВГУ для этой кафедры
        # ЗАМЕНА: file1_df['ФИО_очищенное'] -> file1_df['ФИ']
        mask_is = (file1_df['Кафедра'] == dept) & \
                  (file1_df['ФИ'].apply(lambda x: names_match(fio, x)))

        plan_is = file1_df.loc[mask_is, 'План_ИС_ВВГУ'].sum()

        status = " "
        highlight = False

        if plan_is > 0:
            diff_plan = plan_f2 - plan_is
            if diff_plan != 0:
                highlight = True
                if abs(diff_plan) <= TOLERANCE_HOURS:
                    status = "Расхождение в допуске (±5ч)"
                else:
                    status = "Расхождение"
            else:
                status = "✓ Совпадает"
        else:
            status = "❌ Отсутствует в ИС ВВГУ"
            highlight = True

        diff_fact = round(plan_f2 - fact_f2, 2) if fact_f2 is not None else None

        results.append({
            'ФИО ППС': fio,
            'Кафедра': dept,
            'План (ИС ВВГУ)': round(plan_is, 2) if plan_is > 0 else "Нет данных",
            'План (Файл 2)': round(plan_f2, 2),
            'Факт (Файл 2)': round(fact_f2, 2) if fact_f2 is not None else "-",
            'Разница План - ИС': round(diff_plan, 2) if plan_is > 0 else "-",
            'Разница План - Факт': round(diff_fact, 2) if diff_fact is not None else "-",
            'Статус': status,
            'Файлы-источники': ", ".join(set(data['Источники']))
        })

    return pd.DataFrame(results)