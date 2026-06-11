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
    status VARCHAR2(20) DEFAULT 'EN ATTENTE' NOT NULL,
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
VALUES ('Rakoto', 'Mialy', '0321001001', 'mialy.rakoto@mail.mg', 'Lot IVT 12, Antananarivo');
INSERT INTO clients (nom, prenom, telephone, email, adresse)
VALUES ('Rabe', 'Faly', '0321002002', 'faly.rabe@mail.mg', 'Route circulaire, Mahamasina');
INSERT INTO clients (nom, prenom, telephone, email, adresse)
VALUES ('Andriantsara', 'Nivo', '0321003003', 'nivo.andriantsara@mail.mg', 'BP 45, Antsirabe');

INSERT INTO destinations (pays, ville, description, prix_base, image_path)
VALUES ('Madagascar', 'Antananarivo', 'Capitale des milles collines, artisanat et culture Merina.', 3250000, NULL);
INSERT INTO destinations (pays, ville, description, prix_base, image_path)
VALUES ('Madagascar', 'Nosy Be', 'Île paradisiaque, plages de sable blanc et eaux turquoise.', 3900000, NULL);
INSERT INTO destinations (pays, ville, description, prix_base, image_path)
VALUES ('Madagascar', 'Toliara', 'Plages sauvages et baobabs de renom.', 3600000, NULL);
INSERT INTO destinations (pays, ville, description, prix_base, image_path)
VALUES ('Madagascar', 'Île Sainte-Marie', 'Plages bordées de cocotiers et observation des baleines.', 4450000, NULL);

INSERT INTO voyages (id_destination, date_depart, date_retour, prix, places_disponibles)
VALUES (1, DATE '2026-07-10', DATE '2026-07-17', 4250000, 24);
INSERT INTO voyages (id_destination, date_depart, date_retour, prix, places_disponibles)
VALUES (2, DATE '2026-08-03', DATE '2026-08-12', 5500000, 18);
INSERT INTO voyages (id_destination, date_depart, date_retour, prix, places_disponibles)
VALUES (3, DATE '2026-09-05', DATE '2026-09-12', 4650000, 30);
INSERT INTO voyages (id_destination, date_depart, date_retour, prix, places_disponibles)
VALUES (4, DATE '2026-10-14', DATE '2026-10-24', 6250000, 12);

INSERT INTO reservations (id_client, id_voyage, date_reservation, nombre_personnes, montant)
VALUES (1, 1, DATE '2026-06-01', 2, 8500000);
INSERT INTO reservations (id_client, id_voyage, date_reservation, nombre_personnes, montant)
VALUES (2, 2, DATE '2026-06-02', 1, 5500000);
INSERT INTO reservations (id_client, id_voyage, date_reservation, nombre_personnes, montant)
VALUES (3, 1, DATE '2026-06-03', 3, 12750000);

COMMIT;
