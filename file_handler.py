import tkinter as tk
from tkinter import filedialog, messagebox

class FileHandler:
    def __init__(self, app):
        self.app = app

    def open_file(self):
        file_paths = filedialog.askopenfilenames()
        if file_paths:
            self.app.attach_files(file_paths)

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt")
        if file_path:
            with open(file_path, 'w') as file:
                content = self.app.text_output.get("1.0", tk.END)
                file.write(content)

    def load_text_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.app.text_input.delete("1.0", tk.END)
                self.app.text_input.insert("1.0", content)

    def load_xaml_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("XAML files", "*.xaml")])
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.app.text_input.delete("1.0", tk.END)
                self.app.text_input.insert("1.0", content)

    def load_json_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.app.text_input.delete("1.0", tk.END)
                self.app.text_input.insert("1.0", content)

    def load_html_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("HTML files", "*.html")])
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.app.text_input.delete("1.0", tk.END)
                self.app.text_input.insert("1.0", content)
