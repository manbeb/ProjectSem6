import re

def normalize_name(name: str) -> str:
    if not name: return ""
    # Верхний регистр, убираем точки и лишние пробелы
    clean = re.sub(r'[.\s]+', '', str(name).strip().upper())
    return clean