# Application Web Agence de Voyage (Django)

Application web Django 5 qui remplace l'application desktop CustomTkinter
d'origine. La couche métier existante (services / repositories / accès
Oracle via `python-oracledb`) est réutilisée telle quelle ; Django ne sert
que de frontal HTTP.

## Architecture

- `oracleproject_web/` : projet Django (settings, urls racine)
- `travel/` : application Django (models, views, forms, urls, templates)
- `templates/` : templates HTML (layout + pages)
- `static/` : fichiers statiques (CSS, JS, images)
- `app/services/` : couche métier (réutilisée depuis l'ancien projet)
- `app/repositories/` : accès Oracle bas niveau
- `sql/schema.sql` : schéma Oracle (inchangé)

## Fonctionnalités

- Tableau de bord avec totaux, destination et voyage les plus réservés
- CRUD complet pour clients, destinations, voyages, réservations
- Recherche et tri dynamiques sur chaque module
- Filtres multicritères avec aperçu SQL généré
- Onglet pédagogique SQL Oracle (SELECT, WHERE, LIKE, BETWEEN, IN, ORDER BY, GROUP BY, HAVING, jointures, sous-requêtes)
- Interface sombre reproduisant le thème de l'application desktop

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Préparer Oracle XE

Identique à la version desktop : créer l'utilisateur `travel_admin`,
charger le schéma avec `sql/schema.sql`. Voir la section correspondante
plus bas.

## Lancement du serveur web

```bash
python manage.py migrate            # crée la base SQLite pour auth/admin
python manage.py runserver 0.0.0.0:8000
```

Puis ouvrir <http://localhost:8000/>.

Les variables d'environnement suivantes sont reconnues :

| Variable              | Valeur par défaut             | Description                       |
|-----------------------|-------------------------------|-----------------------------------|
| `ORACLE_USER`         | `travel_admin`                | Utilisateur Oracle                |
| `ORACLE_PASSWORD`     | `travel_admin`                | Mot de passe Oracle               |
| `ORACLE_DSN`          | `localhost:1521/XEPDB1`       | DSN Oracle                        |
| `DJANGO_SECRET_KEY`   | valeur de dev                 | Clé secrète Django                |
| `DJANGO_DEBUG`        | `1`                           | Mettre `0` en production          |
| `DJANGO_ALLOWED_HOSTS`| `*`                           | Liste CSV des hôtes autorisés     |

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

Si vous rencontrez l'erreur `ORA-01950`, voir la section
« Réparer l'erreur ORA-01950 » du README d'origine pour les commandes de
correction.

## Notes techniques

- Les modèles Django (`travel/models.py`) sont déclarés en
  `managed = False` : Django ne crée ni ne modifie jamais les tables
  Oracle existantes. L'accès reste effectué par `python-oracledb` à
  travers `TravelService`.
- Le thème sombre de l'application desktop a été transposé en CSS dans
  `static/travel/css/app.css`.
- L'ancien code desktop (CustomTkinter) reste fonctionnel via
  `python main.py` ; les deux versions partagent la même couche métier.
