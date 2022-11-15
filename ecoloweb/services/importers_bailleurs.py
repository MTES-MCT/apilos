from typing import List

from . import SiretResolver
from .importers import ModelImporter
from bailleurs.models import Bailleur


class BailleurImporter(ModelImporter):
    model = Bailleur

    def __init__(self, debug=False):
        super().__init__(debug)
        self._siret_resolver = SiretResolver()
        self._query = self._get_file_content('resources/sql/bailleurs.sql')

    def _get_sql_one_query(self) -> str:
        return self._query

    def _get_identity_keys(self) -> List[str]:
        return ['siret']

    def _prepare_data(self, data: dict) -> dict:
        codesiret = data.pop('codesiret')
        codesiren = data.pop('codesiren')
        codepersonne = data.pop('codepersonne')
        date_creation = data['cree_le']

        #
        if codesiret is not None:
            data['siret'] = codesiret

        elif (siret := self._siret_resolver.resolve(codesiren, date_creation)) is not None:
            data['siret'] = siret

        elif codesiren is not None:
            data['siret'] = codesiren

        else:
            data['siret'] = codepersonne

        return data
