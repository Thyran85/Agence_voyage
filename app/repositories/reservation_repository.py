from app.repositories.base import BaseRepository


class ReservationRepository(BaseRepository):
    table_name = "reservations"
    id_column = "id_reservation"
    columns = (
        "id_client",
        "id_voyage",
        "date_reservation",
        "nombre_personnes",
        "montant",
    )
    searchable_columns = ("id_client", "id_voyage")
    sortable_columns = ("date_reservation", "montant")

    def list(self, search_by=None, search_value=None, sort_by=None, sort_dir="ASC"):
        sql = """
            SELECT r.id_reservation, r.id_client, c.nom, c.prenom,
                   r.id_voyage, d.pays, d.ville, r.date_reservation,
                   r.nombre_personnes, r.montant
            FROM reservations r
            INNER JOIN clients c ON c.id_client = r.id_client
            INNER JOIN voyages v ON v.id_voyage = r.id_voyage
            INNER JOIN destinations d ON d.id_destination = v.id_destination
        """
        params = {}
        clauses = []

        if search_by == "client" and search_value:
            clauses.append("(LOWER(c.nom) LIKE :search_value OR LOWER(c.prenom) LIKE :search_value)")
            params["search_value"] = f"%{search_value.lower()}%"
        elif search_by == "voyage" and search_value:
            clauses.append("(LOWER(d.pays) LIKE :search_value OR LOWER(d.ville) LIKE :search_value)")
            params["search_value"] = f"%{search_value.lower()}%"

        if clauses:
            sql += " WHERE " + " AND ".join(clauses)

        if sort_by in self.sortable_columns:
            direction = "DESC" if str(sort_dir).upper() == "DESC" else "ASC"
            sql += f" ORDER BY r.{sort_by} {direction}"

        return self.database.fetch_all(sql, params)
