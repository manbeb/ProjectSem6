import re

# Словарь распространенных инициалов для ВВГУ (можно расширять)
INITIALS_MAP = {
    'Е.Г.': ['Екатерина', 'Елена', 'Евгений'],
    'Е.В.': ['Елена', 'Евгений', 'Екатерина'],
    'А.В.': ['Александр', 'Анна', 'Андрей'],
    'С.А.': ['Сергей', 'Светлана', 'Александр'],
    # Добавьте другие常见的 инициалы
}


def normalize_name(name: str) -> str:
    """Приводит имя к верхнему регистру, убирает точки и пробелы"""
    if not name: return ""
    clean = re.sub(r'[.\s]+', '', str(name).strip().upper())
    return clean


def extract_surname(name: str) -> str:
    """Извлекает фамилию (первое слово)"""
    if not name: return ""
    return str(name).strip().split()[0].upper()


def names_match(name1: str, name2: str) -> bool:
    """
    Проверяет, могут ли два имени относиться к одному человеку.
    Поддерживает сопоставление:
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

    # Проверяем, является ли одно из имен инициалами
    def is_initials(name: str) -> bool:
        # Паттерн для инициалов: "Е.Г." или "Е Г"
        return bool(re.match(r'^[А-ЯЁ]\.?[А-ЯЁ]\.?$', name.split()[-1] if len(name.split()) > 1 else name))

    def get_initials_from_fullname(fullname: str) -> str:
        """Извлекает инициалы из полного имени"""
        parts = fullname.split()
        if len(parts) >= 2:
            surname = parts[0]
            firstname = parts[1][0].upper() + '.'
            if len(parts) >= 3:
                middlename = parts[2][0].upper() + '.'
                return f"{firstname}{middlename}"
            return firstname
        return ""

    # Если name1 - инициалы, а name2 - полное имя
    if is_initials(name1):
        initials = name1
        fullname = name2
    elif is_initials(name2):
        initials = name2
        fullname = name1
    else:
        return False

    # Извлекаем фамилию из полного имени
    fullname_parts = fullname.split()
    if not fullname_parts:
        return False

    fullname_surname = fullname_parts[0].upper()

    # Проверяем совпадение фамилий
    if surname1 != fullname_surname:
        return False

    # Проверяем, начинаются ли имя и отчество с нужных букв
    if len(fullname_parts) >= 2:
        firstname_initial = fullname_parts[1][0].upper()
        initials_clean = re.sub(r'[.\s]', '', initials)

        if len(initials_clean) >= 1 and initials_clean[0] == firstname_initial:
            return True

    return False