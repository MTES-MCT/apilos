from typing import List

from programmes.models import Programme, Lot, Logement

from .handlers import ModelImportHandler
from .handlers_bailleurs import BailleurImportHandler


class ProgrammeImportHandler(ModelImportHandler):
    model = Programme
    sql_template = 'resources/sql/programmes.sql'

    def _get_identity_keys(self) -> List[str]:
        return ['numero_galion']

    def _get_dependencies(self):
        return {
            'bailleur': BailleurImportHandler()
        }


class ProgrammeLotImportHandler(ModelImportHandler):
    model = Lot
    sql_template = 'resources/sql/programme_lots.sql'

    def _get_dependencies(self):
        return {
            'programme': ProgrammeImportHandler(),
            'bailleur': BailleurImportHandler(),
        }


class ProgrammeLogementImportHandler(ModelImportHandler):
    model = Logement
    sql_template = 'resources/sql/programme_logements.sql'

    def _get_dependencies(self):
        return {
            'lot': ProgrammeLotImportHandler(),
            'bailleur': BailleurImportHandler(),
        }
