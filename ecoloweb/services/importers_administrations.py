from typing import List

from .importers import ModelImporter

from instructeurs.models import Administration


class AdministrationImporter(ModelImporter):
    model = Administration

    def _get_query_one(self) -> str:
        return self._get_file_content('resources/sql/administrations.sql')

    def _get_identity_keys(self) -> List[str]:
        return ['code']
