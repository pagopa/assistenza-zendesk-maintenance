import sys
import tkinter as tk
from tkinter import scrolledtext


class LogPanel:
    def __init__(self, parent):
        self.parent = parent
        self.text = scrolledtext.ScrolledText(parent, state="disabled", wrap=tk.WORD)
        self.text.pack(expand=True, fill=tk.X, padx=10, pady=5)

        # Save the original stdout/err pointers
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr

        # Redirect stdout/stderr
        sys.stdout = self
        sys.stderr = self

    def write(self, message):
        self.text.configure(state="normal")
        self.text.insert("end", message)
        self.text.see("end")
        self.text.configure(state="disabled")

    def flush(self):
        pass  # Certain flows need this for compatibility (eg. print)

    def close(self):
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
