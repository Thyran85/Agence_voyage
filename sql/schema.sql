CREATE TABLE clients (
    id_client NUMBER PRIMARY KEY,
    nom VARCHAR2(80) NOT NULL,
    prenom VARCHAR2(80) NOT NULL,
    telephone VARCHAR2(30),
    email VARCHAR2(120) UNIQUE,
    adresse VARCHAR2(255)
);

CREATE TABLE destinations (
    id_destination NUMBER PRIMARY KEY,
    pays VARCHAR2(80) NOT NULL,
    ville VARCHAR2(80) NOT NULL,
    description VARCHAR2(500),
    prix_base NUMBER(10, 2) NOT NULL CHECK (prix_base >= 0),
    image_path VARCHAR2(500)
);

CREATE TABLE voyages (
    id_voyage NUMBER PRIMARY KEY,
    id_destination NUMBER NOT NULL,
    date_depart DATE NOT NULL,
    date_retour DATE NOT NULL,
    prix NUMBER(10, 2) NOT NULL CHECK (prix >= 0),
    places_disponibles NUMBER NOT NULL CHECK (places_disponibles >= 0),
    CONSTRAINT fk_voyages_destination
        FOREIGN KEY (id_destination) REFERENCES destinations(id_destination),
    CONSTRAINT ck_voyages_dates CHECK (date_retour >= date_depart)
);

CREATE TABLE reservations (
    id_reservation NUMBER PRIMARY KEY,
    id_client NUMBER NOT NULL,
    id_voyage NUMBER NOT NULL,
    date_reservation DATE DEFAULT SYSDATE NOT NULL,
    nombre_personnes NUMBER NOT NULL CHECK (nombre_personnes > 0),
    montant NUMBER(10, 2) NOT NULL CHECK (montant >= 0),
    CONSTRAINT fk_reservations_client
        FOREIGN KEY (id_client) REFERENCES clients(id_client),
    CONSTRAINT fk_reservations_voyage
        FOREIGN KEY (id_voyage) REFERENCES voyages(id_voyage)
);

CREATE SEQUENCE seq_clients START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE seq_destinations START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE seq_voyages START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE seq_reservations START WITH 1 INCREMENT BY 1;

CREATE OR REPLACE TRIGGER trg_clients_id
BEFORE INSERT ON clients
FOR EACH ROW
WHEN (NEW.id_client IS NULL)
BEGIN
    :NEW.id_client := seq_clients.NEXTVAL;
END;
/

CREATE OR REPLACE TRIGGER trg_destinations_id
BEFORE INSERT ON destinations
FOR EACH ROW
WHEN (NEW.id_destination IS NULL)
BEGIN
    :NEW.id_destination := seq_destinations.NEXTVAL;
END;
/

CREATE OR REPLACE TRIGGER trg_voyages_id
BEFORE INSERT ON voyages
FOR EACH ROW
WHEN (NEW.id_voyage IS NULL)
BEGIN
    :NEW.id_voyage := seq_voyages.NEXTVAL;
END;
/

CREATE OR REPLACE TRIGGER trg_reservations_id
BEFORE INSERT ON reservations
FOR EACH ROW
WHEN (NEW.id_reservation IS NULL)
BEGIN
    :NEW.id_reservation := seq_reservations.NEXTVAL;
END;
/

INSERT INTO clients (nom, prenom, telephone, email, adresse)
VALUES ('Dupont', 'Claire', '0601020304', 'claire.dupont@example.com', '12 rue des Lilas, Paris');
INSERT INTO clients (nom, prenom, telephone, email, adresse)
VALUES ('Martin', 'Hugo', '0605060708', 'hugo.martin@example.com', '8 avenue Victor Hugo, Lyon');
INSERT INTO clients (nom, prenom, telephone, email, adresse)
VALUES ('Benali', 'Sarah', '0611121314', 'sarah.benali@example.com', '5 boulevard Massena, Marseille');

INSERT INTO destinations (pays, ville, description, prix_base, image_path)
VALUES ('France', 'Paris', 'Culture, gastronomie et monuments.', 650, NULL);
INSERT INTO destinations (pays, ville, description, prix_base, image_path)
VALUES ('Italie', 'Rome', 'Circuit historique et dolce vita.', 780, NULL);
INSERT INTO destinations (pays, ville, description, prix_base, image_path)
VALUES ('Espagne', 'Barcelone', 'Mer, architecture et vie nocturne.', 720, NULL);
INSERT INTO destinations (pays, ville, description, prix_base, image_path)
VALUES ('Maroc', 'Marrakech', 'Souks, palais et desert.', 890, NULL);

INSERT INTO voyages (id_destination, date_depart, date_retour, prix, places_disponibles)
VALUES (1, DATE '2026-07-10', DATE '2026-07-17', 850, 24);
INSERT INTO voyages (id_destination, date_depart, date_retour, prix, places_disponibles)
VALUES (2, DATE '2026-08-03', DATE '2026-08-12', 1100, 18);
INSERT INTO voyages (id_destination, date_depart, date_retour, prix, places_disponibles)
VALUES (3, DATE '2026-09-05', DATE '2026-09-12', 930, 30);
INSERT INTO voyages (id_destination, date_depart, date_retour, prix, places_disponibles)
VALUES (4, DATE '2026-10-14', DATE '2026-10-24', 1250, 12);

INSERT INTO reservations (id_client, id_voyage, date_reservation, nombre_personnes, montant)
VALUES (1, 1, DATE '2026-06-01', 2, 1700);
INSERT INTO reservations (id_client, id_voyage, date_reservation, nombre_personnes, montant)
VALUES (2, 2, DATE '2026-06-02', 1, 1100);
INSERT INTO reservations (id_client, id_voyage, date_reservation, nombre_personnes, montant)
VALUES (3, 1, DATE '2026-06-03', 3, 2550);

COMMIT;
