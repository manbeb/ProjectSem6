import os
from openpyxl.styles import PatternFill
from pathlib import Path

# Базовые пути
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE1_PATH = os.path.join(BASE_DIR, "Файл 1.xlsx")
FILE2_DIR = os.path.join(BASE_DIR, "input_files")  # Сюда класть Файлы 2

DOCUMENTS_DIR = os.path.join(Path.home(), "Documents")
OUTPUT_DIR = os.path.join(DOCUMENTS_DIR, "Нагрузка_ППС_ВВГУ")

FILE3_PATH = os.path.join(OUTPUT_DIR, "Файл 3_Агрегированный.xlsx")
FILE4_PATH = os.path.join(OUTPUT_DIR, "Файл 4_Сравнение.xlsx")

# Настройки ТЗ
TOLERANCE_HOURS = 5.0
HEADER_ROW_FILE1 = 7  # Строка заголовка в Файле 1 (0-based индекс)

# Стили для Excel
YELLOW_FILL = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
BLUE_HEADER = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")