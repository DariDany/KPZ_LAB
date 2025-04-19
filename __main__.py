# Імпортуємо потрібні бібліотеки
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

        self.setup_styles()

        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

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

        self.content_panel = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.content_panel.pack(fill=tk.BOTH, expand=True)

        self.code_frame = ttk.Frame(self.content_panel)
        self.content_panel.add(self.code_frame, weight=1)

        self.code_label = ttk.Label(self.code_frame, text="Код Python", font=('Helvetica', 10, 'bold'))
        self.code_label.pack(pady=(0, 5))

        self.code_text = scrolledtext.ScrolledText(
            self.code_frame, wrap=tk.WORD, width=50,
            font=('Consolas', 10) if platform.system() == 'Windows' else ('Monaco', 10))
        self.code_text.pack(fill=tk.BOTH, expand=True)

        self.diagram_frame = ttk.Frame(self.content_panel)
        self.content_panel.add(self.diagram_frame, weight=1)

        self.diagram_label = ttk.Label(self.diagram_frame, text="Блок-схема", font=('Helvetica', 10, 'bold'))
        self.diagram_label.pack(pady=(0, 5))

        # Контейнер для канваса та кнопки збереження
        self.diagram_container = ttk.Frame(self.diagram_frame)
        self.diagram_container.pack(fill=tk.BOTH, expand=True)

        # Канвас для відображення зображення
        self.diagram_canvas = tk.Canvas(
            self.diagram_container, bg="white",
            highlightthickness=1, highlightbackground="#ccc")
        self.diagram_canvas.pack(fill=tk.BOTH, expand=True)

        # Кнопка збереження блок-схеми (прихована за замовчуванням)
        self.save_button = ttk.Button(
            self.diagram_frame, text="Зберегти блок-схему",
            command=self.save_current_image)
        self.save_button.pack_forget()

        # Статус-бар (показує поточний стан)
        self.status_bar = ttk.Frame(self.main_frame)
        self.status_bar.pack(fill=tk.X, pady=(10, 0))

        self.status_label = ttk.Label(self.status_bar, text="Готово", foreground="gray")
        self.status_label.pack(side=tk.LEFT)

        # Ініціалізація внутрішніх змінних
        self.file_path = None
        self.flowchart_image = None
        self.current_image_path = None

        # Встановлення пропорцій між панелями
        self.content_panel.sashpos(0, int(self.root.winfo_width() * 0.4))

    def setup_styles(self):
        style = ttk.Style()
        style.configure('TButton', padding=6)
        style.configure('TLabel', padding=2)
        style.configure('TFrame', background='#f0f0f0')

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
        # Просте підсвічування синтаксису Python
        for tag in self.code_text.tag_names():
            self.code_text.tag_remove(tag, "1.0", tk.END)

        keywords = [
            'def', 'class', 'return', 'if', 'elif', 'else', 'for', 'while',
            'try', 'except', 'finally', 'with', 'import', 'from', 'as',
            'True', 'False', 'None', 'and', 'or', 'not', 'in', 'is'
        ]
        self.code_text.tag_configure("keyword", foreground="blue")
        self.code_text.tag_configure("string", foreground="green")
        self.code_text.tag_configure("comment", foreground="gray")

        # Пошук і підсвітка ключових слів
        text_content = self.code_text.get("1.0", tk.END)
        for word in keywords:
            start = "1.0"
            while True:
                start = self.code_text.search(rf'\y{word}\y', start, stopindex=tk.END, regexp=True)
                if not start:
                    break
                end = f"{start}+{len(word)}c"
                self.code_text.tag_add("keyword", start, end)
                start = end

        # Пошук і підсвітка рядків
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
        # Генерація блок-схеми з коду
        if not self.file_path:
            messagebox.showwarning("Помилка", "Будь ласка, оберіть файл .py")
            return

        try:
            self.status_label.config(text="Обробка файлу...")
            self.root.update()

            # Очищення старих файлів
            self.cleanup_old_files()

            # Обробка коду та генерація діаграми
            with open(self.file_path, 'r', encoding='utf-8') as f:
                p = PyPreprocessor(f)
                programs_list = p.get_programs_list()
                diagram = Py2BlockDiagram.build_from_programs_list(
                    programs_list, Py2PseudoCode, Py2BlockDiagram)

            # Збереження json та створення зображення через зовнішній скрипт
            base_name = os.path.splitext(self.file_path)[0]
            json_file_path = f'{base_name}.json'
            image_path = f'{base_name}.png'

            with open(json_file_path, 'w+', encoding='utf-8') as f:
                f.write(json.dumps(diagram, indent=4))

            self.status_label.config(text="Генерація блок-схеми...")
            self.root.update()

            subprocess.run([sys.executable, "JsonToImage.py", json_file_path], check=True)

            # Відображення зображення в інтерфейсі
            self.show_image(image_path)
            self.status_label.config(text="Блок-схему успішно створено")

        except FileNotFoundError:
            messagebox.showerror("Помилка", "Файл не знайдено")
            self.status_label.config(text="Помилка: файл не знайдено")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Помилка", f"Помилка при створенні блок-схеми:\n{e}")
            self.status_label.config(text="Помилка при генерації блок-схеми")
        except Exception as e:
            messagebox.showerror("Помилка", f"Щось пішло не так:\n{e}")
            self.status_label.config(text=f"Помилка: {str(e)}")

    def cleanup_old_files(self):
        # Видалення старих JSON та PNG файлів у директорії
        folder = os.path.dirname(self.file_path)
        for file in os.listdir(folder):
            if file.endswith(".json") or file.endswith(".png"):
                try:
                    os.remove(os.path.join(folder, file))
                except Exception as e:
                    print(f"Не вдалося видалити файл {file}: {e}")

    def show_image(self, image_path):
        # Відображення зображення блок-схеми на canvas
        try:
            self.current_image_path = image_path
            image = Image.open(image_path)

            canvas_width = self.diagram_canvas.winfo_width()
            canvas_height = self.diagram_canvas.winfo_height()

            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width = 700
                canvas_height = 500

            img_width, img_height = image.size

            scale = min(
                (canvas_width - 20) / img_width,
                (canvas_height - 20) / img_height
            )
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)

            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.flowchart_image = ImageTk.PhotoImage(resized_image)

            self.diagram_canvas.delete("all")
            self.diagram_canvas.create_image(
                canvas_width // 2, canvas_height // 2,
                anchor="center", image=self.flowchart_image
            )

            self.save_button.pack(pady=5)

        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося відкрити зображення:\n{e}")

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
