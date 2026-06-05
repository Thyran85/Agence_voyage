QUERY_EXAMPLES = [
    ("SELECT", "SELECT id_client, nom, prenom, email FROM clients"),
    ("WHERE", "SELECT * FROM destinations WHERE pays = 'France'"),
    ("LIKE", "SELECT * FROM clients WHERE LOWER(nom) LIKE '%dup%'"),
    ("BETWEEN", "SELECT * FROM voyages WHERE prix BETWEEN 500 AND 2000"),
    ("IN", "SELECT * FROM destinations WHERE pays IN ('France', 'Italie', 'Espagne')"),
    ("ORDER BY", "SELECT * FROM voyages ORDER BY date_depart DESC"),
    (
        "GROUP BY",
        """
        SELECT id_voyage, COUNT(*) AS total_reservations
        FROM reservations
        GROUP BY id_voyage
        """,
    ),
    (
        "HAVING",
        """
        SELECT id_voyage, COUNT(*) AS total_reservations
        FROM reservations
        GROUP BY id_voyage
        HAVING COUNT(*) >= 2
        """,
    ),
    (
        "INNER JOIN",
        """
        SELECT c.nom, c.prenom, d.pays, d.ville, r.montant
        FROM reservations r
        INNER JOIN clients c ON c.id_client = r.id_client
        INNER JOIN voyages v ON v.id_voyage = r.id_voyage
        INNER JOIN destinations d ON d.id_destination = v.id_destination
        """,
    ),
    (
        "LEFT JOIN",
        """
        SELECT c.nom, c.prenom, r.id_reservation
        FROM clients c
        LEFT JOIN reservations r ON r.id_client = c.id_client
        """,
    ),
    (
        "Sous-requêtes",
        """
        SELECT *
        FROM voyages
        WHERE prix > (SELECT AVG(prix) FROM voyages)
        """,
    ),
]
