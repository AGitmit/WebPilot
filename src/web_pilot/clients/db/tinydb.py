from tinydb import TinyDB, Query
from web_pilot.utils.db import BaseDB

where = Query()


class TinyDBAdapter(BaseDB):
    def __init__(self, db_config: dict):
        self.db = TinyDB(db_config["db_path"])

    def insert(self, collection: str, data: dict):
        table = self.db.table(collection)
        table.insert(data)

    def update(self, collection: str, query: dict, new_data: dict):
        table = self.db.table(collection)
        table.update(new_data, where(query))

    def delete(self, collection: str, query: dict):
        table = self.db.table(collection)
        table.remove(where(query))

    def query(self, collection: str, query: dict):
        table = self.db.table(collection)
        return table.search(where(query))
