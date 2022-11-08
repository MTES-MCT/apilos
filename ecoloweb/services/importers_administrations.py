from .importers import ModelImporter

from instructeurs.models import Administration


class AdministrationImporter(ModelImporter):
    model = Administration

    def __init__(self):
        super().__init__()
        self._query = self._get_file_content('resources/sql/administrations.sql')

    def _get_sql_query(self) -> str:
        return self._query
