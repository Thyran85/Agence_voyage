from app.views.pages.crud import CrudFrame


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
            ],
            {"Pays": "pays", "Ville": "ville"},
            {"Pays": "pays", "Prix": "prix_base"},
        )
