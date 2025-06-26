from tinydb import Query, TinyDB
from .base import BaseDatabaseClient
from typing import Any, Dict, List

class TinyDBClient(BaseDatabaseClient):
    def __init__(self, db_path:str='./.data/db.json',table_name: str = '2fauth'):
        super().__init__()
        self._client = TinyDB(db_path)
        self._db_path = db_path
        self._table_name = table_name
        self._is_connected = True
        self.connect()

    def _build_query_cmd(self,key: str,value: Any):
        return getattr(Query(),key) == value

    def connect(self):
        if not self._is_connected:
            self._client = TinyDB(self._db_path)
            self._is_connected = True

    def disconnect(self):
        if self._is_connected:
            self._client.close()
            self._is_connected = False

    def is_connected(self):
        return self._is_connected

    def get_client(self):
        if not self.is_connected():
            raise ConnectionError("Database client is not connected.")
        return self._client.table(self._table_name)

    def query(self, query: List, *args: Any, **kwargs: Any):
        q = Query()
        cond = self._build_query_cmd(query[0],query[1])
        return self.get_client().search(cond=cond) # type: ignore
    def query_all(self):
        return self.get_client().all()
    
    def get_by_id(self, doc_id: int, *args: Any, **kwargs: Any):
        return self.get_client().get(doc_id=doc_id)

    def delete(self, query: Any, *args: Any, **kwargs: Any) -> List[int]:
        q = Query()
        return self.get_client().remove(self._build_query_cmd(query[0],query[1]))  # type: ignore

    def insert(self, data: Dict, *args: Any, **kwargs: Any) -> int:
        return self.get_client().insert(data)

    def update(self, query: Any, data: Dict, *args: Any, **kwargs: Any) -> List[int]:
        q = Query()
        return self.get_client().update(data, self._build_query_cmd(query[0],query[1])) # type: ignore