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
                {"name": "status", "label": "Statut", "type": "select", "options": ["CONFIRMÉ", "ANNULÉ"]},
            ],
            {"Client": "client", "Voyage": "voyage"},
            {"Date réservation": "date_reservation", "Montant": "montant"},
        )

    def _refresh_voyages_page(self):
        try:
            top = self.winfo_toplevel()
            if hasattr(top, "pages") and "Voyages" in top.pages:
                top.pages["Voyages"].refresh()
        except (AttributeError, KeyError):
            pass

    def create_item(self):
        try:
            self.service.create_reservation(self.collect_form())
            self.clear_form()
            self.refresh()
            self._refresh_voyages_page()
        except ConnectionError as e:
            messagebox.showerror("Connexion perdue", f"{e}\n\nVérifiez qu'Oracle est démarré et réessayez.")
        except ValueError as e:
            messagebox.showerror("Données invalides", str(e))
        except RuntimeError as e:
            messagebox.showerror("Création impossible", str(e))
        except Exception as e:
            messagebox.showerror("Erreur inattendue", f"{e}\n\nVérifiez les données saisies et réessayez.")

    def update_item(self):
        item_id = self.table.selected_id()
        if not item_id:
            messagebox.showinfo("Sélection requise", "Sélectionnez une ligne à modifier.")
            return
        try:
            self.service.update_reservation(item_id, self.collect_form())
            self.refresh()
            self._refresh_voyages_page()
        except ConnectionError as e:
            messagebox.showerror("Connexion perdue", f"{e}\n\nVérifiez qu'Oracle est démarré et réessayez.")
        except ValueError as e:
            messagebox.showerror("Données invalides", str(e))
        except RuntimeError as e:
            messagebox.showerror("Modification impossible", str(e))
        except Exception as e:
            messagebox.showerror("Erreur inattendue", f"{e}\n\nVérifiez les données et réessayez.")

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
            self._refresh_voyages_page()
        except ConnectionError as e:
            messagebox.showerror("Connexion perdue", f"{e}\n\nVérifiez qu'Oracle est démarré et réessayez.")
        except ValueError as e:
            messagebox.showerror("Données invalides", str(e))
        except RuntimeError as e:
            messagebox.showerror("Suppression impossible", str(e))
        except Exception as e:
            messagebox.showerror("Erreur inattendue", f"{e}\n\nRechargez l'application et réessayez.")
