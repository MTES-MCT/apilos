from typing import List

from django.db import connections
from django.db.backends.utils import CursorWrapper

from ecoloweb.services import ModelImportHandler, ConventionImportHandler


class EcolowebImportService:
    """
    Service en charge de transférer les données depuis la base Ecoloweb vers la base APiLos
    """
    connection: CursorWrapper
    handlers: List[ModelImportHandler]

    def __init__(self, connection='ecoloweb'):
        self.connection: CursorWrapper = connections[connection].cursor()
        self.handlers = [
            # TODO manager dependencies between handlers (ex: ProgrammeLotImportHandler requires ProgrammeImportHandler)
            ConventionImportHandler(self.connection)
        ]

    def process(self):
        for handler in self.handlers:
            handler.handle()
