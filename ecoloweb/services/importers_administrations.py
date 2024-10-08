from datetime import date

from instructeurs.models import Administration

from .importers import ModelImporter


class AdministrationImporter(ModelImporter):

    model = Administration

    def __init__(self, departement: str, import_date: date, debug=False, update=False):
        super().__init__(departement, import_date, debug=debug, update=update)

        self._identity_keys = ["code"]
        self._query_one = self._get_file_content("importers/administration.sql")
