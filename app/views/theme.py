from tkinter import ttk

import customtkinter as ctk


ctk.set_appearance_mode("dark")

COLORS = {
    "background": "#131313",
    "surface": "#201f1f",
    "surface_low": "#1c1b1b",
    "surface_high": "#2a2a2a",
    "surface_highest": "#353534",
    "border": "#3e494a",
    "muted": "#bec8ca",
    "text": "#e5e2e1",
    "primary": "#82d3de",
    "primary_container": "#006d77",
    "secondary": "#ffb59a",
    "danger": "#93000a",
    "danger_hover": "#690005",
    "danger_text": "#ffdad6",
}

FONT_FAMILY = "Hanken Grotesk"
MONO_FAMILY = "JetBrains Mono"


def app_font(size=14, weight="normal", family=FONT_FAMILY):
    return ctk.CTkFont(family=family, size=size, weight=weight)


def configure_tree_style():
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Elite.Treeview",
        background=COLORS["surface_low"],
        foreground=COLORS["text"],
        fieldbackground=COLORS["surface_low"],
        bordercolor=COLORS["border"],
        rowheight=34,
        font=(FONT_FAMILY, 11),
    )
    style.configure(
        "Elite.Treeview.Heading",
        background=COLORS["surface_high"],
        foreground=COLORS["muted"],
        relief="flat",
        font=(FONT_FAMILY, 10, "bold"),
    )
    style.map(
        "Elite.Treeview",
        background=[("selected", COLORS["primary_container"])],
        foreground=[("selected", COLORS["text"])],
    )
    style.configure(
        "Vertical.TScrollbar",
        background=COLORS["surface_high"],
        troughcolor=COLORS["background"],
        bordercolor=COLORS["border"],
        arrowcolor=COLORS["muted"],
    )
    style.configure(
        "Horizontal.TScrollbar",
        background=COLORS["surface_high"],
        troughcolor=COLORS["background"],
        bordercolor=COLORS["border"],
        arrowcolor=COLORS["muted"],
    )
