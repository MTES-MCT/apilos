from typing import List

from programmes.models import Programme, Lot, Logement

from .handlers import ModelImporter
from .handlers_bailleurs import BailleurImporter


class ProgrammeImporter(ModelImporter):
    model = Programme
    sql_template = 'resources/sql/programmes.sql'

    def _get_identity_keys(self) -> List[str]:
        return ['numero_galion']

    def _get_dependencies(self):
        return {
            'bailleur': BailleurImporter()
        }


class ProgrammeLotImporter(ModelImporter):
    model = Lot
    sql_template = 'resources/sql/programme_lots.sql'

    def _get_dependencies(self):
        return {
            'programme': ProgrammeImporter(),
            'bailleur': BailleurImporter(),
        }


class ProgrammeLogementImporter(ModelImporter):
    model = Logement
    sql_template = 'resources/sql/programme_logements.sql'

    def _get_dependencies(self):
        return {
            'lot': ProgrammeLotImporter(),
            'bailleur': BailleurImporter(),
        }
