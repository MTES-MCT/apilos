from datetime import date

from .importers import ModelImporter

from instructeurs.models import Administration


class AdministrationImporter(ModelImporter):

    model = Administration

    def __init__(self, departement: str, import_date: date, debug=False, update=False):
        super().__init__(departement, import_date, debug=debug, update=update)

        self._identity_keys = ["code"]
        self._query_one = self._get_file_content("resources/sql/administrations.sql")
