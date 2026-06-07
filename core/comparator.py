import pandas as pd
from config import TOLERANCE_HOURS
from core.name_utils import names_match


def compare_data(file1_df: pd.DataFrame, file2_records: list) -> pd.DataFrame:
    """
    file1_df: DataFrame с колонками ['ФИ', 'Кафедра', 'Должность', 'План_ИС_ВВГУ', 'План_Учебная', ...]
    file2_records: список словарей из парсера Файла 2 (с ключами 'Кафедра', 'Должность', 'Детализация')
    """
    grouped_data = {}
    detail_keys = ['Учебная', 'Неконтактная', 'Метод', 'Электр', 'Научная', 'Орг', 'Повыш', 'Поручения']

    # 1. Группируем Файл 2 по ПОЛНОМУ составному ключу: (ФИО, Кафедра, Должность)
    for rec in file2_records:
        fio_2 = rec['ФИО']
        dept_2 = rec.get('Кафедра', 'Не указана')
        pos_2 = rec.get('Должность', 'Не указана')

        key = (fio_2, dept_2, pos_2)

        if key not in grouped_data:
            grouped_data[key] = {
                'ФИО': fio_2,
                'Кафедра': dept_2,
                'Должность': pos_2,
                'План_Сумма': 0.0,
                'Факт_Сумма': 0.0,
                'Есть_Факт': False,
                'Источники': [],
                'Детализация_Факт': {k: 0.0 for k in detail_keys}
            }

        grouped_data[key]['План_Сумма'] += rec['План_Из_Файла2']

        if rec.get('Факт_Из_Файла2') is not None:
            grouped_data[key]['Факт_Сумма'] += rec['Факт_Из_Файла2']
            grouped_data[key]['Есть_Факт'] = True

        grouped_data[key]['Источники'].append(rec['Источник'])

        # Накопление детализации факта
        details = rec.get('Детализация', {})
        for k in detail_keys:
            grouped_data[key]['Детализация_Факт'][k] += details.get(k, 0)

    results = []

    # 2. Формируем итоговые строки, строго сверяясь с Файлом 1 по ВСЕМ трём полям
    for key, data in grouped_data.items():
        fio, dept, pos = key
        plan_f2 = data['План_Сумма']
        fact_f2 = data['Факт_Сумма'] if data['Есть_Факт'] else None
        detail_fact = data['Детализация_Факт']

        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Маска включает Должность!
        # Используем гибкое сравнение должностей (вхождение подстроки), чтобы учесть варианты написания
        mask_is = (file1_df['Кафедра'] == dept) & \
                  (file1_df['ФИ'].apply(lambda x: names_match(fio, x))) & \
                  (file1_df['Должность'].apply(lambda x: pos in str(x) or str(x) in pos))

        row1 = file1_df[mask_is].iloc[0] if not file1_df[mask_is].empty else None

        if row1 is not None:
            plan_is = row1['План_ИС_ВВГУ']
            detail_plan = {k: row1.get(f'План_{k}', 0) for k in detail_keys}
        else:
            plan_is = 0
            detail_plan = {k: 0 for k in detail_keys}

        # 3. Считаем разницы (План - Факт)
        diff_detail = {}
        for k in detail_keys:
            diff_detail[f'Разница_{k}'] = round(detail_plan[k] - detail_fact[k], 2)

        # 4. Определяем статус
        status = " "
        if plan_is > 0:
            diff_plan = plan_f2 - plan_is
            if diff_plan != 0:
                if abs(diff_plan) <= TOLERANCE_HOURS:
                    status = "Расхождение в допуске (±5ч)"
                else:
                    status = "Расхождение"
            else:
                status = "✓ Совпадает"
        else:
            status = "❌ Отсутствует в ИС ВВГУ"

        diff_fact = round(plan_f2 - fact_f2, 2) if fact_f2 is not None else None

        # 5. Собираем итоговый словарь
        base_result = {
            'ФИО ППС': fio,
            'Кафедра': dept,
            'Должность': pos,  # Добавили должность в итоговый отчёт для наглядности
            'План (ИС ВВГУ)': round(plan_is, 2) if plan_is > 0 else "Нет данных",
            'План (Файл 2)': round(plan_f2, 2),
            'Факт (Файл 2)': round(fact_f2, 2) if fact_f2 is not None else "-",
            'Разница План - ИС': round(plan_f2 - plan_is, 2) if plan_is > 0 else "-",
            'Разница План - Факт': diff_fact,
            'Статус': status,
            'Файлы-источники': ", ".join(set(data['Источники']))
        }

        results.append({**base_result, **diff_detail})

    return pd.DataFrame(results)