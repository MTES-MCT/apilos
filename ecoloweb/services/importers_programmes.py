from typing import List, Optional

from programmes.models import Programme, Lot, Logement, ReferenceCadastrale

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

    def _get_o2m_dependencies(self):
        return {
            'cadastre': ReferenceCadastraleImporter(self.debug)
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
        }

    def _get_o2m_dependencies(self):
        return {
            'logement': ProgrammeLogementImporter(self.debug),
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
        }


class ReferenceCadastraleImporter(ModelImporter):
    model = ReferenceCadastrale

    def __init__(self, debug=False):
        super().__init__(debug)
        self._query = self._get_file_content('resources/sql/programme_reference_cadastrale.sql')

    def _prepare_data(self, data: dict) -> dict:
        # Cast numero to int here
        data['numero'] = int(data.pop('raw_numero'))

        superficie = data.pop('superficie', 0)
        if superficie is not None:
            # Compute surface (in hectares / ares / centiares)
            superficie = int(superficie)

            nb_ca = superficie % 100
            nb_a = superficie % 10000 // 100
            nb_ha = superficie // 10000

            data['surface'] = f'{nb_ha} ha {nb_a} a {nb_ca} ca'

        return data

    def _get_sql_one_query(self) -> str:
        return ''

    def _get_sql_many_query(self) -> Optional[str]:
        # No single query defined for Lots, as it's only used to fetch one to many
        return self._query
