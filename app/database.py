from contextlib import contextmanager

import oracledb

from app.config import ORACLE_CONFIG


class Database:
    def __init__(self, config=ORACLE_CONFIG):
        self.config = config

    @contextmanager
    def connection(self):
        connection = oracledb.connect(
            user=self.config.user,
            password=self.config.password,
            dsn=self.config.dsn,
        )
        try:
            yield connection
            connection.commit()
        except Exception:
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
