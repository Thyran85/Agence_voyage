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
