# Application Desktop Agence de Voyage

Application Python 3 avec CustomTkinter, Oracle Database XE et python-oracledb.
Le projet suit une architecture MVC simplifiée :

- `app/views` : interface graphique CustomTkinter
- `app/controllers` : orchestration entre vues et services
- `app/services` : logique métier, filtres, statistiques
- `app/repositories` : accès aux tables Oracle
- `sql/schema.sql` : création des tables, séquences, triggers et données de démonstration

## Fonctionnalités

- CRUD complet pour clients, destinations, voyages et réservations
- Recherche et tri par module
- Calcul automatique du montant d'une réservation
- Filtres multicritères dynamiques pour voyages et réservations
- Onglet pédagogique avec exemples Oracle : `SELECT`, `WHERE`, `LIKE`, `BETWEEN`, `IN`, `ORDER BY`, `GROUP BY`, `HAVING`, jointures et sous-requête
- Dashboard avec totaux, destination la plus réservée et voyage le plus réservé

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Préparer Oracle XE

Connectez-vous avec un utilisateur ayant les droits de création dans la PDB `XEPDB1`, puis créez l'utilisateur applicatif si nécessaire :

```sql
CREATE USER travel_admin IDENTIFIED BY travel_admin
    DEFAULT TABLESPACE USERS
    TEMPORARY TABLESPACE TEMP
    QUOTA UNLIMITED ON USERS;
GRANT CONNECT, RESOURCE TO travel_admin;
ALTER USER travel_admin QUOTA UNLIMITED ON USERS;
```

Chargez ensuite le schéma depuis la racine du projet avec le `sqlplus` du conteneur :

```bash
podman exec -i oracle-xe sqlplus travel_admin/travel_admin@XEPDB1 < sql/schema.sql
```

La forme avec `< sql/schema.sql` est importante : le fichier est sur votre machine, pas dans le conteneur.

Si `sqlplus` est aussi installé sur votre machine, vous pouvez utiliser l'accès réseau Oracle :

```bash
sqlplus travel_admin/travel_admin@localhost:1521/XEPDB1 @sql/schema.sql
```

Avec Oracle XE dans un conteneur Podman, le flux complet est donc :

```bash
podman start oracle-xe
podman exec -it oracle-xe sqlplus system/<mot_de_passe_system>@XEPDB1
```

Puis exécutez les commandes SQL de création de l'utilisateur ci-dessus. Ensuite, depuis la racine du projet, chargez le schéma avec :

```bash
podman exec -i oracle-xe sqlplus travel_admin/travel_admin@XEPDB1 < sql/schema.sql
```

### Réparer l'erreur ORA-01950

Si le chargement du schéma échoue sur :

```text
ORA-01950: no privileges on tablespace 'USERS'
```

connectez-vous en `system` dans `XEPDB1` et redonnez le quota :

```bash
podman exec -it oracle-xe sqlplus system/<mot_de_passe_system>@XEPDB1
```

```sql
ALTER USER travel_admin QUOTA UNLIMITED ON USERS;
EXIT;
```

Si vous avez déjà lancé `sql/schema.sql` avant de corriger le quota, les tables et séquences existent peut-être déjà sans les données de démonstration. Le plus simple en développement est de recréer l'utilisateur :

```bash
podman exec -it oracle-xe sqlplus system/<mot_de_passe_system>@XEPDB1
```

```sql
DROP USER travel_admin CASCADE;
CREATE USER travel_admin IDENTIFIED BY travel_admin
    DEFAULT TABLESPACE USERS
    TEMPORARY TABLESPACE TEMP
    QUOTA UNLIMITED ON USERS;
GRANT CONNECT, RESOURCE TO travel_admin;
EXIT;
```

Puis rechargez le schéma :

```bash
podman exec -i oracle-xe sqlplus travel_admin/travel_admin@XEPDB1 < sql/schema.sql
```

## Configuration

Par défaut, l'application utilise :

- `ORACLE_USER=travel_admin`
- `ORACLE_PASSWORD=travel_admin`
- `ORACLE_DSN=localhost:1521/XEPDB1`

Vous pouvez les surcharger :

```bash
export ORACLE_USER=travel_admin
export ORACLE_PASSWORD=travel_admin
export ORACLE_DSN=localhost:1521/XEPDB1
```

## Lancement

```bash
python main.py
```

Les dates doivent être saisies au format `YYYY-MM-DD`.
