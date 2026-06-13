import logging
from contextlib import contextmanager

import oracledb

from app.config import ORACLE_CONFIG

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, config=ORACLE_CONFIG):
        self.config = config

    @contextmanager
    def connection(self):
        try:
            connection = oracledb.connect(
                user=self.config.user,
                password=self.config.password,
                dsn=self.config.dsn,
            )
        except oracledb.OperationalError:
            logger.exception("Connexion à Oracle impossible")
            raise ConnectionError(
                "Impossible de se connecter à la base Oracle. "
                "Vérifiez qu'Oracle est démarré (lsnrctl status) "
                "et que les identifiants dans la config sont corrects."
            )
        try:
            yield connection
            connection.commit()
        except oracledb.IntegrityError as e:
            logger.exception("Contrainte d'intégrité violée")
            connection.rollback()
            raise ValueError(
                "Opération refusée : une contrainte de base de données a été violée. "
                "Vérifiez que les données sont cohérentes (clés étrangères, unicité)."
            ) from e
        except oracledb.DatabaseError as e:
            logger.exception("Erreur base de données")
            connection.rollback()
            raise RuntimeError(
                "Erreur lors de l'exécution de la requête. "
                "Vérifiez la syntaxe SQL ou contactez l'administrateur."
            ) from e
        except Exception:
            logger.exception("Erreur inattendue - transaction annulée")
            connection.rollback()
            raise
        finally:
            connection.close()

    def fetch_all(self, sql, params=None):
        with self.connection() as connection:
            cursor = connection.cursor()
            cursor.execute(sql, params or {})
            columns = [column[0].lower() for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def fetch_one(self, sql, params=None):
        rows = self.fetch_all(sql, params)
        return rows[0] if rows else None

    def execute(self, sql, params=None):
        with self.connection() as connection:
            cursor = connection.cursor()
            cursor.execute(sql, params or {})
            return cursor.rowcount
