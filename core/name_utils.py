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


def is_initials_format(name: str) -> bool:
    """Проверяет, является ли имя форматом с инициалами (например, 'Шумик Е.Г.')"""
    parts = str(name).strip().split()
    if len(parts) < 2:
        return False
    initials_part = parts[1]
    return bool(re.match(r'^[А-ЯЁ]\.?[А-ЯЁ]?\.?$', initials_part))


def names_match(name1: str, name2: str) -> bool:
    """
    Проверяет, могут ли два имени относиться к одному человеку.
    Поддерживает: "Шумик Е.Г." ↔ "Шумик Екатерина"
    """
    if not name1 or not name2:
        return False

    name1 = str(name1).strip()
    name2 = str(name2).strip()

    surname1 = extract_surname(name1)
    surname2 = extract_surname(name2)

    if surname1 != surname2:
        return False

    if normalize_name(name1) == normalize_name(name2):
        return True

    name1_is_initials = is_initials_format(name1)
    name2_is_initials = is_initials_format(name2)

    if name1_is_initials == name2_is_initials:
        return False

    if name1_is_initials:
        initials_name, full_name = name1, name2
    else:
        initials_name, full_name = name2, name1

    parts = full_name.split()
    if len(parts) < 2:
        return False

    expected_initial = parts[1][0].upper()
    initials_parts = initials_name.split()
    if len(initials_parts) < 2:
        return False

    actual_initial = re.sub(r'[.\s]', '', initials_parts[1])[0].upper()

    return expected_initial == actual_initial