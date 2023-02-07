from datetime import datetime

from .importers import ModelImporter

from instructeurs.models import Administration


class AdministrationImporter(ModelImporter):

    model = Administration

    def __init__(self, departement: str, import_date: datetime, debug=False):
        super().__init__(departement, import_date, debug)

        self._identity_keys = ["code"]
        self._query_one = self._get_file_content("resources/sql/administrations.sql")
