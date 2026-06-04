"""
Сервисный слой - прослойка между GUI и бизнес-логикой.
Инкапсулирует все операции обработки данных.
"""

import os
import glob
from datetime import datetime
from typing import Optional, Tuple
import pandas as pd

from config import FILE1_PATH, FILE2_DIR, OUTPUT_DIR
from parsers.file1_parser import parse_file1
from parsers.file2_parser import parse_file2
from core.comparator import compare_data
from exporters.file4_exporter import export_file4


class WorkloadService:
    """
    Сервис для обработки данных о нагрузке ППС.

    Пример использования:
        service = WorkloadService()
        result = service.process_workload(
            file1_path="путь/к/файлу1.xlsx",
            dir2_path="путь/к/папке/с/файлами2",
            output_dir="путь/для/сохранения"
        )
        if result.success:
            print(f"Обработано: {result.total_count}")
    """

    def __init__(self):
        self.last_result = None
        self.last_error = None

    def process_workload(
            self,
            file1_path: str,
            dir2_path: str,
            output_dir: str
    ) -> 'ProcessingResult':
        """
        Основная операция: обработка и сравнение нагрузки.

        Args:
            file1_path: Путь к Файлу 1 (план из ИС ВВГУ)
            dir2_path: Путь к папке с Файлами 2 (индивидуальные планы)
            output_dir: Путь к папке для сохранения результатов

        Returns:
            ProcessingResult с результатами обработки
        """
        try:
            # Валидация входных данных
            if not os.path.exists(file1_path):
                return ProcessingResult(
                    success=False,
                    error=f"Файл 1 не найден: {file1_path}"
                )

            if not os.path.isdir(dir2_path):
                return ProcessingResult(
                    success=False,
                    error=f"Папка с Файлами 2 не найдена: {dir2_path}"
                )

            # Создаём папку для результатов
            os.makedirs(output_dir, exist_ok=True)

            # Формируем пути для сохранения
            file3_path = os.path.join(output_dir, "Файл 3_Агрегированный.xlsx")
            file4_path = os.path.join(output_dir, "Файл 4_Сравнение.xlsx")

            # Шаг 1: Чтение Файла 1
            file1_df = parse_file1(file1_path)
            file1_df.to_excel(file3_path, index=False)

            # Шаг 2: Чтение Файлов 2
            file2_paths = glob.glob(os.path.join(dir2_path, "*.xlsx"))
            if not file2_paths:
                return ProcessingResult(
                    success=False,
                    error="В выбранной папке не найдены файлы Excel"
                )

            file2_records = []
            errors = []
            for path in file2_paths:
                try:
                    rec = parse_file2(path)
                    if rec:
                        file2_records.append(rec)
                except Exception as e:
                    errors.append(f"Ошибка чтения {os.path.basename(path)}: {str(e)}")

            # Шаг 3: Сравнение
            result_df = compare_data(file1_df, file2_records)

            # Шаг 4: Экспорт
            export_file4(result_df, file4_path)

            # Статистика
            mismatches = result_df[
                result_df['Статус'].str.contains('Расхождение|Отсутствует', na=False)
            ].shape[0]

            result = ProcessingResult(
                success=True,
                total_count=len(result_df),
                mismatches=mismatches,
                file3_path=file3_path,
                file4_path=file4_path,
                errors=errors
            )

            self.last_result = result
            return result

        except Exception as e:
            error_result = ProcessingResult(
                success=False,
                error=str(e)
            )
            self.last_error = e
            return error_result

    def create_report_folder(self, base_dir: str) -> str:
        """
        Создаёт папку для отчёта с датой.

        Args:
            base_dir: Базовая директория

        Returns:
            Путь к созданной папке
        """
        date_str = datetime.now().strftime("%d.%m.%Y")
        folder_name = f"Отчёт_Нагрузка_{date_str}"
        output_dir = os.path.join(base_dir, folder_name)
        os.makedirs(output_dir, exist_ok=True)
        return output_dir

    def get_default_output_dir(self) -> str:
        """Возвращает папку по умолчанию (Документы/Нагрузка_ППС_ВВГУ)"""
        from pathlib import Path
        documents = Path.home() / "Documents"
        return str(documents / "Нагрузка_ППС_ВВГУ")


class ProcessingResult:
    """
    Результат обработки нагрузки.

    Attributes:
        success: Успешно ли выполнена обработка
        total_count: Всего проверено ППС
        mismatches: Количество расхождений
        file3_path: Путь к Файлу 3
        file4_path: Путь к Файлу 4
        errors: Список ошибок (если есть)
        error: Сообщение об ошибке (если не успешно)
    """

    def __init__(
            self,
            success: bool,
            total_count: int = 0,
            mismatches: int = 0,
            file3_path: str = None,
            file4_path: str = None,
            errors: list = None,
            error: str = None
    ):
        self.success = success
        self.total_count = total_count
        self.mismatches = mismatches
        self.file3_path = file3_path
        self.file4_path = file4_path
        self.errors = errors or []
        self.error = error

    def __str__(self):
        if self.success:
            return f"Успешно: {self.total_count} ППС, {self.mismatches} расхождений"
        return f"Ошибка: {self.error}"