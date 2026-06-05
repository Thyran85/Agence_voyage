from tkinter import ttk

import customtkinter as ctk

from app.views.theme import COLORS, app_font


class Panel(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["surface"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=8,
            **kwargs,
        )


class PageHeader(ctk.CTkFrame):
    def __init__(self, master, title, subtitle, action_text=None, action_command=None):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self, text=title, text_color=COLORS["text"], font=app_font(24, "bold")).grid(
            row=0, column=0, sticky="w"
        )
        ctk.CTkLabel(self, text=subtitle, text_color=COLORS["muted"], font=app_font(13)).grid(
            row=1, column=0, sticky="w", pady=(2, 0)
        )
        if action_text and action_command:
            ctk.CTkButton(
                self,
                text=action_text,
                command=action_command,
                height=36,
                fg_color=COLORS["surface_high"],
                hover_color=COLORS["surface_highest"],
                border_color=COLORS["border"],
                border_width=1,
                text_color=COLORS["text"],
                corner_radius=8,
                font=app_font(13, "bold"),
            ).grid(row=0, column=1, rowspan=2, sticky="e")


class DataTable(Panel):
    def __init__(self, master, height=14):
        super().__init__(master)
        self.tree = ttk.Treeview(self, show="headings", height=height, style="Elite.Treeview")
        self.scroll_y = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.scroll_x = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(1, 0), pady=(1, 0))
        self.scroll_y.grid(row=0, column=1, sticky="ns", pady=(1, 0))
        self.scroll_x.grid(row=1, column=0, sticky="ew", padx=(1, 0))
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def set_rows(self, rows):
        columns = list(rows[0].keys()) if rows else []
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = columns
        for column in columns:
            self.tree.heading(column, text=str(column).upper())
            width = 110 if column.startswith("id_") else 150
            self.tree.column(column, width=width, minwidth=90, anchor="w", stretch=True)
        for index, row in enumerate(rows):
            tag = "even" if index % 2 == 0 else "odd"
            self.tree.insert("", "end", values=[row.get(column, "") for column in columns], tags=(tag,))
        self.tree.tag_configure("even", background=COLORS["surface_low"])
        self.tree.tag_configure("odd", background="#181818")

    def bind_select(self, callback):
        self.tree.bind("<<TreeviewSelect>>", callback)

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


class SidebarButton(ctk.CTkButton):
    def __init__(self, master, label, command):
        super().__init__(
            master,
            text=label,
            command=command,
            height=40,
            anchor="w",
            fg_color="transparent",
            hover_color=COLORS["surface_high"],
            text_color=COLORS["muted"],
            corner_radius=0,
            font=app_font(13),
        )

    def set_active(self, active):
        self.configure(
            fg_color=COLORS["primary_container"] if active else "transparent",
            text_color=COLORS["text"] if active else COLORS["muted"],
            font=app_font(13, "bold" if active else "normal"),
        )
