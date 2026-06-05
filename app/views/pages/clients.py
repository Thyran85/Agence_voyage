from app.views.pages.crud import CrudFrame


class ClientsFrame(CrudFrame):
    def __init__(self, master, service):
        super().__init__(
            master,
            "Gestion des clients",
            "Consulter et modifier la base de données clients.",
            service.clients,
            "id_client",
            [
                {"name": "nom", "label": "Nom"},
                {"name": "prenom", "label": "Prénom"},
                {"name": "telephone", "label": "Téléphone"},
                {"name": "email", "label": "Email"},
                {"name": "adresse", "label": "Adresse"},
            ],
            {"Nom": "nom", "Prénom": "prenom", "Téléphone": "telephone", "Email": "email"},
            {"Nom": "nom", "Prénom": "prenom"},
        )
