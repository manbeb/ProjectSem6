import pandas as pd
from config import TOLERANCE_HOURS
from core.name_utils import normalize_name


def compare_data(file1_df: pd.DataFrame, file2_records: list) -> pd.DataFrame:
    results = []

    # Индекс Файла 1 для O(1) поиска
    f1_index = {}
    for _, row in file1_df.iterrows():
        key = normalize_name(row['ФИО_очищенное'])
        f1_index[key] = row['План_ИС_ВВГУ']

    for rec in file2_records:
        key = normalize_name(rec['ФИО'])
        plan_is = f1_index.get(key, None)
        plan_f2 = rec['План_Из_Файла2']
        fact_f2 = rec['Факт_Из_Файла2']

        diff_plan = None
        diff_fact = None
        highlight = False
        status = ""

        if plan_is is not None:
            diff_plan = plan_f2 - plan_is
            # ТЗ: если разница != 0 -> подсветка. Допуск ±5ч для статуса
            if diff_plan != 0:
                highlight = True
                status = "Расхождение"
            elif abs(diff_plan) <= TOLERANCE_HOURS:
                status = "В допуске (±5ч)"
            else:
                status = "В норме"
        else:
            status = "❌ Отсутствует в ИС ВВГУ"
            highlight = True  # Пункт 4 ТЗ

        # Пункт 5 ТЗ: разница План vs Факт
        if fact_f2 is not None:
            diff_fact = plan_f2 - fact_f2

        results.append({
            'ФИО ППС': rec['ФИО'],
            'Кафедра_ИС': "Не найдено" if plan_is is None else "Есть",
            'План (ИС ВВГУ)': plan_is if plan_is is not None else "Нет данных",
            'План (Файл 2)': plan_f2,
            'Факт (Файл 2)': fact_f2 if fact_f2 is not None else "-",
            'Разница План - ИС': round(diff_plan, 2) if diff_plan is not None else "-",
            'Разница План - Факт': round(diff_fact, 2) if diff_fact is not None else "-",
            'Статус': status,
            'Файл': rec['Источник']
        })

    return pd.DataFrame(results)