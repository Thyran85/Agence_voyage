from tkinter import messagebox

import customtkinter as ctk

from app.views.components import PageHeader, Panel
from app.views.theme import COLORS, app_font


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, service, open_reservations=None):
        super().__init__(master, fg_color=COLORS["background"])
        self.service = service
        self.cards = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        PageHeader(
            self,
            "Tableau de bord",
            "Vue d'ensemble de l'activité agence et des performances de réservation.",
            "Nouvelle réservation",
            open_reservations,
        ).grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 16))

        self._build_stat_cards()
        self._build_highlights()
        self.refresh()

    def _build_stat_cards(self):
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.grid(row=1, column=0, padx=24, pady=(0, 16), sticky="ew")
        stats = [
            ("clients", "Total clients", COLORS["primary"]),
            ("destinations", "Destinations", COLORS["secondary"]),
            ("voyages", "Voyages", COLORS["primary"]),
            ("réservations", "Réservations", COLORS["secondary"]),
        ]
        for index, (key, label, accent) in enumerate(stats):
            grid.grid_columnconfigure(index, weight=1)
            card = Panel(grid)
            card.grid(row=0, column=index, padx=(0 if index == 0 else 8, 0), sticky="ew")
            ctk.CTkLabel(card, text=label.upper(), text_color=COLORS["muted"], font=app_font(11, "bold")).pack(
                padx=16, pady=(14, 4), anchor="w"
            )
            value = ctk.CTkLabel(card, text="0", text_color=COLORS["text"], font=app_font(28, "bold"))
            value.pack(padx=16, pady=(0, 2), anchor="w")
            ctk.CTkLabel(card, text="Catalogue actif", text_color=accent, font=app_font(12)).pack(
                padx=16, pady=(0, 14), anchor="w"
            )
            self.cards[key] = value

    def _build_highlights(self):
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=2, column=0, padx=24, pady=(0, 24), sticky="nsew")
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        highlights = Panel(body)
        highlights.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        ctk.CTkLabel(highlights, text="PERFORMANCE", text_color=COLORS["primary"], font=app_font(16, "bold")).pack(
            padx=16, pady=(16, 8), anchor="w"
        )
        self.top_destination = ctk.CTkLabel(
            highlights, text="", text_color=COLORS["text"], font=app_font(15), wraplength=420, justify="left"
        )
        self.top_destination.pack(padx=16, pady=10, anchor="w")
        self.top_voyage = ctk.CTkLabel(
            highlights, text="", text_color=COLORS["text"], font=app_font(15), wraplength=420, justify="left"
        )
        self.top_voyage.pack(padx=16, pady=10, anchor="w")
        ctk.CTkButton(
            highlights,
            text="Actualiser les indicateurs",
            command=self.refresh,
            height=34,
            fg_color=COLORS["surface_high"],
            hover_color=COLORS["surface_highest"],
            corner_radius=8,
            font=app_font(12, "bold"),
        ).pack(padx=16, pady=(12, 16), anchor="w")

        note = Panel(body)
        note.grid(row=0, column=1, padx=(8, 0), sticky="nsew")
        ctk.CTkLabel(note, text="CONCIERGERIE", text_color=COLORS["secondary"], font=app_font(16, "bold")).pack(
            padx=16, pady=(16, 8), anchor="w"
        )
        ctk.CTkLabel(
            note,
            text=(
                "Interface opérationnelle pour suivre les clients, destinations, voyages "
                "et réservations dans Oracle Database."
            ),
            text_color=COLORS["muted"],
            font=app_font(14),
            wraplength=420,
            justify="left",
        ).pack(padx=16, pady=8, anchor="w")
        ctk.CTkLabel(
            note,
            text="Les montants de réservation sont calculés automatiquement depuis le prix du voyage.",
            text_color=COLORS["text"],
            font=app_font(14),
            wraplength=420,
            justify="left",
        ).pack(padx=16, pady=8, anchor="w")

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
                text=f"Destination la plus réservée\n{destination['label']} ({destination['total']})"
            )
            self.top_voyage.configure(text=f"Voyage le plus réservé\n{voyage['label']} ({voyage['total']})")
        except Exception as error:
            messagebox.showerror("Dashboard indisponible", str(error))
