from datetime import date

from . import SiretResolver
from .handlers import ModelImporter
from bailleurs.models import Bailleur


class BailleurImporter(ModelImporter):
    model = Bailleur
    sql_template = 'resources/sql/bailleurs.sql'

    def __init__(self):
        super().__init__()
        self._siret_resolver = SiretResolver()

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

        else:
            # TODO we'd rather create a new attribute on Bailleur model for this
            data['siret'] = codepersonne

        return data
