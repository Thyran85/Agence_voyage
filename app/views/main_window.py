from datetime import datetime
from tkinter import messagebox, ttk

import customtkinter as ctk

from app.controllers.main_controller import MainController


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def parse_value(value, field_type):
    value = value.strip()
    if value == "":
        return None
    if field_type == "int":
        return int(value)
    if field_type == "float":
        return float(value)
    if field_type == "date":
        return datetime.strptime(value, "%Y-%m-%d").date()
    return value


class DataTable(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.tree = ttk.Treeview(self, show="headings", height=14)
        self.scroll_y = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.scroll_x = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.scroll_y.grid(row=0, column=1, sticky="ns")
        self.scroll_x.grid(row=1, column=0, sticky="ew")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def set_rows(self, rows):
        columns = list(rows[0].keys()) if rows else []
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = columns
        for column in columns:
            self.tree.heading(column, text=column)
            self.tree.column(column, width=140, anchor="w")
        for row in rows:
            self.tree.insert("", "end", values=[row.get(column, "") for column in columns])

    def selected_id(self):
        selection = self.tree.selection()
        if not selection:
            return None
        values = self.tree.item(selection[0], "values")
        return values[0] if values else None

    def selected_values(self):
        selection = self.tree.selection()
        if not selection:
            return {}
        columns = self.tree["columns"]
        values = self.tree.item(selection[0], "values")
        return dict(zip(columns, values))


class CrudFrame(ctk.CTkFrame):
    def __init__(self, master, title, repository, id_column, fields, search_options, sort_options):
        super().__init__(master)
        self.repository = repository
        self.id_column = id_column
        self.fields = fields
        self.entries = {}

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=22, weight="bold")).grid(
            row=0, column=0, columnspan=2, padx=16, pady=(14, 8), sticky="w"
        )

        form = ctk.CTkFrame(self)
        form.grid(row=1, column=0, padx=16, pady=8, sticky="new")

        for index, field in enumerate(fields):
            ctk.CTkLabel(form, text=field["label"]).grid(row=index, column=0, padx=10, pady=5, sticky="w")
            entry = ctk.CTkEntry(form, width=220, placeholder_text=field.get("placeholder", ""))
            entry.grid(row=index, column=1, padx=10, pady=5, sticky="ew")
            self.entries[field["name"]] = entry

        actions = ctk.CTkFrame(form, fg_color="transparent")
        actions.grid(row=len(fields), column=0, columnspan=2, pady=10)
        ctk.CTkButton(actions, text="Ajouter", width=90, command=self.create_item).grid(row=0, column=0, padx=4)
        ctk.CTkButton(actions, text="Modifier", width=90, command=self.update_item).grid(row=0, column=1, padx=4)
        ctk.CTkButton(actions, text="Supprimer", width=90, fg_color="#b42318", command=self.delete_item).grid(
            row=0, column=2, padx=4
        )
        ctk.CTkButton(actions, text="Effacer", width=90, command=self.clear_form).grid(row=0, column=3, padx=4)

        tools = ctk.CTkFrame(self)
        tools.grid(row=1, column=1, padx=16, pady=8, sticky="new")
        tools.grid_columnconfigure(1, weight=1)

        self.search_by = ctk.CTkOptionMenu(tools, values=list(search_options.keys()) or [""])
        self.search_by.grid(row=0, column=0, padx=8, pady=8, sticky="w")
        self.search_entry = ctk.CTkEntry(tools, placeholder_text="Recherche")
        self.search_entry.grid(row=0, column=1, padx=8, pady=8, sticky="ew")
        ctk.CTkButton(tools, text="Rechercher", command=self.refresh).grid(row=0, column=2, padx=8, pady=8)

        self.sort_by = ctk.CTkOptionMenu(tools, values=list(sort_options.keys()) or [""])
        self.sort_by.grid(row=1, column=0, padx=8, pady=8, sticky="w")
        self.sort_dir = ctk.CTkSegmentedButton(tools, values=["ASC", "DESC"])
        self.sort_dir.set("ASC")
        self.sort_dir.grid(row=1, column=1, padx=8, pady=8, sticky="w")
        ctk.CTkButton(tools, text="Actualiser", command=self.refresh).grid(row=1, column=2, padx=8, pady=8)

        self.search_options = search_options
        self.sort_options = sort_options
        self.table = DataTable(self)
        self.table.grid(row=2, column=0, columnspan=2, padx=16, pady=(8, 16), sticky="nsew")
        self.table.tree.bind("<<TreeviewSelect>>", self.fill_form)
        self.refresh()

    def collect_form(self):
        data = {}
        for field in self.fields:
            data[field["name"]] = parse_value(
                self.entries[field["name"]].get(),
                field.get("type", "str"),
            )
        return data

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
            search_key = self.search_options.get(self.search_by.get())
            sort_key = self.sort_options.get(self.sort_by.get())
            rows = self.repository.list(
                search_by=search_key,
                search_value=self.search_entry.get().strip(),
                sort_by=sort_key,
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


class ReservationFrame(CrudFrame):
    def __init__(self, master, service):
        self.service = service
        super().__init__(
            master,
            "Gestion des réservations",
            service.reservations,
            "id_reservation",
            [
                {"name": "id_client", "label": "ID client", "type": "int"},
                {"name": "id_voyage", "label": "ID voyage", "type": "int"},
                {"name": "date_reservation", "label": "Date réservation", "type": "date", "placeholder": "YYYY-MM-DD"},
                {"name": "nombre_personnes", "label": "Nombre personnes", "type": "int"},
            ],
            {"Client": "client", "Voyage": "voyage"},
            {"Date réservation": "date_reservation", "Montant": "montant"},
        )

    def create_item(self):
        try:
            self.service.create_reservation(self.collect_form())
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
            self.service.update_reservation(item_id, self.collect_form())
            self.refresh()
        except Exception as error:
            messagebox.showerror("Modification impossible", str(error))


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, service):
        super().__init__(master)
        self.service = service
        self.cards = {}
        ctk.CTkLabel(self, text="Tableau de bord", font=ctk.CTkFont(size=24, weight="bold")).pack(
            padx=18, pady=(18, 8), anchor="w"
        )
        grid = ctk.CTkFrame(self)
        grid.pack(fill="x", padx=18, pady=8)
        for index, label in enumerate(["Clients", "Destinations", "Voyages", "Réservations"]):
            card = ctk.CTkFrame(grid)
            card.grid(row=0, column=index, padx=8, pady=8, sticky="ew")
            grid.grid_columnconfigure(index, weight=1)
            ctk.CTkLabel(card, text=label).pack(padx=16, pady=(14, 4))
            value = ctk.CTkLabel(card, text="0", font=ctk.CTkFont(size=28, weight="bold"))
            value.pack(padx=16, pady=(0, 14))
            self.cards[label.lower()] = value

        self.top_destination = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=16))
        self.top_destination.pack(padx=18, pady=10, anchor="w")
        self.top_voyage = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=16))
        self.top_voyage.pack(padx=18, pady=4, anchor="w")
        ctk.CTkButton(self, text="Actualiser", command=self.refresh).pack(padx=18, pady=16, anchor="w")
        self.refresh()

    def refresh(self):
        try:
            stats = self.service.dashboard_stats()
            self.cards["clients"].configure(text=str(stats["clients"]))
            self.cards["destinations"].configure(text=str(stats["destinations"]))
            self.cards["voyages"].configure(text=str(stats["voyages"]))
            self.cards["réservations"].configure(text=str(stats["reservations"]))
            destination = stats["destination_top"] or {"label": "Aucune", "total": 0}
            voyage = stats["voyage_top"] or {"label": "Aucun", "total": 0}
            self.top_destination.configure(
                text=f"Destination la plus réservée : {destination['label']} ({destination['total']})"
            )
            self.top_voyage.configure(text=f"Voyage le plus réservé : {voyage['label']} ({voyage['total']})")
        except Exception as error:
            messagebox.showerror("Dashboard indisponible", str(error))


class FilterFrame(ctk.CTkFrame):
    def __init__(self, master, service):
        super().__init__(master)
        self.service = service
        self.entries = {}
        ctk.CTkLabel(self, text="Filtrage multicritère", font=ctk.CTkFont(size=22, weight="bold")).pack(
            padx=16, pady=(14, 8), anchor="w"
        )
        self.mode = ctk.CTkSegmentedButton(self, values=["Voyages", "Réservations"], command=self.render_form)
        self.mode.set("Voyages")
        self.mode.pack(padx=16, pady=8, anchor="w")
        self.form = ctk.CTkFrame(self)
        self.form.pack(fill="x", padx=16, pady=8)
        self.sql_box = ctk.CTkTextbox(self, height=110)
        self.sql_box.pack(fill="x", padx=16, pady=8)
        self.table = DataTable(self)
        self.table.pack(fill="both", expand=True, padx=16, pady=(8, 16))
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
            ctk.CTkLabel(self.form, text=field).grid(row=index // 3, column=(index % 3) * 2, padx=8, pady=6, sticky="w")
            entry = ctk.CTkEntry(self.form, width=180)
            entry.grid(row=index // 3, column=(index % 3) * 2 + 1, padx=8, pady=6, sticky="w")
            self.entries[field] = entry
        ctk.CTkButton(self.form, text="Filtrer", command=self.apply_filters).grid(row=2, column=0, padx=8, pady=10)

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


class QueryExamplesFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.examples = dict(controller.query_examples())
        ctk.CTkLabel(self, text="Requêtes Oracle", font=ctk.CTkFont(size=22, weight="bold")).pack(
            padx=16, pady=(14, 8), anchor="w"
        )
        self.selector = ctk.CTkOptionMenu(self, values=list(self.examples.keys()), command=self.load_example)
        self.selector.pack(padx=16, pady=8, anchor="w")
        self.sql_box = ctk.CTkTextbox(self, height=150)
        self.sql_box.pack(fill="x", padx=16, pady=8)
        ctk.CTkButton(self, text="Exécuter", command=self.run_current).pack(padx=16, pady=8, anchor="w")
        self.table = DataTable(self)
        self.table.pack(fill="both", expand=True, padx=16, pady=(8, 16))
        self.load_example(self.selector.get())

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


class TravelAgencyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Agence de voyage - Oracle Database")
        self.geometry("1280x760")
        self.minsize(1100, 680)
        self.controller = MainController()
        self.service = self.controller.service

        tabs = ctk.CTkTabview(self)
        tabs.pack(fill="both", expand=True, padx=12, pady=12)

        dashboard = tabs.add("Dashboard")
        clients = tabs.add("Clients")
        destinations = tabs.add("Destinations")
        voyages = tabs.add("Voyages")
        reservations = tabs.add("Réservations")
        filters = tabs.add("Filtres")
        queries = tabs.add("SQL Oracle")

        DashboardFrame(dashboard, self.service).pack(fill="both", expand=True)
        CrudFrame(
            clients,
            "Gestion des clients",
            self.service.clients,
            "id_client",
            [
                {"name": "nom", "label": "Nom"},
                {"name": "prenom", "label": "Prénom"},
                {"name": "telephone", "label": "Téléphone"},
                {"name": "email", "label": "Email"},
                {"name": "adresse", "label": "Adresse"},
            ],
            {"Nom": "nom", "Prénom": "prenom", "Téléphone": "telephone", "Email": "email"},
            {"Nom": "nom", "Prénom": "prenom"},
        ).pack(fill="both", expand=True)
        CrudFrame(
            destinations,
            "Gestion des destinations",
            self.service.destinations,
            "id_destination",
            [
                {"name": "pays", "label": "Pays"},
                {"name": "ville", "label": "Ville"},
                {"name": "description", "label": "Description"},
                {"name": "prix_base", "label": "Prix base", "type": "float"},
            ],
            {"Pays": "pays", "Ville": "ville"},
            {"Pays": "pays", "Prix": "prix_base"},
        ).pack(fill="both", expand=True)
        CrudFrame(
            voyages,
            "Gestion des voyages",
            self.service.voyages,
            "id_voyage",
            [
                {"name": "id_destination", "label": "ID destination", "type": "int"},
                {"name": "date_depart", "label": "Date départ", "type": "date", "placeholder": "YYYY-MM-DD"},
                {"name": "date_retour", "label": "Date retour", "type": "date", "placeholder": "YYYY-MM-DD"},
                {"name": "prix", "label": "Prix", "type": "float"},
                {"name": "places_disponibles", "label": "Places disponibles", "type": "int"},
            ],
            {"Destination": "destination", "Date départ": "date_depart", "Prix": "prix"},
            {"Prix": "prix", "Date départ": "date_depart"},
        ).pack(fill="both", expand=True)
        ReservationFrame(reservations, self.service).pack(fill="both", expand=True)
        FilterFrame(filters, self.service).pack(fill="both", expand=True)
        QueryExamplesFrame(queries, self.controller).pack(fill="both", expand=True)
