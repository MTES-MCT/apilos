from datetime import datetime
from typing import List, Optional

from programmes.models import Programme, Lot, Logement, ReferenceCadastrale, TypeStationnement

from .importers import ModelImporter
from .importers_administrations import AdministrationImporter
from .importers_bailleurs import BailleurImporter


class ProgrammeImporterSimple(ModelImporter):
    """
    Importer for the Programme model, without one-to-one nor one-to-many dependency
    """
    model = Programme

    def __init__(self, departement: str, import_date: datetime, debug=False):
        super().__init__(departement, import_date, debug)
        self._query = self._get_file_content('resources/sql/programmes.sql')

    def _get_sql_one_query(self) -> str:
        return self._query

    def _get_identity_keys(self) -> List[str]:
        return ['numero_galion']


class ProgrammeImporter(ProgrammeImporterSimple):
    def _get_o2o_dependencies(self):
        return {
            'bailleur': BailleurImporter,
            'administration': AdministrationImporter,
        }

    def _get_o2m_dependencies(self) -> List:
        return [ReferenceCadastraleImporter]


class ProgrammeLotImporterSimple(ModelImporter):
    """
    Importer for the ProgrammeLot model, without one-to-one nor one-to-many dependency
    """
    model = Lot

    def __init__(self, departement: str, import_date: datetime, debug=False):
        super().__init__(departement, import_date, debug)
        self._query_one = self._get_file_content('resources/sql/programme_lots.sql')
        self._query_many = self._get_file_content('resources/sql/programme_lots_many.sql')

    def _get_sql_one_query(self) -> str:
        return self._query_one

    def _get_sql_many_query(self) -> Optional[str]:
        return self._query_many


class ProgrammeLotImporter(ProgrammeLotImporterSimple):
    def _get_o2o_dependencies(self):
        return {
            'programme': ProgrammeImporterSimple,
        }

    def _get_o2m_dependencies(self):
        return [ProgrammeLogementImporter, TypeStationnementImporter]


class ProgrammeLogementImporter(ModelImporter):
    model = Logement

    def __init__(self, departement: str, import_date: datetime, debug=False):
        super().__init__(departement, import_date, debug)
        self._query = self._get_file_content('resources/sql/programme_logements.sql')

    def _get_sql_one_query(self) -> str:
        # No single query defined for Lots, as it's only used to fetch one to many
        return ''

    def _get_sql_many_query(self) -> str:
        return self._query

    def _get_o2o_dependencies(self):
        return {
            'lot': ProgrammeLotImporterSimple,
        }


class ReferenceCadastraleImporter(ModelImporter):
    model = ReferenceCadastrale

    def __init__(self, departement: str, import_date: datetime, debug=False):
        super().__init__(departement, import_date, debug)
        self._query = self._get_file_content('resources/sql/programme_reference_cadastrale.sql')

    def _prepare_data(self, data: dict) -> dict:
        superficie = data.pop('superficie', 0)

        data['surface'] = ReferenceCadastrale.compute_surface(superficie)

        return data

    def _get_sql_one_query(self) -> str:
        # No single query defined here, as it's only used to fetch one to many
        return ''

    def _get_sql_many_query(self) -> Optional[str]:
        return self._query

    def _get_o2o_dependencies(self):
        return {
            'programme': ProgrammeImporterSimple,
        }


class TypeStationnementImporter(ModelImporter):
    model = TypeStationnement

    def __init__(self, departement: str, import_date: datetime, debug=False):
        super().__init__(departement, import_date, debug)
        self._query = self._get_file_content('resources/sql/programme_type_stationnement.sql')

    def _get_sql_one_query(self) -> str:
        # No single query defined here, as it's only used to fetch one to many
        return ''

    def _get_sql_many_query(self) -> Optional[str]:
        return self._query

    def _get_o2o_dependencies(self):
        return {
            'lot': ProgrammeLotImporterSimple,
        }
