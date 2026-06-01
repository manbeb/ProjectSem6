import pandas as pd
from config import TOLERANCE_HOURS
from core.name_utils import normalize_name, names_match


def compare_data(file1_df: pd.DataFrame, file2_records: list) -> pd.DataFrame:
    results = []

    for rec in file2_records:
        found_match = False
        plan_is = None
        matched_row = None
        matched_fio = None

        # Ищем совпадение по ФИО с использованием умного сравнения
        for _, row in file1_df.iterrows():
            if names_match(rec['ФИО'], row['ФИО_очищенное']):
                found_match = True
                plan_is = row['План_ИС_ВВГУ']
                matched_row = row
                matched_fio = row['ФИО_очищенное']
                break

        plan_f2 = rec['План_Из_Файла2']
        fact_f2 = rec['Факт_Из_Файла2']

        diff_plan = None
        diff_fact = None
        highlight = False
        status = ""

        if found_match:
            diff_plan = plan_f2 - plan_is
            # ТЗ: если разница != 0 -> подсветка
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
            highlight = True  # Пункт 4 ТЗ

        # Пункт 5 ТЗ: разница План vs Факт
        if fact_f2 is not None:
            diff_fact = plan_f2 - fact_f2

        results.append({
            'ФИО ППС': rec['ФИО'],
            'Кафедра_ИС': matched_row['Кафедра'] if matched_row is not None else "Не найдено",
            'План (ИС ВВГУ)': plan_is if plan_is is not None else "Нет данных",
            'План (Файл 2)': plan_f2,
            'Факт (Файл 2)': fact_f2 if fact_f2 is not None else "-",
            'Разница План - ИС': round(diff_plan, 2) if diff_plan is not None else "-",
            'Разница План - Факт': round(diff_fact, 2) if diff_fact is not None else "-",
            'Статус': status,
            'Файл': rec['Источник']
        })

    return pd.DataFrame(results)