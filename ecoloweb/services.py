from abc import ABC, abstractmethod
from typing import List

from django.db import connections
from django.db.backends.utils import CursorWrapper


class ModelImportHandler(ABC):
    connection: CursorWrapper
    count: int = 0

    def __init__(self, connection: CursorWrapper):
        self.connection = connection

    @abstractmethod
    def _get_sql_query(self) -> str:
        pass

    @abstractmethod
    def _process_row(self, data: dict) -> bool:
        pass

    def handle(self):
        count: int = 0

        # Run query
        self.connection.execute(self._get_sql_query())
        # Extract metadata to be able to convert each row into a dict
        columns = [col[0] for col in self.connection.description]

        # To reduce memory allocation we fetch rows 1 by 1
        while (row := self.connection.fetchone()) is not None:
            data = dict(zip(columns, row))
            self.count += 1 if self._process_row(data) else 0

        self.on_complete()

    def on_complete(self):
        pass


class EcolowebImportService:
    """
    Service en charge de transférer les données depuis la base Ecoloweb vers la base APiLos
    """
    connection: CursorWrapper
    handlers: List[ModelImportHandler]

    def __init__(self, connection='ecoloweb'):
        self.connection: CursorWrapper = connections[connection].cursor()
        self.handlers = []

    def process(self):
        for handler in self.handlers:
            handler.handle()


