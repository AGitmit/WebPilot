from abc import ABC, abstractmethod


class BaseDB(ABC):
    @abstractmethod
    def insert(self, collection: str, data: dict):
        pass

    @abstractmethod
    def update(self, collection: str, query: dict, new_data: dict):
        pass

    @abstractmethod
    def delete(self, collection: str, query: dict):
        pass

    @abstractmethod
    def query(self, collection: str, query: dict):
        pass
