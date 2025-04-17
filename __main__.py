# from PyPreprocessor import PyPreprocessor
# from Py2BlockDiagram import Py2BlockDiagram
# from Py2PseudoCode import Py2PseudoCode
# import sys
# import json
# import subprocess


# def main():
#     args = sys.argv[1::]

#     try:
#         file_path = args[0]
#         f = open(file_path, 'r', encoding='utf-8')
#     except:
#         try:
#             file_path = input('path: ')
#             f = open(file_path, 'r', encoding='utf-8')
#         except FileNotFoundError:
#             exit('wrong path')

#     p = PyPreprocessor(f)
#     programs_list = p.get_programs_list()
#     diagram = Py2BlockDiagram.build_from_programs_list(
#         programs_list, Py2PseudoCode, Py2BlockDiagram)

#     f.close()

#     json_file_path = f'{file_path}.json'
#     with open(json_file_path, 'w+', encoding='utf-8') as f:
#         f.write(json.dumps(diagram, indent=4))

#     print(f'Diagram has been saved as {json_file_path}')

#     # Виклик JsonToImage.py для створення блок-схеми
#     try:
#         subprocess.run([sys.executable, "JsonToImage.py",
#                        json_file_path], check=True)
#     except subprocess.CalledProcessError as e:
#         print(f"Помилка при створенні блок-схеми: {e}")


# if __name__ == "__main__":
#     main()

# import tkinter as tk
# from tkinter import filedialog, messagebox
# from PIL import Image, ImageTk
# import json
# import subprocess
# import os
# import sys
#
# from PyPreprocessor import PyPreprocessor
# from Py2BlockDiagram import Py2BlockDiagram
# from Py2PseudoCode import Py2PseudoCode
#
#
# class DiagramApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Генератор блок-схем")
#         self.root.geometry("800x600")
#
#         self.file_path = None
#         self.image_label = None
#
#         self.choose_button = tk.Button(
#             root, text="Вибрати файл", command=self.choose_file)
#         self.choose_button.pack(pady=10)
#
#         self.file_label = tk.Label(root, text="Файл не обрано", fg="gray")
#         self.file_label.pack(pady=5)
#
#         self.generate_button = tk.Button(
#             root, text="Створити діаграму", command=self.generate_diagram)
#         self.generate_button.pack(pady=10)
#
#         self.image_canvas = tk.Canvas(root, width=760, height=500, bg="white")
#         self.image_canvas.pack(pady=10)
#
#         self.flowchart_image = None  # Для зберігання зображення, щоб не було кешування
#
#     def choose_file(self):
#         file_path = filedialog.askopenfilename(
#             filetypes=[("Python files", "*.py")])
#         if file_path:
#             self.file_path = file_path
#             self.file_label.config(text=f"Обрано: {file_path}", fg="black")
#
#     def generate_diagram(self):
#         if not self.file_path:
#             messagebox.showwarning("Помилка", "Будь ласка, оберіть файл .py")
#             return
#
#         try:
#             self.cleanup_old_files()
#             with open(self.file_path, 'r', encoding='utf-8') as f:
#                 p = PyPreprocessor(f)
#                 programs_list = p.get_programs_list()
#                 diagram = Py2BlockDiagram.build_from_programs_list(
#                     programs_list, Py2PseudoCode, Py2BlockDiagram)
#
#             base_name = os.path.splitext(self.file_path)[0]  # без .py
#             json_file_path = f'{base_name}.json'
#             image_path = f'{base_name}.png'
#             with open(json_file_path, 'w+', encoding='utf-8') as f:
#                 f.write(json.dumps(diagram, indent=4))
#
#             subprocess.run([sys.executable, "JsonToImage.py",
#                            json_file_path], check=True)
#
#             self.show_image(image_path)
#
#         except FileNotFoundError:
#             messagebox.showerror("Помилка", "Файл не знайдено")
#         except subprocess.CalledProcessError as e:
#             messagebox.showerror(
#                 "Помилка", f"Помилка при створенні блок-схеми:\n{e}")
#         except Exception as e:
#             messagebox.showerror("Помилка", f"Щось пішло не так:\n{e}")
#
#     def cleanup_old_files(self):
#         folder = os.path.dirname(self.file_path)
#         for file in os.listdir(folder):
#             if file.endswith(".json") or file.endswith(".png"):
#                 try:
#                     os.remove(os.path.join(folder, file))
#                 except Exception as e:
#                     print(f"Не вдалося видалити файл {file}: {e}")
#
#     def show_image(self, image_path):
#         try:
#             image = Image.open(image_path)
#
#             # Отримати розміри Canvas
#             canvas_width = self.image_canvas.winfo_width()
#             canvas_height = self.image_canvas.winfo_height()
#
#             # Якщо Canvas ще не відображено — змусити оновити GUI
#             if canvas_width == 1 and canvas_height == 1:
#                 self.root.update()
#                 canvas_width = self.image_canvas.winfo_width()
#                 canvas_height = self.image_canvas.winfo_height()
#
#             # Отримати розміри зображення
#             img_width, img_height = image.size
#
#             # Обчислити коефіцієнт масштабування для збереження пропорцій
#             scale = min(canvas_width / img_width, canvas_height / img_height)
#             new_width = int(img_width * scale)
#             new_height = int(img_height * scale)
#
#             resized_image = image.resize(
#                 (new_width, new_height), Image.Resampling.LANCZOS)
#             self.flowchart_image = ImageTk.PhotoImage(resized_image)
#
#             self.image_canvas.delete("all")  # Очистити Canvas
#             self.image_canvas.create_image(
#                 canvas_width // 2, canvas_height // 2,
#                 anchor="center", image=self.flowchart_image
#             )
#         except Exception as e:
#             messagebox.showerror(
#                 "Помилка", f"Не вдалося відкрити зображення:\n{e}")
#
#
# if __name__ == "__main__":
#     root = tk.Tk()
#     app = DiagramApp(root)
#     root.mainloop()


import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from PIL import Image, ImageTk
import json
import subprocess
import os
import sys
import platform

from PyPreprocessor import PyPreprocessor
from Py2BlockDiagram import Py2BlockDiagram
from Py2PseudoCode import Py2PseudoCode


class DiagramApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор блок-схем з Python коду")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)

        # Налаштування стилів
        self.setup_styles()

        # Основний контейнер
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Верхня панель з кнопками
        self.top_panel = ttk.Frame(self.main_frame)
        self.top_panel.pack(fill=tk.X, pady=(0, 10))

        self.choose_button = ttk.Button(
            self.top_panel, text="Вибрати файл", command=self.choose_file)
        self.choose_button.pack(side=tk.LEFT, padx=5)

        self.generate_button = ttk.Button(
            self.top_panel, text="Створити діаграму", command=self.generate_diagram)
        self.generate_button.pack(side=tk.LEFT, padx=5)

        self.file_label = ttk.Label(self.top_panel, text="Файл не обрано", foreground="gray")
        self.file_label.pack(side=tk.LEFT, padx=10)

        # Панель для відображення вмісту
        self.content_panel = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.content_panel.pack(fill=tk.BOTH, expand=True)

        # Панель з кодом
        self.code_frame = ttk.Frame(self.content_panel)
        self.content_panel.add(self.code_frame, weight=1)

        self.code_label = ttk.Label(self.code_frame, text="Код Python", font=('Helvetica', 10, 'bold'))
        self.code_label.pack(pady=(0, 5))

        self.code_text = scrolledtext.ScrolledText(
            self.code_frame, wrap=tk.WORD, width=50,
            font=('Consolas', 10) if platform.system() == 'Windows' else ('Monaco', 10))
        self.code_text.pack(fill=tk.BOTH, expand=True)

        # Панель з блок-схемою
        self.diagram_frame = ttk.Frame(self.content_panel)
        self.content_panel.add(self.diagram_frame, weight=1)

        self.diagram_label = ttk.Label(self.diagram_frame, text="Блок-схема", font=('Helvetica', 10, 'bold'))
        self.diagram_label.pack(pady=(0, 5))

        # Контейнер для canvas та кнопки збереження
        self.diagram_container = ttk.Frame(self.diagram_frame)
        self.diagram_container.pack(fill=tk.BOTH, expand=True)

        self.diagram_canvas = tk.Canvas(
            self.diagram_container, bg="white",
            highlightthickness=1, highlightbackground="#ccc")
        self.diagram_canvas.pack(fill=tk.BOTH, expand=True)

        # Кнопка збереження (створюється один раз)
        self.save_button = ttk.Button(
            self.diagram_frame, text="Зберегти блок-схему",
            command=self.save_current_image)
        self.save_button.pack_forget()  # Спочатку прихована

        # Статус бар
        self.status_bar = ttk.Frame(self.main_frame)
        self.status_bar.pack(fill=tk.X, pady=(10, 0))

        self.status_label = ttk.Label(self.status_bar, text="Готово", foreground="gray")
        self.status_label.pack(side=tk.LEFT)

        self.file_path = None
        self.flowchart_image = None
        self.current_image_path = None  # Шлях до поточного зображення

        # Початкове розділення панелей
        self.content_panel.sashpos(0, int(self.root.winfo_width() * 0.4))

    def setup_styles(self):
        style = ttk.Style()
        style.configure('TButton', padding=6)
        style.configure('TLabel', padding=2)
        style.configure('TFrame', background='#f0f0f0')

        # Кольори для темної теми (можна змінити)
        self.root.tk_setPalette(
            background='#f0f0f0',
            foreground='black',
            activeBackground='#d9d9d9',
            activeForeground='black'
        )

    def choose_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Python files", "*.py"), ("All files", "*.*")])
        if file_path:
            self.file_path = file_path
            self.file_label.config(text=f"Обрано: {os.path.basename(file_path)}")
            self.status_label.config(text="Файл завантажено")
            self.display_file_content(file_path)

    def display_file_content(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            self.code_text.delete(1.0, tk.END)
            self.code_text.insert(tk.END, content)
            self.highlight_syntax()

        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося прочитати файл:\n{e}")

    def highlight_syntax(self):
        # Спочатку видаляємо всі старі теги
        for tag in self.code_text.tag_names():
            self.code_text.tag_remove(tag, "1.0", tk.END)

        # Проста підсвітка ключових слів Python
        keywords = [
            'def', 'class', 'return', 'if', 'elif', 'else', 'for', 'while',
            'try', 'except', 'finally', 'with', 'import', 'from', 'as',
            'True', 'False', 'None', 'and', 'or', 'not', 'in', 'is'
        ]

        # Налаштовуємо стилі тегів
        self.code_text.tag_configure("keyword", foreground="blue")
        self.code_text.tag_configure("string", foreground="green")
        self.code_text.tag_configure("comment", foreground="gray")

        # Отримуємо весь текст
        text_content = self.code_text.get("1.0", tk.END)

        # Підсвітка ключових слів
        for word in keywords:
            start = "1.0"
            while True:
                start = self.code_text.search(rf'\y{word}\y', start, stopindex=tk.END, regexp=True)
                if not start:
                    break
                end = f"{start}+{len(word)}c"
                self.code_text.tag_add("keyword", start, end)
                start = end

        # Підсвітка рядків
        start = "1.0"
        while True:
            start = self.code_text.search(r'["\']', start, stopindex=tk.END)
            if not start:
                break
            quote_char = self.code_text.get(start)
            end = self.code_text.search(quote_char, f"{start}+1c", stopindex=tk.END)
            if not end:
                break
            self.code_text.tag_add("string", start, f"{end}+1c")
            start = f"{end}+1c"

        # Підсвітка коментарів
        start = "1.0"
        while True:
            start = self.code_text.search('#', start, stopindex=tk.END)
            if not start:
                break
            end = self.code_text.search(r'$', start, stopindex=tk.END)
            if end:
                self.code_text.tag_add("comment", start, end)
            start = end if end else tk.END

    def generate_diagram(self):
        if not self.file_path:
            messagebox.showwarning("Помилка", "Будь ласка, оберіть файл .py")
            return

        try:
            self.status_label.config(text="Обробка файлу...")
            self.root.update()

            self.cleanup_old_files()
            with open(self.file_path, 'r', encoding='utf-8') as f:
                p = PyPreprocessor(f)
                programs_list = p.get_programs_list()
                diagram = Py2BlockDiagram.build_from_programs_list(
                    programs_list, Py2PseudoCode, Py2BlockDiagram)

            base_name = os.path.splitext(self.file_path)[0]  # без .py
            json_file_path = f'{base_name}.json'
            image_path = f'{base_name}.png'

            with open(json_file_path, 'w+', encoding='utf-8') as f:
                f.write(json.dumps(diagram, indent=4))

            self.status_label.config(text="Генерація блок-схеми...")
            self.root.update()

            subprocess.run([sys.executable, "JsonToImage.py",
                            json_file_path], check=True)

            self.show_image(image_path)
            self.status_label.config(text="Блок-схему успішно створено")

        except FileNotFoundError:
            messagebox.showerror("Помилка", "Файл не знайдено")
            self.status_label.config(text="Помилка: файл не знайдено")
        except subprocess.CalledProcessError as e:
            messagebox.showerror(
                "Помилка", f"Помилка при створенні блок-схеми:\n{e}")
            self.status_label.config(text="Помилка при генерації блок-схеми")
        except Exception as e:
            messagebox.showerror("Помилка", f"Щось пішло не так:\n{e}")
            self.status_label.config(text=f"Помилка: {str(e)}")

    def cleanup_old_files(self):
        folder = os.path.dirname(self.file_path)
        for file in os.listdir(folder):
            if file.endswith(".json") or file.endswith(".png"):
                try:
                    os.remove(os.path.join(folder, file))
                except Exception as e:
                    print(f"Не вдалося видалити файл {file}: {e}")

    def show_image(self, image_path):
        try:
            self.current_image_path = image_path  # Зберігаємо поточний шлях
            image = Image.open(image_path)

            # Отримати розміри Canvas
            canvas_width = self.diagram_canvas.winfo_width()
            canvas_height = self.diagram_canvas.winfo_height()

            # Якщо Canvas ще не відображено
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width = 700
                canvas_height = 500

            # Отримати розміри зображення
            img_width, img_height = image.size

            # Обчислити коефіцієнт масштабування для збереження пропорцій
            scale = min(
                (canvas_width - 20) / img_width,
                (canvas_height - 20) / img_height
            )
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)

            resized_image = image.resize(
                (new_width, new_height), Image.Resampling.LANCZOS)
            self.flowchart_image = ImageTk.PhotoImage(resized_image)

            self.diagram_canvas.delete("all")
            self.diagram_canvas.create_image(
                canvas_width // 2, canvas_height // 2,
                anchor="center", image=self.flowchart_image
            )

            # Показуємо кнопку збереження
            self.save_button.pack(pady=5)

        except Exception as e:
            messagebox.showerror(
                "Помилка", f"Не вдалося відкрити зображення:\n{e}")

    def save_current_image(self):
        if self.current_image_path:
            self.save_image(self.current_image_path)

    def save_image(self, image_path):
        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            initialfile=os.path.basename(image_path)
        )
        if save_path:
            try:
                import shutil
                shutil.copyfile(image_path, save_path)
                messagebox.showinfo("Успіх", f"Зображення збережено у:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося зберегти зображення:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = DiagramApp(root)
    root.mainloop()