"""
Сервисный слой - прослойка между GUI и бизнес-логикой.
Инкапсулирует все операции обработки данных.
"""
import os
import glob
from datetime import datetime
from parsers.file1_parser import parse_file1
from parsers.file2_parser import parse_file2
from core.comparator import compare_data
from exporters.file4_exporter import export_reports

class WorkloadService:
    def __init__(self):
        self.last_result = None
        self.last_error = None

    def process_workload(self, file1_path: str, dir2_path: str, output_dir: str) -> 'ProcessingResult':
        try:
            if not os.path.exists(file1_path):
                return ProcessingResult(success=False, error=f"Файл 1 не найден: {file1_path}")
            if not os.path.isdir(dir2_path):
                return ProcessingResult(success=False, error=f"Папка с Файлами 2 не найдена: {dir2_path}")

            os.makedirs(output_dir, exist_ok=True)
            file3_path = os.path.join(output_dir, "Файл 3_Агрегированный.xlsx")

            file1_df = parse_file1(file1_path)
            file1_df.to_excel(file3_path, index=False)

            file2_paths = glob.glob(os.path.join(dir2_path, "*.xlsx"))
            if not file2_paths:
                return ProcessingResult(success=False, error="В выбранной папке не найдены файлы Excel")

            file2_records = []
            errors = []
            for path in file2_paths:
                try:
                    rec = parse_file2(path)
                    if rec:
                        file2_records.append(rec)
                except Exception as e:
                    errors.append(f"Ошибка чтения {os.path.basename(path)}: {str(e)}")

            result_df = compare_data(file1_df, file2_records)

            # 🆕 Экспорт отчётов (общий + по кафедрам)
            export_paths = export_reports(result_df, output_dir)

            mismatches = result_df[
                result_df['Статус'].str.contains('Расхождение|Отсутствует', na=False)
            ].shape[0]

            result = ProcessingResult(
                success=True,
                total_count=len(result_df),
                mismatches=mismatches,
                general_report_path=export_paths['general'],
                department_report_paths=export_paths['departments'],
                errors=errors
            )
            self.last_result = result
            return result

        except Exception as e:
            return ProcessingResult(success=False, error=str(e))

    def create_report_folder(self, base_dir: str) -> str:
        date_str = datetime.now().strftime("%d.%m.%Y")
        folder_name = f"Отчёт_Нагрузка_{date_str}"
        output_dir = os.path.join(base_dir, folder_name)
        os.makedirs(output_dir, exist_ok=True)
        return output_dir

    def get_default_output_dir(self) -> str:
        from pathlib import Path
        documents = Path.home() / "Documents"
        return str(documents / "Нагрузка_ППС_ВВГУ")

class ProcessingResult:
    def __init__(self, success: bool, total_count: int = 0, mismatches: int = 0,
                 general_report_path: str = None, department_report_paths: dict = None,
                 errors: list = None, error: str = None):
        self.success = success
        self.total_count = total_count
        self.mismatches = mismatches
        self.general_report_path = general_report_path
        self.department_report_paths = department_report_paths or {}
        self.errors = errors or []
        self.error = error

    def __str__(self):
        if self.success:
            return f"Успешно: {self.total_count} ППС, {self.mismatches} расхождений"
        return f"Ошибка: {self.error}"