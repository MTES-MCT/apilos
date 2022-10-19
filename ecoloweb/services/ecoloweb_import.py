from typing import List

from django.db import connections
from django.db.backends.utils import CursorWrapper

from ecoloweb.services import ModelImportHandler
from ecoloweb.services.handlers_programmes import ProgrammeImportHandler


class EcolowebImportService:
    """
    Service en charge de transférer les données depuis la base Ecoloweb vers la base APiLos
    """
    connection: CursorWrapper # Connection to Ecoloweb database
    handlers: List[ModelImportHandler]

    def __init__(self, connection='ecoloweb'):
        self.connection: CursorWrapper = connections[connection].cursor()
        self.handlers = [
            # TODO manager dependencies between handlers (ex: ProgrammeLotImportHandler requires ProgrammeImportHandler)
            ProgrammeImportHandler()
        ]

    def process(self):
        for handler in self.handlers:
            handler.import_all(self)
