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

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import json
import subprocess
import os
import sys

from PyPreprocessor import PyPreprocessor
from Py2BlockDiagram import Py2BlockDiagram
from Py2PseudoCode import Py2PseudoCode


class DiagramApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор блок-схем")
        self.root.geometry("800x600")

        self.file_path = None
        self.image_label = None

        self.choose_button = tk.Button(
            root, text="Вибрати файл", command=self.choose_file)
        self.choose_button.pack(pady=10)

        self.file_label = tk.Label(root, text="Файл не обрано", fg="gray")
        self.file_label.pack(pady=5)

        self.generate_button = tk.Button(
            root, text="Створити діаграму", command=self.generate_diagram)
        self.generate_button.pack(pady=10)

        self.image_canvas = tk.Canvas(root, width=760, height=500, bg="white")
        self.image_canvas.pack(pady=10)

        self.flowchart_image = None  # Для зберігання зображення, щоб не було кешування

    def choose_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Python files", "*.py")])
        if file_path:
            self.file_path = file_path
            self.file_label.config(text=f"Обрано: {file_path}", fg="black")

    def generate_diagram(self):
        if not self.file_path:
            messagebox.showwarning("Помилка", "Будь ласка, оберіть файл .py")
            return

        try:
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

            subprocess.run([sys.executable, "JsonToImage.py",
                           json_file_path], check=True)

            self.show_image(image_path)

        except FileNotFoundError:
            messagebox.showerror("Помилка", "Файл не знайдено")
        except subprocess.CalledProcessError as e:
            messagebox.showerror(
                "Помилка", f"Помилка при створенні блок-схеми:\n{e}")
        except Exception as e:
            messagebox.showerror("Помилка", f"Щось пішло не так:\n{e}")

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
            image = Image.open(image_path)

            # Отримати розміри Canvas
            canvas_width = self.image_canvas.winfo_width()
            canvas_height = self.image_canvas.winfo_height()

            # Якщо Canvas ще не відображено — змусити оновити GUI
            if canvas_width == 1 and canvas_height == 1:
                self.root.update()
                canvas_width = self.image_canvas.winfo_width()
                canvas_height = self.image_canvas.winfo_height()

            # Отримати розміри зображення
            img_width, img_height = image.size

            # Обчислити коефіцієнт масштабування для збереження пропорцій
            scale = min(canvas_width / img_width, canvas_height / img_height)
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)

            resized_image = image.resize(
                (new_width, new_height), Image.Resampling.LANCZOS)
            self.flowchart_image = ImageTk.PhotoImage(resized_image)

            self.image_canvas.delete("all")  # Очистити Canvas
            self.image_canvas.create_image(
                canvas_width // 2, canvas_height // 2,
                anchor="center", image=self.flowchart_image
            )
        except Exception as e:
            messagebox.showerror(
                "Помилка", f"Не вдалося відкрити зображення:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = DiagramApp(root)
    root.mainloop()
