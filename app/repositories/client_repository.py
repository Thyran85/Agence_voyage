from app.repositories.base import BaseRepository


class ClientRepository(BaseRepository):
    table_name = "clients"
    id_column = "id_client"
    columns = ("nom", "prenom", "telephone", "email", "adresse")
    searchable_columns = ("nom", "prenom", "telephone", "email")
    sortable_columns = ("nom", "prenom")
