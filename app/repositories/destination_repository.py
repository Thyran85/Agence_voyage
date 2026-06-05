from app.repositories.base import BaseRepository


class DestinationRepository(BaseRepository):
    table_name = "destinations"
    id_column = "id_destination"
    columns = ("pays", "ville", "description", "prix_base", "image_path")
    searchable_columns = ("pays", "ville")
    sortable_columns = ("pays", "prix_base")
