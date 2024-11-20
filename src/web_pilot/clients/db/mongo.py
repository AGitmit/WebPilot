from pymongo import MongoClient
from web_pilot.utils.db import BaseDB


class MongoDBAdapter(BaseDB):
    def __init__(self, db_config: dict):
        self.client = MongoClient(db_config["uri"])
        self.db = self.client[db_config["db_name"]]

    def insert(self, collection: str, data: dict):
        col = self.db[collection]
        col.insert_one(data)

    def update(self, collection: str, query: dict, new_data: dict):
        col = self.db[collection]
        col.update_one(query, {"$set": new_data})

    def delete(self, collection: str, query: dict):
        col = self.db[collection]
        col.delete_one(query)

    def query(self, collection: str, query: dict):
        col = self.db[collection]
        return list(col.find(query))
