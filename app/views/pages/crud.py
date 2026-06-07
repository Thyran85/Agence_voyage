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
        self._select_mappings = {}

        self.grid_columnconfigure(0, weight=0, minsize=300)
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
        # make the form content scrollable so fields stay accessible on small windows
        scroll = ctk.CTkScrollableFrame(form, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        form.grid_rowconfigure(0, weight=1)

        ctk.CTkLabel(scroll, text="FICHE", text_color=COLORS["primary"], font=app_font(16, "bold")).grid(
            row=0, column=0, padx=16, pady=(16, 4), sticky="w"
        )
        ctk.CTkLabel(
            scroll,
            text="Renseignez les champs puis utilisez les actions ci-dessous.",
            text_color=COLORS["muted"],
            font=app_font(12),
            wraplength=300,
            justify="left",
        ).grid(row=1, column=0, padx=16, pady=(0, 12), sticky="w")

        for index, field in enumerate(self.fields, start=2):
            self._build_field(scroll, index, field)

        # action buttons stay fixed at the bottom of the form (outside the scrollable area)
        actions = ctk.CTkFrame(form, fg_color="transparent")
        actions.grid(row=1, column=0, padx=16, pady=(16, 16), sticky="ew")
        actions.grid_columnconfigure(0, weight=1)
        self._action_button(actions, "Ajouter", self.create_item, COLORS["primary_container"], 0, 0)
        self._action_button(actions, "Modifier", self.update_item, COLORS["surface_high"], 1, 0)
        self._action_button(actions, "Supprimer", self.delete_item, COLORS["danger"], 2, 0, COLORS["danger_text"])
        self._action_button(actions, "Effacer", self.clear_form, COLORS["surface_high"], 3, 0)

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
        # support for select/dropdown fields
        if field.get("type") == "select":
            values = []
            mapping = {}
            source = field.get("options_source")
            service = getattr(self, "service", None)
            if service and source and hasattr(service, source):
                try:
                    items = getattr(service, source).list()
                except Exception:
                    items = []
            else:
                items = field.get("options", [])

            # build label/id mapping depending on source
            for item in items:
                if isinstance(item, dict):
                    # common cases
                    if source == "clients":
                        label = f"{item.get('nom','')} {item.get('prenom','')}"
                        _id = item.get('id_client')
                    elif source == "destinations":
                        label = f"{item.get('pays','')} - {item.get('ville','')}"
                        _id = item.get('id_destination')
                    elif source == "voyages":
                        label = f"Voyage #{item.get('id_voyage')} - {item.get('ville','') if 'ville' in item else ''}"
                        _id = item.get('id_voyage')
                    else:
                        # generic: try id column and a display column
                        id_key = next((k for k in item.keys() if k.startswith('id')), None)
                        _id = item.get(id_key) if id_key else None
                        label = " ".join(str(v) for k, v in item.items() if k != id_key)
                else:
                    # if items are simple tuples like (id, label)
                    try:
                        _id, label = item
                    except Exception:
                        label = str(item)
                        _id = item

                if label is None:
                    label = str(_id)
                mapping[str(label)] = str(_id)
                values.append(label)

            option = self._option_menu(group, values or [""])
            option.grid(row=1, column=0, sticky="ew")
            self.entries[field["name"]] = option
            self._select_mappings[field["name"]] = mapping
            return

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
        data = {}
        for field in self.fields:
            name = field["name"]
            ftype = field.get("type", "str")
            raw = self.entries[name].get()
            if ftype == "select":
                mapping = self._select_mappings.get(name, {})
                # map selected label back to id or value
                selected_id = mapping.get(raw, raw)
                value_type = field.get("value_type", "int" if field.get("options_source") else "str")
                data[name] = parse_value(selected_id, value_type)
            else:
                data[name] = parse_value(raw, ftype)
        return data

    def clear_form(self):
        for name, entry in self.entries.items():
            try:
                entry.set("")
            except Exception:
                try:
                    entry.delete(0, "end")
                except Exception:
                    pass

    def fill_form(self, _event=None):
        selected = self.table.selected_values()
        if not selected:
            return
        for field in self.fields:
            name = field["name"]
            entry = self.entries[name]
            value = selected.get(name, "")
            if field.get("type") == "select":
                # map id -> label
                mapping = self._select_mappings.get(name, {})
                # reverse mapping
                rev = {v: k for k, v in mapping.items()}
                label = rev.get(value) or rev.get(str(value)) or ""
                try:
                    entry.set(label)
                except Exception:
                    pass
            else:
                try:
                    entry.delete(0, "end")
                    if value is not None:
                        entry.insert(0, str(value)[:10] if field.get("type") == "date" else str(value))
                except Exception:
                    pass

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
