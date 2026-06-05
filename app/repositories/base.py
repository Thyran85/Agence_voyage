class BaseRepository:
    table_name = ""
    id_column = ""
    columns = ()
    searchable_columns = ()
    sortable_columns = ()

    def __init__(self, database):
        self.database = database

    def list(self, search_by=None, search_value=None, sort_by=None, sort_dir="ASC"):
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

    def get(self, item_id):
        return self.database.fetch_one(
            f"SELECT * FROM {self.table_name} WHERE {self.id_column} = :item_id",
            {"item_id": item_id},
        )

    def create(self, data):
        columns = [column for column in self.columns if column in data]
        placeholders = [f":{column}" for column in columns]
        sql = (
            f"INSERT INTO {self.table_name} ({', '.join(columns)}) "
            f"VALUES ({', '.join(placeholders)})"
        )
        return self.database.execute(sql, {column: data[column] for column in columns})

    def update(self, item_id, data):
        columns = [column for column in self.columns if column in data]
        assignments = [f"{column} = :{column}" for column in columns]
        params = {column: data[column] for column in columns}
        params["item_id"] = item_id
        sql = (
            f"UPDATE {self.table_name} SET {', '.join(assignments)} "
            f"WHERE {self.id_column} = :item_id"
        )
        return self.database.execute(sql, params)

    def delete(self, item_id):
        return self.database.execute(
            f"DELETE FROM {self.table_name} WHERE {self.id_column} = :item_id",
            {"item_id": item_id},
        )
