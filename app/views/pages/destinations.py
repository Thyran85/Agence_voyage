import customtkinter as ctk

from app.views.components import Panel
from app.views.images import destination_image
from app.views.pages.crud import CrudFrame
from app.views.theme import COLORS, app_font


class DestinationsFrame(CrudFrame):
    def __init__(self, master, service):
        super().__init__(
            master,
            "Gestion des destinations",
            "Organiser le catalogue de pays, villes et prix de base.",
            service.destinations,
            "id_destination",
            [
                {"name": "pays", "label": "Pays"},
                {"name": "ville", "label": "Ville"},
                {"name": "description", "label": "Description"},
                {"name": "prix_base", "label": "Prix base", "type": "float"},
                {"name": "image_path", "label": "Image", "type": "file", "placeholder": "Chemin de l'image"},
            ],
            {"Pays": "pays", "Ville": "ville"},
            {"Pays": "pays", "Prix": "prix_base"},
        )

    def create_table(self, master):
        return DestinationTable(master)


class DestinationTable(Panel):
    def __init__(self, master):
        super().__init__(master)
        self.rows = []
        self.selected_index = None
        self.select_callback = None
        self.image_refs = []

        self.grid_columnconfigure(0, weight=1)
        ctk.CTkFrame(self, height=1, fg_color=COLORS["border"]).grid(row=1, column=0, sticky="ew")
        self._build_header()
        self.body = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.body.grid(row=2, column=0, sticky="nsew", padx=1, pady=(0, 1))
        self.body.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=8)
        header.grid(row=0, column=0, sticky="ew", padx=1, pady=1)
        for column, weight in enumerate([0, 1, 1, 2, 1, 1]):
            header.grid_columnconfigure(column, weight=weight)
        labels = ["IMAGE", "PAYS", "VILLE", "DESCRIPTION", "PRIX BASE", "STATUT"]
        for column, label in enumerate(labels):
            anchor = "e" if label == "PRIX BASE" else "w"
            ctk.CTkLabel(header, text=label, text_color=COLORS["muted"], font=app_font(10, "bold")).grid(
                row=0, column=column, padx=12, pady=12, sticky=anchor
            )

    def set_rows(self, rows):
        for child in self.body.winfo_children():
            child.destroy()
        self.rows = rows
        self.selected_index = None
        self.image_refs = []
        for index, row in enumerate(rows):
            self._build_row(index, row)

    def _build_row(self, index, row):
        bg = COLORS["surface_low"] if index % 2 == 0 else "#181818"
        frame = ctk.CTkFrame(self.body, fg_color=bg, corner_radius=0)
        frame.grid(row=index, column=0, sticky="ew")
        frame.grid_columnconfigure(0, weight=0)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(2, weight=1)
        frame.grid_columnconfigure(3, weight=2)
        frame.grid_columnconfigure(4, weight=1)
        frame.grid_columnconfigure(5, weight=1)

        image = destination_image(str(row.get("ville", "")), row.get("image_path"), size=(96, 54))
        self.image_refs.append(image)
        ctk.CTkLabel(frame, text="", image=image).grid(row=0, column=0, padx=12, pady=10, sticky="w")
        self._cell(frame, row.get("pays", ""), 1)
        self._cell(frame, row.get("ville", ""), 2)
        self._cell(frame, row.get("description", ""), 3, muted=True, wrap=240)
        self._cell(frame, self._format_price(row.get("prix_base")), 4, accent=True, anchor="e")
        self._status(frame, 5)

        for child in frame.winfo_children():
            child.bind("<Button-1>", lambda _event, row_index=index: self._select(row_index))
        frame.bind("<Button-1>", lambda _event, row_index=index: self._select(row_index))
        frame.bind("<Enter>", lambda _event, row_frame=frame: self._hover(row_frame, True))
        frame.bind("<Leave>", lambda _event, row_frame=frame, row_index=index: self._hover(row_frame, False, row_index))

    def _cell(self, master, value, column, muted=False, accent=False, anchor="w", wrap=None):
        color = COLORS["primary"] if accent else COLORS["muted"] if muted else COLORS["text"]
        ctk.CTkLabel(
            master,
            text=str(value or ""),
            text_color=color,
            font=app_font(12, "bold" if accent else "normal"),
            wraplength=wrap or 160,
            justify="left",
        ).grid(row=0, column=column, padx=12, pady=10, sticky=anchor)

    def _status(self, master, column):
        badge = ctk.CTkLabel(
            master,
            text="ACTIF",
            text_color=COLORS["primary"],
            fg_color="#16373b",
            corner_radius=4,
            font=app_font(10, "bold"),
            width=52,
            height=22,
        )
        badge.grid(row=0, column=column, padx=12, pady=10, sticky="w")

    def _select(self, index):
        self.selected_index = index
        for row_index, frame in enumerate(self.body.winfo_children()):
            color = COLORS["primary_container"] if row_index == index else COLORS["surface_low"] if row_index % 2 == 0 else "#181818"
            frame.configure(fg_color=color)
        if self.select_callback:
            self.select_callback(None)

    def _hover(self, frame, active, index=None):
        if index is not None and self.selected_index == index:
            return
        base = COLORS["surface_low"] if index is None or index % 2 == 0 else "#181818"
        frame.configure(fg_color=COLORS["surface_high"] if active else base)

    def _format_price(self, value):
        try:
            return f"{float(value):,.0f} Ar".replace(",", " ")
        except (TypeError, ValueError):
            return value or ""

    def bind_select(self, callback):
        self.select_callback = callback

    def selected_id(self):
        values = self.selected_values()
        return values.get("id_destination")

    def selected_values(self):
        if self.selected_index is None:
            return {}
        return self.rows[self.selected_index]
