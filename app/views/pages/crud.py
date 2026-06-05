from tkinter import filedialog, messagebox

import customtkinter as ctk

from app.views.components import DataTable, PageHeader, Panel
from app.views.form_utils import parse_value
from app.views.theme import COLORS, app_font


class CrudFrame(ctk.CTkFrame):
    def __init__(self, master, title, subtitle, repository, id_column, fields, search_options, sort_options):
        super().__init__(master, fg_color=COLORS["background"])
        self.repository = repository
        self.id_column = id_column
        self.fields = fields
        self.search_options = search_options
        self.sort_options = sort_options
        self.entries = {}

        self.grid_columnconfigure(0, weight=0, minsize=360)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        PageHeader(self, title, subtitle, "Actualiser", self.refresh).grid(
            row=0, column=0, columnspan=2, sticky="ew", padx=24, pady=(24, 16)
        )
        self._build_form_panel()
        self._build_table_panel()
        self.refresh()

    def _build_form_panel(self):
        form = Panel(self)
        form.grid(row=1, column=0, padx=(24, 12), pady=(0, 24), sticky="nsew")
        form.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(form, text="FICHE", text_color=COLORS["primary"], font=app_font(16, "bold")).grid(
            row=0, column=0, padx=16, pady=(16, 4), sticky="w"
        )
        ctk.CTkLabel(
            form,
            text="Renseignez les champs puis utilisez les actions ci-dessous.",
            text_color=COLORS["muted"],
            font=app_font(12),
            wraplength=300,
            justify="left",
        ).grid(row=1, column=0, padx=16, pady=(0, 12), sticky="w")

        for index, field in enumerate(self.fields, start=2):
            self._build_field(form, index, field)

        actions = ctk.CTkFrame(form, fg_color="transparent")
        actions.grid(row=len(self.fields) + 2, column=0, padx=16, pady=(16, 16), sticky="ew")
        actions.grid_columnconfigure((0, 1), weight=1)
        self._action_button(actions, "Ajouter", self.create_item, COLORS["primary_container"], 0, 0)
        self._action_button(actions, "Modifier", self.update_item, COLORS["surface_high"], 0, 1)
        self._action_button(actions, "Supprimer", self.delete_item, COLORS["danger"], 1, 0, COLORS["danger_text"])
        self._action_button(actions, "Effacer", self.clear_form, COLORS["surface_high"], 1, 1)

    def _build_field(self, master, index, field):
        group = ctk.CTkFrame(master, fg_color="transparent")
        group.grid(row=index, column=0, padx=16, pady=6, sticky="ew")
        group.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            group,
            text=field["label"].upper(),
            text_color=COLORS["muted"],
            font=app_font(11, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))
        entry = ctk.CTkEntry(
            group,
            height=34,
            fg_color=COLORS["background"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
            placeholder_text=field.get("placeholder", ""),
            corner_radius=8,
            font=app_font(13),
        )
        entry.grid(row=1, column=0, sticky="ew")
        self.entries[field["name"]] = entry
        if field.get("type") == "file":
            entry.grid(row=1, column=0, sticky="ew", padx=(0, 100))
            ctk.CTkButton(
                group,
                text="Parcourir",
                command=lambda field_name=field["name"]: self._choose_file(field_name),
                width=92,
                height=34,
                fg_color=COLORS["surface_high"],
                hover_color=COLORS["surface_highest"],
                text_color=COLORS["text"],
                corner_radius=8,
                font=app_font(12, "bold"),
            ).grid(row=1, column=0, sticky="e")

    def _choose_file(self, field_name):
        path = filedialog.askopenfilename(
            title="Choisir une image",
            filetypes=[
                ("Images", "*.png *.gif *.jpg *.jpeg *.webp"),
                ("Tous les fichiers", "*.*"),
            ],
        )
        if not path:
            return
        entry = self.entries[field_name]
        entry.delete(0, "end")
        entry.insert(0, path)

    def _build_table_panel(self):
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=1, padx=(12, 24), pady=(0, 24), sticky="nsew")
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=1)

        tools = Panel(content)
        tools.grid(row=0, column=0, pady=(0, 12), sticky="ew")
        tools.grid_columnconfigure(1, weight=1)
        self.search_by = self._option_menu(tools, list(self.search_options.keys()) or [""])
        self.search_by.grid(row=0, column=0, padx=12, pady=12, sticky="w")
        self.search_entry = ctk.CTkEntry(
            tools,
            placeholder_text="Rechercher dans la base...",
            fg_color=COLORS["background"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
            corner_radius=8,
            height=34,
        )
        self.search_entry.grid(row=0, column=1, padx=8, pady=12, sticky="ew")
        self._tool_button(tools, "Rechercher", self.refresh, 0, 2)

        self.sort_by = self._option_menu(tools, list(self.sort_options.keys()) or [""])
        self.sort_by.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="w")
        self.sort_dir = ctk.CTkSegmentedButton(
            tools,
            values=["ASC", "DESC"],
            selected_color=COLORS["primary_container"],
            selected_hover_color=COLORS["primary_container"],
            unselected_color=COLORS["surface_high"],
            unselected_hover_color=COLORS["surface_highest"],
            text_color=COLORS["text"],
            corner_radius=8,
            font=app_font(12, "bold"),
        )
        self.sort_dir.set("ASC")
        self.sort_dir.grid(row=1, column=1, padx=8, pady=(0, 12), sticky="w")

        self.table = self.create_table(content)
        self.table.grid(row=1, column=0, sticky="nsew")
        self.table.bind_select(self.fill_form)

    def create_table(self, master):
        return DataTable(master)

    def _option_menu(self, master, values):
        return ctk.CTkOptionMenu(
            master,
            values=values,
            fg_color=COLORS["surface_high"],
            button_color=COLORS["surface_highest"],
            button_hover_color=COLORS["primary_container"],
            text_color=COLORS["text"],
            dropdown_fg_color=COLORS["surface"],
            dropdown_hover_color=COLORS["surface_high"],
            corner_radius=8,
            font=app_font(12),
        )

    def _action_button(self, master, text, command, color, row, column, text_color=None):
        hover = COLORS["danger_hover"] if color == COLORS["danger"] else COLORS["surface_highest"]
        ctk.CTkButton(
            master,
            text=text,
            command=command,
            height=34,
            fg_color=color,
            hover_color=hover,
            text_color=text_color or COLORS["text"],
            corner_radius=8,
            font=app_font(12, "bold"),
        ).grid(row=row, column=column, padx=4, pady=4, sticky="ew")

    def _tool_button(self, master, text, command, row, column):
        ctk.CTkButton(
            master,
            text=text,
            command=command,
            height=34,
            fg_color=COLORS["primary_container"],
            hover_color="#004f56",
            text_color=COLORS["text"],
            corner_radius=8,
            font=app_font(12, "bold"),
        ).grid(row=row, column=column, padx=12, pady=12, sticky="e")

    def collect_form(self):
        return {
            field["name"]: parse_value(
                self.entries[field["name"]].get(),
                field.get("type", "str"),
            )
            for field in self.fields
        }

    def clear_form(self):
        for entry in self.entries.values():
            entry.delete(0, "end")

    def fill_form(self, _event=None):
        selected = self.table.selected_values()
        if not selected:
            return
        for field in self.fields:
            entry = self.entries[field["name"]]
            entry.delete(0, "end")
            value = selected.get(field["name"], "")
            if value is not None:
                entry.insert(0, str(value)[:10] if field.get("type") == "date" else str(value))

    def refresh(self):
        try:
            rows = self.repository.list(
                search_by=self.search_options.get(self.search_by.get()),
                search_value=self.search_entry.get().strip(),
                sort_by=self.sort_options.get(self.sort_by.get()),
                sort_dir=self.sort_dir.get(),
            )
            self.table.set_rows(rows)
        except Exception as error:
            messagebox.showerror("Erreur Oracle", str(error))

    def create_item(self):
        try:
            self.repository.create(self.collect_form())
            self.clear_form()
            self.refresh()
        except Exception as error:
            messagebox.showerror("Ajout impossible", str(error))

    def update_item(self):
        item_id = self.table.selected_id()
        if not item_id:
            messagebox.showinfo("Sélection requise", "Sélectionnez une ligne à modifier.")
            return
        try:
            self.repository.update(item_id, self.collect_form())
            self.refresh()
        except Exception as error:
            messagebox.showerror("Modification impossible", str(error))

    def delete_item(self):
        item_id = self.table.selected_id()
        if not item_id:
            messagebox.showinfo("Sélection requise", "Sélectionnez une ligne à supprimer.")
            return
        if not messagebox.askyesno("Confirmation", "Supprimer l'enregistrement sélectionné ?"):
            return
        try:
            self.repository.delete(item_id)
            self.clear_form()
            self.refresh()
        except Exception as error:
            messagebox.showerror("Suppression impossible", str(error))
