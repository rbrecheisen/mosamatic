import tkinter as tk

from tkinter import ttk


class View:
    def __init__(self, root, controller):
        self.controller = controller
        self.setup_ui(root)

    def handle_button_click(self):
        file_dir = 'D:\\Mosamatic\\AutoSliceSelectionBibiToine\\L3s'
        self.controller.decompress_dicom(file_dir)

    def setup_ui(self, root):
        root.title("Mosamatic")
        root.geometry("400x200")

        self.label = tk.Label(root, text="Progress:")
        self.label.pack(pady=10)

        self.progress_bar = ttk.Progressbar(root, length=300, mode="determinate")
        self.progress_bar.pack(pady=10)

        self.start_button = ttk.Button(
            root, text='Decompress DICOM', command=self.handle_button_click
        )
        self.start_button.pack(pady=10)

    def update_progress(self, progress):
        self.progress_bar["value"] = progress
        self.label["text"] = f"Progress: {progress}%"
