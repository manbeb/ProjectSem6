"""
Сервисный слой - прослойка между GUI и бизнес-логикой.
"""
import os
import glob
from datetime import datetime
from parsers.file1_parser import parse_file1
from parsers.file2_parser import parse_file2
from core.comparator import compare_data
from exporters.file4_exporter import export_reports, _apply_formatting

class WorkloadService:
    def __init__(self):
        self.last_result = None
        self.last_error = None

    def process_workload(
        self,
        file1_path: str,
        dir2_path: str,
        user_selected_dir: str
    ) -> 'ProcessingResult':
        try:
            if not os.path.exists(file1_path):
                return ProcessingResult(success=False, error=f"Файл 1 не найден: {file1_path}")
            if not os.path.isdir(dir2_path):
                return ProcessingResult(success=False, error=f"Папка с Файлами 2 не найдена: {dir2_path}")

            project_dir = os.path.join(user_selected_dir, "Нагрузка ППС ВВГУ")
            os.makedirs(project_dir, exist_ok=True)

            file3_path = os.path.join(project_dir, "План.xlsx")
            date_str = datetime.now().strftime("%d.%m.%Y")
            departments_dir = os.path.join(project_dir, f"Отчёт по кафедрам {date_str}")
            os.makedirs(departments_dir, exist_ok=True)

            # === ШАГ 1: Чтение Файла 1 ===
            file1_df = parse_file1(file1_path)
            file1_df.to_excel(file3_path, index=False)

            # <-- НОВОЕ: Применяем авто-ширину и к Файлу 3
            _apply_formatting(file3_path, file1_df)

            # === ШАГ 2: Чтение Файлов 2 ===
            file2_records = []
            errors = []

            # Проверяем, есть ли подпапки (новая архитектура)
            subdirs = [d for d in os.listdir(dir2_path) if os.path.isdir(os.path.join(dir2_path, d))]
            if not subdirs:
                return ProcessingResult(success=False, error="В выбранной папке не найдены подпапки кафедр.")

            for dept_name in subdirs:
                dept_dir = os.path.join(dir2_path, dept_name)
                for path in glob.glob(os.path.join(dept_dir, "*.xlsx")):
                    try:
                        rec = parse_file2(path, department=dept_name)
                        if rec:
                            file2_records.append(rec)
                    except Exception as e:
                        errors.append(f"Ошибка чтения {os.path.basename(path)}: {str(e)}")

            if not file2_records:
                return ProcessingResult(success=False, error="Не удалось прочитать ни одного файла из подпапок кафедр.")

            # === ШАГ 3: Сравнение ===
            result_df = compare_data(file1_df, file2_records)

            # === ШАГ 4: Экспорт ===
            export_paths = export_reports(result_df, project_dir, departments_dir)

            mismatches = result_df[
                result_df['Статус'].str.contains('Расхождение|Отсутствует', na=False)
            ].shape[0]

            result = ProcessingResult(
                success=True,
                total_count=len(result_df),
                mismatches=mismatches,
                project_dir=project_dir,
                general_report_path=export_paths['general'],
                department_report_paths=export_paths['departments'],
                departments_folder=departments_dir,
                errors=errors
            )
            self.last_result = result
            return result

        except Exception as e:
            return ProcessingResult(success=False, error=str(e))

    def get_default_output_dir(self) -> str:
        from pathlib import Path
        documents = Path.home() / "Documents"
        return str(documents)


class ProcessingResult:
    def __init__(
        self,
        success: bool,
        total_count: int = 0,
        mismatches: int = 0,
        project_dir: str = None,
        general_report_path: str = None,
        department_report_paths: dict = None,
        departments_folder: str = None,
        errors: list = None,
        error: str = None
    ):
        self.success = success
        self.total_count = total_count
        self.mismatches = mismatches
        self.project_dir = project_dir
        self.general_report_path = general_report_path
        self.department_report_paths = department_report_paths or {}
        self.departments_folder = departments_folder
        self.errors = errors or []
        self.error = error

    def __str__(self):
        if self.success:
            return f"Успешно: {self.total_count} ППС, {self.mismatches} расхождений"
        return f"Ошибка: {self.error}"