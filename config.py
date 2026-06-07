import os
from openpyxl.styles import PatternFill

# === Настройки ===
TOLERANCE_HOURS = 5.0

# === Папка по умолчанию для диалога сохранения (только как стартовая точка) ===
# Используем папку "Документы" пользователя, это надёжнее, чем папка со скриптом
DEFAULT_OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "Documents")

# === Стили для Excel ===
YELLOW_FILL = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")