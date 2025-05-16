import tkinter as tk
from tkinter import simpledialog


class FieldDialog(simpledialog.Dialog):
    def __init__(self, parent, label, title=None, initial_value=""):
        self.label = label
        self.initial_value = initial_value
        self.result = None
        super().__init__(parent, title=title)

    def body(self, master):
        self.title("Custom")

        tk.Label(master, text=f"{self.label}:").grid(row=0, sticky="e")
        self.value_entry = tk.Entry(master, width=90)
        self.value_entry.grid(row=0, column=1)

        self.value_entry.insert(0, self.initial_value)
        return self.value_entry

    def apply(self):
        self.result = {"value": self.value_entry.get()}
