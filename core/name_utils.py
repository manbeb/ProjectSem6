import re


def normalize_name(name: str) -> str:
    """Приводит имя к верхнему регистру, убирает точки и пробелы"""
    if not name: return ""
    clean = re.sub(r'[.\s]+', '', str(name).strip().upper())
    return clean


def extract_surname(name: str) -> str:
    """Извлекает фамилию (первое слово)"""
    if not name: return ""
    return str(name).strip().split()[0].upper()


def extract_initials(fullname: str) -> str:
    """Извлекает инициалы из полного имени"""
    parts = str(fullname).strip().split()
    if len(parts) < 2:
        return ""

    surname = parts[0]
    firstname_initial = parts[1][0].upper() + '.'

    if len(parts) >= 3:
        middlename_initial = parts[2][0].upper() + '.'
        return f"{firstname_initial}{middlename_initial}"

    return firstname_initial


def is_initials_format(name: str) -> bool:
    """Проверяет, является ли имя форматом с инициалами (например, 'Шумик Е.Г.')"""
    parts = str(name).strip().split()
    if len(parts) < 2:
        return False

    # Проверяем, выглядит ли вторая часть как инициалы
    initials_part = parts[1]
    return bool(re.match(r'^[А-ЯЁ]\.?[А-ЯЁ]?\.?$', initials_part))


def names_match(name1: str, name2: str) -> bool:
    """
    Проверяет, могут ли два имени относиться к одному человеку.
    Поддерживает:
    - "Шумик Е.Г." ↔ "Шумик Екатерина"
    - "Шумик Екатерина" ↔ "Шумик Екатерина"
    """
    if not name1 or not name2:
        return False

    name1 = str(name1).strip()
    name2 = str(name2).strip()

    # Извлекаем фамилии
    surname1 = extract_surname(name1)
    surname2 = extract_surname(name2)

    # Если фамилии не совпадают - точно разные люди
    if surname1 != surname2:
        return False

    # Если имена полностью совпадают после нормализации
    if normalize_name(name1) == normalize_name(name2):
        return True

    # Определяем, какое имя в формате с инициалами
    name1_is_initials = is_initials_format(name1)
    name2_is_initials = is_initials_format(name2)

    # Если оба в формате с инициалами или оба полные - уже проверили выше
    if name1_is_initials == name2_is_initials:
        return False

    # Одно с инициалами, другое полное
    if name1_is_initials:
        initials_name = name1
        full_name = name2
    else:
        initials_name = name2
        full_name = name1

    # Извлекаем инициалы из полного имени
    expected_initials = extract_initials(full_name)

    # Получаем инициалы из имени с инициалами
    initials_parts = initials_name.split()
    if len(initials_parts) < 2:
        return False

    actual_initials = initials_parts[1]

    # Сравниваем инициалы (с точками и без)
    expected_clean = re.sub(r'[.\s]', '', expected_initials)
    actual_clean = re.sub(r'[.\s]', '', actual_initials)

    # Проверяем совпадение первой буквы имени
    if len(expected_clean) >= 1 and len(actual_clean) >= 1:
        if expected_clean[0] == actual_clean[0]:
            return True

    return False