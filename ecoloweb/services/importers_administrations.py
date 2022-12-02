from datetime import datetime
from typing import List

from .importers import ModelImporter

from instructeurs.models import Administration


class AdministrationImporter(ModelImporter):
    model = Administration

    def __init__(self, departement: str, import_date: datetime, debug=False):
        super().__init__(departement, import_date, debug)
        self._query = self._get_file_content('resources/sql/administrations.sql')

    def _get_sql_one_query(self) -> str:
        return self._query

    def _get_identity_keys(self) -> List[str]:
        return ['code']
