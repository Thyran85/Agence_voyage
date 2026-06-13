from tkinter import messagebox

import customtkinter as ctk

from app.views.components import PageHeader, Panel
from app.views.images import hero_image, destination_image
from app.views.theme import COLORS, app_font


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, service, open_reservations=None):
        super().__init__(master, fg_color=COLORS["background"])
        self.service = service
        self.cards = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        PageHeader(
            self,
            "Tableau de bord",
            "Vue d'ensemble de l'activité agence et des performances de réservation.",
            "Nouvelle réservation",
            open_reservations,
        ).grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 16))

        self._build_stat_cards()
        self._build_hero_cards()
        self._build_recent_reservations()
        self.refresh()

    def _build_stat_cards(self):
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.grid(row=1, column=0, padx=24, pady=(0, 16), sticky="ew")
        stats = [
            ("clients", "Total clients", COLORS["primary"], "+8% ce mois"),
            ("destinations", "Destinations", COLORS["secondary"], "Catalogue actif"),
            ("voyages", "Voyages", COLORS["primary"], "Circuits planifiés"),
            ("réservations", "Réservations", COLORS["secondary"], "Dossiers actifs"),
        ]
        for index, (key, label, accent, caption) in enumerate(stats):
            grid.grid_columnconfigure(index, weight=1)
            card = Panel(grid)
            card.grid(row=0, column=index, padx=(0 if index == 0 else 10, 0), sticky="ew")
            ctk.CTkLabel(card, text=label.upper(), text_color=COLORS["muted"], font=app_font(11, "bold")).pack(
                padx=16, pady=(14, 4), anchor="w"
            )
            value = ctk.CTkLabel(card, text="0", text_color=COLORS["text"], font=app_font(28, "bold"))
            value.pack(padx=16, pady=(0, 2), anchor="w")
            ctk.CTkLabel(card, text=caption, text_color=accent, font=app_font(12)).pack(
                padx=16, pady=(0, 14), anchor="w"
            )
            self.cards[key] = value

    def _build_hero_cards(self):
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=2, column=0, padx=24, pady=(24, 16), sticky="ew")
        body.grid_columnconfigure(0, weight=2)
        body.grid_columnconfigure(1, weight=3)

        self.top_destination = self._hero_card(
            body,
            "maldives",
            "Destination la plus réservée",
            "Aucune destination",
            "0 réservation",
            0,
        )
        self.top_voyage = self._hero_card(
            body,
            "safari",
            "Voyage le plus populaire",
            "Aucun voyage",
            "Aucune session active",
            1,
            use_image=False,
            icon="✈️",
        )

    def _hero_card(self, master, image_kind, kicker, title, subtitle, column, use_image=True, icon=None):
        card = Panel(master)
        card.grid(row=0, column=column, padx=(0, 10) if column == 0 else (10, 0), sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        if use_image:
            image = hero_image(image_kind, size=(520, 220))
            label = ctk.CTkLabel(card, image=image, text="")
            label.image_ref = image
            label.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        else:
            # simple icon/status panel instead of a background image
            placeholder = ctk.CTkFrame(card, fg_color=COLORS["surface_low"])
            placeholder.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
            icon_label = ctk.CTkLabel(placeholder, text=icon or "", font=app_font(48))
            icon_label.place(relx=0.5, rely=0.5, anchor="center")
            label = icon_label

        overlay = ctk.CTkFrame(card, fg_color="transparent")
        overlay.grid(row=0, column=0, sticky="sw", padx=22, pady=20)
        ctk.CTkLabel(overlay, text=kicker, text_color=COLORS["secondary"], font=app_font(12, "bold")).pack(anchor="w")
        title_label = ctk.CTkLabel(overlay, text=title, text_color=COLORS["text"], font=app_font(25, "bold"))
        title_label.pack(anchor="w", pady=(4, 2))
        subtitle_label = ctk.CTkLabel(overlay, text=subtitle, text_color=COLORS["muted"], font=app_font(13))
        subtitle_label.pack(anchor="w")
        return {"title": title_label, "subtitle": subtitle_label, "image_label": label}

    def _build_recent_reservations(self):
        panel = Panel(self)
        panel.grid(row=3, column=0, padx=24, pady=(8, 24), sticky="nsew")
        panel.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(panel, text="Réservations Récentes", text_color=COLORS["text"], font=app_font(18, "bold")).grid(
            row=0, column=0, padx=20, pady=(18, 14), sticky="w"
        )
        ctk.CTkButton(
            panel,
            text="Voir tout",
            width=80,
            height=28,
            command=lambda: None,
            fg_color="transparent",
            hover_color=COLORS["surface_high"],
            text_color=COLORS["primary"],
            font=app_font(12, "bold"),
        ).grid(row=0, column=1, padx=20, pady=(18, 14), sticky="e")

        self.recent_container = ctk.CTkFrame(panel, fg_color="transparent")
        self.recent_container.grid(row=1, column=0, columnspan=2, sticky="nsew")
        for column, weight in enumerate([2, 2, 1, 1]):
            self.recent_container.grid_columnconfigure(column, weight=weight)
        for column, label in enumerate(["CLIENT", "DESTINATION", "DATE", "STATUT"]):
            ctk.CTkLabel(
                self.recent_container,
                text=label,
                text_color=COLORS["muted"],
                font=app_font(10, "bold"),
            ).grid(row=0, column=column, padx=20, pady=10, sticky="w")

    def refresh(self):
        try:
            stats = self.service.dashboard_stats()
            self.cards["clients"].configure(text=str(stats["clients"]))
            self.cards["destinations"].configure(text=str(stats["destinations"]))
            self.cards["voyages"].configure(text=str(stats["voyages"]))
            self.cards["réservations"].configure(text=str(stats["reservations"]))
            destination = stats["destination_top"] or {"label": "Aucune", "total": 0}
            voyage = stats["voyage_top"] or {"label": "Aucun", "total": 0}
            self.top_destination["title"].configure(text=destination.get("label"))
            self.top_destination["subtitle"].configure(text=f"{destination.get('total', 0)} réservations")
            # set image for destination if available
            dest_img = None
            if destination and destination.get("image_path"):
                dest_img = destination_image(None, image_path=destination.get("image_path"), size=(520, 220))
            if dest_img:
                lbl = self.top_destination.get("image_label")
                lbl.configure(image=dest_img)
                lbl.image_ref = dest_img

            self.top_voyage["title"].configure(text=voyage.get("label"))
            self.top_voyage["subtitle"].configure(text=f"{voyage.get('total', 0)} réservations enregistrées")
            self._refresh_recent_reservations()
        except ConnectionError as e:
            messagebox.showerror("Connexion perdue", f"{e}\n\nVérifiez qu'Oracle est démarré et réessayez.")
        except RuntimeError as e:
            messagebox.showerror("Dashboard indisponible", str(e))
        except Exception as e:
            messagebox.showerror("Erreur inattendue", f"{e}\n\nRechargez le dashboard ou contactez l'administrateur.")

    def _refresh_recent_reservations(self):
        for child in self.recent_container.winfo_children()[4:]:
            child.destroy()
        for index, row in enumerate(self.service.recent_reservations(), start=1):
            self._recent_row(index, row)

    def _recent_row(self, row_index, row):
        bg = COLORS["surface_low"] if row_index % 2 else "#181818"
        values = [
            f"{row.get('prenom', '')} {row.get('nom', '')}".strip(),
            f"{row.get('ville', '')}, {row.get('pays', '')}".strip(", "),
            str(row.get("date_reservation", ""))[:10],
            "CONFIRMÉ",
        ]
        for column, value in enumerate(values):
            color = COLORS["primary"] if column == 3 else COLORS["text"]
            cell = ctk.CTkLabel(
                self.recent_container,
                text=value,
                text_color=color,
                fg_color=bg,
                font=app_font(12, "bold" if column == 3 else "normal"),
                height=48,
                anchor="w",
            )
            cell.grid(row=row_index, column=column, padx=(20, 0), pady=0, sticky="ew")
