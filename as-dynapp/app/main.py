import os
import queue
import tkinter as tk
import tkinter.font as tkfont
from tkinter import PhotoImage, messagebox, ttk

from constants import (
    APP_NAME,
    APP_VERSION,
    LABELS_GROUP,
    LABELS_TAG,
    LABELS_TIMERANGE,
    READY,
    VALUES_GROUP,
    VALUES_TAG,
    VALUES_TIMERANGE,
)
from CredentialManager import CredentialManager
from FieldDialog import FieldDialog
from LoginDialog import LoginDialog
from LogPanel import LogPanel
from ZDExtractor import ZDExtractor


class App:
    def __init__(self, project_base_path):
        self.project_base_path = project_base_path
        self.root = tk.Tk()

        # Drop-down menus
        self.labels_option_1 = LABELS_GROUP
        self.values_option_1 = VALUES_GROUP
        self.saved_custom_value_1 = ""

        self.labels_option_2 = LABELS_TAG
        self.values_option_2 = VALUES_TAG
        self.saved_custom_value_2 = ""

        self.labels_option_3 = LABELS_TIMERANGE
        self.values_option_3 = VALUES_TIMERANGE
        self.saved_custom_value_3 = ""

        self.menu_options_1 = tk.StringVar(value=self.labels_option_1[0])
        self.menu_options_2 = tk.StringVar(value=self.labels_option_2[0])
        self.menu_options_3 = tk.StringVar(value=self.labels_option_3[0])

        self.btn_submit = None
        self.pbar = None
        self.zd = None
        self.output_queue = queue.Queue()

    def confirm_and_run(self):
        selected_index_1 = self.labels_option_1.index(self.menu_options_1.get())
        selected_index_2 = self.labels_option_2.index(self.menu_options_2.get())
        selected_index_3 = self.labels_option_3.index(self.menu_options_3.get())
        selected_value_1 = self.values_option_1[selected_index_1]
        selected_value_2 = self.values_option_2[selected_index_2]
        selected_value_3 = self.values_option_3[selected_index_3]

        if selected_value_1 == "":
            custom_value_1 = FieldDialog(
                self.root, "Filtro sui GRUPPI", initial_value=self.saved_custom_value_1
            )
            if custom_value_1.result and custom_value_1.result["value"]:
                selected_value_1 = custom_value_1.result["value"]
                self.saved_custom_value_1 = selected_value_1
            else:
                return
        if selected_value_2 == "":
            custom_value_2 = FieldDialog(
                self.root,
                "Filtro sulle CATEGORIE/TAG",
                initial_value=self.saved_custom_value_2,
            )
            if custom_value_2.result and custom_value_2.result["value"]:
                selected_value_2 = custom_value_2.result["value"]
                self.saved_custom_value_2 = selected_value_2
            else:
                return
        if selected_value_3 == "":
            custom_value_3 = FieldDialog(
                self.root,
                "Filtro sull'INTERVALLO TEMPORALE",
                initial_value=self.saved_custom_value_3,
            )
            if custom_value_3.result and custom_value_3.result["value"]:
                selected_value_3 = custom_value_3.result["value"]
                self.saved_custom_value_3 = selected_value_3
            else:
                return

        message = (
            f"Hai selezionato:\n\n"
            f"{selected_value_1}\n\n"
            f"{selected_value_2}\n\n"
            f"{selected_value_3}\n\n\n"
            "Vuoi avviare l'estrazione?"
        )
        confirm = messagebox.askokcancel("Conferma selezioni", message)

        if confirm:
            # disable submit button meanwhile
            self.btn_submit.config(state="disabled")
            self.pbar.start(20)  # anim speed
            self.zd.run_query(selected_value_1, selected_value_2, selected_value_3)

    def task_completed(self):
        self.pbar.stop()
        self.btn_submit.config(state="normal")

    def sync_output(self):
        try:
            while True:
                msg = self.output_queue.get_nowait()
                print(msg, end="", flush=True)
        except queue.Empty:
            pass
        self.root.after(1000, self.sync_output)  # next check in 1s

    def start(self):
        # Setup root window
        self.root.title(f"{APP_NAME} {APP_VERSION}")
        icon_path = os.path.join(self.project_base_path, "pagopa.png")
        icon = PhotoImage(file=icon_path)
        self.root.iconphoto(True, icon)
        self.root.resizable(False, False)

        window_width = 800
        window_height = 768
        screen_width = self.root.winfo_screenwidth()
        scree_height = self.root.winfo_screenheight()
        pos_x = (screen_width - window_width) // 2
        pos_y = (scree_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")

        # Increase default font size by 30%
        default_font = tkfont.nametofont("TkDefaultFont")
        new_font_size = int(default_font.cget("size") * 1.3)
        default_font.configure(size=new_font_size)

        # ----- Main section -----
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, pady=30)

        # Title
        title = tk.Label(
            main_frame,
            text="ZD Estrattore Conversazioni Laterali",
            font=("Helvetica", 20, "bold"),
        )
        title.pack()

        # Subtitle
        subtitle = tk.Label(
            main_frame,
            text="Generazione file CSV delle conversazioni laterali email, secondo i filtri impostati",
            font=("Helvetica", 12),
        )
        subtitle.pack()

        menu_label_1 = tk.Label(main_frame, text="Selettore Gruppi")
        menu_label_1.pack(pady=(20, 0))
        menu_dropdown_1 = tk.OptionMenu(
            main_frame, self.menu_options_1, *self.labels_option_1
        )
        menu_dropdown_1.pack(pady=(10, 20))

        menu_label_2 = tk.Label(main_frame, text="Selettore Categorie/Tag")
        menu_label_2.pack()
        menu_dropdown_2 = tk.OptionMenu(
            main_frame, self.menu_options_2, *self.labels_option_2
        )
        menu_dropdown_2.pack(pady=(10, 20))

        menu_label_3 = tk.Label(main_frame, text="Selettore Intervallo temporale")
        menu_label_3.pack()
        menu_dropdown_3 = tk.OptionMenu(
            main_frame, self.menu_options_3, *self.labels_option_3
        )
        menu_dropdown_3.pack(pady=(10, 20))

        self.btn_submit = tk.Button(
            main_frame, text="\nProcedi...\n", command=self.confirm_and_run
        )
        self.btn_submit.pack(pady=20)
        self.pbar = ttk.Progressbar(
            main_frame, orient="horizontal", length=300, mode="indeterminate"
        )
        self.pbar.pack(pady=20)

        # ----- Log section -----
        log_frame = tk.Frame(self.root)
        log_frame.pack(fill=tk.X, side=tk.BOTTOM)
        LogPanel(log_frame)

        # ----- Retrieve/Set credentials for Zendesk -----
        cm = CredentialManager()
        print(f"{APP_NAME} {APP_VERSION}\n")
        try:
            creds = cm.get_credentials()
            bearer = creds["password"]
        except Exception as ex:
            print(ex)
            dialog = LoginDialog(self.root)
            if dialog.result and dialog.result["password"]:
                bearer = dialog.result["password"]
                if bool(bearer):
                    cm.set_credentials("as-zd-extractor", "zdpy.client", bearer)
            else:
                print("Login aborted... Exiting.")
                self.root.destroy()
                exit(0)

        self.zd = ZDExtractor(
            bearer, self.output_queue, lambda: self.root.after(0, self.task_completed)
        )
        print(READY)
        self.root.after(
            1000, self.sync_output
        )  # periodically sync output queue to stdout
        self.root.deiconify()  # bring window to top level
        self.root.mainloop()


def main(project_base_path):
    app = App(project_base_path)
    app.start()


if __name__ == "__main__":
    # this is just for running without an external launcher
    main(os.path.dirname(os.path.realpath(__file__)))
