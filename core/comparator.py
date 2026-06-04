import pandas as pd
from config import TOLERANCE_HOURS
from core.name_utils import normalize_name


def compare_data(file1_df: pd.DataFrame, file2_records: list) -> pd.DataFrame:
    """
    file2_records: список словарей с ключами 'ФИО', 'Кафедра', 'План_Из_Файла2', 'Факт_Из_Файла2', 'Источник'
    file1_df: DataFrame с колонками ['ФИО_очищенное', 'Кафедра', 'План_ИС_ВВГУ']
    """
    # 1. Группируем записи из Файлов 2 по паре (ФИО, Кафедра) и суммируем часы
    grouped_f2 = {}
    for rec in file2_records:
        fio_norm = normalize_name(rec['ФИО'])
        dept_norm = normalize_name(rec.get('Кафедра', ''))
        key = (fio_norm, dept_norm)

        if key not in grouped_f2:
            grouped_f2[key] = {
                'ФИО': rec['ФИО'],
                'Кафедра': rec.get('Кафедра', 'Не указана'),
                'План_Сумма': 0.0,
                'Факт_Сумма': 0.0,
                'Есть_Факт': False,
                'Источники': []
            }

        grouped_f2[key]['План_Сумма'] += rec['План_Из_Файла2']
        if rec.get('Факт_Из_Файла2') is not None:
            grouped_f2[key]['Факт_Сумма'] += rec['Факт_Из_Файла2']
            grouped_f2[key]['Есть_Факт'] = True
        grouped_f2[key]['Источники'].append(rec['Источник'])

    # 2. Строим индекс для быстрого поиска по Файлу 1
    f1_index = {}
    for _, row in file1_df.iterrows():
        fio_norm = normalize_name(row['ФИО_очищенное'])
        dept_norm = normalize_name(row['Кафедра'])
        key = (fio_norm, dept_norm)
        # Если в выгрузке ИС дубли, суммируем их
        f1_index[key] = f1_index.get(key, 0.0) + row['План_ИС_ВВГУ']

    # 3. Сравнение и формирование отчёта
    results = []
    for key, f2_data in grouped_f2.items():
        fio_norm, dept_norm = key
        plan_f2 = f2_data['План_Сумма']
        fact_f2 = f2_data['Факт_Сумма'] if f2_data['Есть_Факт'] else None

        # Точное сопоставление по ФИО + Кафедра
        plan_is = f1_index.get(key, None)
        status = ""
        highlight = False

        if plan_is is not None:
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
            # Если в ИС такой связки ФИО+Кафедра нет
            status = "❌ Отсутствует в ИС ВВГУ"
            highlight = True

        diff_fact = None
        if fact_f2 is not None:
            diff_fact = plan_f2 - fact_f2

        results.append({
            'ФИО ППС': f2_data['ФИО'],
            'Кафедра': f2_data['Кафедра'],
            'План (ИС ВВГУ)': round(plan_is, 2) if plan_is is not None else "Нет данных",
            'План (Файл 2)': round(plan_f2, 2),
            'Факт (Файл 2)': round(fact_f2, 2) if fact_f2 is not None else "-",
            'Разница План - ИС': round(diff_plan, 2) if plan_is is not None else "-",
            'Разница План - Факт': round(diff_fact, 2) if fact_f2 is not None else "-",
            'Статус': status,
            'Файлы-источники': ", ".join(set(f2_data['Источники']))
        })

    return pd.DataFrame(results)