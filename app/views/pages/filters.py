from tkinter import messagebox

import customtkinter as ctk

from app.views.components import DataTable, PageHeader, Panel
from app.views.theme import COLORS, MONO_FAMILY, app_font


class FilterFrame(ctk.CTkFrame):
    def __init__(self, master, service):
        super().__init__(master, fg_color=COLORS["background"])
        self.service = service
        self.entries = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        PageHeader(
            self,
            "Filtres multicritères",
            "Explorer les voyages et réservations avec aperçu SQL généré.",
            "Filtrer",
            self.apply_filters,
        ).grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 16))

        self.mode = ctk.CTkSegmentedButton(
            self,
            values=["Voyages", "Réservations"],
            command=self.render_form,
            selected_color=COLORS["primary_container"],
            selected_hover_color=COLORS["primary_container"],
            unselected_color=COLORS["surface_high"],
            unselected_hover_color=COLORS["surface_highest"],
            text_color=COLORS["text"],
            corner_radius=8,
            font=app_font(12, "bold"),
        )
        self.mode.set("Voyages")
        self.mode.grid(row=1, column=0, padx=24, pady=(0, 12), sticky="w")

        self.form = Panel(self)
        self.form.grid(row=2, column=0, padx=24, pady=(0, 12), sticky="ew")
        self.sql_box = ctk.CTkTextbox(
            self,
            height=92,
            fg_color=COLORS["surface_low"],
            border_color=COLORS["border"],
            border_width=1,
            text_color=COLORS["primary"],
            font=app_font(12, family=MONO_FAMILY),
            corner_radius=8,
        )
        self.sql_box.grid(row=3, column=0, padx=24, pady=(0, 12), sticky="ew")
        self.table = DataTable(self)
        self.table.grid(row=4, column=0, padx=24, pady=(0, 24), sticky="nsew")
        self.render_form("Voyages")

    def render_form(self, _value):
        for child in self.form.winfo_children():
            child.destroy()
        self.entries = {}
        fields = (
            ["pays", "ville", "date_depart", "date_retour", "prix_min", "prix_max"]
            if self.mode.get() == "Voyages"
            else ["client", "voyage", "date_reservation", "montant_min", "montant_max"]
        )
        for index, field in enumerate(fields):
            self._build_filter_field(index, field)

    def _build_filter_field(self, index, field):
        column = index % 3
        row = index // 3
        self.form.grid_columnconfigure(column, weight=1)
        group = ctk.CTkFrame(self.form, fg_color="transparent")
        group.grid(row=row, column=column, padx=12, pady=10, sticky="ew")
        group.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(group, text=field.upper(), text_color=COLORS["muted"], font=app_font(11, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 4)
        )
        entry = ctk.CTkEntry(
            group,
            height=34,
            fg_color=COLORS["background"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
            corner_radius=8,
        )
        entry.grid(row=1, column=0, sticky="ew")
        self.entries[field] = entry

    def apply_filters(self):
        filters = {key: entry.get().strip() for key, entry in self.entries.items() if entry.get().strip()}
        try:
            if self.mode.get() == "Voyages":
                sql, rows = self.service.filter_voyages(filters)
            else:
                sql, rows = self.service.filter_reservations(filters)
            self.sql_box.delete("1.0", "end")
            self.sql_box.insert("1.0", " ".join(sql.split()))
            self.table.set_rows(rows)
        except Exception as error:
            messagebox.showerror("Filtrage impossible", str(error))
