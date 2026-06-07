from app.views.pages.crud import CrudFrame


class VoyagesFrame(CrudFrame):
    def __init__(self, master, service):
        self.service = service
        super().__init__(
            master,
            "Gestion des voyages",
            "Planifier les départs, retours, tarifs et disponibilités.",
            service.voyages,
            "id_voyage",
            [
                {"name": "id_destination", "label": "Destination", "type": "select", "options_source": "destinations"},
                {"name": "date_depart", "label": "Date départ", "type": "date", "placeholder": "YYYY-MM-DD"},
                {"name": "date_retour", "label": "Date retour", "type": "date", "placeholder": "YYYY-MM-DD"},
                {"name": "prix", "label": "Prix", "type": "float"},
                {"name": "places_disponibles", "label": "Places disponibles", "type": "int"},
            ],
            {"Destination": "destination", "Date départ": "date_depart", "Prix": "prix"},
            {"Prix": "prix", "Date départ": "date_depart"},
        )
