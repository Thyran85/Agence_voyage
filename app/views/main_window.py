import customtkinter as ctk

from app.controllers.main_controller import MainController
from app.views.components import SidebarButton
from app.views.pages.clients import ClientsFrame
from app.views.pages.dashboard import DashboardFrame
from app.views.pages.destinations import DestinationsFrame
from app.views.pages.filters import FilterFrame
from app.views.pages.reservations import ReservationFrame
from app.views.pages.sql_oracle import QueryExamplesFrame
from app.views.pages.voyages import VoyagesFrame
from app.views.theme import COLORS, app_font, configure_tree_style


NAV_ITEMS = {
    "Dashboard": "▦   Tableau de bord",
    "Clients": "◉   Clients",
    "Destinations": "◎   Destinations",
    "Voyages": "⌁   Voyages",
    "Réservations": "▤   Réservations",
    "Filtres": "≡   Filtres",
    "SQL Oracle": "▣   SQL Oracle",
}


class TravelAgencyApp(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=COLORS["background"])
        configure_tree_style()
        self.title("Elite Concierge - Oracle Database")
        self.geometry("1280x760")
        self.minsize(1100, 680)

        self.controller = MainController()
        self.service = self.controller.service
        self.pages = {}
        self.nav_buttons = {}

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_sidebar()
        self._build_topbar()
        self._build_content_area()
        self._build_pages()
        self.show_page("Dashboard")

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=240, fg_color=COLORS["surface"], corner_radius=0)
        sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(sidebar, text="Elite Concierge", text_color=COLORS["primary"], font=app_font(28, "bold")).pack(
            padx=16, pady=(20, 0), anchor="w"
        )
        ctk.CTkLabel(sidebar, text="GESTION BACK-OFFICE", text_color=COLORS["muted"], font=app_font(10, "bold")).pack(
            padx=16, pady=(0, 24), anchor="w"
        )

        nav = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav.pack(fill="x", padx=8)
        for name, label in NAV_ITEMS.items():
            button = SidebarButton(nav, label, lambda page=name: self.show_page(page))
            button.pack(fill="x", pady=2)
            self.nav_buttons[name] = button

        ctk.CTkFrame(sidebar, height=1, fg_color=COLORS["border"]).pack(fill="x", padx=16, pady=18)
        ctk.CTkButton(
            sidebar,
            text="Nouvelle réservation",
            command=lambda: self.show_page("Réservations"),
            height=38,
            fg_color=COLORS["primary_container"],
            hover_color="#004f56",
            text_color=COLORS["text"],
            corner_radius=8,
            font=app_font(13, "bold"),
        ).pack(fill="x", padx=16, pady=(0, 16), side="bottom")

    def _build_topbar(self):
        topbar = ctk.CTkFrame(self, height=64, fg_color=COLORS["background"], corner_radius=0)
        topbar.grid(row=0, column=1, sticky="ew")
        topbar.grid_propagate(False)
        topbar.grid_columnconfigure(0, weight=1)

        self.top_title = ctk.CTkLabel(topbar, text="", text_color=COLORS["text"], font=app_font(18, "bold"))
        self.top_title.grid(row=0, column=0, padx=24, sticky="w")
        actions = ctk.CTkFrame(topbar, fg_color="transparent")
        actions.grid(row=0, column=1, padx=(0, 24), sticky="e")
        for label in ["!", "?", "⚙"]:
            ctk.CTkButton(
                actions,
                text=label,
                width=34,
                height=34,
                fg_color="transparent",
                hover_color=COLORS["surface_high"],
                text_color=COLORS["muted"],
                corner_radius=8,
                font=app_font(14, "bold"),
            ).pack(side="left", padx=3)
        ctk.CTkFrame(actions, width=1, height=32, fg_color=COLORS["border"]).pack(side="left", padx=14)
        profile = ctk.CTkFrame(actions, fg_color="transparent")
        profile.pack(side="left")
        ctk.CTkLabel(profile, text="Jean Dupont", text_color=COLORS["text"], font=app_font(12, "bold")).pack(anchor="e")
        ctk.CTkLabel(profile, text="Agent Sénior", text_color=COLORS["muted"], font=app_font(11)).pack(anchor="e")
        ctk.CTkFrame(topbar, height=1, fg_color=COLORS["border"]).grid(
            row=1, column=0, columnspan=2, sticky="ew"
        )

    def _build_content_area(self):
        self.content = ctk.CTkFrame(self, fg_color=COLORS["background"])
        self.content.grid(row=1, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

    def _build_pages(self):
        page_specs = self._page_specs()
        for name, frame in page_specs.items():
            frame.grid(row=0, column=0, sticky="nsew")
            self.pages[name] = frame

    def _page_specs(self):
        return {
            "Dashboard": DashboardFrame(self.content, self.service, lambda: self.show_page("Réservations")),
            "Clients": ClientsFrame(self.content, self.service),
            "Destinations": DestinationsFrame(self.content, self.service),
            "Voyages": VoyagesFrame(self.content, self.service),
            "Réservations": ReservationFrame(self.content, self.service),
            "Filtres": FilterFrame(self.content, self.service),
            "SQL Oracle": QueryExamplesFrame(self.content, self.controller),
        }

    def show_page(self, name):
        self.pages[name].tkraise()
        self.top_title.configure(text=name)
        for page, button in self.nav_buttons.items():
            button.set_active(page == name)
