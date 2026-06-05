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
        data["montant"] = self.calculate_reservation_amount(
            data["id_voyage"], data["nombre_personnes"]
        )
        return self.reservations.create(data)

    def update_reservation(self, id_reservation, data):
        data = dict(data)
        data["montant"] = self.calculate_reservation_amount(
            data["id_voyage"], data["nombre_personnes"]
        )
        return self.reservations.update(id_reservation, data)

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
        return {
            "clients": self.database.fetch_one("SELECT COUNT(*) total FROM clients")["total"],
            "destinations": self.database.fetch_one("SELECT COUNT(*) total FROM destinations")["total"],
            "voyages": self.database.fetch_one("SELECT COUNT(*) total FROM voyages")["total"],
            "reservations": self.database.fetch_one("SELECT COUNT(*) total FROM reservations")["total"],
            "destination_top": self.database.fetch_one(
                """
                SELECT label, total FROM (
                    SELECT d.pays || ' - ' || d.ville AS label,
                           COUNT(*) AS total
                    FROM reservations r
                    INNER JOIN voyages v ON v.id_voyage = r.id_voyage
                    INNER JOIN destinations d ON d.id_destination = v.id_destination
                    GROUP BY d.pays, d.ville
                    ORDER BY total DESC
                ) WHERE ROWNUM = 1
                """
            ),
            "voyage_top": self.database.fetch_one(
                """
                SELECT label, total FROM (
                    SELECT 'Voyage #' || v.id_voyage || ' - ' || d.ville AS label,
                           COUNT(*) AS total
                    FROM reservations r
                    INNER JOIN voyages v ON v.id_voyage = r.id_voyage
                    INNER JOIN destinations d ON d.id_destination = v.id_destination
                    GROUP BY v.id_voyage, d.ville
                    ORDER BY total DESC
                ) WHERE ROWNUM = 1
                """
            ),
        }
