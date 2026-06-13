import logging

logger = logging.getLogger(__name__)


class BaseRepository:
    table_name = ""
    id_column = ""
    columns = ()
    searchable_columns = ()
    sortable_columns = ()

    def __init__(self, database):
        self.database = database

    def list(self, search_by=None, search_value=None, sort_by=None, sort_dir="ASC"):
        try:
            sql = f"SELECT * FROM {self.table_name}"
            params = {}
            clauses = []

            if search_by and search_value and search_by in self.searchable_columns:
                clauses.append(f"LOWER({search_by}) LIKE :search_value")
                params["search_value"] = f"%{search_value.lower()}%"

            if clauses:
                sql += " WHERE " + " AND ".join(clauses)

            if sort_by in self.sortable_columns:
                direction = "DESC" if str(sort_dir).upper() == "DESC" else "ASC"
                sql += f" ORDER BY {sort_by} {direction}"

            return self.database.fetch_all(sql, params)
        except ConnectionError:
            raise
        except Exception:
            logger.exception("Erreur lors du listage %s", self.table_name)
            raise RuntimeError(f"Impossible de charger la liste des {self.table_name}. Vérifiez la connexion à la base.")

    def get(self, item_id):
        try:
            return self.database.fetch_one(
                f"SELECT * FROM {self.table_name} WHERE {self.id_column} = :item_id",
                {"item_id": item_id},
            )
        except ConnectionError:
            raise
        except Exception:
            logger.exception("Erreur lors de la récupération %s id=%s", self.table_name, item_id)
            raise RuntimeError(f"Impossible de récupérer l'élément. Vérifiez que l'identifiant est correct.")

    def create(self, data):
        try:
            columns = [column for column in self.columns if column in data]
            placeholders = [f":{column}" for column in columns]
            sql = (
                f"INSERT INTO {self.table_name} ({', '.join(columns)}) "
                f"VALUES ({', '.join(placeholders)})"
            )
            return self.database.execute(sql, {column: data[column] for column in columns})
        except ConnectionError:
            raise
        except ValueError as e:
            raise ValueError(str(e))
        except Exception:
            logger.exception("Erreur lors de la création dans %s", self.table_name)
            raise RuntimeError(
                f"Création impossible. Vérifiez que les données sont valides "
                f"et que la table {self.table_name} est accessible."
            )

    def update(self, item_id, data):
        try:
            columns = [column for column in self.columns if column in data]
            assignments = [f"{column} = :{column}" for column in columns]
            params = {column: data[column] for column in columns}
            params["item_id"] = item_id
            sql = (
                f"UPDATE {self.table_name} SET {', '.join(assignments)} "
                f"WHERE {self.id_column} = :item_id"
            )
            return self.database.execute(sql, params)
        except ConnectionError:
            raise
        except ValueError as e:
            raise ValueError(str(e))
        except Exception:
            logger.exception("Erreur lors de la mise à jour dans %s id=%s", self.table_name, item_id)
            raise RuntimeError(
                f"Modification impossible. Vérifiez que l'élément existe "
                f"et que les données sont valides."
            )

    def delete(self, item_id):
        try:
            return self.database.execute(
                f"DELETE FROM {self.table_name} WHERE {self.id_column} = :item_id",
                {"item_id": item_id},
            )
        except ConnectionError:
            raise
        except ValueError as e:
            raise ValueError(str(e))
        except Exception:
            logger.exception("Erreur lors de la suppression dans %s id=%s", self.table_name, item_id)
            raise RuntimeError(
                f"Suppression impossible. Vérifiez que l'élément existe "
                f"et qu'il n'est pas lié à d'autres enregistrements."
            )
