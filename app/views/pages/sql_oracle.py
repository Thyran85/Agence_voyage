from tkinter import messagebox

import customtkinter as ctk

from app.views.components import DataTable, PageHeader
from app.views.theme import COLORS, MONO_FAMILY, app_font


class QueryExamplesFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color=COLORS["background"])
        self.controller = controller
        self.examples = dict(controller.query_examples())

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        PageHeader(
            self,
            "SQL Oracle",
            "Exemples pédagogiques et exécution directe de requêtes de lecture.",
            "Exécuter",
            self.run_current,
        ).grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 16))
        self.selector = self._build_selector()
        self.selector.grid(row=1, column=0, padx=24, pady=(0, 12), sticky="w")
        self.sql_box = ctk.CTkTextbox(
            self,
            height=150,
            fg_color=COLORS["surface_low"],
            border_color=COLORS["border"],
            border_width=1,
            text_color=COLORS["primary"],
            font=app_font(12, family=MONO_FAMILY),
            corner_radius=8,
        )
        self.sql_box.grid(row=2, column=0, padx=24, pady=(0, 12), sticky="ew")
        self.table = DataTable(self)
        self.table.grid(row=3, column=0, padx=24, pady=(0, 24), sticky="nsew")
        self.load_example(self.selector.get())

    def _build_selector(self):
        return ctk.CTkOptionMenu(
            self,
            values=list(self.examples.keys()),
            command=self.load_example,
            fg_color=COLORS["surface_high"],
            button_color=COLORS["surface_highest"],
            button_hover_color=COLORS["primary_container"],
            text_color=COLORS["text"],
            dropdown_fg_color=COLORS["surface"],
            dropdown_hover_color=COLORS["surface_high"],
            corner_radius=8,
            font=app_font(12),
        )

    def load_example(self, name):
        self.sql_box.delete("1.0", "end")
        self.sql_box.insert("1.0", self.examples[name].strip())
        self.run_current()

    def run_current(self):
        try:
            rows = self.controller.run_query(self.sql_box.get("1.0", "end").strip())
            self.table.set_rows(rows)
        except Exception as error:
            messagebox.showerror("Requête impossible", str(error))
