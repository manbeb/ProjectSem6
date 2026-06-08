import pandas as pd
from config import TOLERANCE_HOURS
from core.name_utils import names_match

# Маппинг внутренних ключей в полные наименования для колонок отчёта
FEATURE_NAMES = {
    'Учебная': 'Учебная нагрузка',
    'Неконтактная': 'Неконтактная работа',
    'Метод': 'Метод. работа',
    'Электр': 'Электр. обучение',
    'Научная': 'Научная работа',
    'Орг': 'Орг. работа',
    'Повыш': 'Повыш. квалификации',
    'Поручения': 'Поручения рук. напр.'
}


def compare_data(file1_df: pd.DataFrame, file2_records: list) -> pd.DataFrame:
    grouped_data = {}
    detail_keys = list(FEATURE_NAMES.keys())  # Берём ключи из маппинга

    # 1. Группируем Файл 2 по составному ключу
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
                'Факт_Сумма': 0.0,
                'Детализация_Факт': {k: 0.0 for k in detail_keys},
                'Источники': []
            }

        grouped_data[key]['Факт_Сумма'] += rec['Факт_Из_Файла2']
        grouped_data[key]['Источники'].append(rec['Источник'])

        details = rec.get('Детализация', {})
        for k in detail_keys:
            grouped_data[key]['Детализация_Факт'][k] += details.get(k, 0)

    results = []

    # 2. Сопоставляем с Файлом 1 (План)
    for key, data in grouped_data.items():
        fio, dept, pos = key
        fact_f2 = data['Факт_Сумма']
        detail_fact = data['Детализация_Факт']

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

        # 3. Считаем разницы: План (Файл 1) - Факт (Файл 2)
        diff_detail = {}
        for k in detail_keys:
            full_name = FEATURE_NAMES[k]
            diff_detail[full_name] = round(detail_plan[k] - detail_fact[k], 2)

        # 4. Определяем статус
        status = " "
        if plan_is > 0:
            diff_total = plan_is - fact_f2
            if diff_total != 0:
                if abs(diff_total) <= TOLERANCE_HOURS:
                    status = "Расхождение в допуске (±5ч)"
                else:
                    status = "Расхождение"
            else:
                status = "✓ Сходится"
        else:
            status = "❌ Отсутствует в ИС ВВГУ"

        # 5. Формируем итоговый словарь
        base_result = {
            'ФИО ППС': fio,
            'Кафедра': dept,
            'Должность': pos,
            'План (ИС ВВГУ)': round(plan_is, 2) if plan_is > 0 else 0.0,
            'Факт (Отчёт кафедры)': round(fact_f2, 2),
            'Разница (План - Факт)': round(plan_is - fact_f2, 2) if plan_is > 0 else 0.0,
            'Статус': status,
            'Файлы-источники': ", ".join(set(data['Источники']))
        }

        # Добавляем колонки с полными наименованиями признаков
        for k in detail_keys:
            full_name = FEATURE_NAMES[k]
            base_result[full_name] = diff_detail[full_name]

        results.append(base_result)

    return pd.DataFrame(results)