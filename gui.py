import os
import glob
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

# Импортируем модули
from parsers.file1_parser import parse_file1
from parsers.file2_parser import parse_file2
from core.comparator import compare_data
# ИЗМЕНЕНО: импортируем новую функцию
from exporters.file4_exporter import export_reports
from config import FILE3_PATH, FILE4_PATH, OUTPUT_DIR


class XPStyleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система контроля учебной нагрузки сотрудников")
        self.root.geometry("800x500")
        self.root.resizable(False, False)

        # Цвета ВВГУ
        self.bg_color = "#F5F5F5"  # Светло-серый фон
        self.blue_color = "#2E5EA3"  # Фирменный синий ВВГУ
        self.blue_light = "#4A7BC9"  # Светлее для эффекта объема
        self.orange_color = "#EB7124"  # Фирменный оранжевый ВВГУ
        self.orange_hover = "#FF8533"  # Светлее при наведении
        self.text_dark = "#1A1A1A"  # Почти черный для контраста

        self.root.configure(bg=self.bg_color)

        # Переменные
        self.file1_path = tk.StringVar()
        self.dir2_path = tk.StringVar()
        self.dir2_display = tk.StringVar(value="Папка не выбрана")
        self.file1_display = tk.StringVar(value="Файл не выбран")
        self.file_count = tk.IntVar(value=0)
        self.status_text = tk.StringVar(value="Ожидание")

        os.makedirs(OUTPUT_DIR, exist_ok=True)

        self.output_dir = tk.StringVar(value=OUTPUT_DIR)
        self.output_dir_display = tk.StringVar(value=f"📁 {os.path.basename(OUTPUT_DIR)}")

        self.is_processing = False

        self.create_widgets()

    def create_widgets(self):
        # === ЗАГОЛОВОК ===
        header_frame = tk.Frame(self.root, bg=self.bg_color)
        header_frame.pack(fill="x", padx=20, pady=(20, 15))

        # Логотип ВВГУ (синий)
        logo_label = tk.Label(header_frame,
                              text="ВВГУ",
                              font=("Arial", 22, "bold"),
                              bg=self.bg_color,
                              fg=self.blue_color)
        logo_label.pack(side="left", padx=(0, 15))

        # Заголовок (темно-синий)
        title_label = tk.Label(header_frame,
                               text="Система контроля учебной нагрузки сотрудников",
                               font=("Tahoma", 16, "bold"),
                               bg=self.bg_color,
                               fg=self.text_dark,
                               anchor="w")
        title_label.pack(fill="x", side="left")

        # Разделительная линия (оранжевая)
        tk.Frame(self.root, bg=self.orange_color, height=3).pack(fill="x", padx=20, pady=10)

        # === БЛОК 1: Запланированная нагрузка ===
        self.create_block(
            "Запланированная нагрузка (ИС ВВГУ)",
            self.select_file1,
            "Прикрепить файл",
            self.file1_path,
            show_path=True
        )

        # === БЛОК 2: Отчёты кафедр ===
        self.create_block(
            "Отчёты кафедр о нагрузке сотрудников",
            self.select_dir2,
            "Выбрать папку",
            self.dir2_path,
            show_count=True
        )

        # === БЛОК 3: Формирование отчёта ===
        self.create_block(
            "Формирование отчёта по контролю",
            self.start_processing,
            "Сформировать",
            None,
            show_status=True,
            show_output_dir=True
        )

    def create_block(self, title, command, button_text, path_var,
                     show_path=False, show_count=False, show_status=False,
                     show_output_dir=False):
        """Создаёт блок в корпоративных цветах ВВГУ"""
        frame = tk.Frame(self.root, bg=self.bg_color)
        frame.pack(fill="x", padx=20, pady=10)

        # Синяя панель с эффектом объема
        blue_panel = tk.Frame(frame, bg=self.blue_color,
                              relief="flat", borderwidth=0,
                              highlightbackground=self.blue_light,
                              highlightthickness=2)
        blue_panel.pack(fill="x")

        # Заголовок блока (белый текст на синем)
        title_label = tk.Label(blue_panel, text=title,
                               font=("Tahoma", 11, "bold"),
                               bg=self.blue_color,
                               fg="white",
                               anchor="w",
                               padx=15, pady=12)
        title_label.pack(fill="x")

        # Контейнер для содержимого
        content_frame = tk.Frame(blue_panel, bg=self.blue_color)
        content_frame.pack(fill="x", padx=15, pady=(0, 12))

        # === ЛЕВАЯ ЧАСТЬ: Кнопка + информация ===
        left_frame = tk.Frame(content_frame, bg=self.blue_color)
        left_frame.pack(side="left")

        # Оранжевая кнопка с черным текстом
        btn = tk.Button(left_frame, text=button_text,
                        command=command,
                        bg=self.orange_color,
                        fg=self.bg_color,
                        font=("Tahoma", 9, "bold"),
                        relief="raised",
                        borderwidth=2,
                        padx=20, pady=5,
                        cursor="hand2",
                        activebackground=self.orange_hover)
        btn.pack(side="left", padx=(0, 15))

        # Сохраняем ссылку на кнопку "Сформировать"
        if show_status:
            self.btn_generate = btn

        # Имя файла (для блока 1)
        if show_path and hasattr(self, 'file1_display'):
            file_label = tk.Label(left_frame, textvariable=self.file1_display,
                                  font=("Tahoma", 9),
                                  bg=self.blue_color,
                                  fg="white",
                                  anchor="w")
            file_label.pack(side="left")

        # Имя папки (для блока 2)
        if hasattr(self, 'dir2_display') and not show_path and not show_status:
            dir_label = tk.Label(left_frame, textvariable=self.dir2_display,
                                 font=("Tahoma", 9),
                                 bg=self.blue_color,
                                 fg="white",
                                 anchor="w")
            dir_label.pack(side="left")

        if show_output_dir and hasattr(self, 'output_dir_display'):
            output_label = tk.Label(left_frame, textvariable=self.output_dir_display,
                                    font=("Tahoma", 9),
                                    bg=self.blue_color,
                                    fg="#FFD700",  # золотой, чтобы отличалось
                                    anchor="w")
            output_label.pack(side="left", padx=(15, 0))

        # === ПРАВАЯ ЧАСТЬ: Счётчик или статус ===
        right_frame = tk.Frame(content_frame, bg=self.blue_color)
        right_frame.pack(side="right")

        # Счетчик файлов (для блока 2)
        if show_count:
            count_label = tk.Label(right_frame, text="Всего файлов:",
                                   font=("Tahoma", 10),
                                   bg=self.blue_color,
                                   fg="white")
            count_label.pack(side="left", padx=(0, 8))

            count_value = tk.Label(right_frame, textvariable=self.file_count,
                                   font=("Tahoma", 14, "bold"),
                                   bg=self.blue_color,
                                   fg="white",
                                   width=4)
            count_value.pack(side="left")

        # Статус (для блока 3)
        if show_status:
            # НОВАЯ кнопка выбора папки сохранения
            btn_save = tk.Button(right_frame, text="📁 Выбрать папку",
                                 command=self.select_output_dir,
                                 bg=self.orange_color,
                                 fg=self.text_dark,
                                 font=("Tahoma", 9, "bold"),
                                 relief="raised",
                                 borderwidth=2,
                                 padx=15, pady=3,
                                 cursor="hand2",
                                 activebackground=self.orange_hover)
            btn_save.pack(side="left", padx=(0, 15))

            status_label = tk.Label(right_frame, text="Статус:",
                                    font=("Tahoma", 10),
                                    bg=self.blue_color,
                                    fg="white")
            status_label.pack(side="left", padx=(0, 8))

            status_value = tk.Label(right_frame, textvariable=self.status_text,
                                    font=("Tahoma", 10, "bold"),
                                    bg=self.blue_color,
                                    fg="#FFD700")
            status_value.pack(side="left")

    def select_file1(self):
        if self.is_processing:
            messagebox.showwarning("Внимание", "Идёт обработка. Дождитесь завершения.")
            return

        path = filedialog.askopenfilename(
            title="Выберите Файл 1 (План из ИС ВВГУ)",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if path:
            self.file1_path.set(path)
            self.file1_display.set(f"📄 {os.path.basename(path)}")
            self._file1_full_path = path

    def select_dir2(self):
        if self.is_processing:
            messagebox.showwarning("Внимание", "Идёт обработка. Дождитесь завершения.")
            return

        path = filedialog.askdirectory(title="Выберите папку с отчётами кафедр")
        if path:
            self.dir2_path.set(path)
            self.dir2_display.set(f"📁 {os.path.basename(os.path.normpath(path))}")
            files = glob.glob(os.path.join(path, "*.xlsx"))
            self.file_count.set(len(files))

    def select_output_dir(self):
        if self.is_processing:
            messagebox.showwarning("Внимание", "Идёт обработка. Дождитесь завершения.")
            return

        path = filedialog.askdirectory(title="Выберите папку для сохранения результатов")
        if path:
            self.output_dir.set(path)
            self.output_dir_display.set(f"📁 {os.path.basename(os.path.normpath(path))}")

    def start_processing(self):
        if self.is_processing:
            return

        if not hasattr(self, '_file1_full_path') or not self._file1_full_path:
            messagebox.showerror("Ошибка", "Выберите файл с запланированной нагрузкой!")
            return

        if not self.dir2_path.get():
            messagebox.showerror("Ошибка", "Выберите папку с отчётами кафедр!")
            return

        if not self.output_dir.get():
            messagebox.showerror("Ошибка", "Выберите папку для сохранения результатов!")
            return

        self.is_processing = True
        self.status_text.set("Обработка...")
        self.btn_generate.config(state="disabled")

        thread = threading.Thread(target=self.run_processing, daemon=True)
        thread.start()

    def run_processing(self):
        try:
            print("🚀 Запуск процедуры сравнения нагрузки ППС ВВГУ...")

            file1_path = self._file1_full_path
            dir2_path = self.dir2_path.get()
            base_output_dir = self.output_dir.get()

            # Создаём папку для отчёта через сервис
            from service import WorkloadService
            service = WorkloadService()
            output_dir = service.create_report_folder(base_output_dir)

            # Обновляем отображение в GUI
            folder_name = os.path.basename(output_dir)
            self.output_dir_display.set(f"📁 {folder_name}")
            print(f"📂 Папка отчёта: {output_dir}")

            # Вызываем обработку через сервис
            result = service.process_workload(file1_path, dir2_path, output_dir)

            if not result.success:
                self.status_text.set("Ошибка")
                messagebox.showerror("Ошибка", result.error)
                return

            # Успех
            self.status_text.set("Готово")

            # Подсчитываем количество созданных файлов по кафедрам
            dept_count = len(result.department_report_paths) if hasattr(result, 'department_report_paths') else 0
            dept_msg = f"\n📊 Создано отчётов по кафедрам: {dept_count}" if dept_count > 0 else ""

            error_details = ""
            if result.errors:
                error_details = f"\n\n⚠️ Предупреждения:\n" + "\n".join(result.errors[:3])
                if len(result.errors) > 3:
                    error_details += f"\n... и ещё {len(result.errors) - 3} ошибок"

            messagebox.showinfo(
                "Успех",
                f"✅ Отчёты сформированы успешно!\n\n"
                f"👥 Всего проверено: {result.total_count} ППС\n"
                f"🔍 Требуют внимания: {result.mismatches}{dept_msg}\n\n"
                f"📁 Папка отчёта:\n{output_dir}"
                f"{error_details}"
            )

        except Exception as e:
            import traceback
            error_msg = f"{str(e)}\n\n{traceback.format_exc()}"
            print(f"\n❌ ОШИБКА: {error_msg}")
            self.status_text.set("Ошибка")
            messagebox.showerror("Ошибка", f"Произошла ошибка:\n{str(e)}")
        finally:
            self.is_processing = False
            self.btn_generate.config(state="normal")
            if self.status_text.get() != "Ошибка":
                self.status_text.set("Ожидание")


def main():
    root = tk.Tk()
    app = XPStyleApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()