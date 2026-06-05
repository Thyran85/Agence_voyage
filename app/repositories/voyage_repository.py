from app.repositories.base import BaseRepository


class VoyageRepository(BaseRepository):
    table_name = "voyages"
    id_column = "id_voyage"
    columns = (
        "id_destination",
        "date_depart",
        "date_retour",
        "prix",
        "places_disponibles",
    )
    searchable_columns = ("prix",)
    sortable_columns = ("prix", "date_depart")

    def list(self, search_by=None, search_value=None, sort_by=None, sort_dir="ASC"):
        sql = """
            SELECT v.id_voyage, v.id_destination, d.pays, d.ville,
                   v.date_depart, v.date_retour, v.prix, v.places_disponibles
            FROM voyages v
            INNER JOIN destinations d ON d.id_destination = v.id_destination
        """
        params = {}
        clauses = []

        if search_by == "destination" and search_value:
            clauses.append("(LOWER(d.pays) LIKE :search_value OR LOWER(d.ville) LIKE :search_value)")
            params["search_value"] = f"%{search_value.lower()}%"
        elif search_by == "date_depart" and search_value:
            clauses.append("TRUNC(v.date_depart) = TO_DATE(:date_depart, 'YYYY-MM-DD')")
            params["date_depart"] = search_value
        elif search_by == "prix" and search_value:
            clauses.append("v.prix = :prix")
            params["prix"] = float(search_value)

        if clauses:
            sql += " WHERE " + " AND ".join(clauses)

        if sort_by in self.sortable_columns:
            direction = "DESC" if str(sort_dir).upper() == "DESC" else "ASC"
            sql += f" ORDER BY v.{sort_by} {direction}"

        return self.database.fetch_all(sql, params)
