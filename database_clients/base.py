from abc import ABC, abstractmethod
from typing import List


class BaseDatabaseClient(ABC):
    def __init__(self):
        self._client = None
        self._is_connected = False
    @abstractmethod
    def connect(self):
        raise NotImplementedError("This method is not implemented.")
    @abstractmethod
    def disconnect(self):
        raise NotImplementedError("This method is not implemented.")
    @abstractmethod
    def is_connected(self):
        return self._is_connected
    @abstractmethod
    def get_client(self):
        if not self.is_connected:
            raise ConnectionError("Database client is not connected.")
        return self._client
    @abstractmethod
    def query(self, query: List, *args, **kwargs):
        raise NotImplementedError("This method is not implemented.")
    @abstractmethod
    def get_by_id(self, doc_id, *args, **kwargs):
        raise NotImplementedError("This method is not implemented.")
    @abstractmethod
    def query_all(self):
        raise NotImplementedError("This method is not implemented.")
    @abstractmethod
    def delete(self, query, *args, **kwargs):
        raise NotImplementedError("This method is not implemented.")
    @abstractmethod
    def insert(self, data, *args, **kwargs):
        raise NotImplementedError("This method is not implemented.")
    @abstractmethod
    def update(self, query, data, *args, **kwargs):
        raise NotImplementedError("This method is not implemented.")


def get_database_client(db_type: str, **kwargs) -> BaseDatabaseClient:
    match(db_type):
        case "tinydb":
            from database_clients.tinydb import TinyDBClient
            return TinyDBClient(**kwargs)
        case _:
            raise ValueError(f"Unsupported database type: {db_type}")