from invisage.clients.db.tinydb import TinyDBAdapter
from invisage.clients.db.mongo import MongoDBAdapter
from invisage.utils.db import BaseDB


# Factory to choose the appropriate database
def get_db_instance(db_type: str, db_config: dict) -> BaseDB:
    if db_type == "tinydb":
        return TinyDBAdapter(db_config)
    elif db_type == "mongodb":
        return MongoDBAdapter(db_config)
    else:
        raise ValueError(f"Unsupported DB type: {db_type}")


# Example config for TinyDB
tinydb_config = {"db_path": "tinydb.json"}

# Example config for MongoDB
mongodb_config = {"uri": "mongodb://localhost:27017/", "db_name": "test_db"}


if __name__ == "__main__":
    # delete this - just for testing
    # Get the DB instance based on type
    db_type = "tinydb"  # Can be "tinydb" or "mongodb"
    db_instance = get_db_instance(db_type, mongodb_config)

    # Insert data
    data = {"name": "Alice", "age": 30}
    db_instance.insert("users", data)

    # Query data
    query_result = db_instance.query("users", {"name": "Alice"})
    print(query_result)

    # Update data
    db_instance.update("users", {"name": "Alice"}, {"age": 31})

    # Delete data
    db_instance.delete("users", {"name": "Alice"})
