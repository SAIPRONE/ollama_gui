import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from file_handler import FileHandler
from model_manager import ModelManager
from PIL import Image, ImageTk

class CodeLlamaApp:
    def __init__(self, root):
        self.root = root
        self.model_manager = ModelManager(self)
        self.file_handler = FileHandler(self)
        self.loading = False
        self.api_files = []

        self.root.title("CodeLlama Assistant")
        self.root.geometry("800x600")
        self.center_window(self.root, 800, 600)

        self.create_menu()
        self.create_widgets()
        self.bind_shortcuts()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        self.file_menu = tk.Menu(menubar, tearoff=0)
        self.file_menu.add_command(label="Open", command=self.file_handler.open_file)
        self.file_menu.add_command(label="Save", command=self.file_handler.save_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Settings", command=self.open_settings)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=self.file_menu)
        
        self.edit_menu = tk.Menu(menubar, tearoff=0)
        self.edit_menu.add_command(label="Cut", command=self.cut_text)
        self.edit_menu.add_command(label="Copy", command=self.copy_text)
        self.edit_menu.add_command(label="Paste", command=self.paste_text)
        menubar.add_cascade(label="Edit", menu=self.edit_menu)
        
        self.data_menu = tk.Menu(menubar, tearoff=0)
        self.data_menu.add_command(label="Load Text", command=self.file_handler.load_text_file)
        self.data_menu.add_command(label="Load XAML", command=self.file_handler.load_xaml_file)
        self.data_menu.add_command(label="Load JSON", command=self.file_handler.load_json_file)
        self.data_menu.add_command(label="Load HTML", command=self.file_handler.load_html_file)
        menubar.add_cascade(label="Data", menu=self.data_menu)
        
        self.model_menu = tk.Menu(menubar, tearoff=0)
        self.model_menu.add_command(label="Load Model", command=self.load_model)
        self.model_menu.add_command(label="Update Model", command=self.model_manager.update_model)
        self.model_menu.add_command(label="Train Model", command=self.start_training)
        self.model_menu.add_command(label="Check Memory", command=self.model_manager.check_memory)
        menubar.add_cascade(label="Model", menu=self.model_menu)
        
        self.help_menu = tk.Menu(menubar, tearoff=0)
        self.help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=self.help_menu)
        
        self.root.config(menu=menubar)

    def create_widgets(self):
        # Text output field
        self.text_output = tk.Text(self.root, wrap=tk.WORD, state=tk.DISABLED)
        self.text_output.pack(expand=True, fill=tk.BOTH)

        # Status bar
        self.status_label = tk.Label(self.root, text="Status: Ready", anchor=tk.W)
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)

        # Input field frame
        self.input_frame = tk.Frame(self.root)
        self.input_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # Clip button
        clip_image = Image.open("./icons/clip.png")
        clip_image = clip_image.resize((20, 20), Image.LANCZOS)
        self.clip_image = ImageTk.PhotoImage(clip_image)
        self.clip_button = tk.Button(self.input_frame, image=self.clip_image, command=self.load_file)
        self.clip_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Input text field
        self.text_input = tk.Text(self.input_frame, height=2)
        self.text_input.pack(expand=True, fill=tk.X, side=tk.LEFT, padx=5, pady=5)
        self.text_input.bind("<Return>", self.on_enter)
        self.text_input.bind("<Shift-Return>", self.newline)
        self.text_input.bind("<KeyRelease>", self.adjust_text_input_height)

        # Load the up arrow image
        arrow_image = Image.open("./icons/up_arrow.png")
        arrow_image = arrow_image.resize((20, 20), Image.LANCZOS)
        self.arrow_image = ImageTk.PhotoImage(arrow_image)

        # Send button
        self.send_button = tk.Button(self.input_frame, image=self.arrow_image, command=self.send_message, borderwidth=0)
        self.send_button.pack(side=tk.RIGHT, padx=5, pady=5)

        # Progress bar
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(fill=tk.X, side=tk.BOTTOM)

    def on_enter(self, event):
        self.send_message()
        return "break"

    def newline(self, event):
        self.text_input.insert(tk.END, "\n")
        self.adjust_text_input_height()
        return "break"

    def send_message(self):
        prompt = self.text_input.get("1.0", tk.END).strip()
        self.text_input.delete("1.0", tk.END)
        if prompt:
            self.update_status(f"Sending prompt to model...")
            response = self.model_manager.generate_response(prompt)
            self.display_message(f"User: {prompt}\nAssistant: {response}\n")

    def display_message(self, message):
        self.text_output.config(state=tk.NORMAL)
        self.text_output.insert(tk.END, message + "\n")
        self.text_output.config(state=tk.DISABLED)
        self.text_output.yview(tk.END)

    def update_status(self, status):
        self.status_label.config(text=f"Status: {status}")

    def load_model(self):
        if self.loading:
            messagebox.showwarning("Warning", "Model is already loading. Please wait.")
            return

        model_path = filedialog.askdirectory(title="Select Model Directory")
        tokenizer_path = filedialog.askopenfilename(title="Select Tokenizer File", filetypes=(("Model Files", "*.model"), ("All Files", "*.*")))
        if model_path and tokenizer_path:
            ckpt_dir = filedialog.askdirectory(title="Select Checkpoint Directory")
            max_seq_len = simpledialog.askinteger("Input", "Enter max sequence length (1024 recommended):", initialvalue=1024, minvalue=1, maxvalue=4096)
            max_batch_size = simpledialog.askinteger("Input", "Enter max batch size (1 recommended):", initialvalue=1, minvalue=1, maxvalue=128)
            self.progress.start()
            self.model_manager.load_model(model_path, tokenizer_path, ckpt_dir, max_seq_len, max_batch_size)

    def load_file(self):
        file_paths = filedialog.askopenfilenames()
        if file_paths:
            self.update_status(f"Selected files: {file_paths}")

    def show_help(self):
        messagebox.showinfo("Help", "This is a help message.")
        
    def bind_shortcuts(self):
        self.root.bind("<Control-f>", self.open_file_menu)  # Ctrl+F for File menu
        self.root.bind("<Control-l>", lambda event: self.file_handler.open_file())  # Ctrl+L for loading file
        self.root.bind("<F1>", lambda event: self.show_about())  # F1 for Help

    def center_window(self, window, width=800, height=600):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        window.geometry(f'{width}x{height}+{int(x)}+{int(y)}')

    def open_file_menu(self, event=None):
        x = self.root.winfo_rootx()
        y = self.root.winfo_rooty()
        self.file_menu.post(x, y + 30)  # Adjust the y offset to position the menu correctly
        return "break"

    def cut_text(self):
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.text_input.selection_get())
            self.text_input.delete("sel.first", "sel.last")
        except tk.TclError:
            pass  # Handle the case where no text is selected

    def copy_text(self):
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.text_input.selection_get())
        except tk.TclError:
            pass  # Handle the case where no text is selected

    def paste_text(self):
        self.text_input.insert(tk.INSERT, self.root.clipboard_get())

    def open_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        self.center_window(settings_window, 400, 300)  # Center the settings window

        # Dark mode toggle
        dark_mode_var = tk.BooleanVar(value=False)
        dark_mode_check = tk.Checkbutton(settings_window, text="Dark Mode", variable=dark_mode_var, command=lambda: self.toggle_dark_mode(dark_mode_var.get()))
        dark_mode_check.pack(padx=10, pady=10)

    def toggle_dark_mode(self, enabled):
        if enabled:
            self.root.config(bg="black")
            self.text_output.config(bg="black", fg="white", insertbackground="white")
            self.text_input.config(bg="black", fg="white", insertbackground="white")
            self.status_label.config(bg="black", fg="white")
        else:
            self.root.config(bg="white")
            self.text_output.config(bg="white", fg="black", insertbackground="black")
            self.text_input.config(bg="white", fg="black", insertbackground="black")
            self.status_label.config(bg="white", fg="black")

    def show_about(self):
        about_window = tk.Toplevel(self.root)
        about_window.title("About")
        self.center_window(about_window, 300, 200)  # Center the about window
        tk.Label(about_window, text="CodeLlama Assistant v1.0 \nAuthor: Fadi Helal\nDate: 31.05.2024").pack(padx=10, pady=10)

    def attach_files(self, file_paths):
        self.api_files.extend(file_paths)
        messagebox.showinfo("Info", f"Attached files: {', '.join(file_paths)}")

    def start_training(self):
        if not self.api_files:
            messagebox.showwarning("Warning", "No API files attached.")
            return

        training_data = []
        for file_path in self.api_files:
            api_methods = preprocess_api_file(file_path)
            for method in api_methods:
                training_data.append({"text": self.format_api_method(method)})
        
        # Simulating a dataset for the purpose of this example
        from datasets import Dataset
        train_data = Dataset.from_dict({"text": [item["text"] for item in training_data]})
        self.model_manager.train_model(train_data)

    def format_api_method(self, method):
        # Convert the API method information to a format suitable for training
        return f"{method['name']}({', '.join(method['params'])}) -> {method['returns']}: {method['description']}"

    def adjust_text_input_height(self, event=None):
        lines = int(self.text_input.index('end-1c').split('.')[0])
        self.text_input.configure(height=lines)

if __name__ == "__main__":
    root = tk.Tk()
    app = CodeLlamaApp(root)
    root.mainloop()
