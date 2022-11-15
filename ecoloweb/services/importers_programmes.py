from typing import List

from programmes.models import Programme, Lot, Logement

from .importers import ModelImporter
from .importers_bailleurs import BailleurImporter


class ProgrammeImporter(ModelImporter):
    model = Programme

    def __init__(self, debug=False):
        super().__init__(debug)
        self._query = self._get_file_content('resources/sql/programmes.sql')

    def _get_sql_one_query(self) -> str:
        return self._query

    def _get_identity_keys(self) -> List[str]:
        return ['numero_galion']

    def _get_o2o_dependencies(self):
        return {
            'bailleur': BailleurImporter()
        }


class ProgrammeLotImporter(ModelImporter):
    model = Lot

    def __init__(self, debug=False):
        super().__init__(debug)
        self._query = self._get_file_content('resources/sql/programme_lots.sql')

    def _get_sql_one_query(self) -> str:
        return self._query

    def _get_o2o_dependencies(self):
        return {
            'programme': ProgrammeImporter(),
            'bailleur': BailleurImporter(),
        }

    def _get_o2m_dependencies(self):
        return {
            'logement': ProgrammeLogementImporter()
        }


class ProgrammeLogementImporter(ModelImporter):
    model = Logement

    def __init__(self, debug=False):
        super().__init__(debug)
        self._query = self._get_file_content('resources/sql/programme_logements.sql')

    def _get_sql_one_query(self) -> str:
        # No single query defined for Lots, as it's only used to fetch one to many
        return ''

    def _get_sql_many_query(self) -> str:
        return self._query

    def _get_o2o_dependencies(self):
        return {
            'lot': ProgrammeLotImporter(),
            'bailleur': BailleurImporter(),
        }
