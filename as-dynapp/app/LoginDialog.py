import tkinter as tk
from tkinter import simpledialog


class LoginDialog(simpledialog.Dialog):
    def body(self, master):
        self.title("Zendesk Bearer Token")

        tk.Label(master, text="Token:").grid(row=0, sticky="e")
        self.password_entry = tk.Entry(master, width=45, show="*")
        self.password_entry.grid(row=0, column=1)

        return self.password_entry

    def apply(self):
        self.result = {"password": self.password_entry.get()}
