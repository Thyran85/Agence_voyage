from app.database import Database
from app.repositories.client_repository import ClientRepository
from app.repositories.destination_repository import DestinationRepository
from app.repositories.reservation_repository import ReservationRepository
from app.repositories.voyage_repository import VoyageRepository


class TravelService:
    def __init__(self, database=None):
        self.database = database or Database()
        self.clients = ClientRepository(self.database)
        self.destinations = DestinationRepository(self.database)
        self.voyages = VoyageRepository(self.database)
        self.reservations = ReservationRepository(self.database)

    def calculate_reservation_amount(self, id_voyage, nombre_personnes):
        voyage = self.database.fetch_one(
            "SELECT prix FROM voyages WHERE id_voyage = :id_voyage",
            {"id_voyage": id_voyage},
        )
        if not voyage:
            raise ValueError("Voyage introuvable.")
        return float(voyage["prix"]) * int(nombre_personnes)

    def create_reservation(self, data):
        data = dict(data)
        nombre = int(data.get("nombre_personnes", 0))
        if nombre <= 0:
            raise ValueError("Le nombre de personnes doit être supérieur à 0.")

        # calculate amount
        data["montant"] = self.calculate_reservation_amount(
            data["id_voyage"], nombre
        )

        # perform reservation and decrement places in a transaction
        with self.database.connection() as conn:
            cursor = conn.cursor()
            # lock voyage row
            cursor.execute(
                "SELECT places_disponibles FROM voyages WHERE id_voyage = :id_voyage FOR UPDATE",
                {"id_voyage": data["id_voyage"]},
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError("Voyage introuvable.")
            available = int(row[0])
            if available < nombre:
                raise ValueError("Pas assez de places disponibles pour ce voyage.")

            # decrement places
            cursor.execute(
                "UPDATE voyages SET places_disponibles = places_disponibles - :n WHERE id_voyage = :id_voyage",
                {"n": nombre, "id_voyage": data["id_voyage"]},
            )

            # insert reservation
            cols = ["id_client", "id_voyage", "nombre_personnes", "montant", "status"]
            params = {
                "id_client": data.get("id_client"),
                "id_voyage": data.get("id_voyage"),
                "nombre_personnes": nombre,
                "montant": data.get("montant"),
                "status": data.get("status", "EN ATTENTE"),
            }
            # handle optional date_reservation
            if data.get("date_reservation"):
                cols.insert(2, "date_reservation")
                params["date_reservation"] = data.get("date_reservation")

            placeholders = ", ".join(f":{c}" for c in cols)
            sql = f"INSERT INTO reservations ({', '.join(cols)}) VALUES ({placeholders})"
            cursor.execute(sql, params)
            return cursor.rowcount

    def update_reservation(self, id_reservation, data):
        data = dict(data)
        nombre = int(data.get("nombre_personnes", 0))

        # recalc amount
        data["montant"] = self.calculate_reservation_amount(
            data["id_voyage"], nombre
        )

        with self.database.connection() as conn:
            cursor = conn.cursor()
            # fetch existing reservation
            cursor.execute(
                "SELECT id_voyage, nombre_personnes FROM reservations WHERE id_reservation = :id",
                {"id": id_reservation},
            )
            old = cursor.fetchone()
            if not old:
                raise ValueError("Réservation introuvable.")
            old_voyage, old_nombre = int(old[0]), int(old[1])

            new_voyage = int(data.get("id_voyage"))
            # if voyage unchanged, adjust by difference
            if new_voyage == old_voyage:
                delta = nombre - old_nombre
                if delta > 0:
                    # need to reserve more seats
                    cursor.execute(
                        "SELECT places_disponibles FROM voyages WHERE id_voyage = :id_voyage FOR UPDATE",
                        {"id_voyage": new_voyage},
                    )
                    avail = cursor.fetchone()
                    if not avail or int(avail[0]) < delta:
                        raise ValueError("Pas assez de places disponibles pour augmenter le nombre de personnes.")
                    cursor.execute(
                        "UPDATE voyages SET places_disponibles = places_disponibles - :n WHERE id_voyage = :id_voyage",
                        {"n": delta, "id_voyage": new_voyage},
                    )
                elif delta < 0:
                    # release seats
                    cursor.execute(
                        "UPDATE voyages SET places_disponibles = places_disponibles + :n WHERE id_voyage = :id_voyage",
                        {"n": -delta, "id_voyage": new_voyage},
                    )
            else:
                # restore seats on old voyage
                cursor.execute(
                    "UPDATE voyages SET places_disponibles = places_disponibles + :n WHERE id_voyage = :id_voyage",
                    {"n": old_nombre, "id_voyage": old_voyage},
                )
                # lock and decrement on new voyage
                cursor.execute(
                    "SELECT places_disponibles FROM voyages WHERE id_voyage = :id_voyage FOR UPDATE",
                    {"id_voyage": new_voyage},
                )
                avail = cursor.fetchone()
                if not avail or int(avail[0]) < nombre:
                    raise ValueError("Pas assez de places disponibles pour ce nouveau voyage.")
                cursor.execute(
                    "UPDATE voyages SET places_disponibles = places_disponibles - :n WHERE id_voyage = :id_voyage",
                    {"n": nombre, "id_voyage": new_voyage},
                )

            # update reservation record
            assignments = []
            params = {"id": id_reservation}
            for col in ("id_client", "id_voyage", "date_reservation", "nombre_personnes", "montant", "status"):
                if col in data:
                    assignments.append(f"{col} = :{col}")
                    params[col] = data[col]
            if assignments:
                sql = f"UPDATE reservations SET {', '.join(assignments)} WHERE id_reservation = :id"
                cursor.execute(sql, params)
            return cursor.rowcount

    def delete_reservation(self, id_reservation):
        with self.database.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id_voyage, nombre_personnes FROM reservations WHERE id_reservation = :id",
                {"id": id_reservation},
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError("Réservation introuvable.")
            id_voyage, nombre = int(row[0]), int(row[1])
            # restore seats
            cursor.execute(
                "UPDATE voyages SET places_disponibles = places_disponibles + :n WHERE id_voyage = :id_voyage",
                {"n": nombre, "id_voyage": id_voyage},
            )
            cursor.execute(
                "DELETE FROM reservations WHERE id_reservation = :id",
                {"id": id_reservation},
            )
            return cursor.rowcount

    def filter_voyages(self, filters):
        sql = """
            SELECT v.id_voyage, d.pays, d.ville, v.date_depart, v.date_retour,
                   v.prix, v.places_disponibles
            FROM voyages v
            INNER JOIN destinations d ON d.id_destination = v.id_destination
            WHERE 1 = 1
        """
        params = {}

        if filters.get("pays"):
            sql += " AND LOWER(d.pays) LIKE :pays"
            params["pays"] = f"%{filters['pays'].lower()}%"
        if filters.get("ville"):
            sql += " AND LOWER(d.ville) LIKE :ville"
            params["ville"] = f"%{filters['ville'].lower()}%"
        if filters.get("date_depart"):
            sql += " AND TRUNC(v.date_depart) >= TO_DATE(:date_depart, 'YYYY-MM-DD')"
            params["date_depart"] = filters["date_depart"]
        if filters.get("date_retour"):
            sql += " AND TRUNC(v.date_retour) <= TO_DATE(:date_retour, 'YYYY-MM-DD')"
            params["date_retour"] = filters["date_retour"]
        if filters.get("prix_min"):
            sql += " AND v.prix >= :prix_min"
            params["prix_min"] = float(filters["prix_min"])
        if filters.get("prix_max"):
            sql += " AND v.prix <= :prix_max"
            params["prix_max"] = float(filters["prix_max"])

        sql += " ORDER BY v.date_depart ASC"
        return sql, self.database.fetch_all(sql, params)

    def filter_reservations(self, filters):
        sql = """
            SELECT r.id_reservation, c.nom, c.prenom, d.pays, d.ville,
                   r.date_reservation, r.nombre_personnes, r.montant
            FROM reservations r
            INNER JOIN clients c ON c.id_client = r.id_client
            INNER JOIN voyages v ON v.id_voyage = r.id_voyage
            INNER JOIN destinations d ON d.id_destination = v.id_destination
            WHERE 1 = 1
        """
        params = {}

        if filters.get("client"):
            sql += " AND (LOWER(c.nom) LIKE :client OR LOWER(c.prenom) LIKE :client)"
            params["client"] = f"%{filters['client'].lower()}%"
        if filters.get("voyage"):
            sql += " AND (LOWER(d.pays) LIKE :voyage OR LOWER(d.ville) LIKE :voyage)"
            params["voyage"] = f"%{filters['voyage'].lower()}%"
        if filters.get("date_reservation"):
            sql += " AND TRUNC(r.date_reservation) = TO_DATE(:date_reservation, 'YYYY-MM-DD')"
            params["date_reservation"] = filters["date_reservation"]
        if filters.get("montant_min"):
            sql += " AND r.montant >= :montant_min"
            params["montant_min"] = float(filters["montant_min"])
        if filters.get("montant_max"):
            sql += " AND r.montant <= :montant_max"
            params["montant_max"] = float(filters["montant_max"])

        sql += " ORDER BY r.date_reservation DESC"
        return sql, self.database.fetch_all(sql, params)

    def dashboard_stats(self):
        stats = {}
        stats["clients"] = self.database.fetch_one("SELECT COUNT(*) total FROM clients")["total"]
        stats["destinations"] = self.database.fetch_one("SELECT COUNT(*) total FROM destinations")["total"]
        stats["voyages"] = self.database.fetch_one("SELECT COUNT(*) total FROM voyages")["total"]
        stats["reservations"] = self.database.fetch_one("SELECT COUNT(*) total FROM reservations")["total"]

        # destination_top: try to include image_path if the column exists, else fallback
        try:
            destination_top = self.database.fetch_one(
                """
                SELECT id_destination AS id, image_path, pays, ville, label, total FROM (
                    SELECT d.id_destination,
                           d.image_path,
                           d.pays,
                           d.ville,
                           d.pays || ' - ' || d.ville AS label,
                           COUNT(*) AS total
                    FROM reservations r
                    INNER JOIN voyages v ON v.id_voyage = r.id_voyage
                    INNER JOIN destinations d ON d.id_destination = v.id_destination
                    GROUP BY d.id_destination, d.image_path, d.pays, d.ville
                    ORDER BY total DESC
                ) WHERE ROWNUM = 1
                """
            )
        except Exception:
            tmp = self.database.fetch_one(
                """
                SELECT pays, ville, label, total FROM (
                    SELECT d.pays,
                           d.ville,
                           d.pays || ' - ' || d.ville AS label,
                           COUNT(*) AS total
                    FROM reservations r
                    INNER JOIN voyages v ON v.id_voyage = r.id_voyage
                    INNER JOIN destinations d ON d.id_destination = v.id_destination
                    GROUP BY d.pays, d.ville
                    ORDER BY total DESC
                ) WHERE ROWNUM = 1
                """
            )
            if tmp:
                destination_top = {"label": tmp.get("label"), "total": tmp.get("total"), "image_path": None, "id": None, "pays": tmp.get("pays"), "ville": tmp.get("ville")}
            else:
                destination_top = None

        # voyage_top: try to include image_path if available, else fallback
        try:
            voyage_top = self.database.fetch_one(
                """
                SELECT id_voyage AS id, v.id_destination, d.image_path, d.pays, d.ville, label, total FROM (
                    SELECT v.id_voyage,
                           v.id_destination,
                           d.image_path,
                           d.pays,
                           d.ville,
                           'Voyage #' || v.id_voyage || ' - ' || d.ville AS label,
                           COUNT(*) AS total
                    FROM reservations r
                    INNER JOIN voyages v ON v.id_voyage = r.id_voyage
                    INNER JOIN destinations d ON d.id_destination = v.id_destination
                    GROUP BY v.id_voyage, v.id_destination, d.image_path, d.pays, d.ville
                    ORDER BY total DESC
                ) WHERE ROWNUM = 1
                """
            )
        except Exception:
            tmp = self.database.fetch_one(
                """
                SELECT pays, ville, label, total FROM (
                    SELECT d.pays,
                           d.ville,
                           'Voyage #' || v.id_voyage || ' - ' || d.ville AS label,
                           COUNT(*) AS total
                    FROM reservations r
                    INNER JOIN voyages v ON v.id_voyage = r.id_voyage
                    INNER JOIN destinations d ON d.id_destination = v.id_destination
                    GROUP BY v.id_voyage, d.pays, d.ville
                    ORDER BY total DESC
                ) WHERE ROWNUM = 1
                """
            )
            if tmp:
                voyage_top = {"label": tmp.get("label"), "total": tmp.get("total"), "image_path": None, "id": None, "pays": tmp.get("pays"), "ville": tmp.get("ville")}
            else:
                voyage_top = None

        stats["destination_top"] = destination_top
        stats["voyage_top"] = voyage_top
        return stats

    def recent_reservations(self, limit=4):
        return self.database.fetch_all(
            """
            SELECT * FROM (
                SELECT c.nom, c.prenom, d.pays, d.ville,
                       r.date_reservation, r.montant
                FROM reservations r
                INNER JOIN clients c ON c.id_client = r.id_client
                INNER JOIN voyages v ON v.id_voyage = r.id_voyage
                INNER JOIN destinations d ON d.id_destination = v.id_destination
                ORDER BY r.date_reservation DESC
            )
            WHERE ROWNUM <= :limit
            """,
            {"limit": limit},
        )
