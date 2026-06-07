from tkinter import messagebox

from app.views.pages.crud import CrudFrame


class ReservationFrame(CrudFrame):
    def __init__(self, master, service):
        self.service = service
        super().__init__(
            master,
            "Gestion des réservations",
            "Créer, modifier et contrôler les dossiers de réservation.",
            service.reservations,
            "id_reservation",
            [
                {"name": "id_client", "label": "Client", "type": "select", "options_source": "clients"},
                {"name": "id_voyage", "label": "Voyage", "type": "select", "options_source": "voyages"},
                {"name": "date_reservation", "label": "Date réservation", "type": "date", "placeholder": "YYYY-MM-DD"},
                {"name": "nombre_personnes", "label": "Nombre personnes", "type": "int"},
                {"name": "status", "label": "Statut", "type": "select", "options": ["CONFIRMÉ", "EN ATTENTE", "ANNULÉ"]},
            ],
            {"Client": "client", "Voyage": "voyage"},
            {"Date réservation": "date_reservation", "Montant": "montant"},
        )

    def create_item(self):
        try:
            self.service.create_reservation(self.collect_form())
            self.clear_form()
            self.refresh()
            # also refresh Voyages page so available seats update
            try:
                top = self.winfo_toplevel()
                if hasattr(top, "pages") and "Voyages" in top.pages:
                    top.pages["Voyages"].refresh()
            except Exception:
                pass
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
            try:
                top = self.winfo_toplevel()
                if hasattr(top, "pages") and "Voyages" in top.pages:
                    top.pages["Voyages"].refresh()
            except Exception:
                pass
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
            self.service.delete_reservation(item_id)
            self.clear_form()
            self.refresh()
            try:
                top = self.winfo_toplevel()
                if hasattr(top, "pages") and "Voyages" in top.pages:
                    top.pages["Voyages"].refresh()
            except Exception:
                pass
        except Exception as error:
            messagebox.showerror("Suppression impossible", str(error))
