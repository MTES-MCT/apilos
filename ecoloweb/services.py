import os

from abc import ABC, abstractmethod
from typing import List

from django.db import connections
from django.db.backends.utils import CursorWrapper
from django.template import Template, Context

from bailleurs.models import Bailleur
from programmes.models import Programme


class ModelImportHandler(ABC):
    connection: CursorWrapper
    count: int = 0

    def __init__(self, connection: CursorWrapper):
        self.connection = connection

    @abstractmethod
    def _get_sql_query(self) -> str:
        pass

    def _get_file_content(self, path):
        return ''.join(open(os.path.join(os.path.dirname(__file__), path), 'r').readlines())

    def _get_sql_from_template(self, path: str, context: dict):
        return Template(self._get_file_content(path)).render(Context(context))

    def _get_sql_from_file(self, path: str) -> str:
        return self._get_file_content(path)

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


class ProgrammeImportHandler(ModelImportHandler):
    """
    Mapping des données entre APiLos et Ecolo:
    * programme = ecolo_programmelogement
    * lot =
    * logement = ecolo_programmeadresse
    Par contre:
    * sur ecolo le type d'opération (NEUF, REHAB, etc...) est par programme, sur ecolo il est par lot. Par chance sur le
    dump que l'on a c'est toujours le même type d'opération même pour les programmes multi lots
    """

    def _get_sql_query(self) -> str:
        return self._get_sql_from_template('resources/sql/programmes.sql', {'max_row': 10})

    def _process_row(self, data: dict) -> bool:
        # TODO: attach a real bailleur instead of a randomly picked one
        data['bailleur'] = Bailleur.objects.order_by('?').first()
        # TODO: save the ecoloweb_id somewhere to prevent duplicate imports
        ecoloweb_id = data.pop('id')

        if data['numero_galion'] is not None:
            _, created = Programme.objects.get_or_create(numero_galion=data['numero_galion'], defaults=data)
        else:
            _ = Programme.objects.create(**data)
            created = True

        return created

    def on_complete(self):
        print(f"Migrated {self.count} programme(s)")


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


